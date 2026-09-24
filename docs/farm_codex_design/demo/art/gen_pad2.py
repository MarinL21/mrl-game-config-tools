# -*- coding: utf-8 -*-
"""只要土面、不要草皮包边 —— 让地块边缘直接是场景的草坪。"""
import sys, time, traceback
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
SK=Path('/Users/marinl/游戏运营策划工具/.agents/skills/p2-art-gen/scripts')
sys.path.insert(0,str(SK))
from ai_art_client import AiArtClient
OUT=Path('/Users/marinl/游戏运营策划工具/output/farm_demo/art/raw')
BASE=('形状是一块四角圆润的方形地面，从上方约 50 度俯视带轻微透视，很薄、只比地面高出一点点；'
      '⛔ 不要草皮包边、不要绿色外圈、不要任何边框或围栏，主体只有这块地面本身，'
      '边缘自然收边、略带不规则；'
      '柔和的软3D卡通渲染，低饱和淡雅，明亮干净；主体居中占满画面；'
      '纯白 #FFFFFF 单一实底背景，边缘干净方便抠图，严禁灰白棋盘格假透明；'
      '不要作物、石头、文字、人物')
JOBS=[
 ('soil2','一块翻耕好的橙棕色松土地面，表面平整细腻、只有极淡的耕痕和两三颗小土粒。'+BASE),
 ('gold2','一块深色肥沃湿土的地面，表面平整，四边内侧有一道很细的浅金色描边。'+BASE),
]
def run(j):
    name,prompt=j
    c=AiArtClient()
    urls=c.generate(prompt=prompt,refs=[],engine='gemini',batch=2,aspect_ratio='1:1',timeout_s=900)
    d=OUT/name; d.mkdir(parents=True,exist_ok=True)
    for i,u in enumerate(urls): c.download(u, d/f'{name}_{i}.png')
    return name,urls
if __name__=='__main__':
    t0=time.time()
    with ThreadPoolExecutor(max_workers=2) as ex:
        fs={ex.submit(run,j):j[0] for j in JOBS}
        for f in as_completed(fs):
            try: n,g=f.result(); print(f'[OK] {n}: {len(g)} 张 ({time.time()-t0:.0f}s)',flush=True)
            except Exception as e: print(f'[FAIL] {fs[f]}: {e}',flush=True); traceback.print_exc()
    print(f'=== 耗时 {time.time()-t0:.0f}s ===',flush=True)
