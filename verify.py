"""本地站点健康度验证：抽样页面 200 + 资源命中率"""
import os, re, sys, random, urllib.request as uq

site = sys.argv[1]
port = sys.argv[2] if len(sys.argv) > 2 else "8899"
random.seed(42)

htmls = []
for dp, _, fs in os.walk(site):
    for f in fs:
        if f.lower().endswith((".html", ".htm")):
            htmls.append(os.path.join(dp, f))
random.shuffle(htmls)
sample = htmls[:60]

ATTR = re.compile(r'(?:href|src|action|background)\s*=\s*(["\'])(.*?)\1', re.I)
CSSU = re.compile(r'url\(\s*(["\']?)([^"\')]+)\1\s*\)', re.I)

op = uq.build_opener(uq.ProxyHandler({}))
uq.install_opener(op)


def head(path):
    try:
        with op.open(f"http://127.0.0.1:{port}/{path}", timeout=10) as r:
            return r.status, len(r.read())
    except Exception as e:
        return 0, 0


print(f"=== {site} 页面抽样（{len(sample)}/{len(htmls)}）===")
bad_page = 0
for p in sample:
    rel = os.path.relpath(p, site).replace("\\", "/")
    st, sz = head(rel)
    if st != 200 or sz < 500:
        bad_page += 1
        print(f"  [BAD] {st} {sz}B {rel}")
print(f"页面异常: {bad_page}/{len(sample)}")

print(f"\n=== 资源命中率（抽样 40 个页面，HTTP 实查）===")
total_ref = hit = miss = 0
misslist = []
import posixpath
for p in sample[:40]:
    rel = os.path.relpath(p, site).replace("\\", "/")
    base = os.path.dirname(rel)
    raw = open(p, "rb").read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("gbk", "replace")
    refs = [m.group(2) for m in ATTR.finditer(text)]
    for m in CSSU.finditer(text):
        refs.append(m.group(2))
    for r in refs:
        r = r.strip()
        if not r or r.startswith(("http://", "https://", "//", "mailto:", "tel:",
                                  "javascript:", "#", "data:", "about:")):
            continue
        # 查询串由改写阶段处理，这里只验真实文件路径
        if "?" in r:
            continue
        r = r.split("#")[0]
        if not r or r in (".", ".."):
            continue
        tgt = posixpath.normpath(posixpath.join(base, r)).replace("\\", "/")
        total_ref += 1
        st, sz = head(tgt)
        if st == 200 and sz > 0:
            hit += 1
        else:
            miss += 1
            if len(misslist) < 12:
                misslist.append(tgt)
print(f"引用 {total_ref} 个，命中 {hit}，缺失 {miss}（命中率 {hit*100//max(total_ref,1)}%）")
for m in misslist:
    print("   缺:", m)
