"""生成 site_njls 索引页：列出所有已下载的区教育网文章"""
import os, re, json, html

BASE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(BASE, "site_njls")

items = []
for dp, _, fs in os.walk(SITE):
    for f in fs:
        if f in ("index.html", "all.html"):
            continue
        if not f.endswith(".html"):
            continue
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, SITE).replace("\\", "/")
        raw = open(p, "rb").read()
        try:
            t = raw.decode("utf-8")
        except UnicodeDecodeError:
            t = raw.decode("gbk", "replace")
        m = re.search(r"<title[^>]*>(.*?)</title>", t, re.I | re.S)
        title = re.sub(r"\s+", " ", m.group(1)).strip() if m else rel
        title = re.sub(r"[-－—]\s*溧水教育网\s*$", "", title).strip() or rel
        # 去掉所有链接后判断是否真提到学校
        t2 = re.sub(r"<a\b[^>]*>.*?</a>", "", t, flags=re.I | re.S)
        t2 = re.sub(r"<script.*?</script>", "", t2, flags=re.I | re.S)
        body = re.sub(r"<[^>]+>", " ", t2)
        school = bool(re.search(r"省溧中|溧水高级中学", body))
        items.append((title, rel, school))

school_items = [x for x in items if x[2]]
other_items = [x for x in items if not x[2]]
school_items.sort(key=lambda x: x[0])
other_items.sort(key=lambda x: x[0])
print(f"文章 {len(items)} 篇，其中提及学校 {len(school_items)} 篇")


def rows(lst, star):
    out = []
    for t, r, _ in lst:
        badge = '<b style="color:#c00">★</b> ' if star else ""
        out.append(f'      <li>{badge}<a href="{html.escape(r)}">{html.escape(t)}</a></li>')
    return "\n".join(out)


page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>区教育网 · 涉及省溧中的存档文章 - 江苏省溧水高级中学时光机</title>
<style>
  :root{{--win-bg:#c0c0c0;--title-a:#0a246a;--title-b:#3a6ea5;--link:#0000ee}}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:Tahoma,Verdana,"宋体","Microsoft YaHei",sans-serif;background:#008080;
    color:#1a1a1a;line-height:1.7;padding:20px 14px 70px;min-height:100vh}}
  .wrap{{max-width:900px;margin:0 auto}}
  .win{{background:var(--win-bg);border:2px outset #fff;box-shadow:4px 4px 0 rgba(0,0,0,.35);margin-bottom:16px}}
  .win-title{{background:linear-gradient(180deg,var(--title-a),var(--title-b));color:#fff;
    padding:7px 12px;font-weight:700;font-size:13px;display:flex;gap:8px;align-items:center}}
  .win-title .dots{{margin-left:auto;display:flex;gap:4px}}
  .win-title .dots i{{width:15px;height:14px;background:var(--win-bg);border:1px outset #fff;display:block}}
  .win-body{{padding:16px 18px}}
  h1{{color:#fff;font-size:22px;text-shadow:2px 2px 0 #000;line-height:1.4}}
  .sub{{color:#bfe3ff;font-size:12px;margin-top:6px}}
  .lead{{font-size:13px;color:#333;margin-bottom:12px}}
  .lead b{{color:#000080}}
  .cnt{{background:#fff;border:2px inset #fff;padding:10px 14px;font-size:12.5px;margin-bottom:14px}}
  .cnt b{{color:#c00;font-size:15px}}
  ol{{background:#fff;border:2px inset #fff;padding:14px 14px 14px 38px;
     max-height:56vh;overflow:auto;font-size:13px}}
  ol li{{margin-bottom:6px;padding-bottom:6px;border-bottom:1px dotted #ccc}}
  ol li:last-child{{border-bottom:0}}
  a{{color:var(--link)}}
  h2.sec{{font-size:14px;color:#000080;margin:16px 0 8px}}
  .tip{{background:#fffbe6;border:2px inset #fff;padding:12px 14px;font-size:12.5px;color:#5a4a1a;margin-top:14px}}
  @media (max-width:720px){{
    body{{padding:12px 8px 50px}}
    h1{{font-size:18px}}
    ol{{font-size:12.5px;max-height:52vh}}
  }}
</style>
</head>
<body>
<div class="wrap">
  <div class="win">
    <div class="win-title"><span>📰</span> 区教育信息网 · 涉及省溧中的存档文章
      <span class="dots"><i></i><i></i><i></i></span></div>
    <div class="win-body">
      <h1>溧水教育网上的省溧中</h1>
      <div class="sub">www.njlsedu.cn · 2018 — 2023 年存档</div>
    </div>
  </div>

  <div class="win">
    <div class="win-title"><span>📄</span> 文章目录
      <span class="dots"><i></i><i></i><i></i></span></div>
    <div class="win-body">
      <p class="lead">这些文章发布在<b>溧水区教育信息网</b>（区教育局主办），
         内容涉及省溧中的招生、招聘、表彰、教研活动等。
         它们是教育局网站的内容，不是学校官网本身的页面。</p>
      <div class="cnt">
        共存档 <b>{len(items)}</b> 篇文章，其中正文提及
        「省溧中 / 溧水高级中学」的有 <b>{len(school_items)}</b> 篇（下面带 ★ 号）。
      </div>

      <h2 class="sec">★ 涉及省溧中的文章（{len(school_items)} 篇）</h2>
      <ol>
{rows(school_items, True)}
      </ol>

      <h2 class="sec">区教育网其他文章（{len(other_items)} 篇）</h2>
      <ol>
{rows(other_items, False)}
      </ol>

      <div class="tip">💡 想看更早的学校内容，请去
        <a href="../site_old/index.html">学校主站 lsgjzx.cn（2010—2017）</a>
        或 <a href="../site_new/index.html">后期官网 lsgj.njlsedu.cn（2018—2021）</a>。</div>
    </div>
  </div>
</div>
</body>
</html>
"""

with open(os.path.join(SITE, "index.html"), "w", encoding="utf-8") as fh:
    fh.write(page)
with open(os.path.join(SITE, "articles.json"), "w", encoding="utf-8") as fh:
    json.dump({"n": len(school_items), "total": len(items)}, fh)
print(f"已生成索引：学校相关 {len(school_items)} / 全部 {len(items)}")

