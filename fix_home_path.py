"""修正注入的 HOME 相对路径：需额外往上退一层（站点目录本身）"""
import os, re

SITES = ["site_old", "site_new", "site_vod", "site_students", "site_njls", "site_lsjyj"]
HUB = "index.html"

fixed = 0
for site in SITES:
    if not os.path.isdir(site):
        continue
    for dp, _, fs in os.walk(site):
        for f in fs:
            if not f.lower().endswith((".html", ".htm")):
                continue
            p = os.path.join(dp, f)
            raw = open(p, "rb").read()
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                text = raw.decode("gbk", "replace")
            if "lsgz-shell-js" not in text:
                continue

            rel = os.path.relpath(p, site).replace("\\", "/")
            depth = 1 + rel.count("/")          # 1 = 站点目录自身
            home = "../" * depth + HUB

            new = re.sub(r'var HOME="[^"]*"', 'var HOME="' + home + '"', text, count=1)
            if new != text:
                open(p, "w", encoding="utf-8", newline="").write(new)
                fixed += 1

print(f"修正 {fixed} 个页面的返回路径")
