# -*- coding: utf-8 -*-
"""0924 重做苗床：用场景图当风格/视角参考，出真正带厚度的 3/4 视角菜畦（普通 / 良田 / 未开垦）。"""
import sys, time, traceback
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
SK=Path('/Users/marinl/游戏运营策划工具/.agents/skills/p2-art-gen/scripts')
sys.path.insert(0,str(SK))
from ai_art_client import AiArtClient
OUT=Path('/Users/marinl/游戏运营策划工具/output/farm_demo/art/raw')
REF='/Users/marinl/游戏运营策划工具/output/farm_demo/assets/art/scene.jpg'
BASE=('参考图是这个农场游戏的场景背景，请用与参考图完全一致的柔和软3D卡通渲染、明亮低饱和配色、同样的斜上方约 45 度俯视视角。'
      '只画一个孤立物件：{what}'
      '形状是横向的长方形，宽高比约 1.6:1，四角圆润；'
      '⭐ 必须有薄薄的立体厚度——前侧和右侧能看到一条稍深色的土壁，底部贴着一小圈柔和的接地阴影；'
      '主体居中占满画面、四周留少量空白；'
      '纯白 #FFFFFF 单一实底背景，边缘干净方便抠图，严禁灰白棋盘格假透明；'
      '不要任何作物、文字、人物、UI 元素')
JOBS=[
 ('bed_soil','一块翻耕好的菜畦：暖棕色松软的泥土，土面有 4 条平行的浅浅耕垄（横向排列），两三颗小土粒；'
             '菜畦四周包着一圈很窄的青草边和零星小碎石。'),
 ('bed_gold','一块高级的「灌溉良田」菜畦：深褐色湿润肥沃的泥土，土面有 4 条平行的浅耕垄；'
             '菜畦边缘是一圈细细的浅金色石砌镶边，前角有一小段清水细渠在流淌，克制不浮夸。'),
 ('bed_wild','一块尚未开垦的荒地块：同样的长方形地块形状，但表面是干硬发灰的土，长着稀疏的杂草丛、两三朵小野花和几块小石子，'
             '边缘同样包一圈窄草边；整体色调比草坪略暗、略灰。'),
]
def run(j):
    name,what=j
    c=AiArtClient(); ref=c.upload_image(REF)
    urls=c.generate(prompt=BASE.format(what=what),refs=[ref],engine='gemini',batch=2,aspect_ratio='16:9',timeout_s=900)
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
