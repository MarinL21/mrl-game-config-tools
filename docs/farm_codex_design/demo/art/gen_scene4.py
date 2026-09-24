import sys, time, traceback
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
SK=Path('/Users/marinl/游戏运营策划工具/.agents/skills/p2-art-gen/scripts')
sys.path.insert(0,str(SK))
from ai_art_client import AiArtClient
OUT=Path('/Users/marinl/游戏运营策划工具/output/farm_demo/art/raw/scene4'); OUT.mkdir(parents=True,exist_ok=True)
P=('游戏活动界面用的横屏场景背景插画：明亮柔和的农场绿洲。'
   '⭐ 画面正中间必须是一大片完全空旷干净的浅绿色草地，'
   '这片空草地要占满画面中部到下部、横向几乎铺满，上面绝对不要放任何东西；'
   '所有景物——小木屋、矮木栅栏、竹筐南瓜、灌木、树、小溪、水塔——'
   '全部安排在画面最上沿和左右两条窄边上，不要侵入中间的草地；'
   '远景是柔和虚化的沙丘与天空；'
   '柔和的软3D卡通渲染，低饱和明亮，干净留白多；不要任何文字和 UI 元素')
def run(i):
    c=AiArtClient()
    urls=c.generate(prompt=P,refs=[],engine='gemini',batch=2,aspect_ratio='16:9',timeout_s=900)
    for k,u in enumerate(urls): c.download(u, OUT/f'scene4_{i}{k}.png')
    return i,len(urls)
if __name__=='__main__':
    t0=time.time()
    with ThreadPoolExecutor(max_workers=2) as ex:
        fs={ex.submit(run,i):i for i in (0,1)}
        for f in as_completed(fs):
            try: i,n=f.result(); print(f'[OK] batch{i}: {n} 张 ({time.time()-t0:.0f}s)',flush=True)
            except Exception as e: print(f'[FAIL] {fs[f]}: {e}',flush=True)
    print('=== 耗时 %.0fs ==='%(time.time()-t0),flush=True)
