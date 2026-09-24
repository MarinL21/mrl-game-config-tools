# -*- coding: utf-8 -*-
"""田地地基 + 中间已开垦的场景，两个任务各 2 张。"""
import sys, time, traceback
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
SK=Path('/Users/marinl/游戏运营策划工具/.agents/skills/p2-art-gen/scripts')
sys.path.insert(0,str(SK))
from ai_art_client import AiArtClient
OUT=Path('/Users/marinl/游戏运营策划工具/output/farm_demo/art/raw')
JOBS=[
 ('plotbase','16:9',
  '游戏农场用的一整片等距菜园地基：大面积平整的深褐色松土平台，土面有轻微起伏、车辙和零星小石子，'
  '边缘不规则、由一圈矮草皮和碎石自然过渡；从斜上方约 35 度俯视，菱形构图铺满画面；'
  '软3D卡通渲染，暖阳光照；纯白 #FFFFFF 单一实底背景，边缘干净方便抠图；'
  '严禁灰白棋盘格假透明；不要任何作物、木箱、围栏、人物、文字'),
 ('scene3','16:9',
  '游戏活动界面用的横屏场景背景插画：末世废土上的一小片绿洲农园。'
  '远景是沙尘色地平线、破损铁丝网与一座高高的储水塔，带空气透视虚化；'
  '中景一条清澈小溪横穿，一座旧木板桥，一间铁皮小屋，几丛变异植物；'
  '前景左右两侧压着大株绿叶、野花与碎石；'
  '画面中间偏下是一大片已经开垦过的褐色田地空地，被矮木栅栏松松围住，地上有车辙和零星草丛，'
  '这片空地上不要放任何作物、箱子或人物；'
  '光线柔和通透，色彩明亮高饱和，层次分明有景深；软3D卡通渲染；不要任何文字和 UI 元素'),
]
def run(j):
    name,ar,prompt=j
    c=AiArtClient()
    urls=c.generate(prompt=prompt,refs=[],engine='gemini',batch=2,aspect_ratio=ar,timeout_s=900)
    d=OUT/name; d.mkdir(parents=True,exist_ok=True)
    got=[]
    for i,u in enumerate(urls):
        p=d/f'{name}_{i}.png'; c.download(u,p); got.append(str(p))
    return name,got
if __name__=='__main__':
    t0=time.time()
    with ThreadPoolExecutor(max_workers=2) as ex:
        fs={ex.submit(run,j):j[0] for j in JOBS}
        for f in as_completed(fs):
            try: n,g=f.result(); print(f'[OK] {n}: {len(g)} 张 ({time.time()-t0:.0f}s)',flush=True)
            except Exception as e: print(f'[FAIL] {fs[f]}: {e}',flush=True); traceback.print_exc()
    print(f'=== 耗时 {time.time()-t0:.0f}s ===',flush=True)
