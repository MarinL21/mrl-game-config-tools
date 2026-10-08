#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合集页：一个文件装下「可玩 demo」+「图文规则说明」两个页签。
两份单文件 HTML 原样塞进 <template>，运行时用 iframe.srcdoc 装载（同源，demo 能读到父页的 ?参数）。
    python3 build_all.py   →  farm_all.html   （先跑 art/bundle.py 和 build_intro.py）"""
import io,os,re,time
HERE=os.path.dirname(os.path.abspath(__file__))
demo=io.open(os.path.join(HERE,'绿洲农园_玩法示意_单文件.html'),encoding='utf-8').read()
intro=io.open(os.path.join(HERE,'farm_intro.html'),encoding='utf-8').read()
for name,src in (('demo',demo),('intro',intro)):
    assert '</template>' not in src, name+' 里有 </template>'
page=f'''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>绿洲农园 · demo + 图文规则说明</title>
<style>
*{{box-sizing:border-box}}html,body{{height:100%;margin:0;background:#0f1114;color:#e6e2d8;font-family:"PingFang SC","Hiragino Sans GB","Microsoft YaHei",system-ui,sans-serif}}
#bar{{position:fixed;left:0;right:0;top:0;height:46px;display:flex;align-items:center;gap:8px;padding:0 14px;background:#0f1114;border-bottom:1px solid #2a2d33;z-index:10}}
#bar b{{font-size:15px;color:#fff;margin-right:10px;white-space:nowrap}}
.tab{{height:32px;padding:0 16px;border-radius:8px;border:1px solid #2a2d33;background:#1a1d22;color:#C8CDD4;font-size:14px;font-weight:700;cursor:pointer;white-space:nowrap}}
.tab.on{{background:linear-gradient(180deg,#ffd34d,#e09a12);color:#3A2A00;border-color:#7a4a00}}
#bar .sp{{flex:1}}#bar small{{font-size:12px;color:#6d7480;white-space:nowrap}}
#bar small a{{color:#8fd3ff;text-decoration:none;margin-left:10px}}
iframe{{position:fixed;left:0;right:0;top:46px;bottom:0;width:100%;height:calc(100% - 46px);border:0;background:#000;display:none}}
iframe.on{{display:block}}
#tip{{position:fixed;left:50%;top:50%;transform:translate(-50%,-50%);color:#C8CDD4;font-size:14px}}
@media (max-width:700px){{#bar small{{display:none}}}}
</style></head><body>
<div id="bar"><b>绿洲农园</b>
 <button class="tab on" data-t="demo">玩法 demo</button><button class="tab" data-t="intro">图文规则说明（程序 / QA）</button>
 <span class="sp"></span><small>生成 {time.strftime("%Y-%m-%d")} · demo 页签支持 ?state=mid / ?rule=N / ?ring 等直达参数（拼在本页链接后）</small></div>
<div id="tip">加载中…</div>
<iframe id="f-demo" class="on" title="玩法 demo"></iframe><iframe id="f-intro" title="图文规则说明"></iframe>
<template id="t-demo">{demo}</template>
<template id="t-intro">{intro}</template>
<script>
(function(){{
 const q=new URLSearchParams(location.search);
 const loaded={{}};
 function load(k){{if(loaded[k])return;loaded[k]=1;const t=document.getElementById('t-'+k);
  // htmlpreview 之类的外壳会把全文里每个 <script 改成 type="text/htmlpreview" 再自己执行，<template> 里的它不管 → 装载前改回来。
  // 注意：这段代码自己也不能出现 script 开标签字面量，否则同样会被它改坏，所以用拼接。
  const T='<scr'+'ipt', L='<li'+'nk';
  const inner=t.innerHTML.replace(new RegExp(T+' type="text\\/htmlpreview"','gi'),T).replace(new RegExp(L+'([^>]*)type="text\\/htmlpreview"','gi'),L+'$1');
  const html='<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">'+inner+'</body></html>';
  document.getElementById('f-'+k).srcdoc=html;}}
 function show(k){{document.querySelectorAll('.tab').forEach(b=>b.classList.toggle('on',b.dataset.t===k));
  document.querySelectorAll('iframe').forEach(f=>f.classList.toggle('on',f.id==='f-'+k));load(k);
  try{{history.replaceState(null,'','#'+k);}}catch(e){{}}}}   // 用 hash 记页签：htmlpreview 之类的外壳占着 search，别动它
 document.querySelectorAll('.tab').forEach(b=>b.onclick=()=>show(b.dataset.t));
 show(q.get('tab')==='intro'||location.hash==='#intro'?'intro':'demo');
 document.getElementById('f-demo').addEventListener('load',()=>{{const e=document.getElementById('tip');if(e)e.remove();}});
}})();
</script></body></html>'''
out=os.path.join(HERE,'farm_all.html'); io.open(out,'w',encoding='utf-8').write(page)
print(f'→ {out}  {os.path.getsize(out)/1048576:.1f} MB')
