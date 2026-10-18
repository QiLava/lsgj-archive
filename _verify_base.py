"""核对改写结果：抽验页面链接，统计 _missing 占比"""
import os, re, posixpath, random

BASE = os.path.dirname(os.path.abspath(__file__))
SITES = ["site_old", "site_new", "site_vod", "site_students", "site_njls", "site_lsjyj"]
A = re.compile(r'<a\b[^>]*?\bhref\s*=\s*(["\'])(.*?)\1', re.I)

files = []
for s in SITES:
    r = os.path.join(BASE, s)
    if not os.path.isdir(r):
        continue
    for dp, _, fs in os.walk(r):
        for f in fs:
            if f.endswith(".html"):
                files.append(os.path.join(dp, f))

random.seed(7)
random.shuffle(files)

tot_a = tot_miss = tot_bad = 0
badlist = []
for p in files:
    raw = open(p, "rb").read()
    try:
        t = raw.decode("utf-8")
    except UnicodeDecodeError:
        t = raw.decode("gbk", "replace")
    t = re.sub(r"<script\b[^>]*>.*?</script>", "", t, flags=re.I | re.S)
    rel = os.path.relpath(p, BASE).replace("\\", "/")
    rel_dir = posixpath.dirname(rel)
    for m in A.finditer(t):
        v = m.group(2).strip()
        if not v or v.startswith(("#", "data:", "mailto:", "tel:", "javascript:",
                                  "javacript:", "about:", "http://", "https://", "//")):
            continue
        tot_a += 1
        if "_missing.html" in v:
            tot_miss += 1
            continue
        path = v.split("?")[0].split("#")[0]
        if not path:
            continue
        if path.startswith("/"):
            tgt = rel.split("/")[0] + path
        else:
            tgt = posixpath.normpath(posixpath.join(rel_dir, path))
        fp = os.path.join(BASE, tgt.replace("/", os.sep))
        if not (os.path.isfile(fp) and os.path.getsize(fp) > 0):
            tot_bad += 1
            if len(badlist) < 8:
                badlist.append((rel, v[:70]))

print(f"全站 <a href> 站内链接: {tot_a}")
print(f"  已改指 _missing.html: {tot_miss}  ({tot_miss*100//max(tot_a,1)}%)")
print(f"  仍是坏链: {tot_bad}")
for r, v in badlist:
    print(f"    {r}  ->  {v}")
