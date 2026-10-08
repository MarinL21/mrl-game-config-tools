# -*- coding: utf-8 -*-
"""场景微调：以现有 scene.jpg 为参考，去掉右侧中部自带的几排菜地（和我们的田垄重复），其他保持不变。"""
import sys, time
from pathlib import Path
SK=Path('/Users/marinl/游戏运营策划工具/.agents/skills/p2-art-gen/scripts'); sys.path.insert(0,str(SK))
from ai_art_client import AiArtClient
OUT=Path('/Users/marinl/游戏运营策划工具/output/farm_demo/art/raw/scene5'); OUT.mkdir(parents=True,exist_ok=True)
REF='/Users/marinl/游戏运营策划工具/output/farm_demo/assets/art/scene.jpg'
P=('参考图是这个农场游戏的场景背景。请输出同一张图的修改版，只改一处：把画面右侧中部那几排已经种着蔬菜的田垄（带胡萝卜的褐色菜地）去掉，'
   '换成与周围一致的平整草地，可以点缀两三丛灌木和小花；'
   '其余所有内容——木屋、水塔、风车、小溪、栅栏、树木、南瓜与木车、远景沙丘与天空、构图与机位、色调、16:9 画幅——全部保持完全一致，不要重新构图。'
   '不要任何文字和 UI 元素。')
t0=time.time(); c=AiArtClient(); ref=c.upload_image(REF)
urls=c.generate(prompt=P,refs=[ref],engine='gemini',batch=2,aspect_ratio='16:9',timeout_s=900)
for i,u in enumerate(urls): c.download(u, OUT/f'scene5_{i}.png')
print(f'[OK] scene5: {len(urls)} 张 ({time.time()-t0:.0f}s)',flush=True)
