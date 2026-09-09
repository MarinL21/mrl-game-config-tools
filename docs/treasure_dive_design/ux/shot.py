#!/usr/bin/env python3
"""单屏出图：python3 shot.py 1  →  intro3_p1.png（1920×1080）"""
import os, subprocess, sys, tempfile
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
n = sys.argv[1] if len(sys.argv) > 1 else "1"
out = os.path.abspath(f"intro3_p{n}.png")
url = "file://" + os.path.abspath("intro3.html") + f"?only={n}"
with tempfile.TemporaryDirectory() as ud:          # 并发实例必须各自独立 user-data-dir
    try:   # Chrome 截完图常不自己退，超时杀掉即可，PNG 那时已经落盘
        subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
                        "--allow-file-access-from-files", f"--user-data-dir={ud}",
                        "--virtual-time-budget=9000", "--window-size=1920,1080",
                        f"--screenshot={out}", url], capture_output=True, timeout=90)
    except subprocess.TimeoutExpired:
        subprocess.run(["pkill", "-f", ud], capture_output=True)
print(out, os.path.getsize(out) if os.path.exists(out) else "FAILED")
