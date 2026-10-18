"""移除原站的移动端跳转脚本调用（手机访问会被跳去原站活站）
   只替换 mobile_device_detect("http://...") 这种调用，不动函数定义。
   幂等：跑多次结果一样。
"""
import os, re

BASE = os.path.dirname(os.path.abspath(__file__))
SITES = ["site_old", "site_new", "site_vod", "site_students", "site_njls", "site_lsjyj"]

CALL = re.compile(r'mobile_device_detect\s*\(\s*(["\'])http[^"\']*\1\s*\)')

fixed_files = 0
fixed_calls = 0
targets = set()

for site in SITES:
    root = os.path.join(BASE, site)
    if not os.path.isdir(root):
        continue
    for dp, _, fs in os.walk(root):
        for f in fs:
            if not f.lower().endswith((".html", ".htm", ".js")):
                continue
            p = os.path.join(dp, f)
            raw = open(p, "rb").read()
            try:
                t = raw.decode("utf-8")
            except UnicodeDecodeError:
                t = raw.decode("gbk", "replace")
            if "mobile_device_detect" not in t:
                continue

            # 记录跳转目标
            for m in CALL.finditer(t):
                targets.add(m.group(0)[:80])

            new, n = CALL.subn("void 0", t)
            if n:
                open(p, "w", encoding="utf-8", newline="").write(new)
                fixed_files += 1
                fixed_calls += n

print(f"修复 {fixed_files} 个文件，共移除 {fixed_calls} 处移动跳转调用")
print("跳转目标（已移除）：")
for t in sorted(targets):
    print("  ", t[:90])
