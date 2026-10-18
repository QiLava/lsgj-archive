"""扫描已下载文件里的停靠页，删掉以便重新抓取"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mirror as M

site = sys.argv[1]
umap = sys.argv[2]

urlmap = json.load(open(umap, encoding="utf-8"))
rev = {}
for u, lp in urlmap.items():
    rev.setdefault(lp.replace("/", os.sep), u)

parked, checked = [], 0
for dirpath, _, files in os.walk(site):
    for f in files:
        p = os.path.join(dirpath, f)
        if not f.lower().endswith((".html", ".htm")):
            continue
        try:
            raw = open(p, "rb").read()
        except OSError:
            continue
        checked += 1
        if M.is_parked(raw):
            rel = os.path.relpath(p, site).replace("\\", "/")
            parked.append(rel)

print(f"检查 {checked} 个 HTML，发现 {len(parked)} 个停靠页")
for p in parked[:30]:
    print("  ", p)
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       f"parked_{os.path.basename(site)}.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(parked))
print(f"清单已写入 parked_{os.path.basename(site)}.txt")
