"""向所有还原页面注入：
1. 返回复刻站主页的浮动按钮（按文件深度算相对路径）
2. 外链点击拦截 —— 弹出提示说明指向哪里、此处未还原
3. viewport 适配手机
"""
import os, re, sys, posixpath

SITES = ["site_old", "site_new", "site_vod", "site_students", "site_njls", "site_lsjyj"]
HUB = "index.html"

# 属于本站（已还原）的域名，这些不算外链
INTERNAL = ("lsgjzx.cn", "njlsedu.cn")

STYLE = """<style id="lsgz-shell-css">
#lsgz-home-btn{position:fixed;right:14px;bottom:14px;z-index:2147483000;display:flex;
align-items:center;gap:6px;padding:9px 14px;border-radius:22px;border:1px solid #b9c6d8;
background:#fff;color:#1a56c4;font:600 13px/1 "Microsoft YaHei","PingFang SC",sans-serif;
text-decoration:none;box-shadow:0 3px 14px rgba(20,40,80,.18);cursor:pointer;
transition:transform .15s,box-shadow .15s;-webkit-tap-highlight-color:transparent}
#lsgz-home-btn:hover{transform:translateY(-2px);box-shadow:0 6px 20px rgba(20,40,80,.24)}
#lsgz-home-btn .i{font-size:15px}
#lsgz-mask{position:fixed;inset:0;z-index:2147484000;background:rggb(0,0,0)}
#lsgz-mask{background:rgba(15,25,45,.55);display:none;align-items:center;justify-content:center;padding:18px}
#lsgz-mask.on{display:flex}
#lsgz-box{background:#fff;border-radius:14px;max-width:430px;width:100%;padding:26px 26px 22px;
box-shadow:0 18px 50px rgba(0,0,0,.3);font-family:"Microsoft YaHei","PingFang SC",sans-serif}
#lsgz-box h4{margin:0 0 12px;font-size:17px;color:#1c2733}
#lsgz-box p{margin:0 0 10px;font-size:13.5px;line-height:1.75;color:#4a5568}
#lsgz-url{word-break:break-all;background:#f2f5f9;border:1px solid #e2e8f0;border-radius:8px;
padding:9px 11px;font:12px/1.6 Consolas,monospace;color:#33415c;margin:0 0 14px}
#lsgz-box .row{display:flex;gap:10px;flex-wrap:wrap}
#lsgz-box button{flex:1;min-width:120px;padding:10px 14px;border-radius:9px;border:1px solid #d3dae4;
background:#fff;color:#33415c;font:600 13px/1.4 "Microsoft YaHei",sans-serif;cursor:pointer}
#lsgz-box button.go{background:#1a56c4;border-color:#1a56c4;color:#fff}
#lsgz-box button:active{transform:translateY(1px)}
@media (max-width:520px){
  #lsgz-home-btn{right:10px;bottom:10px;padding:8px 12px;font-size:12px}
  #lsgz-box{padding:20px 18px 18px}
}
</style>"""

