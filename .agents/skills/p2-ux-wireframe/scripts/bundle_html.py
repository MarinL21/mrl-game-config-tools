#!/usr/bin/env python3
"""把交互流程 HTML 打包成单文件自包含版 —— 给浏览器评审 + 给 Figma 插件导入。

    python3 bundle_html.py flow_marble.html          # → flow_marble.bundle.html

做三件事：
  1. <link rel=stylesheet> → 内联 <style>
  2. <img src> / CSS url() 的本地图片 → data URI
  3. <script src> 本地脚本 → 内联（生成型 HTML 靠它建 DOM，插件才看得到）

为什么必须自包含：Figma 的 HTML 导入插件（html.to.design 等）走「粘代码」这条路时
不会去拉相对路径的资源，外链图片一律丢失。
"""
import argparse
import base64
import mimetypes
import os
import re
import sys

MAX_MB = 40

# 评审用的缩放条。⛔ 只注进 *.preview.html，绝不进 *.bundle.html ——
# 插件按渲染后的几何导入，带 transform 会让整板缩水。
VIEWER = """
<style>
  #__vp { position: relative; }
  #__bar { position: fixed; right: 16px; top: 16px; z-index: 99999; display: flex; gap: 6px;
    align-items: center; background: rgba(18,22,30,.94); border: 1px solid #3A4658;
    border-radius: 10px; padding: 7px 11px; box-shadow: 0 8px 28px rgba(0,0,0,.6);
    font: 13px/1 -apple-system, "PingFang SC", sans-serif; color: #E8EDF3; }
  #__bar button { background: #232B36; border: 1px solid #3A4658; color: #E8EDF3;
    border-radius: 6px; padding: 6px 10px; font: 600 13px/1 inherit; cursor: pointer; }
  #__bar button:hover { background: #2F3A49; }
  #__bar .pct { min-width: 48px; text-align: center; color: #7FE7F0;
    font-variant-numeric: tabular-nums; }
  #__bar .sep { width: 1px; height: 18px; background: #3A4658; }
</style>
<div id="__bar">
  <button id="__out">&minus;</button><span class="pct" id="__pct">100%</span><button id="__in">+</button>
  <span class="sep"></span>
  <button id="__fw">适应宽度</button><button id="__fh">整板</button><button id="__11">100%</button>
</div>
<script>
(function () {
  var b = document.querySelector('.canvas') || document.body.firstElementChild;
  var W = b.offsetWidth, H = b.offsetHeight;
  var vp = document.createElement('div'); vp.id = '__vp';
  b.parentNode.insertBefore(vp, b); vp.appendChild(b);
  b.style.transformOrigin = '0 0';
  var k = 1;
  function apply(n) {
    k = Math.min(2, Math.max(0.03, n));
    b.style.transform = 'scale(' + k + ')';
    vp.style.width = (W * k) + 'px'; vp.style.height = (H * k) + 'px';
    document.getElementById('__pct').textContent = Math.round(k * 100) + '%';
  }
  var fw = function () { apply((innerWidth - 36) / W); };
  var fh = function () { apply(Math.min((innerWidth - 36) / W, (innerHeight - 36) / H)); };
  document.getElementById('__in').onclick  = function () { apply(k * 1.25); };
  document.getElementById('__out').onclick = function () { apply(k / 1.25); };
  document.getElementById('__fw').onclick  = fw;
  document.getElementById('__fh').onclick  = fh;
  document.getElementById('__11').onclick  = function () { apply(1); };
  addEventListener('keydown', function (e) {
    if (!(e.metaKey || e.ctrlKey)) return;
    if (e.key === '=' || e.key === '+') { e.preventDefault(); apply(k * 1.25); }
    if (e.key === '-') { e.preventDefault(); apply(k / 1.25); }
    if (e.key === '0') { e.preventDefault(); fw(); }
  });
  // 按住空格拖动平移
  var pan = false, sx, sy, ox, oy;
  addEventListener('mousedown', function (e) {
    if (e.target.closest('#__bar')) return;
    pan = true; sx = e.clientX; sy = e.clientY; ox = scrollX; oy = scrollY;
    document.body.style.cursor = 'grabbing';
  });
  addEventListener('mousemove', function (e) {
    if (pan) scrollTo(ox - (e.clientX - sx), oy - (e.clientY - sy));
  });
  addEventListener('mouseup', function () { pan = false; document.body.style.cursor = ''; });
  fw();
})();
</script>
"""


