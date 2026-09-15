#!/usr/bin/env python3
"""给已生成的大板 HTML（*.bundle.html 等）补一条缩放工具条。

    python3 inject_zoom.py flow_marble3.bundle.html [更多.html ...]

为什么单独一个脚本：bundle_html.py 的缩放条只注进 *.preview.html
（当年为了 Figma 插件按真实几何导入，bundle 必须无 transform）。
0828 已定版交付走 HTML 不走 Figma，bundle 才是实际发出去被打开的那一个，
所以需要能单独补。幂等：重复执行只保留一份。
"""
import io, os, re, sys

MARK = "__zoombar"

BAR = r"""
<!-- ══════ 缩放工具条（inject_zoom.py 注入） ══════ -->
<style>
#__zoombar{position:fixed;right:16px;top:16px;z-index:99999;display:flex;gap:6px;align-items:center;
  background:rgba(18,22,30,.94);border:1px solid #3A4658;border-radius:10px;padding:7px 11px;
  box-shadow:0 8px 28px rgba(0,0,0,.6);font:13px/1 -apple-system,"PingFang SC",sans-serif;color:#E8EDF3;
  -webkit-user-select:none;user-select:none}
#__zoombar button{background:#232B36;border:1px solid #3A4658;color:#E8EDF3;border-radius:6px;
  padding:6px 10px;font:600 13px/1 inherit;cursor:pointer}
#__zoombar button:hover{background:#2F3A49;border-color:#5BD6E0}
#__zoombar .pct{min-width:54px;text-align:center;color:#7FE7F0;font-variant-numeric:tabular-nums;cursor:pointer}
#__zoombar .sep{width:1px;height:18px;background:#3A4658}
#__zoombar .tip{color:#7C8797;font-size:12px}
body.__panning{cursor:grabbing}
</style>
<div id="__zoombar">
  <button id="__zout" title="缩小 (⌘−)">&minus;</button>
  <span class="pct" id="__zpct" title="点一下 = 适应宽度">100%</span>
  <button id="__zin" title="放大 (⌘+)">+</button>
  <span class="sep"></span>
  <button id="__zfw" title="⌘0">适应宽度</button>
  <button id="__zfh">整板</button>
  <button id="__z11">100%</button>
  <span class="tip">⌘/Ctrl+滚轮缩放 · 拖动平移</span>
</div>
<script>
(function(){
  var b=document.querySelector('.canvas')||document.getElementById('board')||document.body.firstElementChild;
  if(!b||b.id==='__zoombar') return;
  var W=b.offsetWidth||b.scrollWidth, H=b.offsetHeight||b.scrollHeight;
  var vp=document.createElement('div'); vp.id='__zvp'; vp.style.position='relative';
  b.parentNode.insertBefore(vp,b); vp.appendChild(b);
  b.style.transformOrigin='0 0';
  var k=1;
  function apply(n,anchor){
    var cp=null,r;
    if(anchor){ r=b.getBoundingClientRect(); cp={x:(anchor.x-r.left)/k,y:(anchor.y-r.top)/k}; }
    k=Math.min(3,Math.max(.02,n));
    b.style.transform='scale('+k+')';
    vp.style.width=(W*k)+'px'; vp.style.height=(H*k)+'px';
    document.getElementById('__zpct').textContent=Math.round(k*100)+'%';
    if(cp){ var r2=b.getBoundingClientRect();
      scrollBy(r2.left+cp.x*k-anchor.x, r2.top+cp.y*k-anchor.y); }
  }
  var fw=function(){ apply((innerWidth-36)/W); };
  var fh=function(){ apply(Math.min((innerWidth-36)/W,(innerHeight-36)/H)); };
  document.getElementById('__zin').onclick =function(){ apply(k*1.25); };
  document.getElementById('__zout').onclick=function(){ apply(k/1.25); };
  document.getElementById('__zfw').onclick =fw;
  document.getElementById('__zfh').onclick =fh;
  document.getElementById('__z11').onclick =function(){ apply(1); };
  document.getElementById('__zpct').onclick=fw;
  addEventListener('wheel',function(e){ if(!(e.ctrlKey||e.metaKey)) return; e.preventDefault();
    apply(k*Math.exp(-e.deltaY*0.0035),{x:e.clientX,y:e.clientY}); },{passive:false});
  addEventListener('keydown',function(e){ if(!(e.metaKey||e.ctrlKey)) return;
    if(e.key==='='||e.key==='+'){ e.preventDefault(); apply(k*1.25); }
    if(e.key==='-'||e.key==='_'){ e.preventDefault(); apply(k/1.25); }
    if(e.key==='0'){ e.preventDefault(); fw(); } });
  var pan=null;
  addEventListener('mousedown',function(e){ if(e.target.closest('#__zoombar')) return;
    pan={x:e.clientX,y:e.clientY,l:scrollX,t:scrollY}; document.body.classList.add('__panning'); });
  addEventListener('mousemove',function(e){ if(pan) scrollTo(pan.l-(e.clientX-pan.x),pan.t-(e.clientY-pan.y)); });
  addEventListener('mouseup',function(){ pan=null; document.body.classList.remove('__panning'); });
  fw(); addEventListener('resize',function(){ });
})();
</script>
"""

def inject(path):
    s = io.open(path, encoding="utf-8").read()
    if MARK in s:                                   # 幂等：先剥掉旧的
        s = re.sub(r"\n<!-- ══════ 缩放工具条.*?</script>\n", "\n", s, flags=re.S)
    s = s.rstrip() + "\n" + BAR
    io.open(path, "w", encoding="utf-8").write(s)
    print("✓ %s  %.1f MB  已带缩放条" % (os.path.basename(path), os.path.getsize(path)/1e6))

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(__doc__)
    for f in sys.argv[1:]:
        if not os.path.isfile(f): sys.exit("no such file: " + f)
        inject(f)
