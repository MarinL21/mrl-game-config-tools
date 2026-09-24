import sys, time
from pathlib import Path
SK=Path('/Users/marinl/游戏运营策划工具/.agents/skills/p2-art-gen/scripts')
sys.path.insert(0,str(SK))
from ai_art_client import AiArtClient
OUT=Path('/Users/marinl/游戏运营策划工具/output/farm_demo/art/raw/guardsoft'); OUT.mkdir(parents=True,exist_ok=True)
c=AiArtClient()
urls=c.generate(prompt=(
 '一只守护农场的大猩猩角色：圆润敦厚的软3D卡通造型，戴宽檐草帽、系一条浅色麻布围裙，'
 '手里拄着一把小木叉，神情温和地站着；'
 '柔和的软3D卡通渲染，低饱和明亮配色，干净不脏，边缘圆润；全身正面站姿，主体占满画面；'
 '纯白 #FFFFFF 单一实底背景，边缘干净方便抠图，严禁灰白棋盘格假透明；不要任何文字、边框'),
 refs=[],engine='gemini',batch=2,aspect_ratio='1:1',timeout_s=900)
for i,u in enumerate(urls): c.download(u, OUT/f'guardsoft_{i}.png')
print('OK', len(urls))
