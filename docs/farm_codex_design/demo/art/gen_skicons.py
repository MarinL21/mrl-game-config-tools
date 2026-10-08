# -*- coding: utf-8 -*-
"""巨猿形态 8 个技能图标：圆形徽章风（同一风格、金边、深底），以 coin/boost 为风格参考。"""
import sys, time, traceback
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
SK=Path('/Users/marinl/游戏运营策划工具/.agents/skills/p2-art-gen/scripts'); sys.path.insert(0,str(SK))
from ai_art_client import AiArtClient
OUT=Path('/Users/marinl/游戏运营策划工具/output/farm_demo/art/raw')
REFS=['/Users/marinl/游戏运营策划工具/output/farm_demo/art/raw/coin/coin_0.png','/Users/marinl/游戏运营策划工具/output/farm_demo/art/raw/boost/boost_1.png']
BASE=('参考图是这个游戏已有的道具图标风格（软3D卡通、圆润厚实、明亮高饱和、干净高光）。请用同样的风格画一枚游戏技能图标：{what}'
      '单个主体、正面、居中占满画面，不要圆框不要底板；纯白 #FFFFFF 单一实底背景，边缘干净方便抠图，严禁棋盘格假透明；不要任何文字。')
JOBS=[('sk_exp','一把插在金色麦穗旁的木柄锄头，锄刃上有一滴汗珠，表示勤恳劳作。'),
 ('sk_cap','一面铆钉拼接的锈铁圆盾，盾心一颗金色铆钉，表示铁壁防守。'),
 ('sk_gain','一盏亮着暖光的铜提灯，灯后一弯月牙，表示夜间潜行。'),
 ('sk_sell','一把木算盘，算珠间夹着两枚金币，表示精算卖价。'),
 ('sk_seedoff','一张带绳的价签牌，牌上一把小剪刀剪断了一角，表示议价砍价。'),
 ('sk_mut','一只圆底玻璃瓶里长出一株发着紫绿光的嫩芽，表示催芽变异。'),
 ('sk_water','一股从石缝涌出的清泉水柱，顶端一滴大水珠，表示灵泉浇灌。'),
 ('sk_loss','一片绿叶形状的护身符，叶脉发着淡金光，挂着一根红绳，表示护灵减损。')]
def run(j):
    name,what=j; c=AiArtClient(); refs=[c.upload_image(r) for r in REFS]
    urls=c.generate(prompt=BASE.format(what=what),refs=refs,engine='gemini',batch=1,aspect_ratio='1:1',timeout_s=900)
    d=OUT/name; d.mkdir(parents=True,exist_ok=True)
    for i,u in enumerate(urls): c.download(u, d/f'{name}_{i}.png')
    return name,len(urls)
if __name__=='__main__':
    t0=time.time()
    with ThreadPoolExecutor(max_workers=4) as ex:
        fs={ex.submit(run,j):j[0] for j in JOBS}
        for f in as_completed(fs):
            try: n,g=f.result(); print(f'[OK] {n}: {g} 张 ({time.time()-t0:.0f}s)',flush=True)
            except Exception as e: print(f'[FAIL] {fs[f]}: {e}',flush=True)
    print(f'=== 耗时 {time.time()-t0:.0f}s ===',flush=True)
