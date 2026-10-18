"""试探性补抓：CDX 未记录但页面在引用的栏目页（并发版）"""
import json, re, os, sys, urllib.parse as up
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mirror as M

PROXIES = [l.strip() for l in open(
    r"C:\Users\QiLava\WorkBuddy\2026-10-18-03-37-58\clash-run\proxies.txt",
    encoding="utf-8") if l.strip()]

urlmap = json.load(open("urlmap_site_old.json", encoding="utf-8"))

# 收集所有站内未存档链接
want = {}
for dp, _, fs in os.walk("site_old"):
    for f in fs:
        if not f.endswith(".html"):
            continue
        p = os.path.join(dp, f)
        r2 = open(p, "rb").read()
        try:
            t2 = r2.decode("utf-8")
        except UnicodeDecodeError:
            t2 = r2.decode("gbk", "replace")
        for l in re.findall(r'href=["\']([^"\']+)["\']', t2):
            if "archive.org" in l or l.startswith(("#", "javascript:", "mailto:", "file:")):
                continue
            a = up.urljoin("http://www.lsgjzx.cn/", l)
            p_ = up.urlparse(a)
            net = p_.netloc.replace(":80", "")
            if "lsgjzx.cn" not in net:
                continue
            n = up.urlunparse((p_.scheme, net, p_.path, "", p_.query, ""))
            if n not in urlmap:
                want[n] = M.local_path(n)

# 只补列表页/栏目页，且目标文件不存在
todo = []
for u, lp in want.items():
    if not any(k in u for k in ("list.php", "bencandy.php", "index.php")):
        continue
    dst = os.path.join("site_old", lp.replace("/", os.sep))
    if os.path.exists(dst) and os.path.getsize(dst) > 0:
        continue
    todo.append((u, lp))

print(f"候选未存档站内页 {len(want)} 个，可尝试补抓 {len(todo)} 个", flush=True)

STAMPS = ["20170213", "20160822", "20160108"]
ok, fail = 0, 0
results = []


def job(args):
    i, (u, lp) = args
    px = PROXIES[i % len(PROXIES)]
    d, ts = M.fetch_multi(u, STAMPS, proxy=px, max_try=3)
    return u, lp, d, ts


with ThreadPoolExecutor(max_workers=14) as ex:
    futs = [ex.submit(job, (i, t)) for i, t in enumerate(todo)]
    for n, f in enumerate(as_completed(futs), 1):
        u, lp, d, ts = f.result()
        if d and not M.is_parked(d):
            dst = os.path.join("site_old", lp.replace("/", os.sep))
            os.makedirs(os.path.dirname(dst) or "site_old", exist_ok=True)
            with open(dst, "wb") as fh:
                fh.write(d)
            urlmap[u] = lp
            results.append((u, lp))
            ok += 1
            if ok <= 15:
                print(f"  [OK] {len(d):>6}B  {lp}", flush=True)
        else:
            fail += 1
        if n % 20 == 0:
            print(f"  ... {n}/{len(todo)}  成功={ok} 失败={fail}", flush=True)

print(f"\n补抓完成：成功 {ok}，失败 {fail}", flush=True)
json.dump(urlmap, open("urlmap_site_old.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("映射表已更新", flush=True)
