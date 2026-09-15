#!/usr/bin/env python3
"""闯关弹珠 · 交互流程板 v4 —— 从主界面交互稿 marble_main_v4.html 的「流程模式」逐步截图拼板。

    python3 build_flow_board.py            # → flow4/step_NN.jpg ×16 + flow_marble4.html
    python3 build_flow_board.py --no-shot  # 只重拼板，不重截图

为什么这么做：旧 flow_marble3 板是另一套 DOM 渲染器（marble3.js）画的，跟 v4 主界面稿两边各改各的，
用户 0915 反馈「和交互示意的演示对不上」。现在流程的每一屏都直接由 v4 稿真实渲染（?bare=1&step=N），
步骤定义（FLOW 数组）只在 v4 里维护一份；板上每屏可点 → 打开可操作的 v4 稿并跳到该状态。
"""
import argparse, html, json, os, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageStat

HERE   = os.path.dirname(os.path.abspath(__file__))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SRC    = os.path.join(HERE, "marble_main_v4.html")
OUTDIR = os.path.join(HERE, "flow4")
BOARD  = os.path.join(HERE, "flow_marble4.html")
TMP    = os.environ.get("TMPDIR", "/tmp")

def chrome(args, udd, timeout=60, wait_file=None):
    """headless Chrome 在本稿的流程模式下会把截图/DOM 写完却不退出（rAF 已停也一样），
    所以不等它退出：有 wait_file 就轮询文件出现，出现后再等 0.6s 让写盘完成、直接 kill。"""
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
           "--allow-file-access-from-files", f"--user-data-dir={udd}"] + args
    if wait_file:
        if os.path.exists(wait_file): os.remove(wait_file)
        p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        t0 = time.time()
        while time.time() - t0 < timeout:
            if os.path.exists(wait_file) and os.path.getsize(wait_file) > 0:
                time.sleep(0.6); break
            time.sleep(0.25)
        p.kill(); p.wait()
        if not os.path.exists(wait_file): sys.exit(f"{timeout}s 内没出文件: {wait_file}")
        return None
    try:
        return subprocess.run(cmd, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired as e:      # DOM 多半已经吐出来了
        class R: stdout = e.stdout or b""
        return R()

def read_flow():
    """FLOW 步骤文案从 v4 里取（?flowjson=1 写进 #testlog），板与稿永远同源。"""
    r = chrome(["--virtual-time-budget=3000", "--dump-dom", f"file://{SRC}?flowjson=1&bare=1"],
               os.path.join(TMP, "fb_udd_json"), timeout=40)
    dom = r.stdout.decode("utf-8", "replace")
    m = re.search(r'<pre id="testlog">(.*?)</pre>', dom, re.S)
    if not m:
        sys.exit("读不到 FLOW（#testlog 为空）")
    return json.loads(html.unescape(m.group(1)))

def shoot(i):
    png = os.path.join(OUTDIR, f"step_{i:02d}.png")
    jpg = os.path.join(OUTDIR, f"step_{i:02d}.jpg")
    chrome([f"--screenshot={png}", "--window-size=1920,1080", "--virtual-time-budget=5000",
            f"file://{SRC}?bare=1&still=1&step={i}"], os.path.join(TMP, f"fb_udd_{i}"), wait_file=png)
    im = Image.open(png)
    if im.size != (1920, 1080):
        sys.exit(f"step {i}: 尺寸 {im.size} ≠ 1920×1080")
    sd = sum(ImageStat.Stat(im.convert("L")).stddev)
    if sd < 20:
        sys.exit(f"step {i}: 画面近乎纯色（stddev={sd:.1f}），大概率没渲染出来")
    im.convert("RGB").save(jpg, "JPEG", quality=86, optimize=True)
    os.remove(png)
    return i, os.path.getsize(jpg) // 1024, round(sd, 1)

def build_board(flow):
    X, CAP_H, NOTE_H, GAP_Y, SEC_H = [140, 2420], 66, 170, 110, 110
    y, out = 300, []
    rows = []                                  # 两屏一行；新段必起新行
    for f in flow:
        if not rows or f["sec"] or len(rows[-1]) == 2: rows.append([])
        rows[-1].append(f)
    for row in rows:
        idx0 = flow.index(row[0])
        if row[0]["sec"]:
            y += SEC_H
            out.append(f'<div class="sec abs" style="left:186px;top:{y-76}px;font-size:44px">{row[0]["sec"]}</div>')
        for c, f in enumerate(row):
            n = flow.index(f) + 1; x = X[c]
            out.append(f'<div class="cap abs" style="left:{x}px;top:{y}px">{f["cap"]}</div>')
            out.append(f'<a class="scr abs" href="marble_main_v4.bundle.html?step={n}" target="_blank" '
                       f'style="left:{x}px;top:{y+CAP_H}px" title="打开可操作稿 · 跳到第 {n} 步">'
                       f'<img src="flow4/step_{n:02d}.jpg" width="1920" height="1080" alt="{f["cap"]}">'
                       f'<span class="live">▶ 可操作 · 点开跳到此状态</span></a>')
            out.append(f'<div class="note-d abs" style="left:{x}px;top:{y+CAP_H+1080+24}px;width:1920px">{f["note"]}</div>')
            if c == 0 and len(row) > 1:
                my = y + CAP_H + 540
                out.append(f'<div class="ln abs" style="left:{x+1930}px;top:{my}px;width:440px"></div>'
                           f'<div class="ar r abs" style="left:{x+2370}px;top:{my-10}px"></div>')
        y += CAP_H + 1080 + NOTE_H + GAP_Y
    H = y + 120
    page = f"""<!doctype html>
<meta charset="utf-8">
<title>闯关弹珠 · 交互流程 v4</title>
<link rel="stylesheet" href="p2ux19.css">
<style>
.scr{{display:block;width:1920px;height:1080px;position:absolute;box-shadow:0 0 0 2px #2A2740;cursor:pointer}}
.scr img{{display:block;width:1920px;height:1080px}}
.scr .live{{position:absolute;right:18px;top:18px;background:rgba(62,216,224,.92);color:#062A2E;font:900 26px/1 "PingFang SC",sans-serif;padding:12px 18px;border-radius:12px;opacity:0;transition:opacity .15s}}
.scr:hover .live{{opacity:1}}
.scr:hover{{box-shadow:0 0 0 6px #3ED8E0}}
.note-d b{{color:#fff;font-weight:800}}
.tag{{display:inline-block;background:#3ED8E0;color:#062A2E;font-weight:900;padding:4px 14px;border-radius:10px;margin-right:16px}}
</style>

<div class="canvas board" id="board" style="width:4560px;height:{H}px">
  <div class="board-title abs" style="left:120px;top:70px"><div class="bar"></div><div class="txt">闯关弹珠 · 交互流程 v4</div></div>
  <div class="note-d abs" style="left:186px;top:186px;width:4200px">
    <span class="tag">同源</span>每一屏都是主界面交互稿 v4 的真实渲染（<code>marble_main_v4.html?step=N</code>），不是另画的示意；<b>点任一屏</b>打开可操作稿并跳到该状态，可从该状态继续发射。
    标注只讲功能与判定，奖励内容与数值以数值页为准。共 {len(flow)} 步 · 6 段：进入与准备 / 发射 / 计分核心循环 / 闯关 / 充能 Buff 与付费转化 / 排行与边界态。
  </div>
{chr(10).join('  '+l for l in out)}
</div>
"""
    open(BOARD, "w", encoding="utf-8").write(page)
    return H

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--no-shot", action="store_true"); a = ap.parse_args()
    os.makedirs(OUTDIR, exist_ok=True)
    flow = read_flow(); n = len(flow)
    print(f"FLOW {n} 步（来自 v4）")
    if not a.no_shot:
        with ThreadPoolExecutor(4) as ex:
            for i, kb, sd in ex.map(shoot, range(1, n + 1)):
                print(f"  ✓ step_{i:02d}.jpg  {kb} KB  stddev={sd}")
    H = build_board(flow)
    print(f"✓ flow_marble4.html  板 4560×{H}")

if __name__ == "__main__":
    main()