def data_uri(path):
    mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode()


def bundle(src):
    src = os.path.abspath(src)
    base = os.path.dirname(src)
    html = open(src, encoding="utf-8").read()
    stats = {"css": 0, "img": 0, "js": 0, "miss": []}

    def local(p):
        p = p.split("?")[0].split("#")[0]
        if p and not p.startswith(("http", "data:", "/")) and not os.path.isfile(os.path.join(base, p)):
            alt = os.path.join(base, "assets", p)
            if os.path.isfile(alt):
                p = os.path.join("assets", p)
        if p.startswith(("http://", "https://", "data:", "//")):
            return None
        f = os.path.normpath(os.path.join(base, p))
        return f if os.path.isfile(f) else None

    # 1) CSS
    def css_repl(m):
        f = local(m.group(1))
        if not f:
            stats["miss"].append(m.group(1)); return m.group(0)
        text = open(f, encoding="utf-8").read()
        # CSS 里的 url() 也要转
        def u(mm):
            g = local(mm.group(1).strip("'\""))
            return f'url("{data_uri(g)}")' if g else mm.group(0)
        text = re.sub(r'url\(([^)]+)\)', u, text)
        stats["css"] += 1
        return f"<style>\n{text}\n</style>"

    html = re.sub(r'<link[^>]+href=["\']([^"\']+)["\'][^>]*>', css_repl, html)

    # 2) <img src>
    def img_repl(m):
        pre, path, post = m.group(1), m.group(2), m.group(3)
        f = local(path)
        if not f:
            stats["miss"].append(path); return m.group(0)
        stats["img"] += 1
        return f'{pre}{data_uri(f)}{post}'

    html = re.sub(r'(<img[^>]*\ssrc=["\'])([^"\']+)(["\'])', img_repl, html)

    # 3) <script src>
    def js_repl(m):
        f = local(m.group(1))
        if not f:
            stats["miss"].append(m.group(1)); return m.group(0)
        stats["js"] += 1
        return "<script>\n" + open(f, encoding="utf-8").read() + "\n</script>"

    html = re.sub(r'<script[^>]+src=["\']([^"\']+)["\'][^>]*>\s*</script>', js_repl, html)

    # 4) 通用路径替换 —— 覆盖内联 JS / 内联 CSS 里运行时拼出来的资源路径
    #    例：marble.js 写的是 src="${A}nav/x.png"，静态正则扫不到，必须按路径字面量兜底
    def sweep(m):
        raw = m.group(0)
        rel = m.group(1)
        f = local(rel)
        if not f:
            stats["miss"].append(rel); return raw
        stats["img"] += 1
        return data_uri(f)

    html = re.sub(r'(?:\$\{A\}|assets/)([\w\u4e00-\u9fa5./_-]+\.(?:png|jpg|jpeg|webp|gif|svg))',
                  sweep, html)

    stem = os.path.splitext(os.path.basename(src))[0]
    out = os.path.join(os.path.dirname(src), stem + ".bundle.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)

    # 评审版：同样自包含，额外带缩放条
    prev = os.path.join(os.path.dirname(src), stem + ".preview.html")
    with open(prev, "w", encoding="utf-8") as f:
        f.write(html + VIEWER)

    mb = os.path.getsize(out) / 1e6
    flag = "✓" if mb < MAX_MB else "⚠ 偏大，插件可能吃不下"
    print(f"{flag} {os.path.basename(out)}  {mb:.1f} MB   "
          f"内联 CSS {stats['css']} · 图片 {stats['img']} · JS {stats['js']}")
    print(f"  评审版 {os.path.basename(prev)}  带缩放条（适应宽度 / 整板 / 100% / ⌘±0 / 拖动平移）")
    if stats["miss"]:
        print("  ⛔ 没找到（会以外链形式残留，导入必丢）：")
        for p in dict.fromkeys(stats["miss"]):
            print("     " + p)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html", nargs="+")
    a = ap.parse_args()
    for f in a.html:
        if not os.path.isfile(f):
            sys.exit(f"no such file: {f}")
        bundle(f)


if __name__ == "__main__":
    main()
