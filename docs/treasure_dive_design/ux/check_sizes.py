#!/usr/bin/env python3
"""交互稿自检：单屏必须 1920×1080，内容不许溢出弹窗 / 内容井。靠脚本读数字，不靠肉眼。"""
import re, subprocess, sys
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
path = sys.argv[1] if len(sys.argv) > 1 else "intro3.html"
import os
url = "file://" + os.path.abspath(path)
dom = subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
                      "--allow-file-access-from-files", "--virtual-time-budget=8000",
                      "--dump-dom", url], capture_output=True).stdout.decode("utf-8", "replace")
m = re.search(r'<pre id="__assert"[^>]*>(.*?)</pre>', dom, re.S)
if not m:
    sys.exit("✗ 没找到自检探针（页面没跑起来？）")
report = m.group(1).strip().replace("&lt;", "<").replace("&gt;", ">")
bad = [l for l in report.splitlines() if l.startswith(("OVERFLOW", "CLIP"))]
sizes = [l for l in report.splitlines() if l.startswith("screen")]
for s in sizes:
    ok = s.endswith("=1920x1080")
    print(("✓ " if ok else "✗ ") + s)
for b in bad:
    print("⚠ " + b)
print(f"— {len(sizes)} 屏 / {len(bad)} 处溢出")
sys.exit(0 if all(s.endswith("=1920x1080") for s in sizes) and not bad else 1)
