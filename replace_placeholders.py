"""把占位图（1x1 PNG）替换成另一站的真实文件"""
import os, sys, shutil

PH_LEN = 70          # 占位 PNG 字节数
PH_SIG = b"\x89PNG\r\n\x1a\n"

pairs = [("site_new", "site_old"), ("site_old", "site_new")]

for target, source in pairs:
    replaced = still = 0
    for dp, _, fs in os.walk(target):
        for f in fs:
            p = os.path.join(dp, f)
            try:
                if os.path.getsize(p) != PH_LEN:
                    continue
                with open(p, "rb") as fh:
                    if fh.read(8) != PH_SIG:
                        continue
            except OSError:
                continue
            rel = os.path.relpath(p, target).replace("\\", "/")
            src = os.path.join(source, rel.replace("/", os.sep))
            if os.path.isfile(src) and os.path.getsize(src) > PH_LEN:
                shutil.copy2(src, p)
                replaced += 1
            else:
                still += 1
    print(f"{target}: 占位图替换为真实文件 {replaced} 个，仍缺 {still} 个")
