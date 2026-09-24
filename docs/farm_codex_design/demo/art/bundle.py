# -*- coding: utf-8 -*-
"""farm_demo.html + assets/ → 单文件（图片转 data URI），双击即开、可单独发人。
思路：只把 JS 里的路径常量（ART+'x.png' / P2+'x.png' / art(n) 助手）和 HTML 里的 src/url() 换掉，
call site（BTN[kind] / BED[k] / x.ic / ENTRIES 的 ic）自然拿到 data URI，不做调用点正则。"""
import base64, io, re, sys
from pathlib import Path
src=Path('farm_demo.html'); out=Path('绿洲农园_玩法示意_单文件.html')
s=io.open(src,encoding='utf-8').read()
MIME={'.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg'}
cache={}
def uri(rel):
    rel=rel.strip()
    if rel in cache: return cache[rel]
    f=Path(rel)
    if not f.exists(): raise SystemExit('!! 缺文件 '+rel)
    cache[rel]='data:%s;base64,%s'%(MIME[f.suffix.lower()],base64.b64encode(f.read_bytes()).decode())
    return cache[rel]
# 只内嵌真正被引用到的文件：HTML 静态 + JS 字面量 + art(n) 可能拼出的作物/苗床/图标
used=set(re.findall(r'assets/[^"\')\s]+\.(?:png|jpg)',s))
used|={f"assets/art/{f}_s{k}.png" for f in ['c1','c2','c3','c4','c5','c6'] for k in (1,2,3)}
used|={f"assets/art/{n}.png" for n in ['coin','boost','guard','seedbag','form_iron','form_trade','form_shaman','form_night','shop_speed','shop_food','shop_wood','shop_iron','shop_ticket','shop_emoji','shop_frame','shop_plate','shop_scarecrow','shop_book']}
used=sorted(p for p in used if Path(p).exists())
tbl='{'+','.join('"%s":"%s"'%(x,uri(x)) for x in used)+'}'
anchor="const A='assets/', ART=A+'art/', P2=A+'p2/';"
assert anchor in s, '找不到路径常量锚点'
s=s.replace(anchor,"const __EMB="+tbl+";\n"+anchor+"\nconst __r=p=>__EMB[p]||p;")
s=s.replace("const art=n=>ART+n+'.png';","const art=n=>__r(ART+n+'.png');")
n1=len(re.findall(r"\b(?:ART|P2)\+'[^']+\.(?:png|jpg)'",s))
s=re.sub(r"\b(ART|P2)\+'([^']+\.(?:png|jpg))'", r"__r(\1+'\2')", s)
n2=len(re.findall(r'src="assets/[^"]+"',s))+len(re.findall(r'url\(assets/[^)]+\)',s))
s=re.sub(r'src="(assets/[^"]+)"',lambda m:'src="%s"'%uri(m.group(1)),s)
s=re.sub(r'url\((assets/[^)]+)\)',lambda m:'url(%s)'%uri(m.group(1)),s)
s=re.sub(r'<link rel="preload"[^>]*>\n?','',s)   # 单文件不需要预加载外链
io.open(out,'w',encoding='utf-8').write(s)
body=s.split('const __EMB=',1)[1].split(';\nconst A=',1)[1]
leftover=sorted(set(re.findall(r"['\"(](assets/[^'\")]+)",body)))
print('%s  %.1f MB   内嵌 %d 图 / JS 常量 %d 处 / HTML 静态 %d 处'%(out,out.stat().st_size/1048576,len(used),n1,n2))
print('正文里残留的 assets 路径:', leftover or '无')
