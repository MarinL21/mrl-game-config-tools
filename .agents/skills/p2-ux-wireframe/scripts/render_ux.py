#!/usr/bin/env python3
"""P2 交互示意图出图器：一份 HTML → 分层 SVG + 评审 PNG，并强制校验交付像素。

    python3 render_ux.py fig_31.html
    python3 render_ux.py ux/*.html --outdir out

产物（同名三件）：
    fig_31.svg       分组命名 SVG —— 拖进 Figma 自动成图层树
    fig_31.png       由 SVG 渲染，所见即 Figma 所得（交付/评审用）
    fig_31.src.png   由 HTML 直接截图 —— 只用来跟上面那张比对，验证烘焙没跑偏

p2-game-ux 规范硬约束：
    单屏 1376x768 / 三连 4128x768 / 流程板必须是 1376x768 的整数倍
    「出图后必须校验最终文件像素尺寸，而不是只在提示词里声明尺寸」→ 本脚本自动校验
"""
import argparse
import glob
import os
import re
import subprocess
import sys
import tempfile

from PIL import Image

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
BASE_W, BASE_H = 1920, 1080

SVG_RE = re.compile(r'<script[^>]*id="__svg__"[^>]*>(.*?)</script>', re.S)
SCREENS_RE = re.compile(r'id="__svg__"[^>]*data-screens="([^"]*)"')


def chrome(args, **kw):
    return subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                           "--no-sandbox", "--allow-file-access-from-files"] + args,
                          capture_output=True, **kw)


def dump_svg(html_path):
    r = chrome(["--dump-dom", "--virtual-time-budget=3000", f"file://{html_path}"])
    dom = r.stdout.decode("utf-8", "replace")
    sm = SCREENS_RE.search(dom)
    screens = [s for s in (sm.group(1).split(',') if sm else []) if s]
    m = SVG_RE.search(dom)
    if not m:
        sys.exit(f"✗ {os.path.basename(html_path)}：没找到烘焙结果。"
                 f"检查 HTML 是否引了 svgbake.js、根节点是否有 class=\"canvas\"")
    return m.group(1).strip(), screens


def shoot(html_path, out_png, w, h):
    chrome([f"--screenshot={out_png}", f"--window-size={w},{h}",
            "--force-device-scale-factor=1", "--default-background-color=00000000",
            "--virtual-time-budget=3000", f"file://{html_path}"], check=True)


def shoot_svg(svg_text, out_png, w, h):
    """把 SVG 内联进壳页再截图 —— 内联可以绕开 <img> 载入 SVG 时的外部资源封锁。"""
    shell = (f'<!doctype html><meta charset="utf-8">'
             f'<body style="margin:0;width:{w}px;height:{h}px;overflow:hidden">{svg_text}</body>')
    fd, tmp = tempfile.mkstemp(suffix=".html", dir=os.path.dirname(out_png) or ".")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(shell)
    try:
        shoot(tmp, out_png, w, h)
    finally:
        os.unlink(tmp)


def check_size(png, expect_w, expect_h):
    w, h = Image.open(png).size
    ok = (w == expect_w and h == expect_h)
    mult = (w % BASE_W == 0 and h % BASE_H == 0 and w and h)
    flag = "✓" if ok else ("~" if mult else "✗")
    note = "" if ok else (f"  ⚠ 期望 {expect_w}x{expect_h}"
                          if not mult else f"  ({w // BASE_W}x{h // BASE_H} 倍基准，合法)")
    return f"{flag} {os.path.basename(png)}  {w}x{h}{note}", ok or mult


def run(html_path, outdir=None):
    html_path = os.path.abspath(html_path)
    base = os.path.splitext(os.path.basename(html_path))[0]
    d = outdir or os.path.dirname(html_path)
    os.makedirs(d, exist_ok=True)

    svg_text, screens = dump_svg(html_path)
    svg_path = os.path.join(d, base + ".svg")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_text)

    m = re.search(r'width="(\d+)"\s+height="(\d+)"', svg_text)
    w, h = (int(m.group(1)), int(m.group(2))) if m else (BASE_W, BASE_H)

    png = os.path.join(d, base + ".png")
    src = os.path.join(d, base + ".src.png")
    shoot_svg(svg_text, png, w, h)
    shoot(html_path, src, w, h)

    layers = len(re.findall(r'<g id="', svg_text))
    slots = len(re.findall(r'<g id="[^"]*"[^>]*data-name="[^"]*"', svg_text))
    line, ok = check_size(png, w, h)
    bad = [s for s in screens if s != f"{BASE_W}x{BASE_H}"]
    scr = (f"   ⛔ 有 {len(bad)} 屏尺寸不对：{','.join(bad)}" if bad
           else (f"   ✓ {len(screens)} 屏均为 {BASE_W}x{BASE_H}" if screens else ""))
    print(f"{line}   图层组 {layers} 个{scr}   →  {os.path.relpath(svg_path)}")
    return ok and not bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html", nargs="+")
    ap.add_argument("--outdir")
    a = ap.parse_args()
    files = [f for pat in a.html for f in (sorted(glob.glob(pat)) or [pat])]
    if not files:
        sys.exit("no html matched")
    allok = all([run(f, a.outdir) for f in files])
    sys.exit(0 if allok else 1)


if __name__ == "__main__":
    main()