JS = """<script id="lsgz-shell-js">
(function(){
  if(window.__lsgzShell) return; window.__lsgzShell=1;
  var HOME=%(home)s;
  var INTERNAL=%(internal)s;
  var btn=document.createElement('a');
  btn.id='lsgz-home-btn'; btn.href=HOME; btn.innerHTML='<span class="i">\\u2302</span> 返回复刻站主页';
  btn.setAttribute('title','返回复刻站主页');
  document.body?document.body.appendChild(btn):document.addEventListener('DOMContentLoaded',function(){document.body.appendChild(btn)});
  var mask=document.createElement('div'); mask.id='lsgz-mask';
  mask.innerHTML='<div id="lsgz-box"><h4>\\u8fd9\\u4e2a\\u94fe\\u63a5\\u6307\\u5411\\u7ad9\\u5916</h4>'
   +'<p>\\u5b83\\u5c5e\\u4e8e\\u5f53\\u5e74\\u7f51\\u7ad9\\u7684\\u5916\\u90e8\\u94fe\\u63a5\\uff08\\u5176\\u4ed6\\u5b66\\u6821\\u3001\\u6559\\u80b2\\u5c40\\u3001\\u65b0\\u95fb\\u7f51\\u7ad9\\u7b49\\uff09\\u3002'
   +'\\u672c\\u7ad9\\u53ea\\u8fd8\\u539f\\u4e86\\u6df7\\u6c34\\u9ad8\\u7ea7\\u4e2d\\u5b66\\u81ea\\u5df1\\u7684\\u9875\\u9762\\uff0c<b>\\u8fd9\\u4e2a\\u76ee\\u6807\\u9875\\u9768\\u672a\\u8fd8\\u539f</b>\\u3002</p>'
   +'<div id="lsgz-url"></div>'
   +'<div class="row"><button class="go">\\u4ecd\\u7136\\u6253\\u5f00\\uff08\\u65b0\\u7a97\\u53e3\\uff09</button>'
   +'<button class="no">\\u53d6\\u6d88</button></div></div>';
  document.body?document.body.appendChild(mask):document.addEventListener('DOMContentLoaded',function(){document.body.appendChild(mask)});
  var urlEl=mask.querySelector('#lsgz-url');
  function isInternal(h){for(var i=0;i<INTERNAL.length;i++){if(h.indexOf(INTERNAL[i])>=0)return true}return false}
  function open(u){urlEl.textContent=u;mask.classList.add('on')}
  function close(){mask.classList.remove('on')}
  mask.querySelector('.no').onclick=close;
  mask.addEventListener('click',function(e){if(e.target===mask)close()});
  mask.querySelector('.go').onclick=function(){
    var u=urlEl.getAttribute('data-u'); close();
    if(u) window.open(u,'_blank','noopener');
  };
  document.addEventListener('click',function(e){
    var a=e.target; while(a&&a.tagName!=='A'){a=a.parentElement}
    if(!a) return;
    var h=a.getAttribute('href'); if(!h) return;
    if(/^(javascript:|#|mailto:|tel:|data:)/i.test(h)) return;
    var abs; try{ abs=new URL(h,location.href) }catch(err){ return }
    if(abs.protocol!=='http:'&&abs.protocol!=='https:') return;
    if(abs.host===location.host) return;              // 同源，正常跳转
    if(isInternal(abs.host)) return;                  // 本站已还原域名
    e.preventDefault(); urlEl.setAttribute('data-u',abs.href); open(abs.href);
  },true);
  document.addEventListener('keydown',function(e){ if(e.key==='Escape') close() });
})();
</script>"""


def decode(raw):
    for enc in ("utf-8", "gbk", "gb18030"):
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "replace"), "unknown"


def has_viewport(text):
    return re.search(r'<meta[^>]+name=["\']?viewport', text, re.I) is not None


def add_viewport(text):
    # 老站多为 980px 定宽，用 width=980 让手机按原始宽度渲染并可缩放
    if re.search(r'<head[^>]*>', text, re.I):
        return re.sub(r'(<head[^>]*>)',
                      r'\1<meta name="viewport" content="width=980">', text, count=1, flags=re.I)
    return '<meta name="viewport" content="width=980">' + text


total_files = 0
total_ext = 0
for site in SITES:
    if not os.path.isdir(site):
        continue
    nf = 0
    for dp, _, fs in os.walk(site):
        for f in fs:
            if not f.lower().endswith((".html", ".htm")):
                continue
            p = os.path.join(dp, f)
            raw = open(p, "rb").read()
            if not raw:
                continue
            text, enc = decode(raw)
            if "lsgz-shell-js" in text:
                continue

            # 计算回到主页的相对路径
            rel = os.path.relpath(p, site).replace("\\", "/")
            depth = 1 + rel.count("/")
            home = "../" * depth + HUB

            js = JS.replace("%(home)s", '"' + home + '"')
            js = js.replace("%(internal)s", '["' + '","'.join(INTERNAL) + '"]')

            block = STYLE + js

            if re.search(r"</body\s*>", text, re.I):
                text = re.sub(r"(</body\s*>)",
                              lambda m: block + m.group(1), text, count=1, flags=re.I)
            else:
                text = text + block

            if not has_viewport(text):
                text = add_viewport(text)

            open(p, "w", encoding="utf-8", newline="").write(text)
            nf += 1
    print(f"{site}: 注入 {nf} 个页面")
    total_files += nf

print(f"\n合计注入 {total_files} 个页面")
