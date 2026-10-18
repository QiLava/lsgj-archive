"""跨站资源互补 v2：解析 /web/<ts><模式>/http:/host/path 形式，跨站补文件并改写引用"""
import os, re, sys, posixpath, shutil

WB = re.compile(r'/web/\d+[a-z_]*/(?:https?:)?/*([a-z0-9.\-]+\.[a-z]{2,6})?(/[^"\'<>\s]*)', re.I)

pairs = [("site_new", "site_old"), ("site_old", "site_new")]

for target, source in pairs:
    copied, patched = 0, 0
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
            orig = text

            def fix(m):
                global copied
                host = (m.group(1) or "").lower()
                path = m.group(2) or ""
                # 只处理两个目标站的路径
                if host and host not in ("lsgjzx.cn", "www.lsgjzx.cn",
                                         "lsgj.njlsedu.cn", "njlsedu.cn"):
                    return m.group(0)
                path = path.split("?")[0].split("#")[0]
                if not re.search(r'\.(jpg|jpeg|png|gif|css|js|ico|swf|bmp)$', path, re.I):
                    return m.group(0)
                lp = path.lstrip("/")
                dst = os.path.join(target, lp.replace("/", os.sep))
                src = os.path.join(source, lp.replace("/", os.sep))
                if not os.path.isfile(src):
                    return m.group(0)
                if not os.path.exists(dst):
                    try:
                        os.makedirs(os.path.dirname(dst) or target, exist_ok=True)
                        shutil.copy2(src, dst)
                        copied += 1
                    except OSError:
                        return m.group(0)
                # 改写为相对路径
                import posixpath as pp
                relp = pp.relpath(lp, base) if base else lp
                if not relp.startswith("."):
                    relp = "./" + relp
                return relp

            text = WB.sub(fix, text)
            if text != orig:
                open(p, "w", encoding="utf-8", newline="").write(text)
                patched += 1
    print(f"{target} <- {source}: 复制 {copied} 个文件，改写 {patched} 个页面")
