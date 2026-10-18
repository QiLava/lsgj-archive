"""用 HTTP 实测坏链目标，分辨真 404 与误报（目录重定向等）"""
import os, json, urllib.request as uq, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = os.path.dirname(os.path.abspath(__file__))
PORT = 8897

d = json.load(open(os.path.join(BASE, "broken_clickable.json"), encoding="utf-8"))
targets = sorted(d.keys(), key=lambda k: -d[k]["count"])
print(f"待实测 {len(targets)} 个坏链目标", flush=True)

op = uq.build_opener(uq.ProxyHandler({}))


class NoRedirect(uq.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


noop = uq.build_opener(uq.ProxyHandler({}), NoRedirect)


def probe(tgt):
    url = f"http://127.0.0.1:{PORT}/" + tgt
    try:
        with noop.open(url, timeout=8) as r:
            return tgt, r.status, r.headers.get("Location", "")
    except urllib.error.HTTPError as e:
        return tgt, e.code, e.headers.get("Location", "") if e.headers else ""
    except Exception as e:
        return tgt, 0, str(e)[:40]


real404 = {}
not404 = []
with ThreadPoolExecutor(max_workers=16) as ex:
    futs = [ex.submit(probe, t) for t in targets]
    for n, f in enumerate(as_completed(futs), 1):
        tgt, code, loc = f.result()
        if code == 404:
            real404[tgt] = d[tgt]["count"]
        else:
            not404.append((tgt, code, loc))
        if n % 200 == 0:
            print(f"  {n}/{len(targets)}  真404={len(real404)}", flush=True)

print(f"\n实测结果：真 404 {len(real404)} 个，非 404 {len(not404)} 个")
print(f"真 404 的引用总次数: {sum(real404.values())}")
print()
print("=== 非 404 的（说明是误报）===")
for tgt, code, loc in not404[:10]:
    print(f"  {code}  {tgt[:60]}  -> {loc[:50]}")

print()
print("=== 真 404 被点最多的 Top 20 ===")
for tgt, n in sorted(real404.items(), key=lambda x: -x[1])[:20]:
    print(f"  {n:>5} 次  {tgt[:76]}")

json.dump(real404, open(os.path.join(BASE, "real404.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\n已写入 real404.json")
