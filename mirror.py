"""
Wayback 全站镜像抓取 —— 江苏省溧水高级中学
用法: python mirror.py <cdx_file> <cdx_full_file> <out_dir> [--workers 16]
"""
import os, sys, json, time, re, hashlib, urllib.parse as up
import urllib.request as uq
from concurrent.futures import ThreadPoolExecutor, as_completed

PROXY = "http://127.0.0.1:7890"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

# 多出口分流：每个本地端口对应一个独立的 Clash 实例/节点（不同出口 IP）
PROXIES = [PROXY] + [f"http://127.0.0.1:789{i}" for i in range(1, 12)]

import threading
_openers = {}
_olock = threading.Lock()


def get_opener(proxy):
    with _olock:
        if proxy not in _openers:
            o = uq.build_opener(uq.ProxyHandler({"http": proxy, "https": proxy}),
                                uq.HTTPRedirectHandler())
            o.addheaders = [("User-Agent", UA),
                            ("Accept", "*/*"),
                            ("Accept-Language", "zh-CN,zh;q=0.9,en;q=0.8")]
            _openers[proxy] = o
        return _openers[proxy]


# ---------------- URL -> 本地路径 ----------------
def norm_url(u):
    """去掉 :80 端口、末尾多余斜杠"""
    p = up.urlparse(u)
    netloc = p.netloc.replace(":80", "").replace(":443", "")
    return up.urlunparse((p.scheme, netloc, p.path, p.params, p.query, p.fragment))


def qmap(query):
    """解析 fid-124-id-1737-page-1.htm 这类 '-' 分隔格式"""
    seg = query.replace(".htm", "").split("-")
    d = {}
    for i in range(0, len(seg) - 1, 2):
        d[seg[i]] = seg[i + 1]
    return d


def slug(s):
    return hashlib.md5(s.encode("utf-8")).hexdigest()[:8]


def local_path(url):
    p = up.urlparse(url)
    path = p.path or "/"
    query = p.query or ""
    qs = up.parse_qs(query)
    base = path.rsplit("/", 1)[-1]

    # --- 静态资源：保持原路径 ---
    if base and "." in base and not base.endswith(".php") and not base.endswith(".aspx"):
        return path.lstrip("/") or "index.html"

    # --- 首页 ---
    if path in ("", "/") and not query:
        return "index.html"
    if path in ("/index.php", "/index.php/") and query.strip() in ("", "?", "&"):
        return "index.html"

    # --- PHP168 齐博 CMS ---
    if base == "bencandy.php":
        m = qmap(query)
        fid, aid, pg = m.get("fid", "0"), m.get("id", "0"), m.get("page", "1")
        return f"art_f{fid}_i{aid}_p{pg}.html"
    if base == "list.php":
        m = qmap(query)
        return f"list_f{m.get('fid', '0')}_p{m.get('page', '1')}.html"

    # --- 早期 Mambo 风格 index.php ---
    if base == "index.php":
        task = (qs.get("task") or [""])[0]
        oid = (qs.get("id") or [""])[0]
        itemid = (qs.get("Itemid") or [""])[0]
        if task == "view" and oid:
            return f"art_v{oid}.html"
        if task == "category" and oid:
            return f"cat_{oid}_{itemid or '0'}.html"
        if oid:
            return f"page_{oid}_{itemid or '0'}.html"
        if query:
            return f"page_{slug(query)}.html"
        return "index.html"

    # --- 新站 ?t=... 模式 (lsgj.njlsedu.cn) ---
    t = (qs.get("t") or [""])[0]
    c = (qs.get("c") or [""])[0]
    i = (qs.get("id") or [""])[0]
    if t == "index" or (not t and not path.strip("/")):
        return "index.html" if not c else f"index_c{c}.html"
    if t == "arts" and c:
        return f"list_c{c}.html"
    if t == "arts2" and c:
        return f"sub_c{c}.html"
    if t == "article" and c and i:
        return f"art_c{c}_{i}.html"
    if t == "index_wap":
        return "m/index.html"
    if t:
        return f"page_{t}_{c}_{i}.html".replace("__", "_")

    # --- 其他动态页 ---
    if query:
        stem = re.sub(r"[^A-Za-z0-9]", "", base.split(".")[0]) or "p"
        return f"{stem}_{slug(query)}.html"
    if path and path != "/":
        return path.lstrip("/").rstrip("/") or "index.html"
    return "index.html"


SKIP_EXT = (".php", ".aspx", ".asp", ".jsp")
SKIP_KW = ("robots.txt", "do/hack.php", "Ajax/Default.aspx", "admin/")


def load_cdx(path_cdx):
    rows = {}
    for line in open(path_cdx, encoding="utf-8", errors="replace"):
        parts = line.split()
        if len(parts) < 4 or not parts[0].isdigit():
            continue
        ts, url, status, mime = parts[0], parts[1], parts[2], parts[3]
        if status != "200":
            continue
        url = norm_url(url)
        if any(k in url for k in SKIP_KW):
            continue
        if url.lower().endswith(SKIP_EXT) and "?" not in url:
            continue
        rows[url] = (ts, mime)
    return rows


def load_full(path_full):
    """url -> [ts...] 全部时间戳，倒序（最新优先）"""
    m = {}
    for line in open(path_full, encoding="utf-8", errors="replace"):
        parts = line.split()
        if len(parts) < 3 or not parts[0].isdigit():
            continue
        ts, url, status = parts[0], parts[1], parts[2]
        if status != "200":
            continue
        m.setdefault(norm_url(url), []).append(ts)
    for k in m:
        m[k] = sorted(set(m[k]), reverse=True)
    return m


# ---------------- 抓取 ----------------
_last_429 = [0.0] * 16
_lock_429 = threading.Lock()
_gate = [0.0] * 16


