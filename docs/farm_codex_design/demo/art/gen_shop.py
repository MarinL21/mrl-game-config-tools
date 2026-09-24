# -*- coding: utf-8 -*-
"""商店道具图标 10 个：以 coin/boost 为风格参考（软3D卡通、纯白底）。"""
import sys, time, traceback
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
SK=Path('/Users/marinl/游戏运营策划工具/.agents/skills/p2-art-gen/scripts')
sys.path.insert(0,str(SK))
from ai_art_client import AiArtClient
OUT=Path('/Users/marinl/游戏运营策划工具/output/farm_demo/art/raw')
REFS=['/Users/marinl/游戏运营策划工具/output/farm_demo/art/raw/coin/coin_0.png','/Users/marinl/游戏运营策划工具/output/farm_demo/art/raw/boost/boost_1.png']
BASE=('参考图是这个游戏已有的道具图标风格（软3D卡通渲染、圆润厚实、明亮高饱和、干净的高光）。请用完全相同的风格画一个新的游戏道具图标：{what}'
      '单个物件、正面略俯视、居中占满画面；纯白 #FFFFFF 单一实底背景，边缘干净方便抠图，严禁棋盘格假透明；不要任何文字。')
JOBS=[
 ('shop_speed','一只蓝色发光的沙漏，周围绕着一圈加速箭头，表示通用加速道具。'),
 ('shop_food','一只敞口的木箱，里面堆满金黄的麦穗和面包，表示粮食资源箱。'),
 ('shop_wood','一捆整齐扎好的原木，用麻绳捆着，表示木材资源箱。'),
 ('shop_iron','一只敞口的木箱，里面是几块银灰色带金属光泽的铁锭，表示铁矿资源箱。'),
 ('shop_ticket','一张金色边框的招募券卡片，中央一枚红色蜡封印章，略微倾斜。'),
 ('shop_emoji','一个圆形聊天气泡徽章，里面是一只咧嘴大笑、举着胡萝卜的卡通大猩猩脸，表示行军表情。'),
 ('shop_frame','一个华丽的圆形头像框：藤蔓缠绕的金色边框，顶部一小簇麦穗装饰，中间是空的。'),
 ('shop_plate','一块横向的木质铭牌，边缘包金属角，牌面上斜插一把小金锄头。'),
 ('shop_scarecrow','一个可爱的小稻草人摆件，草帽、格子衬衫、张开双臂，站在小土墩上。'),
 ('shop_book','一本翻开的绿色封皮手册，封面有金色麦穗徽记，周围飘着几颗小星星，表示手册经验。'),
]
def run(j):
    name,what=j
    c=AiArtClient(); refs=[c.upload_image(r) for r in REFS]
    urls=c.generate(prompt=BASE.format(what=what),refs=refs,engine='gemini',batch=2,aspect_ratio='1:1',timeout_s=900)
    d=OUT/name; d.mkdir(parents=True,exist_ok=True)
    got=[]
    for i,u in enumerate(urls):
        p=d/f'{name}_{i}.png'; c.download(u,p); got.append(str(p))
    return name,got
if __name__=='__main__':
    t0=time.time()
    with ThreadPoolExecutor(max_workers=5) as ex:
        fs={ex.submit(run,j):j[0] for j in JOBS}
        for f in as_completed(fs):
            try: n,g=f.result(); print(f'[OK] {n}: {len(g)} 张 ({time.time()-t0:.0f}s)',flush=True)
            except Exception as e: print(f'[FAIL] {fs[f]}: {e}',flush=True); traceback.print_exc()
    print(f'=== 耗时 {time.time()-t0:.0f}s ===',flush=True)
