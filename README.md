# 江苏省溧水高级中学 · 官网时光机

**一个非官方的历史存档还原项目。**

把学校官网 2003—2023 年的可寻回页面，从互联网档案馆（Internet Archive
Wayback Machine）抢救出来，整理成一个可以点着逛的怀旧站，供校友回来看看。

- 数据源：`web.archive.org`
- 还原完成：2026 年 10 月 18 日
- 规模：**7 个站点 / 2191 个 HTML 页面 / 111 MB**

## 🌐 在线访问

| 地址 | 说明 |
|---|---|
| **https://bak.slz.ink** | 正式入口（Cloudflare Pages + 自定义域） |
| https://lsgj-archive.pages.dev | Cloudflare Pages 默认域名 |
| 本仓库 | 全部源码与还原脚本 |

---

## 目录

1. [怎么打开](#一怎么打开)
2. [站点清单](#二站点清单)
3. [为参观者做的四件事](#三为参观者做的四件事)
4. [永久丢失的部分](#四永久丢失的部分)
5. [给后人的操作手册](#五给后人的操作手册)
6. [踩过的坑](#六踩过的坑)
7. [文件说明](#七文件说明)
8. [免责声明](#八免责声明)

---

## 一、怎么打开

### 本地服务（推荐）

```bash
cd 省溧中官网还原站
python -m http.server 8897
# 浏览器打开 http://127.0.0.1:8897/index.html
```

Python 3 即可，无需任何第三方依赖。

### ⚠ 不要直接双击 HTML

页面里有 `/` 开头的资源路径（当年的站就是这么写的），
**必须通过 HTTP 服务访问**，双击打开会大量资源 404。

### 部署到网上

把整个文件夹传到任意静态托管（GitHub Pages / Cloudflare Pages / Vercel /
阿里云 OSS / 腾讯云 COS 等）。

**目录结构必须保持不变**——返回主页用的是相对路径 `../index.html`，
是按「站点目录自身 + 文件深度」逐层算的。如果移动了某个 `site_*` 目录的位置，
所有返回按钮都会失效。

改目录结构的话，重跑一次 `fix_home_path.py` 即可（见第五节）。

---

## 二、站点清单

学校历史上出现过 **2 个主域名 + 4 个子站**，全部找回来了：

| # | 站点 | 域名 | 时期 | 页面 | 图片 | 体积 |
|---|---|---|---|---|---|---|
| 1 | **学校主站** | `lsgjzx.cn` | 2010–2017 | 587 | 695 | 43 MB |
| 2 | 化学生物课程基地 | `lsgjzx.cn`（根路径挂载） | 2016 | 1 | — | — |
| 3 | 视频点播系统 | `vod.lsgjzx.cn` | 2016–2018 | 1 | 45 | 731 KB |
| 4 | 后期官网 | `lsgj.njlsedu.cn` | 2018–2021 | 143 | 483 | 7.3 MB |
| 5 | 区教育网 · 学校相关 | `www.njlsedu.cn` | 2018–2023 | 1131 | 3347 | 40 MB |
| 6 | 区教研室 · 教研文章 | `lsjyj.njlsedu.cn` | 2019–2023 | 328 | — | 13 MB |
| 7 | 学生子站 | `students.lsgjzx.cn` | 2016 | 0 | 9 | 387 KB |

**第 1 项是重点**：PHP168 齐博 CMS，完整导航含学校概况、历任领导、知名校友、
校风校训、办学目标、学校掠影、光辉历程、学校荣誉、校长风采、组织机构、
中层领导、新闻中心、教学教研、招考专栏、教师频道、学生园地、德育天地、
文化长廊、党建工作、课程基地。

第 5、6 项是**区教育局/教研室的网站**，不是学校官网本身，但里面有大量
涉及省溧中的官方文章（招生、招聘、表彰、教研通知），索引进来了。

### 域名变迁史（重要，别再搞错）

`lsgjzx.cn` 根路径 `/` 共有 **41 个快照**，横跨 2008–2025，内容完全不同：

| 时期 | 根路径实际是什么 |
|---|---|
| 2008–2015 | 学校主站早期（Mambo 系统） |
| 2016 前后 | 「化学生物课程基地」占用根路径 |
| **2016-08 ~ 2017-02** | **真正的学校主站首页**（PHP168）← 现采用此版 |
| 2018 起 | 锐捷网络（Ruijie）设备错误页，服务器已失控 |
| 2019 起 | 404 |
| 2022 后 | 4.cn 域名停放页 |

被误抓的课程基地版已另存为 `site_old/course_base_2016.html`，没有丢。

### 查过但没有收录的域名

| 域名 | 结果 |
|---|---|
| `lsgj.jsnje.cn` | 0 条存档 |
| `lsgjzx.com` | 有 2003 年快照，但实际是**无锡市洛社高级中学**（另一所学校） |
| `lsgz.cn` | 2003–2008 有快照，但是个人博客 |
| `njlsgz.cn` / `lsgjzx.org` / `lsgjzx.net` | 0 条 |
| `mp.weixin.qq.com` | 0 条相关微信公众号文章 |
| `archive.ph` / `archive.today` | 429 + 验证码，且小站收录几乎为零 |

> **教训：不能凭域名猜归属，一定要把快照抓下来看 `<title>`。**

---

## 三、为参观者做的四件事

### 1. 每个页面都能退回主页

所有还原页面右下角有浮动按钮「⌂ 返回复刻站主页」。
相对路径按文件深度逐个计算，深层目录也能正确退回。

### 2. 打不开会告诉你是为什么（不再是裸 404）

全站 **35617 个**原本会 404 的链接，已全部改指向 `_missing.html`，
按原因分类显示，而不是甩一个 HTTP 404 给参观者：

| 原因 | 链接数 | 说明 |
|---|---|---|
| `list` 栏目列表页未存档 | 24070 | 点了导航栏目但该栏目从未被爬取 |
| `article` 文章页未存档 | 7132 | 有链接没正文 |
| `unknown` 链接目标缺失 | 3223 | 未能归类 |
| `attach` 附件未存档 | 459 | 当年通知的 Word/Excel/PDF |
| `admin` 后台/登录入口 | 409 | 当年就不对外开放 |
| `wayback` 档案馆地址残留 | 185 | 清理遗漏 |
| `tpl` 原站模板未渲染 | 112 | 原站自身的 bug |
| `inner` 原站内网死链 | 27 | `file://172.20.1.1`，当年就是坏的 |

说明页会显示：原因分类、原始链接地址、这段内容为什么没了、以及
「为什么会这样」的总说明。返回主页按钮按页面深度算，深层目录也能正确退回。

**想改文案**：搜 `_missing.html` 里的 `REASONS` 对象。
**想重新生成**：`python -u fix_broken_links.py`（幂等，可反复重跑，
会先撤销上轮改写再重新判定）。

### 3. 外链不直接跳转

**1854+ 个页面**都装了拦截逻辑（`inject_shell.py` 注入）。

点击外链会弹窗：

> **这个链接指向站外** —— 它属于当年网站的外部链接（其他学校、教育局、
> 新闻网站等）。本站只还原了溧水高级中学自己的页面，**这个目标页面未还原**。

并提供「仍然打开（新窗口）」和「取消」。

判定规则（`INTERNAL` 常量，可按需扩充）：
- 同源地址 → 正常跳转
- 属于 `lsgjzx.cn` / `njlsedu.cn` 体系 → 正常跳转
- 其余一律拦截

### 4. 手机适配

- **主页**完全响应式，720px / 400px 两档断点，手机上变单列卡片
- **还原页面**补了 `<meta name="viewport" content="width=980">`
  - 老站是 980px 定宽表格布局，用 `width=980` 让手机按原始宽度渲染、可缩放
  - 比 `width=device-width` 把文字挤成一团要好
  - 如果日后要彻底重做成响应式，需要改 HTML 结构，工作量很大，不建议

### 5. 首次打开有免责声明

`localStorage` 键名 `lsgz_disclaimer_seen`，只弹一次。
页脚「免责声明」入口可随时重看。

改文案：搜 `index.html` 里的 `#dlg-b` 区块。

---

## 四、永久丢失的部分

### 1. 服务器端源码（最重要，务必理解）

**Wayback 存的是浏览器渲染后的 HTML，不是 PHP 程序。**

`.php` 源文件、数据库结构、后台配置、视频系统的 `.NET` 代码
**从未被存档，已永久消失。**

拿到的是：全部 HTML 页面、CSS、JS、图片。
想还原「网站程序本身」是不可能的，这个项目做的是「页面内容」的还原。

### 2. 约 790 张图片

逐一核对过 CDX 与实时接口，确认从未被存档：

| 位置 | 占位数 |
|---|---|
| `site_old/images/stories/`（早期 Mambo 配图） | 283 |
| `site_old/upload_files/article/` | 57 |
| `site_old/templates/zx200608008/` 等模板图 | 56 |
| `site_new` 各处 | 398 |

已用**内联 SVG 占位符**替换（`fix_placeholders.py`），共 1778 处：
灰色虚线框 + 「图片未存档」+ 原始文件名。
这样缺失可见、版式不塌，比显示破图图标好。

**恢复方法**：如果哪天从别的渠道（校友硬盘、旧服务器备份）找到真实图片，
按 `urlmap_site_*.json` 里的路径放回去就行，HTML 不用改。

### 3. 主站首页导航 106 个栏目链接无对应存档

真主页 242 个站内链接中 136 个能跳通。
批量试抓过 1245 个候选页面，CDX 与实时接口均确认无存档。

### 4. 区教育网 6 篇、教研室 6 篇下载失败

重试过多次，Wayback 侧持续报错，放弃。

---

## 五、给后人的操作手册

### 目录里的脚本（都在本目录，Python 3 无第三方依赖）

| 脚本 | 作用 | 何时重跑 |
|---|---|---|
| `mirror.py` | 核心抓取器。读 CDX 清单，多时间戳退避重试，写文件 + 生成 urlmap | 要抓新域名时 |
| `rewrite.py` | 链接本地化、GBK→UTF-8、清 Wayback 注入、子域归一、缺图占位 | 抓完新页面后 |
| `inject_shell.py` | 注入返回按钮 + 外链拦截 + viewport | 抓完新页面后 |
| `fix_home_path.py` | 修正返回主页的相对路径 | 改了目录结构后 |
| `fix_broken_links.py` | 坏链改指说明页 + 修大小写/Wayback残留/模板标签（幂等） |
| `fix_placeholders.py` | 把 `<img>` 占位图换成可见 SVG 占位符 | rewrite 之后 |
| `scan_parked.py` | 扫描域名停放页/设备错误页 | 怀疑抓到假首页时 |
| `gen_sub_index.py` | 生成索引进页（列文章、标★） | 新增站点后 |
| `verify.py` | HTTP 实查页面与资源健康度 | 每次改动后 |
| `harvest_sub.py` | 从缓存 CDX 抓指定子域 | 要加新区子站时 |
| `probe_lists.py` | 试探性补抓未存档页面 | 想再抢救一次时 |

### 标准流程（抓一个新域名）

```bash
# 1. 查 CDX 清单（去重 + 全时间戳两份）
curl -s -x http://127.0.0.1:7890 \
  "http://web.archive.org/cdx/search/cdx?url=<域名>&matchType=domain\
&fl=timestamp,original,statuscode,mimetype&collapse=urlkey&limit=40000" \
  -o _cdx/cdx_<名>.txt
curl -s -x http://127.0.0.1:7890 \
  "http://web.archive.org/cdx/search/cdx?url=<域名>&matchType=domain\
&fl=timestamp,original,statuscode&limit=60000" \
  -o _cdx/full_<名>.txt

# 2. 抓取（务必多代理分流，见下）
python -u mirror.py _cdx/cdx_<名>.txt _cdx/full_<名>.txt site_<名> --workers 16

# 3. 本地化改写
python -u rewrite.py site_<名> urlmap_site_<名>.json

# 4. 注入导航
python -u inject_shell.py
python -u fix_home_path.py

# 5. 占位图
python -u fix_placeholders.py

# 6. 索引（可选）
python -u gen_sub_index.py

# 7. 验证
python -u verify.py site_<名> 8897
```

### ⚠ 网络：必须多代理分流，否则慢到想弃坑

**archive.org 的 429 限流是跟着出口 IP 走的。**

- 单节点 8 线程：约 8 分钟下 174 个文件，63% 失败
- 7 节点分流（每线程一个出口）：100 秒下 153 个，失败率 < 5%

**提速 4 倍以上。**

本项目用了 8 个独立 Clash 实例，配置在 `clash-run/`：
每个实例独立 `-d` 数据目录、独立 mixed-port（7890–7897）、
独立 external-controller（9090–9097），各绑一个不同节点。

端口列表在 `../clash-run/proxies.txt`，`mirror.py` 用 `--proxies` 读取。

**复现方式**：
1. Clash for Windows 的 GUI 起不来（沙箱限制），直接调内核：
   `resources/static/files/win/x64/clash-win64.exe`
2. `spawn_instances.py` 会读 `archive_ok_nodes.json` 启动 N 个实例
   （注意 7890/7891 被主实例占用，从 7892 起）
3. 每个实例需复制 `Country.mmdb`，secret 要手动追加

**节点筛选**：44 个节点里只有 32 个能访问 archive.org，
香港 IEPL 系列多不可用（SSL 失败），日本节点最稳。
跑 `find_archive_nodes.py` 重新筛。

### CDX 查询的两个大坑

**坑 1：`matchType=domain` 会把所有子域都包进来。**

```bash
# 这样查 www.njlsedu.cn 会得到 6247 条，混着 yyxqxx/lsgj/lssg 等几十个学校子域
curl "http://web.archive.org/cdx/search/cdx?url=www.njlsedu.cn&matchType=domain&..."
```

更坑的是 `local_path()` 会剥掉域名，导致**不同子域的同名页面互相覆盖**。

**正确做法**：抓完后用正则精确过滤

```python
pat = re.compile(r"https?://www\.njlsedu\.cn(:80)?/\?t=article")
```

**坑 2：CDX 里 http/https 混用。**
比对 URL 时要把协议也归一化，否则明明有存档却查不到。

**坑 3：IA 会间歇性返回 "Temporarily Offline" 页面。**
CDX 查询可能返回一个 HTML 错误页（约 14 行），看起来像"有 14 条记录"。
**每次查完必须检查内容是不是真 CDX 数据**，sleep 几秒重试。

### 判断"某站是否含目标机构内容"的正确方法

**必须匹配正文区域，排除导航/友链模板。**

溧水教育网每个页面底部都有友情链接
`<a href="http://lsgj.njlsedu.cn">江苏省溧水高级中学</a>`，
导致 90%+ 的页面被误判为"提到学校"。

正确做法：

```python
t = re.sub(r"<a\b[^>]*>.*?</a>", "", html, flags=re.I|re.S)  # 去掉所有链接
t = re.sub(r"<script.*?</script>", "", t, flags=re.I|re.S)
body = re.sub(r"<[^>]+>", " ", t)
if re.search(r"省溧中|溧水高级中学", body): ...
```

抽样 25 篇时，23 篇匹配但 22 篇是友链 → 实际只有 1 篇。
按这个错误比例外推，差点错过 73 篇真内容。

### 域名停放页/设备错误页的识别

`is_parked()` 检测这些特征（**不要加体积限制**，停放页也可能 4.7KB）：

- `www.4.cn`、`stencil-overall`、`stencil-tip`、`domain-name`、`a-header`
- `您正在访问`、`官网首页`（4.cn 停放模板）
- `锐捷网络`、`ruijie`、`4008 111 000`（Ruijie 设备错误页）
- `©2000-2015 锐捷网络`

命中 2 个即判定为停放页，`fetch_multi()` 会自动换更早的时间戳。

---

## 六、踩过的坑

按踩到的顺序，给后人避雷：

1. **`re.sub` 替换串含 `\u` 会报 `bad escape`**
   注入 HTML/JS 时，替换串里有 `\u2302` 这类转义 → 必须用
   `lambda m: block + m.group(1)` 做替换函数，不能直接把 block 当替换串。

2. **相对路径少算一层站点目录**
   ```python
   depth = rel.count("/")            # 错！site_old/CuPlayer/index.html 会算成 1
   depth = 1 + rel.count("/")        # 对，1 = 站点目录自身
   ```
   这个 bug 让深层页面的返回按钮指回站点自己的首页，而不是复刻站主页。

3. **`EXT_ROOT` 里放了 `"http://"`**
   导致本站的绝对 URL 全部被当成外链跳过，链接改写出错。
   `EXT_ROOT` 只能放 `mailto:` / `javascript:` / `data:` / `#` 这类。

4. **URL 里的冒号被当 Windows 非法字符**
   路径校验前必须先剥掉 scheme：
   ```python
   re.sub(r"^[a-z][a-z0-9+.\-]*://", "", v, flags=re.I)
   ```

5. **Wayback 地址有两种形态**
   - `/web/<ts>cs_/http://host/path`（双斜杠）
   - `/web/<ts>im_/http:/host/path`（**单斜杠**）
   正则要都覆盖。

6. **文件名与目录冲突**
   资源目录 `html/` 和页面文件名 `html` 撞车 → `safe_dst()` 自动加 `.html` 后缀。

7. **串行抓取会超时且日志丢**
   长任务必须 `python -u`（关缓冲），否则进程被杀时 stdout 全丢，日志 0 字节。
   并且要并发。

8. **改写过的文件不能重跑 rewrite**
   相对路径链接无法反推回绝对 URL，重跑会保持原样。
   要重跑先把文件恢复成原始下载。

---

## 七、文件说明

```
省溧中官网还原站/
├── index.html                  # ★ 入口：怀旧风复刻站主页
├── README.md                   # 本文件
├── site_old/                   # ➊ 学校主站 lsgjzx.cn
│   ├── index.html              #     首页（2017-02 快照，真主站）
│   ├── course_base_2016.html   #     课程基地版首页（另存）
│   ├── art_f124_i1737_p1.html  #     文章页
│   ├── art_v1053.html          #     早期 Mambo 系统文章页
│   ├── list_f124_p2.html       #     列表页
│   ├── cat_100_19.html         #     早期栏目页
│   └── images/ upload_files/
├── site_new/                   # ➍ 后期官网 lsgj.njlsedu.cn
├── site_vod/                   # ➌ 视频系统
├── site_students/              # ➐ 学生子站（仅说明页）
├── site_njls/                  # ➎ 区教育网
├── site_lsjyj/                 # ➏ 区教研室
├── _cdx/                       #     Wayback CDX 原始清单
├── *.py                        #     处理脚本（见第五节）
└── urlmap_*.json               #     各站 URL → 本地路径映射
```

**URL → 文件名映射规则**（找文章用）：

| 原始 URL | 本地文件 |
|---|---|
| `?t=article&c=131&id=1505` | `art_c131_1505.html` |
| `?t=arts&c=10` | `list_c10.html` |
| `bencandy.php?fid-124-id-1737-page-1.htm` | `art_f124_i1737_p1.html` |
| `list.php?fid-124-page-2.htm` | `list_f124_p2.html` |
| `index.php?option=content&task=view&id=1053` | `art_v1053.html` |
| `index.php?option=content&task=category&...&id=100&Itemid=19` | `cat_100_19.html` |
| 静态资源 | 保持原路径 |

**想找某篇具体文章**：搜 `urlmap_site_*.json`。
在 `missing_site_*.txt` 里就说明从未被存档。

---

## 八、免责声明

**本站不是江苏省溧水高级中学的官方网站，与学校无任何关联。**

站内所有页面均来自互联网档案馆（Internet Archive / Wayback Machine）
对学校历年官网的公开快照，由校友整理、转换、链接本地化后发布。

- 站内信息为历史快照，**不代表学校现状**，请勿作为任何依据
- 页面中的职务、名单、数据等均为当年内容，可能已变动
- 若本站内容涉及权益问题，请联系我们，将及时处理

我们只是想把当年那个网站找回来，给校友们一个回去看看的地方。

---

*还原于 2026 年 10 月 18 日 · 仅供校友怀旧参观*
