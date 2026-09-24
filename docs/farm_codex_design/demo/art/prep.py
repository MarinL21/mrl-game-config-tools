# -*- coding: utf-8 -*-
"""挑定稿 → 三阶段切片 → 压到显示尺寸 → 入 assets/art/"""
from pathlib import Path
from PIL import Image
import numpy as np

RAW = Path('art/raw'); OUT = Path('assets/art'); OUT.mkdir(parents=True, exist_ok=True)
PICK = {'c1':'c1_1','c2':'c2_1','c3':'c3_1','c4':'c4_0','c5':'c5_0','c6':'c6_0',
        'coin':'coin_0','boost':'boost_1','guard':'guard_0','scene':'scene_1','soil':'soil_0'}

def load(name):
    fam = name.split('_')[0]
    return Image.open(RAW/fam/f'{name}.png').convert('RGBA')

def runs(alpha, thresh=8, min_w=12):
    col = (alpha > 24).sum(axis=0)
    on = col > thresh
    out, s = [], None
    for x, v in enumerate(on):
        if v and s is None: s = x
        elif not v and s is not None:
            if x - s >= min_w: out.append((s, x))
            s = None
    if s is not None and len(on) - s >= min_w: out.append((s, len(on)))
    return out

def slice3(name, key):
    im = load(name); a = np.array(im)[:, :, 3]
    segs = runs(a)
    # 合并过近的碎段，直到只剩 3 段
    while len(segs) > 3:
        gaps = [(segs[i+1][0]-segs[i][1], i) for i in range(len(segs)-1)]
        g, i = min(gaps)
        segs[i:i+2] = [(segs[i][0], segs[i+1][1])]
    assert len(segs) == 3, f'{name}: 切出 {len(segs)} 段 {segs}'
    boxes = []
    for s, e in segs:
        sub = im.crop((s, 0, e, im.height))
        bb = sub.getbbox()
        boxes.append((s + bb[0], bb[1], s + bb[2], bb[3]))
    mw = max(b[2]-b[0] for b in boxes); mh = max(b[3]-b[1] for b in boxes)
    H = 300; sc = H / mh
    W = int(mw * sc)
    for i, b in enumerate(boxes):
        part = im.crop(b)
        w, h = int(part.width*sc), int(part.height*sc)
        part = part.resize((max(w,1), max(h,1)), Image.LANCZOS)
        cv = Image.new('RGBA', (W, H), (0,0,0,0))
        cv.paste(part, ((W-part.width)//2, H-part.height), part)
        cv.save(OUT/f'{key}_s{i+1}.png')
    print(f'{key}: 3 阶段 {W}x{H}  段位={segs}')

for fam in ['c1','c2','c3','c4','c5','c6']:
    slice3(PICK[fam], fam)

def one(key, size, mode='RGBA', quality=None):
    im = load(PICK[key])
    if mode == 'RGB':
        bg = Image.new('RGB', im.size, (26,22,18)); bg.paste(im, (0,0), im); im = bg
    im.thumbnail(size, Image.LANCZOS)
    ext = 'jpg' if mode == 'RGB' else 'png'
    p = OUT/f'{key}.{ext}'
    im.save(p, quality=quality or 86)
    print(f'{key}: {im.size} -> {p.name} {p.stat().st_size//1024}KB')

one('coin', (128,128)); one('boost', (128,128)); one('guard', (420,420))
one('soil', (400,400)); one('scene', (1600,1600), mode='RGB', quality=84)
