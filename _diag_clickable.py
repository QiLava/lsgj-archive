"""只扫描 <a href> 可点击链接的 404 情况（用户实际点到的）"""
import os, re, posixpath, collections, json

BASE = os.path.dirname(os.path.abspath(__file__))
SITES = ["site_old", "site_new", "site_vod", "site_students", "site_njls", "site_lsjyj"]

A_HREF = re.compile(r'<a\b[^>]*?\bhref\s*=\s*(["\'])(.*?)\1', re.I)

broken = collections.Counter()
broken_from = collections.defaultdict(set)
total = 0
ok = 0
ext = 0

for site in SITES:
    root = os.path.join(BASE, site)
    if not os.path.isdir(root):
        continue
    for dp, _, fs in os.walk(root):
        for f in fs:
            if not f.lower().endswith((".html", ".htm")):
                continue
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, BASE).replace("\\", "/")
            base_dir = posixpath.dirname(rel)
            raw = open(p, "rb").read()
            try:
                t = raw.decode("utf-8")
            except UnicodeDecodeError:
                t = raw.decode("gbk", "replace")
            # 去掉 script 块，避免误解析
            t = re.sub(r"<script\b[^>]*>.*?</script>", "", t, flags=re.I | re.S)

            for m in A_HREF.finditer(t):
                v = m.group(2).strip()
                if not v:
                    continue
                if v.startswith(("#", "data:", "mailto:", "tel:", "javascript:",
                                 "about:", "blob:", "javacript:")):
                    continue
                if v.startswith(("http://", "https://", "//")):
                    ext += 1
                    continue
                path = v.split("?")[0].split("#")[0]
                if not path:
                    continue
                if path.startswith("/"):
                    tgt = site + path
                else:
                    tgt = posixpath.normpath(posixpath.join(base_dir, path))
                total += 1
                fp = os.path.join(BASE, tgt.replace("/", os.sep))
                if os.path.isfile(fp) and os.path.getsize(fp) > 0:
                    ok += 1
                else:
                    broken[tgt] += 1
                    if len(broken_from[tgt]) < 3:
                        broken_from[tgt].add(rel)

print(f"可点击链接总数: {total}")
print(f"  正常: {ok}   外链: {ext}   坏链: {sum(broken.values())}")
print(f"  坏链目标数: {len(broken)}")
print()

print("=== 坏链形态分布（按扩展名/模式）===")
cats = collections.Counter()
for tgt in broken:
    b = tgt.split("/")[-1]
    if ".php" in b:
        cats[f"{b.split('?')[0]} 动态页（未存档）"] += 1
    elif re.search(r"\.(css|js)$", b):
        cats["CSS/JS"] += 1
    elif re.search(r"\.(jpg|jpeg|png|gif|ico|swf|bmp)$", b, re.I):
        cats["图片"] += 1
    elif tgt.endswith("/"):
        cats["目录"] += 1
    elif not os.path.splitext(b)[1]:
        cats["无扩展名路径"] += 1
    else:
        cats["其他 " + os.path.splitext(b)[1]] += 1
for k, v in cats.most_common(15):
    print(f"  {v:>5} 个目标  {k}")

print()
print("=== 被点最多的坏链 Top 25 ===")
for tgt, n in broken.most_common(25):
    print(f"  {n:>5} 次  {tgt[:76]}")

json.dump({k: {"count": v, "from": sorted(broken_from[k])}
           for k, v in broken.items()},
          open(os.path.join(BASE, "broken_clickable.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\n明细已写入 broken_clickable.json")
