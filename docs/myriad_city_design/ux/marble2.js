/* ===========================================================================
   marble2.js —— 宇宙弹弹乐 界面构件器 v2
   骨架照搬 P2 现有的「幸运弹弹弹」（8月周年庆本体 gacha），不再自创。

   两版布局，state.layout 切换：
     'A' 严格套壳  —— 盘面占满，辅助功能挂四角，无右面板
     'B' 套壳+面板 —— 盘面收窄，右侧 739 面板承两条进度与大奖

   弹弹乐比幸运弹弹弹多出来的四样东西，各自找位置挂：
     撞击计数 7/11 + 本发累计 → 复用盘顶提示条，发射后由「怎么玩」变「实时读数」
     入槽进度 Buff          → 盘底导轨上方的横条（A）／右面板（B）
     高级弹珠 ×5            → 盘左侧「弹珠类型」切换器（幸运弹弹弹「免费」按钮的位置语义）
     榜首限定皮肤            → 排行榜卡里的大奖缩略图（幸运弹弹弹本来就有这个位）
   =========================================================================== */
(function () {
  const A = 'assets/';
  const L = (n) => `data-layer="${n}" data-name="${n}"`;
  const QC = ['#9AA6B4', '#3E7BD6', '#A25BD6', '#FFC600', '#A25BD6', '#3E7BD6', '#9AA6B4'];

  // ── 布局参数：两版只差盘面与右侧 ──
  function geo(s) {
    if (s.layout === 'C') return { bx: 424, bw: 1096, by: 306, bh: 630, cab: true };
    return s.layout === 'B'
      ? { bx: 392, bw: 980, by: 290, bh: 700, panel: true, px: 1392, pw: 508 }
      : { bx: 620, bw: 980, by: 250, bh: 700, panel: false };
  }

  // ── 左侧导航条（真切图） ──
  function nav() {
    return `<div class="nav abs" ${L('左侧导航条')}>
      <img class="abs" style="left:0;top:0" width="358" height="1080" src="${A}nav/导航底板_358x1080.png">
      <div class="abs" style="left:11px;top:17px" ${L('返回按钮')}>
        <img class="abs" style="left:0;top:0" width="189" height="113" src="${A}nav/返回按钮底_189x113.png">
        <img class="abs" style="left:70px;top:22px" width="49" height="69" src="${A}nav/返回箭头_49x69.png"></div>
      <div class="abs" style="left:6px;top:158px" ${L('分组条-热门活动')}>
        <img class="abs" style="left:0;top:0" width="345" height="56" src="${A}nav/分组标题条_345x56.png">
        <div class="t group abs nav-tab-hit" style="left:0;top:0;width:345px;height:56px;font-size:30px">热门活动</div></div>
      <div class="abs" style="left:0;top:236px" ${L('页签-宇宙弹弹乐 选中态')}>
        <img class="abs" style="left:0;top:0" width="368" height="152" src="${A}nav/页签_黄选中含尖角_368x152.png">
        <div class="t dark abs nav-tab-hit" style="left:0;top:0;width:345px;height:152px;font-size:44px;line-height:1.15">宇宙<br>弹弹乐</div></div>
      <div class="t abs nav-tab-hit" style="left:6px;top:412px;width:345px;height:76px;font-size:50px;color:#C8CDD4" ${L('页签-活动2')}>活动 2</div>
      <div class="abs" style="left:6px;top:520px" ${L('分组条-普通活动')}>
        <img class="abs" style="left:0;top:0" width="345" height="56" src="${A}nav/分组标题条_345x56.png">
        <div class="t group abs nav-tab-hit" style="left:0;top:0;width:345px;height:56px;font-size:30px">普通活动</div></div>
      <div class="t abs nav-tab-hit" style="left:6px;top:600px;width:345px;height:76px;font-size:50px;color:#C8CDD4" ${L('页签-活动3')}>活动 3</div>
      <div class="abs" style="left:6px;top:700px" ${L('分组条-赛事')}>
        <img class="abs" style="left:0;top:0" width="345" height="56" src="${A}nav/分组标题条_345x56.png">
        <div class="t group abs nav-tab-hit" style="left:0;top:0;width:345px;height:56px;font-size:30px">赛事</div></div>
      <div class="t abs nav-tab-hit" style="left:6px;top:780px;width:345px;height:76px;font-size:50px;color:#C8CDD4" ${L('页签-活动4')}>活动 4</div>
    </div>`;
  }

  // ── 右上资产条 ──
  function assets(s) {
    const chip = (icon, num, gold, name) => `
      <div class="abs" style="position:relative;width:210px;height:62px;background:rgba(10,12,18,.78);border:2px solid ${gold ? '#FFC600' : '#4C586A'};border-radius:31px" ${L(name)}>
        <img class="abs" style="left:5px;top:5px" width="52" height="52" src="${A}task/${icon}">
        <div class="t ${gold ? 'gold' : ''} abs sm" style="left:66px;top:13px;font-size:32px">${num}</div>
        <div class="t dark abs" style="left:154px;top:7px;width:48px;height:48px;background:#3EEE00;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:36px">+</div></div>`;
    return `<div class="abs" style="right:20px;top:16px;display:flex;gap:12px" ${L('资产条')}>
      ${chip('道具图标A_UiItemsGoldAllPower.png', s.balls, false, '资产-弹珠')}
      ${chip('道具图标B_IconRisingStarStone4.png', s.adv, true, '资产-高级弹珠')}</div>
      ${s.lowHint ? `<div class="abs" style="right:20px;top:88px;width:432px;height:52px;background:rgba(255,90,78,.18);border:2px solid #FF5A4E;border-radius:10px;display:flex;align-items:center;justify-content:center" ${L('弹珠不足提示')}><div class="t sm" style="font-size:26px;color:#FF8A80">${s.lowHint}</div></div>` : ''}`;
  }

  // ── 档位选择器（盘左上外侧，橙按钮 + 竖向下拉） ──
  function tier(s) {
    const list = [1, 5, 10].map((v, i) => `
      <div class="abs" style="left:0;top:${88 + i * 72}px;width:200px;height:72px;background:${s.mult === v ? '#FFD24A' : '#EDEFF2'};border-bottom:2px solid #C9CFD8;display:flex;align-items:center;gap:12px;padding-left:18px" ${L('档位选项-x' + v)}>
        <img width="42" height="42" src="${A}task/道具图标A_UiItemsGoldAllPower.png">
        <div style="font-weight:900;font-size:32px;color:#2A2A2A">×${v}</div></div>`).join('');
    const ty = s.layout === 'B' ? 112 : 150;
    return `<div class="abs" style="left:392px;top:${ty}px;width:200px" ${L('档位选择器')}>
      <div class="abs" style="left:0;top:0;width:200px;height:76px;background:linear-gradient(180deg,#FFC94A,#E08A0C);border:3px solid #7A4A06;border-radius:12px;display:flex;align-items:center;gap:10px;padding-left:16px" ${L('档位-当前')}>
        <img width="44" height="44" src="${A}task/道具图标A_UiItemsGoldAllPower.png">
        <div class="t dark" style="font-size:34px">×${s.mult}</div></div>
      ${s.tierOpen ? `<div class="abs" style="left:0;top:0;width:200px;height:${88 + 3 * 72}px" ${L('档位下拉')}>${list}</div>` : ''}
      ${s.layout === 'B' ? '' : `<div class="t abs sm" style="left:0;top:${s.tierOpen ? 320 : 84}px;width:200px;text-align:center;font-size:22px;color:#C8CDD4">得分 / 消耗倍数</div>`}</div>`;
  }

  // ── 弹珠类型切换（盘左下外侧） ──
  function ballType(s) {
    if (s.layout === 'B') {
      return `<div class="abs" style="left:612px;top:112px;width:264px;height:76px;background:rgba(10,12,18,.72);border:3px solid ${s.advSel ? '#FFC600' : '#4C586A'};border-radius:12px;display:flex;align-items:center;gap:12px;padding-left:16px" ${L('弹珠类型切换')}>
        <img width="48" height="48" src="${A}task/${s.advSel ? '道具图标B_IconRisingStarStone4.png' : '道具图标A_UiItemsGoldAllPower.png'}">
        <div class="t ${s.advSel ? 'gold' : ''} sm" style="font-size:28px;white-space:nowrap">${s.advSel ? '高级 ×5' : '普通弹珠'}</div></div>`;
    }
    return `<div class="abs" style="left:392px;top:660px;width:200px;height:150px;background:rgba(10,12,18,.72);border:3px solid ${s.advSel ? '#FFC600' : '#4C586A'};border-radius:14px" ${L('弹珠类型切换')}>
      <div class="t abs sm" style="left:0;top:12px;width:200px;text-align:center;font-size:24px;color:#C8CDD4">弹珠类型</div>
      <img class="abs" style="left:70px;top:44px" width="60" height="60" src="${A}task/${s.advSel ? '道具图标B_IconRisingStarStone4.png' : '道具图标A_UiItemsGoldAllPower.png'}">
      <div class="t ${s.advSel ? 'gold' : ''} abs sm" style="left:0;top:110px;width:200px;text-align:center;font-size:28px">${s.advSel ? '高级 ×5' : '普通'}</div></div>`;
  }

  // ── 排行榜卡（盘右上，大奖缩略图 + 全服/本服 + 奖杯按钮） ──
  function rankCard(s, g) {
    if (g.panel) return '';
    const x = 1330;
    return `<div class="abs" style="left:${x}px;top:110px;width:470px;height:168px" ${L('排行榜卡')}>
      <div class="slot abs" style="left:0;top:10px;width:104px;height:70px" data-slot="榜首大奖_限定主城皮肤">大奖</div>
      <div class="slot abs" style="left:0;top:88px;width:104px;height:70px" data-slot="次档大奖_限时皮肤">次档</div>
      <div class="abs" style="left:112px;top:10px;width:230px;height:70px;background:linear-gradient(180deg,#F4C86A,#C98A22);border:3px solid #7A4A06;border-radius:8px" ${L('全服榜')}>
        <div class="t dark abs" style="left:0;top:8px;width:230px;text-align:center;font-size:24px">全服</div>
        <div class="t dark abs" style="left:0;top:38px;width:230px;text-align:center;font-size:26px">TIPS</div></div>
      <div class="abs" style="left:112px;top:88px;width:230px;height:70px;background:linear-gradient(180deg,#4FC3D8,#1F7C97);border:3px solid #0C3B4C;border-radius:8px" ${L('本服榜')}>
        <div class="t abs sm" style="left:0;top:6px;width:230px;text-align:center;font-size:24px">本服</div>
        <div class="t gold abs sm" style="left:0;top:36px;width:230px;text-align:center;font-size:28px">${s.rank}th</div></div>
      <div class="abs" style="left:352px;top:16px;width:118px;height:118px;border-radius:50%;background:linear-gradient(160deg,#6FD8F0,#2A6E9C);border:4px solid #123A55;display:flex;flex-direction:column;align-items:center;justify-content:center" ${L('排行榜按钮')}>
        <div class="slot" style="width:48px;height:48px;border-width:2px"></div>
        <div class="t sm" style="font-size:22px;margin-top:4px">排行榜</div></div></div>`;
  }

  // ── 顶部发射口 ×5 ──
  function launchers(s, g) {
    const n = 5, w = 118, gap = (g.bw - n * w) / (n + 1);
    let h = '';
    for (let i = 0; i < n; i++) {
      const x = g.bx + gap + i * (w + gap);
      const off = s.flying;
      h += `<div class="abs" style="left:${x}px;top:${g.by - 92}px;width:${w}px;height:104px" ${L('发射口' + (i + 1) + (off ? ' 置灰' : ''))}>
        <div class="abs" style="left:14px;top:0;width:90px;height:62px;border-radius:50%;background:${off ? 'linear-gradient(180deg,#5C7C99,#33506B)' : 'linear-gradient(180deg,#FFD24A,#E08A0C)'};border:4px solid ${off ? '#22364A' : '#7A4A06'}"></div>
        ${off ? '' : `<div class="abs" style="left:44px;top:18px;width:0;height:0;border-left:15px solid transparent;border-right:15px solid transparent;border-top:20px solid #7A4A06"></div>`}
        <div class="abs" style="left:28px;top:52px;width:62px;height:50px;background:#C9A882;border:4px solid #7A5A34;border-radius:6px 6px 14px 14px"></div></div>`;
    }
    return h;
  }

  // ── 盘顶提示条 / 实时读数（弹弹乐把它复用成 HUD） ──
  function hintBar(s, g) {
    const live = s.hits > 0 || s.flying;
    const inner = live
      ? `<div class="abs" style="left:0;top:0;width:${g.bw}px;height:52px;display:flex;align-items:center;justify-content:center;gap:14px">
           <div class="t sm" style="font-size:28px">撞击</div>
           <div class="t ${s.burst ? 'gold' : 'cyan'}" style="font-size:36px">${s.hits} / 11</div>
           <div class="t sm" style="font-size:28px;color:#8A929B">·</div>
           <div class="t sm" style="font-size:28px">本发累计</div>
           <div class="t gold" style="font-size:36px">${s.acc.toLocaleString()}</div></div>`
      : `<div class="t dark abs" style="left:0;top:6px;width:${g.bw}px;text-align:center;font-size:30px">点击任意洞口发射弹珠</div>`;
    return `<div class="abs" style="left:${g.bx}px;top:${g.by + 14}px;width:${g.bw}px;height:52px;background:${live ? 'rgba(10,14,26,.82)' : 'linear-gradient(180deg,#FFD98A,#E0A83C)'};border-radius:8px" ${L(live ? '实时读数条' : '操作提示条')}>${live ? '' : ''}${inner}</div>`;
  }

  // ── 盘面：钉阵 + 撞柱 + 弹珠 + 拖尾 + 飘字 ──
  function plinko(s, g) {
    const ROWS = 8, PAD = 70, IY = 90, IH = g.bh - 210;
    let h = '';
    const POSTS = { '1-3': 3, '3-1': 5, '3-5': 5, '5-2': 8, '5-4': 8 };
    for (let r = 0; r < ROWS; r++) {
      const n = r % 2 === 0 ? 7 : 6;
      const y = IY + r * (IH / (ROWS - 1));
      const gap = (g.bw - PAD * 2) / (n - 1 + (r % 2 === 0 ? 0 : 1));
      for (let c = 0; c < n; c++) {
        const x = PAD + c * gap + (r % 2 ? gap / 2 : 0);
        const num = POSTS[r + '-' + c];
        if (num) {
          const dead = s.dead;
          h += `<div class="abs" style="left:${x - 34}px;top:${y - 34}px;width:68px;height:68px;border-radius:50%;background:${dead ? '#3B4250' : 'linear-gradient(160deg,#6FD8F0,#2A6E9C)'};border:4px solid ${dead ? '#2A303C' : '#123A55'};display:flex;align-items:center;justify-content:center" ${L('撞柱-' + num + '分' + (dead ? ' 熄灭' : ''))}>
            <div class="t ${dead ? '' : 'gold'} sm" style="font-size:26px;${dead ? 'color:#5A6272' : ''}">${num}</div></div>`;
        } else {
          h += `<div class="abs" style="left:${x - 11}px;top:${y - 11}px;width:22px;height:22px;border-radius:50%;background:#C9A882;box-shadow:0 3px 0 #8A6A44"></div>`;
        }
      }
    }
    const trail = (s.trail || []).map((p, i) =>
      `<div class="abs" style="left:${p[0] - 9}px;top:${p[1] - 9}px;width:18px;height:18px;border-radius:50%;background:${s.advSel ? '#FFC600' : '#EAF2FF'};opacity:${0.15 + i * 0.14}"></div>`).join('');
    const ball = s.ball
      ? `<div class="abs" style="left:${s.ball[0] - 21}px;top:${s.ball[1] - 21}px;width:42px;height:42px;border-radius:50%;background:${s.advSel ? '#FFC600' : '#EAF2FF'};box-shadow:0 0 26px 8px ${s.advSel ? 'rgba(255,198,0,.8)' : 'rgba(160,210,255,.65)'}" ${L('弹珠')}></div>` : '';
    const pop = s.pop
      ? `<div class="t green abs" style="left:${s.pop[0]}px;top:${s.pop[1]}px;font-size:44px" ${L('命中飘字')}>+${s.pop[2]}</div>` : '';
    const burst = s.burst
      ? `<div class="abs" style="left:${g.bw / 2 - 260}px;top:${g.bh / 2 - 110}px;width:520px;height:190px;border:5px solid #FFC600;border-radius:18px;background:rgba(255,198,0,.18);display:flex;flex-direction:column;align-items:center;justify-content:center" ${L('第11次翻倍演出')}>
           <div class="t gold" style="font-size:66px">累计 ×2</div>
           <div class="t sm" style="font-size:26px;color:#FFE9A8">第 11 次撞击 · 翻倍并封顶</div></div>` : '';

    return `<div class="abs" style="left:${g.bx}px;top:${g.by}px;width:${g.bw}px;height:${g.bh}px" ${L('弹珠盘')}>
      <div class="slot abs" style="left:0;top:0;width:${g.bw}px;height:${g.bh}px" data-slot="盘面木框与背板"></div>
      <div class="abs" style="left:0;top:0;width:${g.bw}px;height:${g.bh}px" ${L('钉阵与撞柱')}>${h}</div>
      ${trail}${ball}${pop}${burst}</div>`;
  }

  // ── 落点槽 ×7：道具图标 + ×数量 + 品质色圆盘 ──
  function slots(s, g) {
    const vals = [1, 2, 3, 10, 3, 2, 1], w = g.bw / 7;
    return `<div class="abs" style="left:${g.bx}px;top:${g.by + g.bh - 118}px;width:${g.bw}px;height:118px;display:flex" ${L('落点槽 ×7')}>
      ${vals.map((v, i) => {
        const hit = s.slot === i;
        return `<div style="position:relative;width:${w}px;height:118px" ${L('槽' + (i + 1) + '-x' + v + (hit ? ' 命中' : ''))}>
          <div style="position:absolute;left:${w / 2 - 36}px;top:0;width:72px;height:72px">
            <img style="position:absolute;left:0;top:0" width="72" height="72" src="${A}task/奖励格底_${v === 10 ? '黄' : '青'}.png">
            <img style="position:absolute;left:11px;top:11px" width="50" height="50" src="${A}task/道具图标${v === 10 ? 'A_UiItemsGoldAllPower' : 'B_IconRisingStarStone4'}.png">
          </div>
          <div class="t abs" style="left:0;top:66px;width:${w}px;text-align:center;font-size:${v === 10 ? 32 : 26}px">×${v}</div>
          <div style="position:absolute;left:${w / 2 - 44}px;top:${v === 10 ? 100 : 104}px;width:88px;height:${v === 10 ? 22 : 18}px;border-radius:50%;background:${QC[i]};border:3px solid rgba(0,0,0,.45)${hit ? ';box-shadow:0 0 0 5px #FFC600' : ''}"></div>
        </div>`;
      }).join('')}</div>`;
  }

  // ── 垂直积分进度条 + 奖励格竖排（A 版） ──
  function gaugeV(s) {
    const marks = [10, 30, 50, 80, 110], pct = Math.min(1, s.score / 160000);
    return `<div class="abs" style="left:1624px;top:300px;width:276px;height:620px" ${L('积分进度条 · 垂直')}>
      <div class="abs" style="left:0;top:0;width:56px;height:560px;background:#2A2118;border:4px solid #7A5A34;border-radius:28px"></div>
      <div class="abs" style="left:6px;top:${6 + (548 - 548 * pct)}px;width:44px;height:${548 * pct}px;background:linear-gradient(180deg,#8CE84A,#3EAE12);border-radius:22px" ${L('进度填充')}></div>
      ${marks.map((m, i) => `<div class="t abs sm" style="left:64px;top:${520 - i * 130}px;font-size:24px">×${m}</div>`).join('')}
      ${marks.map((m, i) => `<div class="abs" style="left:124px;top:${498 - i * 130}px;width:88px;height:88px" ${L('阶段奖励' + (i + 1))}>
          <img style="position:absolute;left:0;top:0" width="88" height="88" src="${A}task/奖励格底_${i > 2 ? '黄' : '青'}.png">
          <img style="position:absolute;left:12px;top:12px" width="64" height="64" src="${A}task/道具图标${i > 2 ? 'A_UiItemsGoldAllPower' : 'B_IconRisingStarStone4'}.png"></div>`).join('')}
      <div class="abs" style="left:-8px;top:566px;width:88px;height:88px;border-radius:50%;background:linear-gradient(160deg,#4A5568,#232A34);border:4px solid #12171F;display:flex;align-items:center;justify-content:center" ${L('当前积分徽章')}>
        <div class="t gold" style="font-size:28px">${Math.round(s.score / 1000)}k</div></div></div>`;
  }

  // ── 入槽进度横条（A 版，压在盘底导轨上方） ──
  function gaugeH(s, g) {
    const full = s.gauge[0] >= s.gauge[1];
    return `<div class="abs" style="left:${g.bx}px;top:${g.by + g.bh + 16}px;width:${g.bw}px;height:56px;background:rgba(10,12,18,.78);border:2px solid #4C586A;border-radius:12px" ${L('入槽进度条')}>
      <div class="t abs sm" style="left:18px;top:14px;font-size:28px">入槽进度</div>
      <div class="abs" style="left:170px;top:20px;width:${g.bw - 340}px;height:16px;background:#3A3A3A;border-radius:8px"></div>
      <div class="abs" style="left:170px;top:20px;width:${(g.bw - 340) * Math.min(1, s.gauge[0] / s.gauge[1])}px;height:16px;background:${full ? '#FFC600' : '#00CFEE'};border-radius:8px" ${L('入槽填充')}></div>
      <div class="t ${full ? 'gold' : 'cyan'} abs sm" style="right:18px;top:14px;font-size:28px">${s.gauge[0]} / ${s.gauge[1]}　满则抽 Buff</div></div>`;
  }

  // ── 右侧信息面板（B 版，508 宽 —— 压面板不压盘面） ──
  function panelB(s, g) {
    const PW = g.pw, X = g.px;
    const item = (bg, ic, x, y, w) => `<div class="abs" style="left:${x}px;top:${y}px;width:${w}px;height:${w}px">
      <img style="position:absolute;left:0;top:0" width="${w}" height="${w}" src="${A}task/奖励格底_${bg}.png">
      <img style="position:absolute;left:${w * .14}px;top:${w * .14}px" width="${w * .72}" height="${w * .72}" src="${A}task/道具图标${ic}.png"></div>`;
    const full = s.gauge[0] >= s.gauge[1];
    const TH = [10, 25, 60];
    const rows = [0, 1, 2].map((i) => `
      <div class="abs" style="left:0;top:${44 + i * 138}px;width:${PW - 40}px;height:126px;background:${i === 0 ? 'rgba(255,255,255,.055)' : 'transparent'};border-radius:8px" ${L('阶段行' + (i + 1))}>
        <div class="t abs sm" style="left:14px;top:8px;font-size:26px;white-space:nowrap">累计</div>
        <div class="t ${i === 0 ? 'green' : ''} abs sm" style="left:82px;top:8px;font-size:26px;white-space:nowrap;${i ? 'color:#C8CDD4' : ''}">${TH[i]},000</div>
        <div class="t ${i === 0 ? 'cyan' : ''} abs sm" style="right:14px;top:8px;font-size:24px;white-space:nowrap;${i ? 'color:#8A929B' : ''}">${i === 0 ? '已达成' : '未达成'}</div>
        ${i === 1
          ? `<div class="slot abs" style="left:14px;top:46px;width:196px;height:66px" data-slot="限时主城皮肤">限时主城皮肤</div>`
          : item(i > 1 ? '黄' : '青', i > 1 ? 'A_UiItemsGoldAllPower' : 'B_IconRisingStarStone4', 14, 46, 66) +
            item('青', 'B_IconRisingStarStone4', 90, 46, 66)}
        <div class="abs" style="right:14px;top:48px;width:150px;height:62px${i ? ';opacity:.5' : ''}" ${L('按钮' + (i + 1))}>
          <img class="abs" style="left:0;top:0;width:150px;height:62px" src="${A}task/按钮_${i ? '前往蓝' : '领取绿'}.png">
          <div class="t abs" style="left:0;top:0;width:150px;height:62px;display:flex;align-items:center;justify-content:center;font-size:28px">${i ? '未达成' : '领取'}</div></div></div>`).join('');

    return `<div class="abs" style="left:${X}px;top:120px" ${L('右侧信息面板')}>
      <div class="abs" style="left:0;top:0;width:${PW}px;height:872px;background:#161013;border-radius:10px" ${L('面板底')}></div>
      <div class="abs" style="left:${(PW - 298) / 2}px;top:-62px" ${L('面板标题标签')}>
        <img class="abs" style="left:0;top:0" width="298" height="127" src="${A}floor/楼层标签底b.png">
        <div class="t abs nav-tab-hit" style="left:0;top:0;width:298px;height:112px;font-size:38px">积分进度</div></div>

      <div class="abs" style="left:20px;top:84px" ${L('总积分')}>
        <div class="t abs sm" style="left:0;top:8px;font-size:28px;white-space:nowrap">总积分</div>
        <div class="t gold abs" style="left:118px;top:-4px;font-size:46px;white-space:nowrap">${s.score.toLocaleString()}</div>
        ${s.gain ? `<div class="t green abs sm" style="left:118px;top:48px;font-size:28px;white-space:nowrap">+${s.gain.toLocaleString()}</div>` : ''}</div>

      <div class="abs" style="left:20px;top:${s.gain ? 200 : 158}px;width:${PW - 40}px" ${L('入槽进度')}>
        <div class="t abs sm" style="left:0;top:0;font-size:26px;white-space:nowrap">入槽进度</div>
        <div class="t ${full ? 'gold' : 'cyan'} abs sm" style="right:0;top:0;font-size:26px;white-space:nowrap">${s.gauge[0]} / ${s.gauge[1]}</div>
        <div class="abs" style="left:0;top:40px;width:${PW - 40}px;height:14px;background:#3A3A3A;border-radius:7px"></div>
        <div class="abs" style="left:0;top:40px;width:${(PW - 40) * Math.min(1, s.gauge[0] / s.gauge[1])}px;height:14px;background:${full ? '#FFC600' : '#00CFEE'};border-radius:7px"></div>
        <div class="t abs sm" style="left:0;top:62px;font-size:22px;color:#8A929B;white-space:nowrap">满则从 Buff 池 3 选 1</div></div>

      <div class="abs" style="left:20px;top:260px;width:${PW - 40}px" ${L('阶段奖励')}>
        <div class="t abs sm" style="left:0;top:0;font-size:26px;white-space:nowrap">阶段奖励</div>${rows}</div>

      <div class="abs" style="left:14px;top:720px;width:${PW - 28}px;height:134px;background:rgba(255,198,0,.08);border:2px solid #FFC600;border-radius:10px" ${L('榜首大奖')}>
        <div class="slot abs" style="left:12px;top:12px;width:120px;height:106px" data-slot="榜首大奖_限定主城皮肤">限定皮肤</div>
        <div class="t gold abs sm" style="left:144px;top:14px;font-size:26px;white-space:nowrap">跨服总榜 · 第 1 名</div>
        <div class="t cyan abs sm" style="left:144px;top:52px;font-size:24px;white-space:nowrap">我的排名 ${s.rank}</div>
        <div class="abs" style="left:144px;top:84px;width:150px;height:40px;border-radius:8px;background:linear-gradient(160deg,#6FD8F0,#2A6E9C);border:2px solid #123A55;display:flex;align-items:center;justify-content:center" ${L('排行榜按钮')}>
          <div class="t sm" style="font-size:24px;white-space:nowrap">排行榜</div></div></div></div>`;
  }

  // ═══════════ C 版：机柜整合 ═══════════
  // 竞品的核心做法 —— 玩法区是一台实体弹珠机，所有 HUD 长在机器上，没有一个浮在外面
  function cabinet(s, g) {
    const CX = 392, CY = 92, CW = 1508, CH = 956;
    const nodes = [10, 25, 60, 100, 160];
    const pct = Math.min(1, s.score / 160000);
    const chip = (icon, num, gold, x, name) => `
      <div class="abs" style="left:${x}px;top:140px;width:150px;height:86px;background:rgba(8,10,16,.72);border:3px solid ${gold ? '#FFC600' : '#4C586A'};border-radius:14px" ${L(name)}>
        <img class="abs" style="left:12px;top:16px" width="54" height="54" src="${A}task/${icon}">
        <div class="t ${gold ? 'gold' : ''} abs" style="left:74px;top:22px;font-size:34px">${num}</div>
        <div class="t dark abs" style="left:112px;top:-14px;width:40px;height:40px;background:#3EEE00;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:30px">+</div></div>`;

    return `
    <div class="slot abs" style="left:${CX}px;top:${CY}px;width:${CW}px;height:${CH}px;border-width:4px;border-radius:28px" data-slot="弹珠机柜_外框与机身"></div>

    <div class="abs" style="left:760px;top:52px;width:560px;height:96px;background:linear-gradient(180deg,#FFD24A,#D9840A);border:5px solid #7A4A06;border-radius:48px 48px 14px 14px;display:flex;align-items:center;justify-content:center" ${L('机柜招牌')}>
      <div class="t dark" style="font-size:54px">宇宙弹弹乐</div></div>
    <div class="abs" style="left:1382px;top:74px;width:210px;height:52px;background:rgba(8,10,16,.8);border:3px solid #8A929B;border-radius:26px;display:flex;align-items:center;justify-content:center;gap:8px" ${L('活动倒计时')}>
      <div class="t sm" style="font-size:26px;white-space:nowrap">剩余</div>
      <div class="t gold" style="font-size:28px;white-space:nowrap">6d 11h</div></div>

    <div class="slot abs" style="left:424px;top:166px;width:126px;height:126px;border-radius:63px" data-slot="当期外显主视觉_圆窗">主视觉</div>

    <div class="abs" style="left:576px;top:172px;width:800px;height:120px" ${L('阶段进度条')}>
      <div class="abs" style="left:0;top:66px;width:800px;height:26px;background:#241A10;border:3px solid #7A5A34;border-radius:13px"></div>
      <div class="abs" style="left:3px;top:69px;width:${794 * pct}px;height:20px;background:linear-gradient(90deg,#8CE84A,#3EAE12);border-radius:10px" ${L('进度填充')}></div>
      ${nodes.map((n, i) => `<div class="abs" style="left:${i * 180}px;top:0px;width:76px;height:76px" ${L('阶段奖励' + (i + 1))}>
          <img style="position:absolute;left:0;top:0" width="76" height="76" src="${A}task/奖励格底_${i > 2 ? '黄' : '青'}.png">
          <img style="position:absolute;left:11px;top:11px" width="54" height="54" src="${A}task/道具图标${i > 2 ? 'A_UiItemsGoldAllPower' : 'B_IconRisingStarStone4'}.png">
          <div class="t abs sm" style="left:0;top:78px;width:76px;text-align:center;font-size:22px">${n}k</div></div>`).join('')}
      </div>
    <div class="abs" style="left:556px;top:70px;width:196px;height:56px;background:rgba(8,10,16,.8);border:3px solid #7A5A34;border-radius:28px;display:flex;align-items:center;justify-content:center;gap:8px" ${L('总积分')}>
      <div class="t sm" style="font-size:24px;white-space:nowrap">积分</div>
      <div class="t gold" style="font-size:30px;white-space:nowrap">${s.score.toLocaleString()}</div></div>

    <div class="abs" style="left:1412px;top:160px;width:150px;height:136px" ${L('排行榜入口')}>
      <div class="abs" style="left:16px;top:0;width:118px;height:100px;border-radius:14px;background:linear-gradient(160deg,#6FD8F0,#2A6E9C);border:4px solid #123A55;display:flex;align-items:center;justify-content:center">
        <div class="slot" style="width:56px;height:56px;border-width:2px"></div></div>
      <div class="t abs sm" style="left:0;top:104px;width:150px;text-align:center;font-size:24px;white-space:nowrap">排行榜 ${s.rank}th</div></div>

    <div class="abs" style="left:1540px;top:306px;width:340px;height:630px" ${L('操作柱')}>
      <div class="abs" style="left:80px;top:8px;width:180px;height:84px;background:linear-gradient(180deg,#FFC94A,#E08A0C);border:4px solid #7A4A06;border-radius:42px;display:flex;align-items:center;justify-content:center;gap:10px" ${L('档位徽章')}>
        <img width="44" height="44" src="${A}task/道具图标A_UiItemsGoldAllPower.png">
        <div class="t dark" style="font-size:36px">×${s.mult}</div></div>
      <div class="t abs sm" style="left:0;top:98px;width:340px;text-align:center;font-size:22px;color:#C8CDD4;white-space:nowrap">点击切换得分 / 消耗倍数</div>
      ${chip('道具图标A_UiItemsGoldAllPower.png', s.balls, false, 12, '余量-普通弹珠')}
      ${chip('道具图标B_IconRisingStarStone4.png', s.adv, true, 178, '余量-高级弹珠')}
      <div class="t ${s.advSel ? 'gold' : ''} abs sm" style="left:0;top:236px;width:340px;text-align:center;font-size:26px;white-space:nowrap">${s.advSel ? '已选 高级弹珠 ×5' : '已选 普通弹珠'}</div>
      <div class="abs" style="left:158px;top:286px;width:24px;height:106px;background:repeating-linear-gradient(180deg,#8A929B 0 8px,#4C586A 8px 16px);border-radius:6px" ${L('发射齿轨')}></div>
      <div class="abs" style="left:90px;top:398px;width:160px;height:160px;border-radius:50%;background:${s.flying ? 'linear-gradient(160deg,#5C7C99,#2B4257)' : 'linear-gradient(160deg,#7BF04A,#2C9A0C)'};border:6px solid ${s.flying ? '#22364A' : '#1A5C08'};display:flex;align-items:center;justify-content:center" ${L('发射器' + (s.flying ? ' 发射中' : ''))}>
        <div class="t" style="font-size:${s.flying ? 30 : 40}px">${s.flying ? '发射中' : '发 射'}</div></div>
      <div class="abs" style="left:52px;top:576px;width:236px;height:60px;background:rgba(8,10,16,.72);border:3px solid #8A929B;border-radius:12px;display:flex;align-items:center;justify-content:center;gap:10px" ${L('兑换商店入口')}>
        <div class="slot" style="width:42px;height:42px;border-width:2px"></div>
        <div class="t sm" style="font-size:26px;white-space:nowrap">兑换商店</div></div></div>

    <div class="abs" style="left:424px;top:952px;width:1096px;height:58px;background:rgba(8,10,16,.72);border:3px solid #4C586A;border-radius:12px" ${L('入槽进度条')}>
      <div class="t abs sm" style="left:20px;top:14px;font-size:28px;white-space:nowrap">入槽进度</div>
      <div class="abs" style="left:180px;top:21px;width:660px;height:16px;background:#3A3A3A;border-radius:8px"></div>
      <div class="abs" style="left:180px;top:21px;width:${660 * Math.min(1, s.gauge[0] / s.gauge[1])}px;height:16px;background:${s.gauge[0] >= s.gauge[1] ? '#FFC600' : '#00CFEE'};border-radius:8px"></div>
      <div class="t ${s.gauge[0] >= s.gauge[1] ? 'gold' : 'cyan'} abs sm" style="right:20px;top:14px;font-size:26px;white-space:nowrap">${s.gauge[0]} / ${s.gauge[1]}　满则抽 Buff</div></div>

    <div class="abs" style="left:1560px;top:950px;width:64px;height:64px;border-radius:50%;background:rgba(8,10,16,.7);border:3px solid #8A929B;display:flex;align-items:center;justify-content:center" ${L('规则入口 ⓘ')}><div class="t" style="font-size:38px">i</div></div>`;
  }

  // ── 角落挂件 ──
  function corners(s, g) {
    return `<div class="abs" style="left:${g.panel ? 396 : 392}px;top:${g.panel ? 1000 : 996}px;width:64px;height:64px;border-radius:50%;background:rgba(10,12,18,.7);border:3px solid #8A929B;display:flex;align-items:center;justify-content:center" ${L('规则入口 ⓘ')}><div class="t" style="font-size:38px">i</div></div>
      ${g.panel
        ? `<div class="abs" style="left:478px;top:1000px;width:210px;height:64px;background:rgba(10,12,18,.72);border:2px solid #8A929B;border-radius:12px;display:flex;align-items:center;gap:10px;padding-left:12px" ${L('兑换商店入口')}>
             <div class="slot" style="width:44px;height:44px;border-width:2px"></div>
             <div class="t sm" style="font-size:26px;white-space:nowrap">兑换商店</div></div>`
        : `<div class="abs" style="left:392px;top:826px;width:170px;height:120px" ${L('兑换商店入口')}>
             <div class="slot abs" style="left:24px;top:0;width:122px;height:80px" data-slot="兑换商店图标"></div>
             <div class="t abs sm" style="left:0;top:84px;width:170px;text-align:center;font-size:26px">兑换商店</div></div>`}
      <div class="abs" style="right:20px;bottom:18px" ${L('活动倒计时')}>
        <div class="t sm" style="font-size:30px">进行中 <span class="t gold" style="font-size:32px">06天11时</span></div></div>`;
  }

  // ── L3 弹窗层 ──
  function dialog(s) {
    if (!s.dialog) return '';
    const shade = `<div class="abs" style="left:0;top:0;width:1920px;height:1080px;background:rgba(0,0,0,.64)" ${L('遮罩')}></div>`;
    const D = s.dialog; let inner = '';
    if (D === 'buff') {
      const card = (i, t, d, hot) => `<div class="abs" style="left:${40 + i * 306}px;top:150px;width:280px;height:360px;background:${hot ? 'rgba(255,198,0,.12)' : '#1F2630'};border:3px solid ${hot ? '#FFC600' : '#4C586A'};border-radius:14px" ${L('Buff卡-' + t)}>
          <div class="slot abs" style="left:60px;top:36px;width:160px;height:160px" data-slot="Buff图标_${t}"></div>
          <div class="t ${hot ? 'gold' : ''} abs" style="left:0;top:222px;width:280px;text-align:center;font-size:34px">${t}</div>
          <div class="t abs sm" style="left:16px;top:274px;width:248px;text-align:center;font-size:24px;color:#C8CDD4;line-height:1.4">${d}</div></div>`;
      inner = `<div class="abs" style="left:428px;top:210px;width:1004px;height:600px;background:#161013;border:3px solid #4C586A;border-radius:18px" ${L('L3 Buff池弹窗')}>
        <div class="t abs" style="left:0;top:34px;width:1004px;text-align:center;font-size:46px">入槽进度已满 · 三选一</div>
        <div class="t cyan abs sm" style="left:0;top:96px;width:1004px;text-align:center;font-size:26px">抽后进度重置，继续累计</div>
        ${card(0, '触发礼包', '限时只售高级弹珠<br>高 ROI', true)}${card(1, '阶段积分', '直接获得一笔<br>额外进度条积分')}${card(2, '弹珠返还', '返还随机数量弹珠')}</div>`;
    }
    if (D === 'pack') {
      inner = `<div class="abs" style="left:530px;top:190px;width:800px;height:640px;background:#161013;border:3px solid #FFC600;border-radius:18px" ${L('L3 触发礼包弹窗')}>
        <div class="t gold abs" style="left:0;top:30px;width:800px;text-align:center;font-size:46px">限时触发礼包</div>
        <div class="t cyan abs sm" style="left:0;top:92px;width:800px;text-align:center;font-size:28px">剩余 59:41　·　仅本次触发可购</div>
        <div class="slot abs" style="left:60px;top:150px;width:220px;height:220px" data-slot="高级弹珠礼包主视觉">高级弹珠<br>礼包主视觉</div>
        <div class="t abs sm" style="left:312px;top:150px;font-size:30px">高级弹珠 ×20</div>
        <div class="t green abs sm" style="left:312px;top:198px;font-size:26px">本次发射得分 ×5，只出自礼包</div>
        <div class="abs" style="left:312px;top:246px;width:94px;height:94px"><img style="position:absolute;left:0;top:0" width="94" height="94" src="${A}task/奖励格底_青.png"><img style="position:absolute;left:13px;top:13px" width="68" height="68" src="${A}task/道具图标B_IconRisingStarStone4.png"></div>
        <div class="t gold abs" style="left:432px;top:268px;font-size:44px">×20</div>
        <div class="t abs" style="left:60px;top:412px;width:220px;text-align:center;font-size:30px;color:#C8CDD4">ROI 标签位</div>
        <div class="abs" style="left:290px;top:470px" ${L('主按钮-购买')}>
          <img class="abs" style="left:0;top:0;width:280px;height:104px" src="${A}task/按钮_领取绿.png">
          <div class="t abs" style="left:0;top:0;width:280px;height:104px;display:flex;align-items:center;justify-content:center;font-size:40px">$ 4.99</div></div>
        <div class="t abs sm" style="left:0;top:590px;width:800px;text-align:center;font-size:24px;color:#8A929B">限购 1 次</div></div>`;
    }
    if (D === 'rank') {
      const row = (i, n, me) => `<div class="abs" style="left:30px;top:${190 + i * 92}px;width:940px;height:80px;background:${me ? 'rgba(255,198,0,.16)' : 'rgba(255,255,255,.04)'};border:${me ? '2px solid #FFC600' : '0'};border-radius:8px" ${L('榜行-' + n)}>
          <div class="t ${me ? 'gold' : ''} abs" style="left:24px;top:18px;font-size:34px">${n}</div>
          <div class="slot abs" style="left:110px;top:12px;width:56px;height:56px;border-width:2px"></div>
          <div class="t abs sm" style="left:186px;top:22px;font-size:30px;color:#C8CDD4">玩家名</div>
          <div class="t cyan abs sm" style="left:760px;top:22px;font-size:30px">弹珠消耗</div></div>`;
      inner = `<div class="abs" style="left:460px;top:150px;width:1000px;height:780px;background:#161013;border:3px solid #4C586A;border-radius:18px" ${L('L3 排行榜弹窗')}>
        <div class="t abs" style="left:0;top:30px;width:1000px;text-align:center;font-size:46px">跨服总榜</div>
        <div class="t cyan abs sm" style="left:0;top:96px;width:1000px;text-align:center;font-size:26px">按活动期累计弹珠消耗量排名</div>
        ${row(0, '1', false)}${row(1, '2', false)}${row(2, '3', false)}${row(3, String(s.rank), true)}
        <div class="abs" style="left:30px;top:566px;width:940px;height:150px;background:rgba(255,198,0,.08);border:2px solid #FFC600;border-radius:10px" ${L('名次奖励预览')}>
          <div class="slot abs" style="left:16px;top:16px;width:160px;height:118px" data-slot="榜首大奖_限定主城皮肤"></div>
          <div class="t gold abs sm" style="left:196px;top:24px;font-size:30px">第 1 名 · 限定高级主城皮肤 · 永久</div>
          <div class="t abs sm" style="left:196px;top:68px;font-size:26px;color:#C8CDD4">2~3 名 限时 30 天　·　4~10 名 初级永久</div>
          <div class="t cyan abs sm" style="left:196px;top:106px;font-size:26px">活动结束统一发放</div></div></div>`;
    }
    if (D === 'end') {
      inner = `<div class="abs" style="left:560px;top:250px;width:800px;height:540px;background:#161013;border:3px solid #4C586A;border-radius:18px" ${L('L3 活动结束弹窗')}>
        <div class="t abs" style="left:0;top:36px;width:800px;text-align:center;font-size:46px">活动已结束</div>
        <div class="t cyan abs sm" style="left:0;top:104px;width:800px;text-align:center;font-size:28px">名次奖励将统一发放至邮件</div>
        <div class="abs" style="left:70px;top:170px;width:660px;height:110px;background:rgba(255,255,255,.05);border-radius:10px" ${L('最终名次')}>
          <div class="t abs sm" style="left:24px;top:34px;font-size:30px">最终名次</div>
          <div class="t gold abs" style="left:210px;top:24px;font-size:44px">${s.rank}</div>
          <div class="t abs sm" style="left:400px;top:34px;font-size:28px;color:#C8CDD4">总积分 ${s.score.toLocaleString()}</div></div>
        <div class="abs" style="left:70px;top:300px;width:660px;height:110px;background:rgba(255,198,0,.08);border:2px solid #FFC600;border-radius:10px" ${L('剩余弹珠折算')}>
          <div class="t gold abs sm" style="left:24px;top:14px;font-size:28px">剩余弹珠折算金币</div>
          <div class="t abs sm" style="left:24px;top:58px;font-size:26px;color:#C8CDD4">普通 ×12 + 高级 ×2　→　邮件发放</div></div>
        <div class="abs" style="left:260px;top:430px" ${L('主按钮-确定')}>
          <img class="abs" style="left:0;top:0;width:280px;height:88px" src="${A}task/按钮_前往蓝.png">
          <div class="t abs" style="left:0;top:0;width:280px;height:88px;display:flex;align-items:center;justify-content:center;font-size:38px">确定</div></div></div>`;
    }
    if (D === 'error') {
      inner = `<div class="abs" style="left:660px;top:340px;width:600px;height:400px;background:#161013;border:3px solid #FF5A4E;border-radius:18px" ${L('L3 加载失败弹窗')}>
        <div class="t abs" style="left:0;top:44px;width:600px;text-align:center;font-size:42px;color:#FF5A4E">数据加载失败</div>
        <div class="t abs sm" style="left:40px;top:120px;width:520px;text-align:center;font-size:28px;color:#C8CDD4;line-height:1.5">排行榜 / 积分数据拉取超时。<br>本次发射结果已保留，重试后刷新。</div>
        <div class="abs" style="left:160px;top:250px" ${L('主按钮-重试')}>
          <img class="abs" style="left:0;top:0;width:280px;height:88px" src="${A}task/按钮_前往蓝.png">
          <div class="t abs" style="left:0;top:0;width:280px;height:88px;display:flex;align-items:center;justify-content:center;font-size:38px">重试</div></div></div>`;
    }
    return shade + inner;
  }

  window.renderScreen2 = function (s) {
    const g = geo(s);
    if (g.cab) {
      return `<div class="screen abs" style="left:${s.x}px;top:${s.y}px" ${L(s.key)}>
        <div class="slot corner abs" style="left:0;top:0;width:1920px;height:1080px;padding:0 0 8px 400px" data-slot="场景底_深空霓虹街机">场景底（按档期替换）</div>
        ${nav()}${cabinet(s, g)}${plinko(s, g)}${hintBar(s, g)}${slots(s, g)}${dialog(s)}
      </div>`;
    }
    return `<div class="screen abs" style="left:${s.x}px;top:${s.y}px" ${L(s.key)}>
      <div class="slot corner abs" style="left:0;top:0;width:1920px;height:1080px;padding:0 0 12px 900px" data-slot="场景底_深空霓虹街机">场景底　·　深空霓虹街机（按档期替换）</div>
      ${nav()}
      <div class="t abs" style="left:398px;top:20px;font-size:74px;-webkit-text-stroke-width:7px" ${L('活动名')}>宇宙弹弹乐</div>
      ${assets(s)}${tier(s)}${ballType(s)}
      ${launchers(s, g)}${plinko(s, g)}${hintBar(s, g)}${slots(s, g)}
      ${g.panel ? panelB(s, g) : gaugeV(s) + gaugeH(s, g)}
      ${rankCard(s, g)}${corners(s, g)}${dialog(s)}
    </div>`;
  };
})();
