"""
链接本地化 + 编码修复 + 资源补全
用法: python rewrite.py <site_dir> <urlmap.json>
"""
import os, re, sys, json, base64, urllib.parse as up

ROOT = os.path.dirname(os.path.abspath(__file__))

ATTR_RE = re.compile(
    r'(?P<attr>\b(?:href|src|action|background|data-src|data-href|lowsrc)\s*=\s*)'
    r'(?P<q>["\'])(?P<val>.*?)(?P=q)', re.I)
CSS_URL_RE = re.compile(r'url\(\s*(?P<q>["\']?)(?P<val>[^"\')\s]*)(?P=q)\s*\)', re.I)
META_CHARSET_RE = re.compile(
    r'(<meta[^>]*?charset\s*=\s*["\']?)([A-Za-z0-9\-_]+)(["\']?[^>]*>)', re.I)
CONTENT_CHARSET_RE = re.compile(
    r'(<meta[^>]*?content\s*=\s*["\'][^"\']*?charset\s*=\s*)([A-Za-z0-9\-_]+)([^"\']*["\'][^>]*>)', re.I)
ARCHIVE_RE = re.compile(r'https?://web\.archive\.org/web/\d+(?:[a-z_]+)?/', re.I)
ARCHIVE_JS_RE = re.compile(r'/(?:static|web)/[a-z0-9_\-]+\.(?:js|css)', re.I)
# Wayback 注入的一整块内容：<script src=".../_static/js/bundle-playback.js..."> 到 toolbar
WB_INJECT_RE = re.compile(
    r'<script[^>]*(?:web-static\.archive\.org|archive\.org/web/\d+)[^>]*>.*?</script>\s*'
    r'|<link[^>]*(?:web-static\.archive\.org|archive\.org/web/\d+)[^>]*>\s*'
    r'|<div[^>]*id="wm-ipp-base"[^>]*>.*?</div>\s*</div>\s*'
    r'|<!-- BEGIN WAYBACK TOOLBAR INSERT -->.*?<!-- END WAYBACK TOOLBAR INSERT -->\s*'
    r'|<script[^>]*>[^<]*(?:__wm\.|RufflePlayer)[^<]*</script>\s*'
    r'|<script[^>]*src\s*=\s*["\']?(?:/web/\d+[a-z_]*/|https?://web\.archive\.org/web/\d+)[^"\'>]*["\']?[^>]*>\s*</script>\s*',
    re.I | re.S)
# 残留的 archive.org 绝对地址（协议相对 / 裸域）
ARCHIVE_BARE_RE = re.compile(
    r'(?:https?:)?//(?:web-static\.)?archive\.org/(?:web/\d+[a-z_]*/|_static/)', re.I)

PLACEHOLDER = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk"
    "YPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==")

# 首页类别名：站内"首页"链接常指向 index.php 或裸域名
ALIAS = {
    "http://www.lsgjzx.cn/index.php": "index.html",
    "http://www.lsgjzx.cn/index.php?": "index.html",
    "http://www.lsgjzx.cn": "index.html",
    "http://lsgjzx.cn/index.php": "index.html",
    "http://lsgj.njlsedu.cn/index.php": "index.html",
    "http://lsgj.njlsedu.cn": "index.html",
    "http://www.lsgjzx.cn/index.htm": "index.html",
    "http://www.lsgjzx.cn/default.htm": "index.html",
}

# 另存的页面 -> 其原始 URL（用于正确解析相对链接）
REV_ALIAS = {
    "course_base_2016.html": "http://www.lsgjzx.cn/",
}

# 子站域名 -> 本地目录前缀（相对站点根）
SUBDIR = {
    "vod.lsgjzx.cn": "../site_vod/",
    "www.vod.lsgjzx.cn": "../site_vod/",
    "students.lsgjzx.cn": "../site_students/",
    "www.students.lsgjzx.cn": "../site_students/",
}

# 同一套上传目录的镜像子域 -> 归一成主域，复用主域的存档
# （zt=专题站, pic=图片站，与 www 共用 upload_files/）
DOMAIN_ALIAS = {
    "zt.lsgjzx.cn": "www.lsgjzx.cn",
    "www.zt.lsgjzx.cn": "www.lsgjzx.cn",
    "pic.lsgjzx.cn": "www.lsgjzx.cn",
    "www.pic.lsgjzx.cn": "www.lsgjzx.cn",
    "lsgjzx.cn": "www.lsgjzx.cn",
}

EXT_ROOT = ("mailto:", "tel:", "javascript:", "#", "data:", "about:", "ftp://", "file://")


