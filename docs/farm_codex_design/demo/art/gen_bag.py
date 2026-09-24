# -*- coding: utf-8 -*-
import sys, time
from pathlib import Path
SK=Path('/Users/marinl/游戏运营策划工具/.agents/skills/p2-art-gen/scripts'); sys.path.insert(0,str(SK))
from ai_art_client import AiArtClient
OUT=Path('/Users/marinl/游戏运营策划工具/output/farm_demo/art/raw/seedbag'); OUT.mkdir(parents=True,exist_ok=True)
REFS=['/Users/marinl/游戏运营策划工具/output/farm_demo/art/raw/coin/coin_0.png','/Users/marinl/游戏运营策划工具/output/farm_demo/art/raw/boost/boost_1.png']
P=('参考图是这个游戏已有的道具图标风格（软3D卡通渲染、圆润厚实、明亮高饱和、干净的高光）。请用完全相同的风格画：'
   '一只鼓鼓的浅棕色麻布种子袋，袋口用红绳松松系着、微微敞开，露出几粒彩色的种子，袋身贴一张画着小嫩芽的标签；'
   '单个物件、正面略俯视、居中占满画面；纯白 #FFFFFF 单一实底背景，边缘干净方便抠图，严禁棋盘格假透明；不要任何文字。')
t0=time.time(); c=AiArtClient(); refs=[c.upload_image(r) for r in REFS]
urls=c.generate(prompt=P,refs=refs,engine='gemini',batch=2,aspect_ratio='1:1',timeout_s=900)
for i,u in enumerate(urls): c.download(u, OUT/f'seedbag_{i}.png')
print(f'[OK] seedbag: {len(urls)} 张 ({time.time()-t0:.0f}s)',flush=True)
