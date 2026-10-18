"""全量下载区教育网主站 www.njlsedu.cn 的 1136 篇已存档文章"""
import os, re, sys, json
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mirror as M

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "site_njls")
os.makedirs(OUT, exist_ok=True)
PROXIES = [l.strip() for l in open(
    os.path.join(BASE, "..", "clash-run", "proxies.txt"), encoding="utf-8") if l.strip()]

# 只取 www.njlsedu.cn 精确域名的文章
rows = {}
for line in open(os.path.join(BASE, "_cdx", "cdx_njlsedu_www.txt"),
                 encoding="utf-8", errors="replace"):
    p = line.split()
    if len(p) < 4 or not p[0].isdigit() or p[2] != "200":
        continue
    u = p[1]
    if not re.match(r"https?://www\.njlsedu\.cn(:80)?/\?t=article", u):
        continue
    rows.setdefault(M.norm_url(u), []).append(p[0])

print(f"www.njlsedu.cn 文章: {len(rows)} 篇", flush=True)

todo = [(u, sorted(sts, reverse=True)) for u, sts in rows.items()
        if not os.path.exists(os.path.join(OUT, M.local_path(u).replace("/", os.sep)))]
print(f"待下载 {len(todo)}", flush=True)

ok = 0
with ThreadPoolExecutor(max_workers=14) as ex:
    futs = {ex.submit(M.fetch_multi, u, sts, PROXIES[i % len(PROXIES)]): u
            for i, (u, sts) in enumerate(todo)}
    for n, f in enumerate(as_completed(futs), 1):
        u = futs[f]
        d, ts = f.result()
        if d:
            dst = os.path.join(OUT, M.local_path(u).replace("/", os.sep))
            os.makedirs(os.path.dirname(dst) or OUT, exist_ok=True)
            with open(dst, "wb") as fh:
                fh.write(d)
            ok += 1
        if n % 100 == 0:
            print(f"  {n}/{len(todo)}  成功={ok}", flush=True)

print(f"\n完成：成功 {ok}/{len(todo)}", flush=True)
json.dump({u: M.local_path(u) for u in rows},
          open(os.path.join(BASE, "urlmap_site_njls.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
