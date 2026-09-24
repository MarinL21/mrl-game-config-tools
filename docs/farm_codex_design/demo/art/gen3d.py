# -*- coding: utf-8 -*-
"""立体地块三态：空床 / 灌溉良田 / 未开垦荒地。每个 2 张 nano。"""
import sys, time, traceback
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
SK = Path('/Users/marinl/游戏运营策划工具/.agents/skills/p2-art-gen/scripts')
sys.path.insert(0, str(SK))
from ai_art_client import AiArtClient
OUT = Path('/Users/marinl/游戏运营策划工具/output/farm_demo/art/raw')

VIEW = ('从斜上方约 35 度俯视的立体视角，能清楚看到泥土的厚度和侧壁，像一块摆在地面上的实体，'
        '底部有一圈柔和的接地投影；软3D卡通渲染，厚涂高光，主体占满画面居中；'
        '纯白 #FFFFFF 单一实底背景，主体边缘干净利落方便抠图，'
        '严禁灰白棋盘格假透明、渐变背景、光晕；不要任何文字、边框、植物、人物')
JOBS = [
 ('bed','游戏农场用的一块方形立体种植床：四周是旧木板和铆钉箍成的围框，床里是翻整过的深褐色土垄一道道排列，'
        '土面湿润有颗粒感，边角有零星碎石。'+VIEW),
 ('bedgold','游戏农场用的一块方形立体高级种植床：围框是黄铜与鎏金木板，四角有小铜阀，'
            '床沿嵌一圈引水渠有清水流动，床里泥土油黑肥沃泛湿光。'+VIEW),
 ('bedlock','游戏里一块还没开垦的方形荒地：干裂发白的板结土块，缝里钻出几根枯草，散落碎石与生锈铁片，'
            '没有木框、没有土垄。'+VIEW),
 ('scene2','游戏活动界面用的横屏场景背景插画：末世废土上的一小片绿洲农园。'
           '远景是沙尘色地平线、破损钢铁围栏与一座高高的储水塔，带空气透视轻微虚化；'
           '中景一条清澈小溪横穿，一座旧木板桥，几丛变异植物和一间铁皮小屋；'
           '前景左右两侧压着大株绿叶、野花与碎石；'
           '画面中间偏下留出一大片平整的浅草空地，上面不要放任何物体；'
           '光线柔和通透，色彩明亮高饱和，层次分明有景深；软3D卡通渲染；不要任何文字和 UI 元素'),
]
def run(j):
    name, prompt = j
    c = AiArtClient()
    urls = c.generate(prompt=prompt, refs=[], engine='gemini', batch=2,
                      aspect_ratio=('16:9' if name=='scene2' else '1:1'), timeout_s=900)
    d = OUT/name; d.mkdir(parents=True, exist_ok=True)
    got=[]
    for i,u in enumerate(urls):
        p = d/f'{name}_{i}.png'; c.download(u,p); got.append(str(p))
    return name, got
if __name__=='__main__':
    t0=time.time()
    with ThreadPoolExecutor(max_workers=3) as ex:
        fs={ex.submit(run,j):j[0] for j in JOBS}
        for f in as_completed(fs):
            try:
                n,g=f.result(); print(f'[OK] {n}: {len(g)} 张 ({time.time()-t0:.0f}s)',flush=True)
            except Exception as e:
                print(f'[FAIL] {fs[f]}: {e}',flush=True); traceback.print_exc()
    print(f'=== 耗时 {time.time()-t0:.0f}s ===',flush=True)
