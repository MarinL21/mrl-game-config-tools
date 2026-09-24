# -*- coding: utf-8 -*-
"""照参考：干净圆角土块（普通/良田）+ 柔和草地场景。"""
import sys, time, traceback
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
SK=Path('/Users/marinl/游戏运营策划工具/.agents/skills/p2-art-gen/scripts')
sys.path.insert(0,str(SK))
from ai_art_client import AiArtClient
OUT=Path('/Users/marinl/游戏运营策划工具/output/farm_demo/art/raw')

SOFT=('柔和的软3D卡通渲染，低对比度，明亮干净，颜色淡雅不脏；'
      '从斜上方约 40 度俯视，主体居中占满画面；'
      '纯白 #FFFFFF 单一实底背景，边缘干净方便抠图，严禁灰白棋盘格假透明；'
      '不要任何作物、文字、边框、人物')
JOBS=[
 ('soilplot','游戏农场用的一块简洁的方形菜地：浅棕色松软的土，表面只有极浅的耕痕和两三颗小石子，'
             '四角圆润，厚度很薄几乎贴着地面，底边有一圈很淡的接地阴影；'
             '没有木框、没有围栏、没有石头堆。'+SOFT),
 ('soilgold','游戏农场用的一块简洁的方形高级菜地：深一些的肥沃湿润泥土，四角圆润，厚度很薄；'
             '边缘只有一圈细细的浅金色描边和一道细水渠，克制不浮夸；'
             '没有木框、没有石头堆。'+SOFT),
 ('scenesoft','游戏活动界面用的横屏场景背景插画：明亮柔和的绿洲农场。'
              '画面中间偏下是一大片平整干净的浅绿色草地，这片草地上不要放任何东西；'
              '四周点缀一间圆润的小木屋、一段矮木栅栏、几个竹筐和南瓜、圆乎乎的灌木和小花；'
              '一条清浅的小溪从右侧绕过；远景是柔和虚化的沙丘和一座小水塔；'
              '柔和的软3D卡通渲染，低饱和明亮，干净不堆砌，留白充足；不要任何文字和 UI 元素'),
]
def run(j):
    name,prompt=j
    c=AiArtClient()
    ar='16:9' if name=='scenesoft' else '1:1'
    urls=c.generate(prompt=prompt,refs=[],engine='gemini',batch=2,aspect_ratio=ar,timeout_s=900)
    d=OUT/name; d.mkdir(parents=True,exist_ok=True)
    got=[]
    for i,u in enumerate(urls):
        p=d/f'{name}_{i}.png'; c.download(u,p); got.append(str(p))
    return name,got
if __name__=='__main__':
    t0=time.time()
    with ThreadPoolExecutor(max_workers=3) as ex:
        fs={ex.submit(run,j):j[0] for j in JOBS}
        for f in as_completed(fs):
            try: n,g=f.result(); print(f'[OK] {n}: {len(g)} 张 ({time.time()-t0:.0f}s)',flush=True)
            except Exception as e: print(f'[FAIL] {fs[f]}: {e}',flush=True); traceback.print_exc()
    print(f'=== 耗时 {time.time()-t0:.0f}s ===',flush=True)
