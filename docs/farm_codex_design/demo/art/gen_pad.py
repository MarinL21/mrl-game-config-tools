# -*- coding: utf-8 -*-
"""照竞品：草地上「平底 + 一块隆起」的薄地块，两态（可种土面 / 未开垦草面）。"""
import sys, time, traceback
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
SK=Path('/Users/marinl/游戏运营策划工具/.agents/skills/p2-art-gen/scripts')
sys.path.insert(0,str(SK))
from ai_art_client import AiArtClient
OUT=Path('/Users/marinl/游戏运营策划工具/output/farm_demo/art/raw')

BASE=('这是一块从草地上微微隆起的方形小平台，非常薄、几乎贴着地面，顶面完全平整，'
      '四边由一圈很矮很软的草皮包边、自然过渡下去，没有硬边框也没有厚侧壁；'
      '四角圆润；从上方约 50 度俯视，带轻微透视；'
      '柔和的软3D卡通渲染，低饱和淡雅配色，明亮干净，边缘柔和；主体居中占满画面；'
      '纯白 #FFFFFF 单一实底背景，边缘干净方便抠图，严禁灰白棋盘格假透明；'
      '不要任何作物、围栏、石头、文字、人物')
JOBS=[
 ('padsoil','顶面是平整细腻的橙棕色松土，只有极淡的耕痕。'+BASE),
 ('padgrass','顶面是平整的浅绿色草地，和周围草坪同色，只是微微高出一点。'+BASE),
 ('padgold','顶面是平整的深色肥沃湿土，四周草皮里嵌一圈很细的浅金色描边。'+BASE),
]
def run(j):
    name,prompt=j
    c=AiArtClient()
    urls=c.generate(prompt=prompt,refs=[],engine='gemini',batch=2,aspect_ratio='1:1',timeout_s=900)
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
