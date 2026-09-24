# -*- coding: utf-8 -*-
"""看园巨猿 4 个形态：以现有 guard.png 为参考做平级变体（同角色同站姿，只换装备道具）。"""
import sys, time, traceback
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
SK=Path('/Users/marinl/游戏运营策划工具/.agents/skills/p2-art-gen/scripts')
sys.path.insert(0,str(SK))
from ai_art_client import AiArtClient
OUT=Path('/Users/marinl/游戏运营策划工具/output/farm_demo/art/raw')
REF='/Users/marinl/游戏运营策划工具/output/farm_demo/art/raw/guardsoft/guardsoft_1.png'
BASE=('参考图是这个农场游戏里的看园巨猿角色（戴草帽、系围裙、拿干草叉的软3D卡通大猩猩）。'
      '请画同一个角色的另一套形态：⭐ 必须保持同一张脸、同样的体型比例、同样的正面站姿和柔和软3D卡通渲染，'
      '只更换服装与手持道具：{outfit}'
      '全身、居中、占满画面；纯白 #FFFFFF 单一实底背景，边缘干净方便抠图，严禁棋盘格假透明；不要文字、不要多余物件。')
JOBS=[
 ('form_iron','废土风的铁卫守护者：锈色金属胸甲与肩甲、带护目镜的圆顶头盔、左手举一面拼接铁皮圆盾、右手拿一根缠铁丝的木棒，神情威武。'),
 ('form_trade','绿洲商贾：暗红色商人长袍配金线滚边、腰间挂两只鼓鼓的钱袋、右眼戴单片眼镜、手里托一把木算盘，笑容精明。'),
 ('form_shaman','部落巫医：彩色羽毛头饰、脸上有白色图腾彩绘、脖子挂骨头项链、手持顶端发着绿光的草药法杖、身上披草编短披肩。'),
 ('form_night','夜行者：深靛蓝连帽斗篷、蒙住下半脸的面巾、腰间挂一盏小铜灯笼和一只麻布口袋、脚步轻盈像要去偷菜，眼神狡黠。'),
]
def run(j):
    name,outfit=j
    c=AiArtClient(); ref=c.upload_image(REF)
    urls=c.generate(prompt=BASE.format(outfit=outfit),refs=[ref],engine='gemini',batch=2,aspect_ratio='1:1',timeout_s=900)
    d=OUT/name; d.mkdir(parents=True,exist_ok=True)
    got=[]
    for i,u in enumerate(urls):
        p=d/f'{name}_{i}.png'; c.download(u,p); got.append(str(p))
    return name,got
if __name__=='__main__':
    t0=time.time()
    with ThreadPoolExecutor(max_workers=4) as ex:
        fs={ex.submit(run,j):j[0] for j in JOBS}
        for f in as_completed(fs):
            try: n,g=f.result(); print(f'[OK] {n}: {len(g)} 张 ({time.time()-t0:.0f}s)',flush=True)
            except Exception as e: print(f'[FAIL] {fs[f]}: {e}',flush=True); traceback.print_exc()
    print(f'=== 耗时 {time.time()-t0:.0f}s ===',flush=True)