def _slot(proxy):
    return PROXIES.index(proxy) % 16


def _throttle(proxy, min_gap=0.12):
    s = _slot(proxy)
    with _lock_429:
        now = time.time()
        wait = max(0.0, _gate[s] - now)
        _gate[s] = now + wait + min_gap
    if wait > 0:
        time.sleep(wait)


def fetch(url, ts, mode="id_", retries=3, proxy=PROXY):
    target = f"https://web.archive.org/web/{ts}{mode}/{url}"
    s = _slot(proxy)
    for k in range(retries):
        try:
            _throttle(proxy)
            req = uq.Request(target, headers={"User-Agent": UA})
            with get_opener(proxy).open(req, timeout=90) as r:
                data = r.read()
                if len(data) < 200 and b"Temporarily Offline" in data:
                    raise RuntimeError("IA offline")
                return data
        except Exception as e:
            msg = str(e)
            code = getattr(e, "code", None)
            if code in (429, 502, 503) or "429" in msg or "Too Many" in msg:
                with _lock_429:
                    _gate[s] = max(_gate[s], time.time() + 12)
                if k == retries - 1:
                    return None
                time.sleep(2 + 3 * k)
                continue
            if k == retries - 1:
                return None
            time.sleep(1.5 + 2.5 * k)
    return None


PARK_MARKERS = (
    b"www.4.cn", b"stencil-overall", b"stencil-tip", b"domain-name",
    b"a-header", b"you are visiting",
    "\xe6\x82\xa8\xe6\xad\xa3\xe5\x9c\xa8\xe8\xae\xbf\xe9\x97\xae".encode("latin-1").decode("utf-8").encode("utf-8"),
    "\xe5\xae\x98\xe7\xbd\x91\xe9\xa6\x96\xe9\xa1\xb5".encode("latin-1").decode("utf-8").encode("utf-8"),
)


def is_parked(data):
    """域名过期后的停靠/停放页检测（不看体积，停靠页也可能很大）"""
    if not data:
        return True
    head = data[:8000]
    hits = sum(1 for m in PARK_MARKERS if m in head)
    return hits >= 2


def fetch_multi(url, stamps, proxy=PROXY, max_try=6):
    """遍历多个时间戳，直到拿到非停靠页的内容"""
    fallback = None
    ordered = list(stamps)
    if url.rstrip("/").count("/") <= 2:      # 首页类 URL
        ordered = ordered[len(ordered) // 3:] + ordered[:len(ordered) // 3]
    for ts in ordered[:max_try]:
        for mode in ("id_", ""):
            d = fetch(url, ts, mode, retries=2, proxy=proxy)
            if not d:
                continue
            if not is_parked(d):
                return d, ts
            if fallback is None:
                fallback = (d, ts)
    return fallback if fallback else (None, None)


# ---------------- 主流程 ----------------
def safe_dst(dst):
    """避免文件名与已存在的目录冲突"""
    if os.path.isdir(dst):
        cand = dst + ".html"
        n = 1
        while os.path.isdir(cand):
            cand = f"{dst}_{n}.html"
            n += 1
        return cand
    return dst


def main():
    cdx_f, full_f, out_dir = sys.argv[1], sys.argv[2], sys.argv[3]
    workers = 8
    if "--workers" in sys.argv:
        workers = int(sys.argv[sys.argv.index("--workers") + 1])
    if "--proxies" in sys.argv:
        pf = sys.argv[sys.argv.index("--proxies") + 1]
        PROXIES[:] = [l.strip() for l in open(pf, encoding="utf-8") if l.strip()]

    base = os.path.dirname(os.path.abspath(__file__))
    cdx_f = os.path.join(base, cdx_f) if not os.path.isabs(cdx_f) else cdx_f
    full_f = os.path.join(base, full_f) if not os.path.isabs(full_f) else full_f
    out_dir = os.path.join(base, out_dir) if not os.path.isabs(out_dir) else out_dir
    os.makedirs(out_dir, exist_ok=True)

    rows = load_cdx(cdx_f)
    stamps = load_full(full_f)
    url_map = {u: local_path(u) for u in rows}
    print(f"清单 {len(rows)} 个文件 -> {out_dir}", flush=True)

    todo = []
    for u, (ts, mime) in rows.items():
        dst = os.path.join(out_dir, url_map[u].replace("/", os.sep))
        dst = safe_dst(dst)
        os.makedirs(os.path.dirname(dst) or out_dir, exist_ok=True)
        if os.path.exists(dst) and os.path.getsize(dst) > 0:
            continue
        todo.append((u, dst))

    print(f"待下载 {len(todo)}（已存在 {len(rows)-len(todo)}）", flush=True)
    print(f"出口分流: {len(PROXIES)} 个代理端口", flush=True)

    fail = []
    done = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {}
        for idx, (u, d) in enumerate(todo):
            px = PROXIES[idx % len(PROXIES)]
            futs[ex.submit(fetch_multi, u, stamps.get(u, [""]), px)] = (u, d)
        for f in as_completed(futs):
            u, dst = futs[f]
            data, ts = f.result()
            done += 1
            if data is None:
                fail.append(u)
            else:
                with open(safe_dst(dst), "wb") as fh:
                    fh.write(data)
            if done % 50 == 0:
                print(f"  {done}/{len(todo)}  失败={len(fail)}", flush=True)

    print(f"完成：成功 {done-len(fail)} / 失败 {len(fail)}")
    tag = os.path.basename(out_dir)
    with open(os.path.join(base, f"failed_{tag}.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(fail))
    json.dump(url_map, open(os.path.join(base, f"urlmap_{tag}.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"映射表: urlmap_{tag}.json")


if __name__ == "__main__":
    main()