def declared_charset(raw):
    """从 meta 声明读取原站编码"""
    head = raw[:2048]
    m = re.search(rb'charset\s*=\s*["\']?\s*([A-Za-z0-9\-_]+)', head, re.I)
    if not m:
        return None
    c = m.group(1).decode("ascii", "ignore").lower().replace("/", "")
    if c in ("gb2312", "gbk", "gb-2312"):
        return "gbk"
    if c in ("utf8", "utf-8"):
        return "utf-8"
    if c in ("big5", "gb18030"):
        return c
    return None


def decode(raw):
    # 优先按原站声明解码，避免 GBK 被误判成 utf-8
    hint = declared_charset(raw)
    if hint:
        try:
            return raw.decode(hint), hint
        except UnicodeDecodeError:
            pass
    for enc in ("utf-8", "gbk", "gb18030", "big5"):
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "replace"), "unknown"


class Rewriter:
    def __init__(self, site, urlmap):
        self.site = os.path.abspath(site)
        self.map = {k: v for k, v in urlmap.items()}
        self.rev = {}
        for u, lp in urlmap.items():
            self.rev[lp.replace("/", os.sep)] = u
        self.missing = {}
        self.used = set()

    # ---------- 目标解析 ----------
    def resolve(self, val, base_url, cur_rel_dir):
        """返回 (本地相对路径 or None, 是否外部)"""
        v = val.strip()
        if not v or v.startswith(EXT_ROOT):
            return None, True
        # 剥离 Wayback 的 /web/<时间戳><模式>/ 前缀（相对形式）
        m = re.match(r'^/web/\d+[a-z_]*/(.+)$', v, re.I)
        if m:
            rest = m.group(1)
            # Wayback 有时把协议写成单斜杠 http:/host/...
            rest = re.sub(r'^(https?):/+', r'\1://', rest, flags=re.I)
            v = rest
        # 指向 archive.org 自身的地址一律按外部处理
        if "archive.org" in v.lower() or "web.archive" in v.lower():
            return None, True
        if re.search(r'[:<>|?*"\x00-\x1f]',
                     re.sub(r'^[a-z][a-z0-9+.\-]*://', '', v, flags=re.I)
                     .split("?")[0].split("#")[0]):
            return None, True
        try:
            abs_u = up.urljoin(base_url, v)
        except Exception:
            return None, True
        p = up.urlparse(abs_u)
        if p.scheme in ("http", "https"):
            netloc = p.netloc.replace(":80", "").replace(":443", "")
            # 子站域名 -> 本地目录
            if netloc in SUBDIR:
                prefix = SUBDIR[netloc]
                sub = (p.path or "/").lstrip("/")
                import posixpath
                cur = os.path.dirname(cur_rel_dir.replace("\\", "/"))
                cands = []
                if not sub or sub.endswith("/"):
                    cands = [sub + "index.html", sub.rstrip("/") + ".html"]
                else:
                    cands = [sub]
                picked = None
                for c in cands:
                    if not c:
                        continue
                    if os.path.isfile(os.path.join(self.site, "..", SUBDIR[netloc].lstrip("./"),
                                                   c.replace("/", os.sep))):
                        picked = c
                        break
                if picked is None:
                    picked = cands[0] if cands else "index.html"
                tgt = prefix + picked
                rel = posixpath.normpath(posixpath.join(cur, tgt)) if cur else tgt
                if not rel.startswith("."):
                    rel = "./" + rel if "/" in rel else rel
                return rel, False
            if "lsgjzx.cn" not in netloc and "lsgj.njlsedu.cn" not in netloc \
               and "njlsedu.cn" not in netloc:
                return None, True
            # 镜像子域归一成主域，复用主域存档
            if netloc in DOMAIN_ALIAS:
                netloc = DOMAIN_ALIAS[netloc]
            norm = up.urlunparse((p.scheme, netloc, p.path, "", p.query, ""))
        else:
            return None, True

        if norm in self.map:
            target = self.map[norm]
            self.used.add(norm)
        elif norm in ALIAS:
            target = ALIAS[norm]
        else:
            # 无查询串时再试一次带 / 结尾
            alt = norm + "/"
            if alt in self.map:
                target = self.map[alt]
                self.used.add(alt)
            elif alt in ALIAS:
                target = ALIAS[alt]
            else:
                self.missing.setdefault(norm, 0)
                self.missing[norm] += 1
                return None, False

        # 计算相对路径
        cur = os.path.dirname(cur_rel_dir.replace("\\", "/"))
        t = target.replace("\\", "/")
        if cur:
            # 用 posixpath 做相对化
            import posixpath
            rel = posixpath.relpath(t, cur)
        else:
            rel = t
        if not rel.startswith("."):
            rel = "./" + rel if "/" in rel else rel
        return rel, False

    # ---------- 文件处理 ----------
    def process(self, fpath):
        rel = os.path.relpath(fpath, self.site).replace("\\", "/")
        base_url = self.rev.get(rel) or REV_ALIAS.get(rel)
        if base_url is None:
            base_url = "http://www.lsgjzx.cn/" + rel   # 兜底

        raw = open(fpath, "rb").read()
        if not raw:
            return 0

        ext = os.path.splitext(fpath)[1].lower()
        if ext in (".jpg", ".jpeg", ".png", ".gif", ".ico", ".bmp",
                   ".swf", ".doc", ".docx", ".xls", ".zip", ".mp3", ".mp4", ".woff", ".ttf"):
            return 0        # 二进制，跳过

        text, enc = decode(raw)
        orig_len = len(text)

        # 1) 清 Wayback 注入（整块 script/link/toolbar）
        text = WB_INJECT_RE.sub("", text)
        # 2) 清残留的 archive.org 地址前缀
        text = ARCHIVE_RE.sub("", text)
        text = ARCHIVE_BARE_RE.sub("", text)
        # 3) 清空悬空的 archive 引用属性
        text = re.sub(r'(?:src|href)\s*=\s*(["\'])\s*\1', r'\1\1', text, flags=re.I)

        # 2) 改写属性
        def sub_attr(m):
            v = m.group("val")
            new, external = self.resolve(v, base_url, rel)
            if external or new is None:
                return m.group(0)
            return f'{m.group("attr")}{m.group("q")}{new}{m.group("q")}'

        text = ATTR_RE.sub(sub_attr, text)

        # 3) CSS url()
        if ext == ".css":
            def sub_css(m):
                v = m.group("val")
                new, external = self.resolve(v, base_url, rel)
                if external or new is None:
                    return m.group(0)
                return f'url({new})'
            text = CSS_URL_RE.sub(sub_css, text)
        else:
            # 内联 <style> 里的 url()
            def sub_inline(m):
                inner = m.group(0)
                def rep(mm):
                    new, external = self.resolve(mm.group("val"), base_url, rel)
                    if external or new is None:
                        return mm.group(0)
                    return f'url({new})'
                return CSS_URL_RE.sub(rep, inner)
            text = re.sub(r'<style[^>]*>.*?</style>', sub_inline, text,
                          flags=re.I | re.S)

        # 4) 编码统一 utf-8
        if META_CHARSET_RE.search(text):
            text = META_CHARSET_RE.sub(lambda m: m.group(1) + "utf-8" + m.group(3), text)
        elif CONTENT_CHARSET_RE.search(text):
            text = CONTENT_CHARSET_RE.sub(lambda m: m.group(1) + "utf-8" + m.group(3), text)

        if len(text) == 0 and orig_len > 0:
            return 0
        open(fpath, "w", encoding="utf-8", newline="") .write(text)
        return 1

    def run(self):
        n = 0
        for dirpath, _, files in os.walk(self.site):
            for f in files:
                n += self.process(os.path.join(dirpath, f))
        return n

    def make_placeholders(self):
        """为引用到但缺失的图片生成占位图"""
        cnt = 0
        for u in list(self.missing.keys()):
            if "archive.org" in u.lower():
                continue
            p = up.urlparse(u)
            lp = p.path.lstrip("/")
            if not lp or not re.search(r'\.(jpg|jpeg|png|gif|bmp|ico)$', lp, re.I):
                continue
            # Windows 非法路径字符过滤
            if re.search(r'[:<>|?*"\x00-\x1f]', lp):
                continue
            dst = os.path.join(self.site, lp.replace("/", os.sep))
            # 防止写到站点目录之外
            if not os.path.abspath(dst).startswith(os.path.abspath(self.site)):
                continue
            if os.path.isdir(dst):
                continue
            if os.path.exists(dst):
                continue
            try:
                os.makedirs(os.path.dirname(dst) or self.site, exist_ok=True)
                with open(dst, "wb") as fh:
                    fh.write(PLACEHOLDER)
                cnt += 1
            except OSError:
                continue
        return cnt


def main():
    site = sys.argv[1]
    umap = sys.argv[2]
    site = os.path.join(ROOT, site) if not os.path.isabs(site) else site
    umap = os.path.join(ROOT, umap) if not os.path.isabs(umap) else umap

    urlmap = json.load(open(umap, encoding="utf-8"))
    r = Rewriter(site, urlmap)
    n = r.run()
    ph = r.make_placeholders()
    tag = os.path.basename(site)
    with open(os.path.join(ROOT, f"missing_{tag}.txt"), "w", encoding="utf-8") as fh:
        for u, c in sorted(r.missing.items(), key=lambda x: -x[1]):
            fh.write(f"{c}\t{u}\n")

    print(f"改写文件 {n} 个")
    print(f"缺失资源引用 {len(r.missing)} 个（已生成占位图 {ph} 个）")
    print(f"明细: missing_{tag}.txt")


if __name__ == "__main__":
    main()
