"""跨站资源互补：新站缺失但老站有的文件复制过去（反之亦然）"""
import os, re, sys, posixpath, shutil

ATTR = re.compile(r'(?:href|src|action|background)\s*=\s*(["\'])(.*?)\1', re.I)
CSSU = re.compile(r'url\(\s*(["\']?)([^"\')]+)\1\s*\)', re.I)

pairs = [("site_new", "site_old"), ("site_old", "site_new")]

for target, source in pairs:
    copied = 0
    for dp, _, fs in os.walk(target):
        for f in fs:
            if not f.lower().endswith((".html", ".htm", ".css")):
                continue
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, target).replace("\\", "/")
            base = posixpath.dirname(rel)
            raw = open(p, "rb").read()
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                text = raw.decode("gbk", "replace")
            refs = [m.group(2) for m in ATTR.finditer(text)]
            refs += [m.group(2) for m in CSSU.finditer(text)]
            for r in refs:
                r = r.strip()
                if not r or r.startswith(("http://", "https://", "//", "mailto:",
                                          "tel:", "javascript:", "#", "data:", "about:")):
                    continue
                if "?" in r or r in (".", ".."):
                    continue
                r = r.split("#")[0]
                tgt = posixpath.normpath(posixpath.join(base, r)).replace("\\", "/")
                if tgt.startswith(".."):
                    continue
                dst = os.path.join(target, tgt.replace("/", os.sep))
                src = os.path.join(source, tgt.replace("/", os.sep))
                if os.path.exists(dst) or not os.path.isfile(src):
                    continue
                try:
                    os.makedirs(os.path.dirname(dst) or target, exist_ok=True)
                    shutil.copy2(src, dst)
                    copied += 1
                except OSError:
                    pass
    print(f"{target} <- {source}: 复制 {copied} 个文件")
