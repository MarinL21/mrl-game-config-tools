# -*- coding: utf-8 -*-
"""农场 demo 美术素材批产：11 个任务并行，每任务 2 张 nano(gemini)。"""
import sys, time, traceback
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

SK = Path('/Users/marinl/游戏运营策划工具/.agents/skills/p2-art-gen/scripts')
sys.path.insert(0, str(SK))
from ai_art_client import AiArtClient

AN = SK.parent / 'anchors'
OUT = Path('/Users/marinl/游戏运营策划工具/output/farm_demo/art/raw')

CUT = ('纯白 #FFFFFF 单一实底背景，主体边缘干净利落方便抠图，'
       '严禁灰白棋盘格假透明、渐变、光晕、背景投影；不要任何文字、边框、UI 元素')
STRIP = ('同一种植物的三个生长阶段横向均匀并排，从左到右依次是：刚破土的两片小嫩芽、'
         '长到一半的植株、完全成熟可以收获的植株，三者由小到大；每株独立、互不重叠、'
         '底部对齐；软3D卡通渲染，厚涂高光，高饱和撞色。' + CUT)
ICON = '软3D卡通渲染，正面平视，主体占满画面。' + CUT

FOOD = [str(AN/'item/食物/果篮2.png'), str(AN/'item/食物/糯米.png')]
PANEL = [str(AN/'ui_panel/感恩厨房效果图.png'), str(AN/'ui_panel/宝石返利活动banner效果图.png')]

JOBS = [
 ('scene','16:9',PANEL,
  '游戏活动界面用的横屏场景背景插画：末世废土上一片被绿意包围的农园绿洲，'
  '远处是沙尘色地平线、破损的钢铁围栏和一座高高的储水塔，中景有木栅栏、引水渠和几株变异植物，'
  '天空从暖黄过渡到青绿，光线柔和通透；画面下方约四成留出大片平整空地，不要放任何物体；'
  '软3D卡通渲染，高饱和撞色，不要任何文字和 UI 元素'),
 ('soil','1:1',[],
  '游戏用的一块方形农田地块贴图，俯视略带斜角：翻整过的深褐色土垄一道道排列，'
  '四边围着旧木板和碎石，土面湿润有颗粒感；软3D卡通渲染，主体占满正方形画面；'
  '不要植物、不要人物。' + CUT),
 ('c1','21:9',FOOD,'一种末世废土上的灰绿色苔藓质速生植物，叶片肥厚带绒毛，顶端结灰白孢子囊。'+STRIP),
 ('c2','21:9',FOOD,'一种锈红色的金属质麦穗作物，穗粒像小铁珠，叶片边缘泛铁锈橙。'+STRIP),
 ('c3','21:9',FOOD,'一种外壳焦黑开裂、裂缝里透出橙红炽光的圆形果实作物，藤叶墨绿。'+STRIP),
 ('c4','21:9',FOOD,'一种铅灰蓝色的发光灵株，半透明花瓣像云雾，花心浮着一颗淡青色光球。'+STRIP),
 ('c5','21:9',FOOD,'一种矮壮的沙棘小树，枝干沙黄多刺，结满密集的橙黄浆果。'+STRIP),
 ('c6','21:9',FOOD,'一种神圣感的白金色小树，枝干像船骨，树冠结着水晶质的星形果实，周身浮淡金光尘。'+STRIP),
 ('coin','1:1',[str(AN/'item/MonkeyCoin.png'), str(AN/'item/darkgold_gem.png')],
  '一枚游戏活动货币图标：金色厚重硬币，币面浮雕一束饱满麦穗，外圈是齿轮与麦芒交替的花边。'+ICON),
 ('boost','1:1',FOOD,
  '一瓶游戏道具速生剂：粗矮玻璃药剂瓶，瓶内翠绿色发光液体和上浮气泡，木塞封口缠麻绳并插一片嫩芽，'
  '瓶身带黄铜固定环。'+ICON),
 ('guard','1:1',[str(AN/'item/p2_monkey_char.png')],
  '一只看守农园的巨猿角色：体型壮硕，肩披旧麻布披风，手握一根带叶木叉，头戴草编宽檐帽，神情警惕守望；'
  '末世废土风格；全身正面立绘。'+ICON),
]

def run(job):
    name, ar, refs, prompt = job
    c = AiArtClient()
    up = [c.upload_image(p) for p in refs]
    urls = c.generate(prompt=prompt, refs=up, engine='gemini', batch=2,
                      aspect_ratio=ar, timeout_s=900)
    d = OUT / name; d.mkdir(parents=True, exist_ok=True)
    got = []
    for i, u in enumerate(urls):
        dest = d / f'{name}_{i}.png'
        c.download(u, dest); got.append(str(dest))
    return name, got

if __name__ == '__main__':
    t0 = time.time(); ok = {}; bad = {}
    with ThreadPoolExecutor(max_workers=6) as ex:
        fs = {ex.submit(run, j): j[0] for j in JOBS}
        for f in as_completed(fs):
            n = fs[f]
            try:
                name, got = f.result(); ok[name] = got
                print(f'[OK] {name}: {len(got)} 张  ({time.time()-t0:.0f}s)', flush=True)
            except Exception as e:
                bad[n] = repr(e)
                print(f'[FAIL] {n}: {e}', flush=True)
                traceback.print_exc()
    print(f'\n=== 完成 {len(ok)}/{len(JOBS)} 任务，耗时 {time.time()-t0:.0f}s ===', flush=True)
    for k, v in bad.items(): print('FAIL', k, v, flush=True)
