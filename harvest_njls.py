"""从区教育网精准提取涉及省溧中的文章：
1. 下载全部栏目标题页（t=arts）
2. 提取文章标题+链接
3. 按关键词筛选
4. 只下载匹配的文章
"""
import os, re, sys, json, time, urllib.parse as up
import urllib.request as uq
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mirror as M

BASE = os.path.dirname(os.path.abspath(__file__))
CDX = os.path.join(BASE, "_cdx", "cdx_njlsedu_www.txt")
OUT = os.path.join(BASE, "site_njls")
TMP = os.path.join(BASE, "_tmp", "njls_lists")
os.makedirs(OUT, exist_ok=True)
os.makedirs(TMP, exist_ok=True)

PROXIES = [l.strip() for l in open(
    os.path.join(BASE, "..", "clash-run", "proxies.txt"), encoding="utf-8") if l.strip()]

KEYWORDS = ("省溧中", "溧水高级中学", "溧中", "省溧中附")

# ---------- 1. 收集栏目标题页 ----------
list_pages = {}
for line in open(CDX, encoding="utf-8", errors="replace"):
    p = line.split()
    if len(p) < 4 or not p[0].isdigit() or p[2] != "200":
        continue
    if "t=arts" in p[1]:
        list_pages[M.norm_url(p[1])] = p[0]
print(f"栏目标题页: {len(list_pages)} 个", flush=True)


def dl(url, ts, px):
    d, _ = M.fetch_multi(url, [ts, "2019", "2020", "2021"], proxy=px, max_try=3)
    return d


todo = [(u, ts) for u, ts in list_pages.items()
        if not os.path.exists(os.path.join(TMP, M.local_path(u).replace("/", os.sep)))]
print(f"待下载 {len(todo)}", flush=True)

ok = 0
with ThreadPoolExecutor(max_workers=14) as ex:
    futs = {ex.submit(dl, u, ts, PROXIES[i % len(PROXIES)]): u
            for i, (u, ts) in enumerate(todo)}
    for n, f in enumerate(as_completed(futs), 1):
        u = futs[f]
        d = f.result()
        if d:
            dst = os.path.join(TMP, M.local_path(u).replace("/", os.sep))
            os.makedirs(os.path.dirname(dst) or TMP, exist_ok=True)
            with open(dst, "wb") as fh:
                fh.write(d)
            ok += 1
        if n % 50 == 0:
            print(f"  {n}/{len(todo)}  成功={ok}", flush=True)
print(f"标题页下载完成: {ok}/{len(todo)}", flush=True)

# ---------- 2. 提取文章标题+链接 ----------
ART = re.compile(r'<a[^>]+href=["\']([^"\']*t=article[^"\']*)["\'][^>]*>(.*?)</a>', re.I | re.S)
found = {}
for dp, _, fs in os.walk(TMP):
    for f in fs:
        if not f.endswith(".html"):
            continue
        raw = open(os.path.join(dp, f), "rb").read()
        try:
            t = raw.decode("utf-8")
        except UnicodeDecodeError:
            t = raw.decode("gbk", "replace")
        for m in ART.finditer(t):
            href = m.group(1)
            title = re.sub(r"<[^>]+>", "", m.group(2))
            title = re.sub(r"\s+", " ", title).strip()
            if not title or len(title) < 4:
                continue
            abs_u = up.urljoin("http://www.njlsedu.cn/", href)
            pu = up.urlparse(abs_u)
            norm = up.urlunparse((pu.scheme, pu.netloc.replace(":80", ""),
                                  pu.path, "", pu.query, ""))
            if any(k in title for k in KEYWORDS):
                found[norm] = title

print(f"\n标题命中学校关键词的文章: {len(found)} 篇", flush=True)
for u, t in list(found.items())[:20]:
    print(f"  {t[:50]}")
json.dump(found, open(os.path.join(BASE, "njls_school_articles.json"), "w",
                      encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------- 3. 下载匹配文章 ----------
todo2 = [(u, t) for u, t in found.items()
         if not os.path.exists(os.path.join(OUT, M.local_path(u).replace("/", os.sep)))]
print(f"\n待下载文章 {len(todo2)} 篇", flush=True)

ok2 = 0
with ThreadPoolExecutor(max_workers=14) as ex:
    futs = {ex.submit(dl, u, "2019", PROXIES[i % len(PROXIES)]): (u, t)
            for i, (u, t) in enumerate(todo2)}
    for n, f in enumerate(as_completed(futs), 1):
        u, t = futs[f]
        d = f.result()
        if d:
            dst = os.path.join(OUT, M.local_path(u).replace("/", os.sep))
            os.makedirs(os.path.dirname(dst) or OUT, exist_ok=True)
            with open(dst, "wb") as fh:
                fh.write(d)
            ok2 += 1
        if n % 25 == 0:
            print(f"  {n}/{len(todo2)}  成功={ok2}", flush=True)

print(f"\n文章下载完成: {ok2}/{len(todo2)}", flush=True)
json.dump({u: M.local_path(u) for u in found},
          open(os.path.join(BASE, "urlmap_site_njls.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
