"""从已下载的 293 个栏目标题页提取全部文章标题+URL，
只保留 CDX 里确有存档的，再按学校关键词筛选"""
import os, re, json, urllib.parse as up

BASE = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(BASE, "_tmp", "njls_lists")

ART = re.compile(r'<a[^>]+href=["\']([^"\']*t=article[^"\']*)["\'][^>]*>(.*?)</a>', re.I | re.S)
KEYWORDS = ("省溧中", "溧水高级中学", "溧中")

# 已下载列表页里的全部文章
allarts = {}
for dp, _, fs in os.walk(TMP):
    for f in fs:
        if not f.endswith(".html"):
            continue
        raw = open(os.path.join(dp, f), "rb").read()
        try:
            t = raw.decode("utf-8")
        except UnicodeDecodeError:
            t = raw.decode("gbk", "replace")
        for m in ART.finditer(t):
            title = re.sub(r"<[^>]+>", "", m.group(2))
            title = re.sub(r"\s+", " ", title).strip()
            if len(title) < 4:
                continue
            abs_u = up.urljoin("http://www.njlsedu.cn/", m.group(1))
            p = up.urlparse(abs_u)
            norm = up.urlunparse((p.scheme, p.netloc.replace(":80", ""),
                                  p.path, "", p.query, ""))
            allarts[norm] = title

print(f"列表页中提取到文章链接: {len(allarts)} 个", flush=True)


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

archived = {u: t for u, t in allarts.items() if key(u) in cdx}
print(f"其中 CDX 确有存档: {len(archived)} 个", flush=True)

school = {u: t for u, t in archived.items() if any(k in t for k in KEYWORDS)}
print(f"标题含学校关键词的: {len(school)} 个\n", flush=True)
for u, t in list(school.items())[:25]:
    print(f"  {t[:50]}")

json.dump(school, open(os.path.join(BASE, "njls_school_articles.json"), "w",
                       encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump({u: key(u) for u in school},
          open(os.path.join(BASE, "njls_keys.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"\n已写入 njls_school_articles.json（{len(school)} 篇）", flush=True)
