# -*- coding: utf-8 -*-
"""立体苗床三态 + 分层场景 入库"""
from pathlib import Path
from PIL import Image
RAW=Path('art/raw'); OUT=Path('assets/art')
PICK={'bed':'bed/bed_1','bedgold':'bedgold/bedgold_0','bedlock':'bedlock/bedlock_0'}
for key,rel in PICK.items():
    im=Image.open(RAW/(rel+'.png')).convert('RGBA')
    bb=im.getbbox(); im=im.crop(bb)
    w=380; im=im.resize((w,int(im.height*w/im.width)), Image.LANCZOS)
    im.save(OUT/(key+'.png'))
    print('%s -> %dx%d  %dKB'%(key, im.width, im.height, (OUT/(key+'.png')).stat().st_size//1024))
sc=Image.open(RAW/'scene2/scene2_0.png').convert('RGB')
sc.thumbnail((1600,1600), Image.LANCZOS)
sc.save(OUT/'scene.jpg', quality=86)
print('scene -> %dx%d  %dKB'%(sc.width, sc.height, (OUT/'scene.jpg').stat().st_size//1024))
