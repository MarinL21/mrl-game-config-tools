# -*- coding: utf-8 -*-
import sys, time
from pathlib import Path
SK=Path('/Users/marinl/游戏运营策划工具/.agents/skills/p2-art-gen/scripts'); sys.path.insert(0,str(SK))
from ai_art_client import AiArtClient
OUT=Path('/Users/marinl/游戏运营策划工具/output/farm_demo/art/raw/sk_seedoff2'); OUT.mkdir(parents=True,exist_ok=True)
REFS=['/Users/marinl/游戏运营策划工具/output/farm_demo/art/raw/coin/coin_0.png','/Users/marinl/游戏运营策划工具/output/farm_demo/art/raw/sk_cap/sk_cap_0.png']
P=('参考图是这个游戏已有的图标风格（软3D卡通、圆润厚实、明亮高饱和、干净高光）。请用同样的风格画一枚游戏技能图标：'
   '一张带麻绳的红色价签牌，牌面只有一道斜向的白色折扣条纹，一把小剪刀正剪断牌子一角；'
   '⛔ 牌面上绝对不要任何货币符号、数字或文字（不要 ¥ $ % 等）；'
   '单个主体、正面、居中占满画面，不要圆框不要底板；纯白 #FFFFFF 单一实底背景，边缘干净方便抠图，严禁棋盘格假透明。')
t0=time.time(); c=AiArtClient(); refs=[c.upload_image(r) for r in REFS]
urls=c.generate(prompt=P,refs=refs,engine='gemini',batch=2,aspect_ratio='1:1',timeout_s=900)
for i,u in enumerate(urls): c.download(u, OUT/f'sk_seedoff2_{i}.png')
print(f'[OK] seedoff2: {len(urls)} 张 ({time.time()-t0:.0f}s)',flush=True)
