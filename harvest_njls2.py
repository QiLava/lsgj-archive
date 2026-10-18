"""修正版：只用 CDX 里真实存在的时间戳下载学校文章"""
import os, re, sys, json, urllib.parse as up
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mirror as M

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "site_njls")
os.makedirs(OUT, exist_ok=True)
PROXIES = [l.strip() for l in open(
    os.path.join(BASE, "..", "clash-run", "proxies.txt"), encoding="utf-8") if l.strip()]

# 从 CDX 建 URL -> [时间戳]（协议不敏感，http/https 视为同一 URL）
def key(u):
    p = up.urlparse(u)
    return (p.netloc.replace(":80", "").replace(":443", ""), p.path, p.query)


cdx = {}
for line in open(os.path.join(BASE, "_cdx", "cdx_njlsedu_www.txt"),
                 encoding="utf-8", errors="replace"):
    p = line.split()
    if len(p) < 4 or not p[0].isdigit() or p[2] != "200":
        continue
    cdx.setdefault(key(p[1]), []).append(p[0])

arts = json.load(open(os.path.join(BASE, "njls_school_articles.json"), encoding="utf-8"))

# 只保留 CDX 里真有存档的
avail = {u: t for u, t in arts.items() if key(u) in cdx}
print(f"候选 {len(arts)} 篇，其中 CDX 确有存档 {len(avail)} 篇\n", flush=True)

todo = [(u, cdx[key(u)]) for u in avail
        if not os.path.exists(os.path.join(OUT, M.local_path(u).replace("/", os.sep)))]
print(f"待下载 {len(todo)} 篇", flush=True)

ok = 0
with ThreadPoolExecutor(max_workers=12) as ex:
    futs = {ex.submit(M.fetch_multi, u, sorted(sts, reverse=True),
                      PROXIES[i % len(PROXIES)]): (u, t)
            for i, (u, sts) in enumerate(todo)}
    for n, f in enumerate(as_completed(futs), 1):
        u, title = futs[f]
        d, ts = f.result()
        if d:
            dst = os.path.join(OUT, M.local_path(u).replace("/", os.sep))
            os.makedirs(os.path.dirname(dst) or OUT, exist_ok=True)
            with open(dst, "wb") as fh:
                fh.write(d)
            ok += 1
            print(f"  [OK] {len(d):>6}B {title[:44]}", flush=True)
        if n % 10 == 0:
            print(f"  ... {n}/{len(todo)} 成功={ok}", flush=True)

print(f"\n完成：成功 {ok}/{len(todo)}", flush=True)
json.dump({u: M.local_path(u) for u in avail},
          open(os.path.join(BASE, "urlmap_site_njls.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
