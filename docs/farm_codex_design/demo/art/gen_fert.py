# -*- coding: utf-8 -*-
import sys, time
from pathlib import Path
SK=Path('/Users/marinl/游戏运营策划工具/.agents/skills/p2-art-gen/scripts'); sys.path.insert(0,str(SK))
from ai_art_client import AiArtClient
OUT=Path('/Users/marinl/游戏运营策划工具/output/farm_demo/art/raw/fert'); OUT.mkdir(parents=True,exist_ok=True)
REFS=['/Users/marinl/游戏运营策划工具/output/farm_demo/art/raw/coin/coin_0.png','/Users/marinl/游戏运营策划工具/output/farm_demo/art/raw/boost/boost_1.png']
P=('参考图是这个游戏已有的道具图标风格（软3D卡通、圆润厚实、明亮高饱和、干净高光）。请用同样的风格画一个游戏道具图标：'
   '一小袋敞口的棕色麻布肥料袋，袋口露出深褐色颗粒肥料，袋身贴一片绿叶标签，旁边冒出一颗小嫩芽；'
   '单个主体、正面略俯视、居中占满画面；纯白 #FFFFFF 单一实底背景，边缘干净方便抠图，严禁棋盘格假透明；不要任何文字。')
t0=time.time(); c=AiArtClient(); refs=[c.upload_image(r) for r in REFS]
urls=c.generate(prompt=P,refs=refs,engine='gemini',batch=2,aspect_ratio='1:1',timeout_s=900)
for i,u in enumerate(urls): c.download(u, OUT/f'fert_{i}.png')
print(f'[OK] fert: {len(urls)} 张 ({time.time()-t0:.0f}s)',flush=True)
