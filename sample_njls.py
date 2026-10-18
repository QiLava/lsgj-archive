"""抽样区教育网文章，统计涉及溧中的比例"""
import os, re, subprocess, urllib.request as uq, ssl

BASE = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(BASE, "_tmp", "njls")
os.makedirs(TMP, exist_ok=True)

PROXY = "http://127.0.0.1:7890"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
opener = uq.build_opener(
    uq.ProxyHandler({"http": PROXY, "https": PROXY}),
    uq.HTTPSHandler(context=ctx))
opener.addheaders = [("User-Agent", "Mozilla/5.0")]
uq.install_opener(opener)

urls = [l.strip() for l in open(os.path.join(TMP, "sample.txt"), encoding="utf-8") if l.strip()]
print(f"抽样 {len(urls)} 篇\n")

hits = []
for i, u in enumerate(urls, 1):
    fp = os.path.join(TMP, f"a{i}.html")
    if not os.path.exists(fp):
        try:
            with uq.urlopen(f"https://web.archive.org/web/2019id_/{u}", timeout=35) as r:
                open(fp, "wb").write(r.read())
        except Exception as e:
            print(f"  [{i}] 失败 {str(e)[:40]}")
            continue
    raw = open(fp, "rb").read()
    try:
        t = raw.decode("utf-8")
    except UnicodeDecodeError:
        t = raw.decode("gbk", "replace")
    m = re.search(r"<title[^>]*>(.*?)</title>", t, re.I | re.S)
    title = re.sub(r"\s+", " ", m.group(1)).strip()[:52] if m else "(无标题)"
    body = re.sub(r"<[^>]+>", " ", t)
    if re.search(r"省溧中|溧水高级中学|溧中", body):
        hits.append((i, title))

print(f"提到溧中的: {len(hits)}/{len(urls)}\n")
for i, t in hits:
    print(f"  [{i}] {t}")
