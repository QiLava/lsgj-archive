"""扫描全站坏链：提取所有页面里的链接，解析成本地路径，检查文件是否存在"""
import os, re, posixpath, collections, json

BASE = os.path.dirname(os.path.abspath(__file__))
SITES = ["site_old", "site_new", "site_vod", "site_students", "site_njls", "site_lsjyj"]

ATTR = re.compile(r'(?:href|src|action|background)\s*=\s*(["\'])(.*?)\1', re.I)
CSSU = re.compile(r'url\(\s*(["\']?)([^"\')]+)\1\s*\)', re.I)
#  JS 里的跳转 location.href="..." / window.open("...")
JSNAV = re.compile(r'(?:location\.href|window\.open|location\.replace)\s*\(?\s*["\']([^"\']+)["\']', re.I)

broken = collections.Counter()      # 坏链目标 -> 次数
broken_from = collections.defaultdict(set)   # 坏链目标 -> 引用它的页面（取样）
total_links = 0
ext_links = 0

for site in SITES:
    root = os.path.join(BASE, site)
    if not os.path.isdir(root):
        continue
    for dp, _, fs in os.walk(root):
        for f in fs:
            if not f.lower().endswith((".html", ".htm", ".css", ".js")):
                continue
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, BASE).replace("\\", "/")
            base_dir = posixpath.dirname(rel)
            raw = open(p, "rb").read()
            try:
                t = raw.decode("utf-8")
            except UnicodeDecodeError:
                t = raw.decode("gbk", "replace")

            vals = [m.group(2) for m in ATTR.finditer(t)]
            vals += [m.group(2) for m in CSSU.finditer(t)]
            vals += JSNAV.findall(t)

            for v in vals:
                v = v.strip()
                if not v:
                    continue
                if v.startswith(("#", "data:", "mailto:", "tel:", "javascript:",
                                 "about:", "blob:")):
                    continue
                if v.startswith(("http://", "https://", "//")):
                    ext_links += 1
                    continue
                # 站内相对/绝对路径
                path = v.split("?")[0].split("#")[0]
                if not path:
                    continue
                if path.startswith("/"):
                    # 站点根绝对路径 -> 相对当前站点目录
                    tgt = site + path
                else:
                    tgt = posixpath.normpath(posixpath.join(base_dir, path))
                total_links += 1
                fp = os.path.join(BASE, tgt.replace("/", os.sep))
                if not (os.path.isfile(fp) and os.path.getsize(fp) > 0):
                    broken[tgt] += 1
                    if len(broken_from[tgt]) < 4:
                        broken_from[tgt].add(rel)

print(f"站内链接总数: {total_links}   外链数: {ext_links}")
print(f"坏链目标数: {len(broken)}   坏链引用次数: {sum(broken.values())}")
print()

# 归类
cats = collections.Counter()
for tgt in broken:
    if "index.php" in tgt:
        cats["index.php? 动态页（早期系统）"] += 1
    elif "list.php" in tgt:
        cats["list.php 列表页（未存档）"] += 1
    elif "bencandy.php" in tgt:
        cats["bencandy.php 文章页（未存档）"] += 1
    elif re.search(r"\.(css|js)$", tgt):
        cats["CSS/JS 资源"] += 1
    elif re.search(r"\.(jpg|jpeg|png|gif|ico|swf|bmp)$", tgt, re.I):
        cats["图片资源"] += 1
    elif tgt.endswith("/"):
        cats["目录路径"] += 1
    else:
        cats["其他"] += 1

print("=== 坏链分类 ===")
for k, v in cats.most_common():
    print(f"  {v:>5} 个目标  {k}")

print()
print("=== 被引用最多的坏链 Top 20 ===")
for tgt, n in broken.most_common(20):
    print(f"  {n:>5} 次  {tgt[:78]}")

json.dump({k: {"count": v, "from": sorted(broken_from[k])}
           for k, v in broken.items()},
          open(os.path.join(BASE, "broken_links.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\n明细已写入 broken_links.json")
