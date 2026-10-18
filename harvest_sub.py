"""通用子站收割器：从缓存 CDX 中抓指定子域的已存档页面"""
import os, re, sys, json
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mirror as M

BASE = os.path.dirname(os.path.abspath(__file__))
CDX = os.path.join(BASE, "_cdx", "cdx_njlsedu_www.txt")
PROXIES = [l.strip() for l in open(
    os.path.join(BASE, "..", "clash-run", "proxies.txt"), encoding="utf-8") if l.strip()]

sub = sys.argv[1]                       # 如 lsjyj
out = sys.argv[2] if len(sys.argv) > 2 else f"site_{sub}"
OUT = os.path.join(BASE, out)
os.makedirs(OUT, exist_ok=True)

pat = re.compile(r"https?://" + re.escape(sub) + r"\.njlsedu\.cn(:80)?/")
rows = {}
for line in open(CDX, encoding="utf-8", errors="replace"):
    p = line.split()
    if len(p) < 4 or not p[0].isdigit() or p[2] != "200":
        continue
    if not pat.match(p[1]):
        continue
    u = M.norm_url(p[1])
    if u.lower().endswith((".css", ".js")):
        continue
    rows.setdefault(u, []).append(p[0])

print(f"{sub}.njlsedu.cn: {len(rows)} 个可抓页面", flush=True)

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
          open(os.path.join(BASE, f"urlmap_{out}.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
