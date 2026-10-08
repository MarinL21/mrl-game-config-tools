#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""绿洲农园 · 图文规则说明（给程序 / QA）—— 从 farm_demo.html 真实渲染截图 + 量取元素坐标 + 打编号框，拼成单文件 farm_intro.html。
    python3 build_intro.py            # 全量重截 + 重拼
    python3 build_intro.py --no-shot  # 只重拼（用上次截图）
每屏 = demo 的一个 URL 状态；标注坐标由 demo 的 ?measure= 钩子量出，不靠眼。末尾「数值与口径全集」= demo 规则弹窗第 10 页原样导出。"""
import base64, html, io, json, os, re, subprocess, sys, time, urllib.parse
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__)); SRC=os.path.join(HERE,'farm_demo.html'); OUT=os.path.join(HERE,'farm_intro.html')
SHOTS=os.path.join(HERE,'art','intro_shots'); os.makedirs(SHOTS,exist_ok=True)
CR=os.path.join(HERE,'..','..','.agents','skills','p2-ux-wireframe','scripts','chrome_run.py')
NOSHOT='--no-shot' in sys.argv
POP=(240,60,1680,1020)   # 弹窗类裁到这个区域

SCREENS=[
 dict(id='main0',t='主界面 · 开局',q='noguide&still',crop=None,
  intro='关掉「玩法示意」后的第一屏。盘面占满 1920×1080 固定舞台（按窗口等比缩放），四角挂件；所有二级内容都是从这一屏的入口 / 挂件打开的弹窗。',
  c=[('#title','活动标题横幅','点击 = 打开「玩法示意」弹窗（P2 真切图红绸横幅）'),
     ('#desc','一句话说明','固定文案；写活动目标与永久收益'),
     ('#lvrow','农园等级 / 经验','经验只来自收获；条下「下一目标」= 最近一个会解锁东西的等级（田垄 / 一键 / 种子）'),
     ('#tip','提示条','农园态 / 串门态各一句固定文案'),
     ('#assets','资产条','前三格主城资源（静态示意）；后两格 = 丰收币、速生剂；+ 号打开集市'),
     ('#rank','丰收榜入口','实时名次「第 N 名 / 总人数」；点开榜单'),
     ('#ops','一键操作 ×3 + 去串门','浇水 4 级 / 收获 8 级 / 播种 12 级解锁，锁定时写等级；可操作时红角标显示块数'),
     ('#mile','农会勋绩竖轨','8 档按累计消耗丰收币；节点亮 = 已领；点开勋绩弹窗'),
     ('.plot.empty','空地','虚线 + 钮；点击 = 用手持种子播种（无种子则打开种子袋）'),
     ('.plot.locked:not(.goldlock)','未开垦田垄','木牌写解锁等级或开垦费；等级够且钱够变金牌跳动，点击扣费开垦'),
     ('.plot.goldlock','良田（锁定）','金边 + 水渠、里面还是草；只能付费解锁，点击打开集市付费位'),
     ('#dailyBag','每日种子袋','每活动日领 1 次；可领时浮动 + 红点，领过压灰写倒计时'),
     ('#guard','看园巨猿','立绘随形态换；标签 = 形态名 / 守卫等级 / 抓捕率；点开形态弹窗'),
     ('#status','活动倒计时 + 状态 chips','剩余天数与当日倒计时（P2 规范右下固定位）；chips：植物志进度与速度 buff、偷菜 / 祝福剩余、丰收周末提示'),
     ('#entries','底部入口','种子袋（显示手持与数量）/ 集市 / 植物志 / 勋绩 / 日志 / 谷仓（值 + 件数红点）'),
     ('#ruleBtn','规则 ❗','P2 规范左下角；打开 10 页规则弹窗（第 10 页 = 程序规格）')],
  r=['开局资源：6 块田垄 + 苔灰速苗 ×4 + 丰收币 1,500 + 速生剂 ×3；默认形态农夫猿','只有「结构」变化才重绘田地，倒计时原地刷新；成熟光泡 / 摇摆是 CSS 动画']),
 dict(id='main1',t='主界面 · 进行中',q='state=mid&noguide&still',crop=None,
  intro='同一屏的各种地块状态。头顶信息（计时 / 收获 / 水滴 / 速生剂 / 标记）在独立信息层，贴各自地块近端下沿，不会被前排地块盖住。',
  c=[('.plot.grow','生长中地块','作物贴图三阶段：进度 <42% 幼苗 / ≥42% 生长 / 成熟'),
     ('.hudp .pill:not(.ok)','倒计时药丸','剩余时间 + 进度填充；点地块 = 浇水'),
     ('.hudp .wdrops','浇水点 ×4','亮几个 = 浇过几次；每次 −6.25% 总时长，4 次 −25%'),
     ('.hudp .boostb','速生剂钮','立即成熟 + 本次变异乘数 ×2；没有速生剂时打开集市'),
     ('.plot.mature','成熟地块','玻璃光泡 + 星光 + 作物轻摆；点击收获'),
     ('.hudp .pill.ok','收获提示','作物名 + 异变倍率'),
     ('.plot.mature .ptag','异变词条角标','彩变 / 晶变 / 巨变 / 猿变四色；巨变贴图放大 1.22'),
     ('.tagmini .st','被偷标记','本轮被偷 −30%（护灵技能可减）；下一轮变异 ×1.2'),
     ('.tagmini .bl','祝福标记','收到祝福次数（≤3 计入变异乘数）'),
     ('.plot.gold','良田（已解锁）','深色湿土 + 金边水渠；生长 ×0.75、变异 ×2、不可被偷'),
     ('.sign.can','可开垦金牌','等级与丰收币都满足时跳动'),
     ('.op.n','一键浇水（可用）','角标 = 可浇块数；点击对全部可浇地块各浇 1 次')],
  r=['收获飘字 = 作物名 +颗数 · 总价；一键收获弹汇总（按块、按颗）','被 NPC 偷（demo 每 22 s 抽一次候选）：抓住 → 赔偿 15%；没抓住 → 该株 −30% 并标记下一轮变异 ×1.2']),
 dict(id='ring',t='播种 · 环形选种',q='state=mid&noguide&still&ring',crop=None,
  intro='点任意空地的 +，围着这块地转出一圈种子：手上有的直接种，已解锁但没买的显示价格、点了买 1 颗就种。点 ✕ 或空白处收起。',
  c=[('#ringLayer .rslot:not(.buy)','有种子的格','右上角白标 = 持有数；点击 = 用它播种，并成为「手持」'),
     ('#ringLayer .rslot.buy','没买过的格','虚线框 + 金色价格标；点击 = 扣丰收币买 1 颗并播种；钱不够半透明不可点'),
     ('#ringLayer .rcenter','关闭','✕；点环外任意处同样收起'),
     ('#ringLayer .rslot .rsub','小字','时长 · 单颗售价，帮玩家当场比较')],
  r=['环上只列已解锁的 1~10 号作物 + 手上有的秘种；最多 15 格均匀分布，半径 150px','一键播种（12 级）仍按「手持」种子批量种；手持 = 最近一次环上选的','买种子的钱计入勋绩累计消耗']),
 dict(id='npc',t='串门',q='state=npc&noguide&still',crop=None,
  intro='右上「去串门」进入。同一套田地阵型换成对方的 8 块地，顶部横幅写在谁家与对方抓捕率。',
  c=[('#owner','园主横幅','当前在谁家 + 对方抓捕率'),
     ('#ops','对象切换','4 个 NPC（守卫 1~4 级，按钮写抓捕率）+ 回农园'),
     ('.plot.mature','成熟 → 可偷','点击 = 偷 30%（同株只能一次）；猿变不可偷'),
     ('.plot.grow','生长中 → 可祝福','点击 = 祝福（对方该株变异乘数 ×1.2，累计 ≤3）'),
     ('.plot.locked','已来过','本株已偷 / 已祝福后置灰'),
     ('#guard','对方巨猿','标签换成对方守卫等级与抓捕率'),
     ('#status','剩余次数','偷菜 N/60 · 祝福 N/10，按活动日重置')],
  r=['被抓：空手、次数照扣；偷成功：丰收币直接到账，不计丰收榜','累计祝福 30 次 = 活动任务（速生剂 ×3 + 秘种 ×1）']),
 dict(id='seed',t='种子袋',q='state=mid&noguide&still&pop=seed',crop=POP,
  intro='底部「种子袋」入口打开。15 张卡片，点卡片切换手持种子，底部按钮买种子。',
  c=[('.gcard.on','手持种子','绿框 + 「手持」标；右上角 = 持有数'),
     ('.gcard .tags','四个标签','时长 / 经验 / 单价 / 收获范围，直接来自作物表'),
     ('.gcard .sbtn','购买','价格按钮；商贾猿「议价」时显示划线原价；钱不够置灰'),
     ('.gcard.lock','未到等级','整卡压灰，按钮写「N 级解锁」'),
     ('.gcard@@14','秘种','不售，按钮写来源；收获必返 1 颗')]),
 dict(id='barn',t='谷仓 · 出售',q='state=mid&noguide&still&pop=barn',crop=POP,
  intro='底部「谷仓」入口打开。按「作物 + 形态 + 单价」分组，每组可选数量出售；出售毛额计入丰收榜。',
  c=[('.cxbuff','全部出售可得','所有分组合计'),
     ('.gcard','一组作物','角标 = 库存颗数；异变词条与倍率标签'),
     ('.qsel','数量选择','− / + / 全部'),
     ('[data-sell]','出售本组','按当前数量 × 单价'),
     ('[data-g="sell"]','全部出售','一键清仓')]),
 dict(id='shop0',t='集市 · 农园道具',q='state=mid&noguide&still&shop=0',crop=POP,
  intro='资产条 + 号或底部「集市」打开。左页签「农园道具」= 付费礼包 + 丰收币兑换本活动道具。',
  c=[('.rtabs','两页签 + 余额','农园道具 / 游戏 · 节日道具；下方常驻丰收币与「全部出售」'),
     ('.gcard.pay','付费礼包 ×6','速生剂包 / 良田契 / 秘种礼包 / 农园手册 / 商贾猿 / 巫医猿（demo 直接发货）'),
     ('.rbody .ggrid@@1','丰收币兑换','速生剂每日 5 / 两种秘种活动各 2 / 两个形态各 1；角标写限购进度')]),
 dict(id='shop1',t='集市 · 游戏 · 节日道具',q='state=mid&noguide&still&shop=1',crop=POP,
  intro='右页签。游戏通用道具每日限购；节日专属外观活动各限 1 件（永久）。demo 里买到只记账。',
  c=[('.rbody .ggrid@@0','游戏通用道具','加速 1h / 粮 / 木 / 铁 / 招募券'),
     ('.rbody .ggrid@@1','节日专属','行军表情 / 头像框 / 铭牌 / 主城装饰 各限 1；手册经验每日 3'),
     ('.gcard .corner.r','限购角标','「今日 x/N」或「活动 x/N」，满了按钮变「已售罄」')]),
 dict(id='cx0',t='图鉴 · 植物志',q='state=mid&noguide&still&ctab=0',crop=POP,
  intro='底部「绿洲植物志」打开。每种作物首次收获点亮一格；每格所有作物生长时间 −1%，点亮记录跨节日保留。',
  c=[('.cxbuff','种植速度 buff','已点亮格数 × 1%'),
     ('.cxbar','进度条','n / 15'),
     ('.gcard.on','已点亮','卡片变绿，写「种植速度 +1%」'),
     ('.gcard.lock','未点亮','灰态 + 来源提示')]),
 dict(id='cx1',t='图鉴 · 异变图录',q='state=mid&noguide&still&ctab=1',crop=POP,
  intro='右页签。15 种 × 4 形态 = 60 格；一种作物 4 形态集齐 → 领一份游戏道具（按档）。',
  c=[('.mutlegend','图例','四形态倍率 + 基础概率范围 + 乘数上限'),
     ('.gcard.gold','集齐可领','4 形态齐 → 金框 + 「领取奖励」'),
     ('.mini4','4 形态小格','每格一张该形态预览（同田里的滤镜）+ 倍率 + 是否收集'),
     ('[data-mutr]','领取奖励','按档发游戏道具，只能领一次；入口红点提示')]),
 dict(id='guard',t='看园巨猿 · 守卫与形态',q='state=mid&noguide&still&pop=guard',crop=POP,
  intro='点右下巨猿打开。英雄展示式：左边大立绘舞台，右边称号 + 一句背景 + 三格数据 + 技能列表，底部一排头像点击预览任一形态。只有使用中的形态技能生效，随时免费切换。',
  c=[('.hshow','展示舞台','形态专属配色 + 光环；大立绘 + 名字 / 称号'),
     ('.hbadge','状态角标','使用中 / 已拥有 / ★ 付费形态'),
     ('.hlore','一句背景','FORM_META.lore，纯包装文案'),
     ('.hs.cap','抓捕率','大数 = 形态初始 + 守卫每级 2% + 铁壁技能；小字拆三项'),
     ('[data-g="gup"]','守卫升级','全形态共享；GUARD_COST 600 → 25,000'),
     ('.hs@@2','获取方式','默认 / 丰收币 / 付费 + 是否已拥有'),
     ('.hsk:not(.empty)','技能行','图标 + 名 + 当前效果 + 下一级预览 + 等级点；一个形态所有技能同升'),
     ('.hsk.empty','空技能槽','免费 / 丰收币形态只有 1 条，付费形态 2~3 条'),
     ('.hact','操作','使用中 / 换成这个形态 / 解锁 N 丰收币 / 购买 $；拥有的可技能升级'),
     ('.hstrip','形态切换条','5 个头像，点击只预览不切换；绿点 = 使用中；未拥有压灰')]),
 dict(id='mile',t='农会勋绩',q='state=mid&noguide&still&pop=mile',crop=POP,
  intro='底部「农会勋绩」打开。按累计消耗丰收币 8 档，达标自动发放；另有一条活动任务。',
  c=[('.cxbuff','累计消耗','统计口径：种子 / 开垦 / 守卫 / 形态与技能 / 集市兑换；付费不计'),
     ('.gcard.on','已领档','绿框「已领取」'),
     ('.gcard@@8','活动任务','累计祝福 30 次')]),
 dict(id='rank0',t='丰收榜',q='state=mid&noguide&still&rank=0',crop=POP,
  intro='右上奖杯打开。分 = 出售毛额（偷菜不计），实时排名，同分先到先得；结束按名次邮件发奖。',
  c=[('.rkhead','我的名次卡','毛额 / 距上一名差值 / 当前档 / 再卖多少进上一档'),
     ('.rkrow.me','我在榜中','前 20 名列出；20 名外单独钉一行'),
     ('.rkrow .rw','档位奖励图标','按名次所在档显示'),
     ('[data-ktab="1"]','排名奖励页签','五档奖励卡（1 / 2~3 / 4~10 / 11~50 / 51~100）')]),
 dict(id='bag',t='每日种子袋 · 开袋',q='state=mid&noguide&still&bag',crop=POP,
  intro='点田边种子袋，直接弹结果。2~3 颗，权重偏基础档，只抽已到等级的作物，5% 追加一颗秘种。',
  c=[('.bagres','本次所得','每张卡 = 作物 ×颗数 + 时长 / 单价 / 收获范围'),
     ('[data-g="bagok"]','收下','关闭并自动手持第一种')]),
 dict(id='end',t='活动结束 · 结算',q='state=mid&noguide&still&end',crop=POP,
  intro='第 21 天结束自动弹（规则页也可模拟）。',
  c=[('.kv','结算明细','手上 + 田里（基础价）+ 谷仓（当前价）→ 丰收币 ×20 金币邮件；丰收榜最终名次与奖励；跨节日保留项')]),
 dict(id='rule',t='玩法示意（首次打开自动弹）',q='rule=0&noguide&still',crop=POP,
  intro='无参数打开页面先弹这个；左侧 10 页签，第 10 页「程序规格」= 本文末尾的数值全集。',
  c=[('.rtabs','10 页签','9 页玩家规则 + 第 10 页程序规格'),
     ('.fig','分镜图','用 demo 自己的真实元素拼的 5 步'),
     ('.rul','编号条文','每页 5~6 条'),
     ('[data-g="close"]','开始种菜','关闭后进入新手指引')]),
 dict(id='guide',t='新手指引',q='still',crop=None,
  intro='9 步光圈 + 气泡，按真实状态推进（不是走马灯）：播种 → 浇水 → 等熟 / 速生剂 → 收获 → 谷仓出售 → 种子袋 → 每日种子袋 → 串门 → ❗。可跳过，规则页可重看。',
  c=[('#coach .ring','光圈','套住当前步骤要点的真实元素'),
     ('#coach .bub','气泡','步骤 N/9 + 一句话 + 跳过')]),
]

def chrome(mode,out,url,budget=3000):
    subprocess.run(['python3',CR,mode,out,url,str(budget)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=120)
def testlog(path):
    d=io.open(path,encoding='utf-8',errors='ignore').read()
    m=re.search(r'<pre id="testlog"[^>]*>(.*?)</pre>',d,re.S)
    return json.loads(html.unescape(m.group(1))) if m else None

def build():
    base='file://'+SRC
    secs=[]
    for i,S in enumerate(SCREENS):
        png=os.path.join(SHOTS,S['id']+'.png'); mj=os.path.join(SHOTS,S['id']+'.json')
        if not NOSHOT or not os.path.exists(png):
            for _ in range(3):   # 无头 Chrome 偶发不落盘：最多重截 3 次
                chrome('shot',png,f"{base}?{S['q']}",2500)
                if os.path.exists(png) and os.path.getsize(png)>0: break
            if not os.path.exists(png): sys.exit(f'!! 截图失败 {S["id"]}')
            sels='|'.join(c[0] for c in S['c'])
            chrome('dom',os.path.join(SHOTS,S['id']+'.dom.html'),f"{base}?{S['q']}&measure={urllib.parse.quote(sels,safe='')}",2500)
            m=testlog(os.path.join(SHOTS,S['id']+'.dom.html')) or {}
            for _ in range(2):   # 首个 Chrome 实例偶尔没等到量取钩子，缺了就重量
                if all(m.get(c[0]) for c in S['c']): break
                chrome('dom',os.path.join(SHOTS,S['id']+'.dom.html'),f"{base}?{S['q']}&measure={urllib.parse.quote(sels,safe='')}",4000)
                m=testlog(os.path.join(SHOTS,S['id']+'.dom.html')) or m
            json.dump(m,open(mj,'w'),ensure_ascii=False)
        m=json.load(open(mj))
        im=Image.open(png).convert('RGB'); x0,y0,x1,y1=S['crop'] or (0,0,1920,1080)
        im=im.crop((x0,y0,x1,y1)); W,H=im.size
        buf=io.BytesIO(); im.save(buf,'JPEG',quality=82,optimize=True); b64=base64.b64encode(buf.getvalue()).decode()
        marks=[];legend=[]
        for n,(sel,label,note) in enumerate(S['c'],1):
            r=m.get(sel)
            if not r: print(f'  !! [{S["id"]}] 没量到 {sel}'); legend.append(f'<li><b>{n}. {html.escape(label)}</b><span class="miss">（本屏未截到）</span> {html.escape(note)}</li>'); continue
            rx,ry,rw,rh=r; rx-=x0; ry-=y0
            marks.append(f'<i class="box" style="left:{rx/W*100:.2f}%;top:{ry/H*100:.2f}%;width:{rw/W*100:.2f}%;height:{rh/H*100:.2f}%"></i>'
                         f'<i class="num" style="left:{rx/W*100:.2f}%;top:{ry/H*100:.2f}%">{n}</i>')
            legend.append(f'<li><b>{n}. {html.escape(label)}</b> {html.escape(note)}</li>')
        rules=''.join(f'<li>{html.escape(x)}</li>' for x in S.get('r',[]))
        secs.append(f'<section id="{S["id"]}"><h2><span>{i+1:02d}</span>{html.escape(S["t"])}<code>?{html.escape(S["q"])}</code></h2><p class="intro">{html.escape(S["intro"])}</p>'
                    f'<div class="shot" style="aspect-ratio:{W}/{H}"><img src="data:image/jpeg;base64,{b64}" alt="">{"".join(marks)}</div>'
                    f'<ol class="legend">{"".join(legend)}</ol>'+(f'<ul class="rules">{rules}</ul>' if rules else '')+'</section>')
        print(f'  ok {S["id"]}  {len(S["c"])} 处标注')
    # 数值全集：demo 规则弹窗第 10 页原样导出
    chrome('dom',os.path.join(SHOTS,'spec.dom.html'),f"{base}?rule=9&noguide&still&dumpspec",2500)
    sp=testlog(os.path.join(SHOTS,'spec.dom.html')) or {'html':'<p>导出失败</p>','md':''}
    spec_html=re.sub(r'<button class="sbtn[^"]*"[^>]*data-g="copyspec".*?</button>','',sp['html'],flags=re.S)
    toc=''.join(f'<a href="#{S["id"]}">{i+1:02d} {html.escape(S["t"])}</a>' for i,S in enumerate(SCREENS))+'<a href="#spec">17 数值与口径全集</a>'
    css=open(SRC,encoding='utf-8').read()
    spec_css=re.search(r'/\* ── 程序规格页 ── \*/(.*?)/\* ── 巨猿形态卡 ── \*/',css,re.S).group(1)
    page=f'''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>绿洲农园 · 图文规则说明</title>
<style>
:root{{--gold:#FFC600;--green:#3EEE00;--dim:#C8CDD4;--ink:#1A1A1A}}
*{{box-sizing:border-box}}body{{margin:0;background:#141619;color:#e6e2d8;font-family:"PingFang SC","Hiragino Sans GB","Microsoft YaHei",system-ui,sans-serif;line-height:1.6}}
header{{padding:28px 32px 18px;border-bottom:1px solid #2a2d33;background:#0f1114}}
header h1{{margin:0 0 6px;font-size:26px;color:#fff}}header h1 small{{font-size:14px;color:var(--dim);margin-left:12px;font-weight:400}}
header p{{margin:0;color:var(--dim);font-size:14px}}
nav{{position:sticky;top:0;z-index:5;background:rgba(15,17,20,.96);border-bottom:1px solid #2a2d33;padding:8px 32px;display:flex;flex-wrap:wrap;gap:6px 14px}}
nav a{{font-size:12px;color:var(--dim);text-decoration:none;white-space:nowrap}}nav a:hover{{color:var(--gold)}}
main{{max-width:1440px;margin:0 auto;padding:10px 32px 60px}}
section{{margin:34px 0 0;padding-top:10px}}
h2{{font-size:20px;color:#fff;margin:0 0 6px;display:flex;align-items:center;gap:12px}}h2 span{{color:var(--gold);font-variant-numeric:tabular-nums}}
h2 code{{font-size:12px;color:#8fd3ff;background:#1b1f26;padding:2px 8px;border-radius:6px;font-weight:400;margin-left:auto}}
.intro{{margin:0 0 10px;color:var(--dim);font-size:14px}}
.shot{{position:relative;width:100%;border-radius:10px;overflow:hidden;border:1px solid #2a2d33;background:#000}}
.shot img{{display:block;width:100%;height:100%}}
.box{{position:absolute;border:2px solid var(--gold);border-radius:6px;box-shadow:0 0 0 2px rgba(0,0,0,.55),inset 0 0 0 1px rgba(0,0,0,.35);pointer-events:none}}
.num{{position:absolute;width:26px;height:26px;border-radius:50%;background:var(--gold);color:#3A2A00;font:900 14px/22px system-ui;text-align:center;border:2px solid var(--ink);transform:translate(-50%,-50%);font-style:normal;box-shadow:0 2px 6px rgba(0,0,0,.6)}}
.legend{{list-style:none;margin:12px 0 0;padding:0;display:grid;grid-template-columns:1fr 1fr;gap:6px 24px;font-size:13.5px;color:#ded2bd}}
.legend li{{padding:6px 10px;background:#1a1d22;border:1px solid #262a31;border-radius:8px}}
.legend b{{color:#fff;margin-right:6px}}.legend .miss{{color:#ff8b72;font-size:12px;margin-right:6px}}
.rules{{margin:10px 0 0;padding:10px 14px 10px 30px;background:#1b2416;border:1px solid #2c3e22;border-radius:8px;font-size:13px;color:#d9ecd0}}
#spec{{margin-top:44px;border-top:2px solid #2a2d33;padding-top:20px}}
.spec .cxhead{{display:flex;align-items:center;gap:16px;margin-bottom:10px}}.spec .ph{{font-size:22px;color:var(--gold);font-weight:800;margin-bottom:6px}}.spec .pd{{font-size:14px;color:var(--dim);margin:0}}
{spec_css}
.copy{{position:fixed;right:22px;bottom:22px;z-index:9;background:var(--gold);color:#3A2A00;border:2px solid var(--ink);border-radius:10px;padding:10px 16px;font-weight:800;font-size:14px;cursor:pointer;box-shadow:0 4px 12px rgba(0,0,0,.5)}}
@media (max-width:900px){{.legend{{grid-template-columns:1fr}}main,header,nav{{padding-left:16px;padding-right:16px}}}}
</style></head><body>
<header><h1>绿洲农园 · 图文规则说明<small>给程序 / QA · 生成于 {time.strftime("%Y-%m-%d")} · 截图与坐标由可玩 demo 真实渲染量出</small></h1>
<p>每屏 = demo 的一个 URL 状态（标题右侧的参数可直接拼到 demo 链接后复现）。金框 + 编号对应下方说明；末尾第 17 节是全部数值与口径，按钮可复制为 Markdown。</p></header>
<nav>{toc}</nav>
<main>{''.join(secs)}
<section id="spec"><h2><span>17</span>数值与口径全集<code>?rule=9</code></h2><p class="intro">与 demo 规则弹窗第 10 页同源：数字由数据表现算生成，改表即改文档。</p>{spec_html}</section>
</main>
<button class="copy" onclick="copyMd()">复制数值全集为 Markdown</button>
<textarea id="md" style="display:none">{html.escape(sp["md"])}</textarea>
<script>function copyMd(){{const t=document.getElementById('md').value;const ok=()=>{{const b=document.querySelector('.copy');b.textContent='已复制 ✓';setTimeout(()=>b.textContent='复制数值全集为 Markdown',1600);}};
if(navigator.clipboard)navigator.clipboard.writeText(t).then(ok,()=>{{}});else{{const ta=document.createElement('textarea');ta.value=t;document.body.appendChild(ta);ta.select();document.execCommand('copy');ta.remove();ok();}}}}</script>
</body></html>'''
    io.open(OUT,'w',encoding='utf-8').write(page)
    print(f'→ {OUT}  {os.path.getsize(OUT)/1048576:.1f} MB  {len(SCREENS)} 屏 + 数值全集')
if __name__=='__main__': build()
