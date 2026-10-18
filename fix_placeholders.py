"""把 <img> 指向占位图的地方换成内联 SVG 占位符，让缺失图片可见且带说明"""
import os, re, sys, posixpath, urllib.parse

SITES = ["site_old", "site_new", "site_vod", "site_students"]

IMG_RE = re.compile(r'<img\b[^>]*?\bsrc\s*=\s*(["\'])(.*?)\1[^>]*>', re.I)


def svg_placeholder(name):
    label = "图片未存档"
    sub = name if len(name) <= 26 else name[:24] + ".."
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' width='132' height='96' "
        "viewBox='0 0 132 96'>"
        "<rect width='132' height='96' fill='#eef1f6' stroke='#d3dae4' "
        "stroke-width='1' stroke-dasharray='4 3'/>"
        f"<text x='66' y='46' text-anchor='middle' font-family='Microsoft YaHei,sans-serif' "
        f"font-size='12' fill='#8a94a6'>{label}</text>"
        f"<text x='66' y='66' text-anchor='middle' font-family='Consolas,monospace' "
        f"font-size='8' fill='#b3bcc9'>{sub}</text>"
        "</svg>"
    )
    return "data:image/svg+xml," + urllib.parse.quote(svg)


total = 0
for site in SITES:
    if not os.path.isdir(site):
        continue
    n = 0
    for dp, _, fs in os.walk(site):
        for f in fs:
            if not f.lower().endswith((".html", ".htm")):
                continue
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, site).replace("\\", "/")
            base = posixpath.dirname(rel)
            raw = open(p, "rb").read()
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                text = raw.decode("gbk", "replace")
            orig = text

            def fix(m):
                global n
                v = m.group(2).strip()
                if v.startswith(("http://", "https://", "//", "data:", "#")):
                    return m.group(0)
                v = v.split("?")[0].split("#")[0]
                if not v:
                    return m.group(0)
                tgt = posixpath.normpath(posixpath.join(base, v))
                fp = os.path.join(site, tgt.replace("/", os.sep))
                if not os.path.isfile(fp) or os.path.getsize(fp) != 70:
                    return m.group(0)
                n += 1
                return m.group(0).replace(m.group(2), svg_placeholder(tgt), 1)

            text = IMG_RE.sub(fix, text)
            if text != orig:
                open(p, "w", encoding="utf-8", newline="").write(text)
    print(f"{site}: 替换 {n} 处 <img> 占位图")
    total += n
print(f"\n合计 {total} 处")
