#!/usr/bin/env python3
"""深海探宝交互稿素材：从真机截图裁切 + 派生（空气泡 / 金银海螺 / 工具图标）。

源图 = `assets/td/_src_真机截图_20260901.png`
      （0901 徐琮淦发的 treasure_dive 测试包真机截图，2000×1159，游戏区 y117..1057）
盘面网格已逐格核过：列心 772/860/948/1036/1124/1212，行心 290/378/468/557/645/734/822/910，格 88px。

    cd docs/treasure_dive_design/ux && python3 scripts/prep_assets.py

⚠ `道具_水母.png` 不在本脚本内生成 —— 它是 p2-art-gen nano 出的发光水母抠图
  （prompt「深海发光水母风格：主题水母+半透明伞盖+飘曳触须+微光气泡；青蓝荧光配色」，
  按亮度做的软抠 + 椭圆羽化），AI 原图 5MB 没进仓库，成品直接入库。重跑本脚本不会动它。
"""
import math
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, '..', 'assets', 'td'))
SRC = Image.open(os.path.join(OUT, '_src_真机截图_20260901.png')).convert('RGBA')


def crop(box, name, size=None, ext='png'):
    im = SRC.crop(box)
    if size:
        im = im.resize(size, Image.LANCZOS)
    if ext == 'jpg':
        im.convert('RGB').save(f'{OUT}/{name}.jpg', quality=84, optimize=True)
    else:
        im.save(f'{OUT}/{name}.png')
    return im


# —— 盘面格子（88×88）
cell_bubble = crop((730, 248, 818, 336), '格_气泡')
crop((904, 336, 992, 424), '格_石块')
crop((992, 424, 1080, 512), '格_海藻')
crop((904, 690, 992, 778), '格_海藻中心')       # ⚠ 现网蓝晶格，暂当九宫格中心格占位
cell_empty = crop((816, 690, 904, 778), '格_空格')
crop((730, 601, 818, 689), '格_奖励露出')

# —— UI 真件（钮的裁切要避开右下角烘死的「进行中 04天13时」）
crop((1372, 918, 1598, 1002), 'UI_钮_炸弹')
crop((1622, 918, 1838, 1002), 'UI_钮_手电')
crop((1865, 225, 1985, 335), 'UI_入口_兑换商店')
crop((1885, 355, 1975, 445), 'UI_钮_预览')
crop((298, 968, 382, 1052), 'UI_钮_规则i')
crop((325, 235, 505, 1015), 'UI_深度轨')
crop((340, 658, 428, 746), 'UI_奖_宝箱')
crop((340, 248, 428, 336), 'UI_奖_装饰件')
crop((1570, 140, 1990, 205), 'UI_资产条')
crop((1380, 222, 1700, 282), 'UI_条_提示')
crop((1360, 280, 1810, 960), 'UI_潜水员')
crop((690, 160, 1330, 1075), 'UI_盘面石框')
# 场景底出 JPEG：HTML 引它，单文件 bundle 要内联 3 次，PNG 会把包撑到 10MB+
crop((0, 117, 2000, 1057), 'UI_场景全屏', ext='jpg')

# —— 派生①：空气泡 = 空格底 + 气泡外环（r≥27 羽化 4px）
def ring_mask(size, r_in=27.0, feather=4.0):
    w, h = size
    cx, cy = (w - 1) / 2, (h - 1) / 2
    m = Image.new('L', (w, h), 0)
    px = m.load()
    for y in range(h):
        for x in range(w):
            d = math.hypot(x - cx, y - cy)
            px[x, y] = 0 if d < r_in else (255 if d > r_in + feather
                                           else int(255 * (d - r_in) / feather))
    return m


empty_bubble = cell_empty.copy()
empty_bubble.paste(cell_bubble, (0, 0), ring_mask(cell_bubble.size))
empty_bubble.save(f'{OUT}/格_空气泡.png')

# —— 派生②：金海螺 = 从气泡里抠海螺（蓝底 chroma-key + 圆形裁边）
conch = cell_bubble.crop((16, 16, 72, 72)).resize((112, 112), Image.LANCZOS)
px = conch.load()
for y in range(112):
    for x in range(112):
        r, g, b, a = px[x, y]
        out = (b > r + 12 or (r + g + b) < 150 or math.hypot(x - 55.5, y - 55.5) > 52)
        px[x, y] = (r, g, b, 0 if out else a)
conch.save(f'{OUT}/道具_金海螺.png')

# —— 派生③：银海螺 = 金海螺亮度线性拉伸后上冷银（直接去饱和会糊成一坨）
sil = conch.copy()
sp = sil.load()
lums = [0.3 * sp[x, y][0] + 0.6 * sp[x, y][1] + 0.1 * sp[x, y][2]
        for y in range(112) for x in range(112) if sp[x, y][3] > 40]
lo, hi = min(lums), max(lums)
for y in range(112):
    for x in range(112):
        r, g, b, a = sp[x, y]
        if a == 0:
            continue
        l = max(0.0, min(1.0, (0.3 * r + 0.6 * g + 0.1 * b - lo) / max(1.0, hi - lo)))
        v = 60 + 165 * l
        sp[x, y] = (int(v * 0.96), int(v + 6), int(min(255, v * 1.06 + 18)), a)
sil.save(f'{OUT}/道具_银海螺.png')

# —— 派生④：工具图标（从真钮里取图标区，居中）
crop((1415, 945, 1500, 1025), '道具_炸弹', (112, 112))
crop((1655, 940, 1745, 1020), '道具_手电', (112, 112))

print('素材已重建 →', OUT)
