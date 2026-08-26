/* ===========================================================================
   marble.js —— 宇宙弹弹乐 界面构件器
   renderScreen(state) → 一屏 1920×1080 的 HTML。8 屏共用，只改 state。

   图层命名：每个结构块都带 data-layer + data-name，
   前者给 svgbake 烘焙 SVG，后者给 Figma 的 HTML 导入插件识别。
   =========================================================================== */
(function () {
  const A = 'assets/';
  const L = (n) => `data-layer="${n}" data-name="${n}"`;

  // —— 盘面几何，与真实排布一致 ——
  const BW = 620, BH = 540, ROWS = 9, PAD = 46;
  const POSTS = { '2-3': 3, '4-1': 5, '4-6': 5, '6-2': 8, '6-5': 8 };

  function pegXY(r, c) {
    const n = r % 2 === 0 ? 8 : 7;
    const y = PAD + r * ((BH - PAD * 2) / (ROWS - 1));
    const gap = (BW - PAD * 2) / (n - 1 + (r % 2 === 0 ? 0 : 1));
    return { x: PAD + c * gap + (r % 2 ? gap / 2 : 0), y, n };
  }

  function pegs(dead) {
    let h = '';
    for (let r = 0; r < ROWS; r++) {
      const n = r % 2 === 0 ? 8 : 7;
      for (let c = 0; c < n; c++) {
        const { x, y } = pegXY(r, c);
        const num = POSTS[r + '-' + c];
        if (num) {
          const off = dead ? ';border-color:#3A4152;color:#5A6272;background:#161B24' : '';
          h += `<div class="post" style="left:${x - 26}px;top:${y - 26}px;width:52px;height:52px${off}" ${L('撞柱-' + num + '分')}>${num}</div>`;
        } else {
          h += `<div class="peg" style="left:${x - 6}px;top:${y - 6}px"></div>`;
        }
      }
    }
    return h;
  }

  // —— 左侧导航条 ——
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
      <div class="t abs nav-tab-hit" style="left:6px;top:700px;width:345px;height:76px;font-size:50px;color:#C8CDD4" ${L('页签-活动4')}>活动 4</div>
    </div>`;
  }

  // —— ④ 资产条 ——
  function assets(s) {
    const chip = (icon, num, gold, name) => `
      <div class="abs" style="position:relative;width:230px;height:64px;background:#161013;border:2px solid ${gold ? '#FFC600' : '#4C586A'};border-radius:32px" ${L(name)}>
        <img class="abs" style="left:6px;top:6px" width="52" height="52" src="${A}task/${icon}">
        <div class="t ${gold ? 'gold' : ''} abs sm" style="left:70px;top:14px;font-size:32px">${num}</div>
        <div class="t dark abs" style="left:172px;top:8px;width:48px;height:48px;background:#FFC600;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:36px">+</div></div>`;
    return `<div class="abs" style="right:20px;top:18px;display:flex;gap:14px" ${L('④ 资产条')}>
      ${chip('道具图标A_UiItemsGoldAllPower.png', s.balls, false, '资产-弹珠')}
      ${chip('道具图标B_IconRisingStarStone4.png', s.adv, true, '资产-高级弹珠')}</div>
      ${s.lowHint ? `<div class="abs" style="right:20px;top:96px;width:474px;height:56px;background:rgba(255,90,78,.16);border:2px solid #FF5A4E;border-radius:10px;display:flex;align-items:center;justify-content:center" ${L('弹珠不足提示')}><div class="t sm" style="font-size:26px;color:#FF8A80">${s.lowHint}</div></div>` : ''}`;
  }

  // —— ⑨ 实时信息 + ③ 倍数选择器 ——
  function hud(s) {
    const m = (v) => `<div class="t ${s.mult === v ? 'dark' : ''} abs" style="left:${v === 1 ? 0 : v === 5 ? 92 : 184}px;top:0;width:80px;height:76px;background:${s.mult === v ? '#FFC600' : '#1F2630'};border:2px solid ${s.mult === v ? '#FFE27A' : '#4C586A'};border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:32px" ${L('倍数-x' + v)}>×${v}</div>`;
    const hot = s.burst ? 'gold' : 'cyan';
    return `<div class="abs" style="left:400px;top:190px;width:400px;height:76px;background:rgba(10,14,26,.72);border:2px solid ${s.burst ? '#FFC600' : '#33405C'};border-radius:12px" ${L('⑨ 本次发射实时信息')}>
        <div class="t abs sm" style="left:18px;top:20px;font-size:28px">撞击</div>
        <div class="t ${hot} abs" style="left:86px;top:12px;font-size:40px">${s.hits} / 11</div>
        <div class="t abs sm" style="left:202px;top:20px;font-size:28px">累计</div>
        <div class="t gold abs" style="left:274px;top:12px;font-size:40px">${s.acc.toLocaleString()}</div></div>
      <div class="abs" style="left:826px;top:190px;width:264px;height:76px" ${L('③ 倍数选择器')}>
        <div class="t abs sm" style="left:0;top:-32px;font-size:22px;color:#C8CDD4">得分 / 消耗倍数</div>
        ${m(1)}${m(5)}${m(10)}</div>`;
  }

  // —— ① 弹珠盘 + 倍数槽 ——
  function board(s) {
    const trail = (s.trail || []).map((p, i) =>
      `<div class="abs" style="left:${p[0] - 7}px;top:${p[1] - 7}px;width:14px;height:14px;border-radius:50%;background:#FFC600;opacity:${0.18 + i * 0.12}"></div>`).join('');
    const ball = s.ball
      ? `<div class="abs" style="left:${s.ball[0] - 17}px;top:${s.ball[1] - 17}px;width:34px;height:34px;border-radius:50%;background:${s.advSel ? '#FFC600' : '#EAF2FF'};box-shadow:0 0 22px 6px ${s.advSel ? 'rgba(255,198,0,.75)' : 'rgba(160,210,255,.6)'}" ${L('弹珠')}></div>` : '';
    const burst = s.burst
      ? `<div class="abs" style="left:60px;top:180px;width:500px;height:180px;border:4px solid #FFC600;border-radius:16px;background:rgba(255,198,0,.14);display:flex;flex-direction:column;align-items:center;justify-content:center" ${L('第11次翻倍演出')}>
           <div class="t gold" style="font-size:64px">累计 ×2</div>
           <div class="t sm" style="font-size:26px;color:#FFE9A8">第 11 次撞击 · 翻倍并封顶</div></div>` : '';

    const cells = [1, 2, 3, 10, 3, 2, 1].map((v, i) => {
      const hit = s.slot === i;
      const hotCls = v === 10 ? ' hot' : '';
      const st = hit ? 'background:rgba(255,198,0,.32);box-shadow:inset 0 0 0 3px #FFC600' : '';
      return `<div class="slotcell${hotCls}" style="${st}" ${L('槽' + (i + 1) + '-x' + v)}>×${v}</div>`;
    }).join('');

    return `<div class="abs" style="left:400px;top:288px;width:620px;height:540px" ${L('① 弹珠盘')}>
        <div class="slot abs" style="left:0;top:0;width:620px;height:540px" data-slot="盘面底_钉阵背景"></div>
        <div class="abs" style="left:0;top:0;width:620px;height:540px" ${L('钉阵与撞柱')}>${pegs(s.dead)}</div>
        <div class="post abs" style="left:274px;top:236px;width:72px;height:72px;border-color:${s.dead ? '#3A4152' : '#FFC600'};color:${s.dead ? '#5A6272' : '#FFC600'};font-size:26px" ${L('中央高倍撞柱')}>×</div>
        ${trail}${ball}${burst}</div>
      <div class="abs" style="left:400px;top:842px;width:620px;height:84px;background:rgba(10,14,26,.78);border:2px solid #33405C;border-radius:12px;display:flex" ${L('倍数槽 ×7')}>${cells}</div>`;
  }

  // —— ② 发射区 ——
  function fire(s) {
    const dis = s.fireOff;
    return `<div class="abs" style="left:400px;top:948px;width:620px;height:104px" ${L('② 发射区')}>
        <div class="abs" style="left:0;top:0;width:200px;height:104px;background:#1F2630;border:2px solid ${s.advSel ? '#FFC600' : '#4C586A'};border-radius:12px" ${L('普通/高级弹珠切换')}>
          <div class="t abs sm" style="left:14px;top:10px;font-size:24px;color:#C8CDD4">弹珠类型</div>
          <div class="t ${s.advSel ? 'gold' : ''} abs sm" style="left:14px;top:46px;font-size:30px">${s.advSel ? '高级 ×5' : '普通'}</div></div>
        <div class="abs" style="left:222px;top:0${dis ? ';opacity:.5;filter:grayscale(1)' : ''}" ${L('主按钮-发射')}>
          <img class="abs" style="left:0;top:0;width:398px;height:104px" src="${A}task/按钮_领取绿.png">
          <div class="t abs" style="left:0;top:0;width:398px;height:104px;display:flex;align-items:center;justify-content:center;font-size:46px">${s.fireLabel || '发 射'}</div></div>
</div>`;
  }

  // —— ⑦⑧ 功能入口列 ——
  function entries() {
    const e = (n) => `<div class="ent" ${L(n + '入口')}><div class="slot" style="width:52px;height:52px;border-width:2px"></div><div class="lb">${n}</div></div>`;
    return `<div class="abs" style="left:1046px;top:290px;display:flex;flex-direction:column;gap:22px" ${L('⑦⑧ 功能入口列')}>
      ${e('排行榜')}${e('成就')}${e('礼包')}</div>`;
  }

  // —— 右侧信息面板 ——
  function panel(s) {
    const g = s.gauge, pct = Math.round(g[0] / g[1] * 100);
    const item = (bg, ic, x, y) => `<div class="abs" style="left:${x}px;top:${y}px;width:94px;height:94px">
      <img style="position:absolute;left:0;top:0" width="94" height="94" src="${A}task/奖励格底_${bg}.png">
      <img style="position:absolute;left:13px;top:13px" width="68" height="68" src="${A}task/道具图标${ic}.png"></div>`;
    const btn = (img, label, x, y, off) => `<div class="abs" style="left:${x}px;top:${y}px${off ? ';opacity:.5' : ''}" ${L('按钮-' + label)}>
      <img class="abs" style="left:0;top:0" width="199" height="75" src="${A}task/按钮_${img}.png">
      <div class="t abs" style="left:0;top:0;width:199px;height:75px;display:flex;align-items:center;justify-content:center;font-size:34px">${label}</div></div>`;

    return `<div class="abs" style="left:1170px;top:130px" ${L('右侧信息面板')}>
      <div class="abs" style="left:0;top:0;width:739px;height:850px;background:#161013;border-radius:10px" ${L('面板底')}></div>
      <div class="abs" style="left:220px;top:-64px" ${L('面板标题标签')}>
        <img class="abs" style="left:0;top:0" width="298" height="127" src="${A}floor/楼层标签底b.png">
        <div class="t abs nav-tab-hit" style="left:0;top:0;width:298px;height:112px;font-size:38px">积分进度</div></div>

      <div class="abs" style="left:36px;top:88px;width:668px" ${L('总积分')}>
        <div class="t abs sm" style="left:0;top:8px;font-size:32px">总积分</div>
        <div class="t gold abs" style="left:130px;top:-6px;font-size:56px">${s.score.toLocaleString()}</div>
        ${s.gain ? `<div class="t green abs sm" style="left:400px;top:6px;font-size:34px">+${s.gain.toLocaleString()}</div>` : ''}</div>

      <div class="abs" style="left:36px;top:162px;width:668px" ${L('⑤ 入槽进度')}>
        <div class="t abs sm" style="left:0;top:0;font-size:30px">入槽进度</div>
        <div class="t cyan abs sm" style="left:150px;top:4px;font-size:26px">${g[0] >= g[1] ? '已满 · 触发 Buff 抽取' : '满则从 Buff 池 3 选 1'}</div>
        <div class="t cyan abs sm" style="left:576px;top:0;font-size:28px">${g[0]} / ${g[1]}</div>
        <div class="abs" style="left:0;top:48px;width:668px;height:16px;background:#3A3A3A;border-radius:8px"></div>
        <div class="abs" style="left:0;top:48px;width:${Math.round(668 * Math.min(1, pct / 100))}px;height:16px;background:${g[0] >= g[1] ? '#FFC600' : '#00CFEE'};border-radius:8px" ${L('入槽条进度')}></div></div>

      <div class="abs" style="left:18px;top:252px;width:704px" ${L('⑥ 阶段奖励')}>
        <div class="t abs sm" style="left:18px;top:0;font-size:30px">阶段奖励</div>
        <div class="abs" style="left:0;top:44px;width:704px;height:150px;background:rgba(255,255,255,.045);border-radius:8px${s.claimed ? ';opacity:.5' : ''}" ${L('阶段行1')}>
          <div class="t abs sm" style="left:18px;top:14px;font-size:28px">累计</div>
          <div class="t green abs sm" style="left:88px;top:14px;font-size:28px">10,000</div>
          <div class="t cyan abs sm" style="left:606px;top:14px;font-size:28px">${s.claimed ? '已领取' : '已达成'}</div>
          ${item('黄', 'A_UiItemsGoldAllPower', 18, 52)}${item('黄', 'A_UiItemsGoldAllPower', 126, 52)}${item('青', 'B_IconRisingStarStone4', 234, 52)}
          ${s.claimed ? '' : btn('领取绿', '领取', 470, 64, false)}</div>
        <div class="abs" style="left:0;top:206px;width:704px;height:150px;border-radius:8px" ${L('阶段行2')}>
          <div class="t abs sm" style="left:18px;top:14px;font-size:28px">累计</div>
          <div class="t abs sm" style="left:88px;top:14px;font-size:28px;color:#C8CDD4">25,000</div>
          <div class="t cyan abs sm" style="left:330px;top:14px;font-size:28px">${s.score.toLocaleString()} / 25,000</div>
          <div class="slot abs" style="left:18px;top:52px;width:310px;height:94px" data-slot="阶段奖励2_含限时主城皮肤">限时主城皮肤（覆盖中小 R）</div>
          ${btn('前往蓝', '未达成', 470, 64, true)}</div></div>

      <div class="abs" style="left:18px;top:672px;width:704px;height:158px;background:rgba(255,198,0,.08);border:2px solid #FFC600;border-radius:10px" ${L('榜首大奖')}>
        <div class="slot abs" style="left:16px;top:16px;width:180px;height:126px" data-slot="限定主城皮肤_榜首大奖">限定主城皮肤</div>
        <div class="t gold abs sm" style="left:214px;top:22px;font-size:32px">跨服总榜 · 第 1 名</div>
        <div class="t abs sm" style="left:214px;top:66px;font-size:26px;color:#C8CDD4">限定高级主城皮肤 · 永久</div>
        <div class="t cyan abs sm" style="left:214px;top:104px;font-size:26px">我的排名 ${s.rank || 128}　·　按弹珠消耗量排</div></div>
    </div>`;
  }

  // —— L3 弹窗层 ——
  function dialog(s) {
    if (!s.dialog) return '';
    const shade = `<div class="abs" style="left:0;top:0;width:1920px;height:1080px;background:rgba(0,0,0,.62)" ${L('遮罩')}></div>`;
    const D = s.dialog;
    let inner = '';

    if (D === 'buff') {
      const card = (i, t, d, hot) => `<div class="abs" style="left:${40 + i * 306}px;top:150px;width:280px;height:360px;background:${hot ? 'rgba(255,198,0,.10)' : '#1F2630'};border:3px solid ${hot ? '#FFC600' : '#4C586A'};border-radius:14px" ${L('Buff卡' + (i + 1) + '-' + t)}>
          <div class="slot abs" style="left:60px;top:36px;width:160px;height:160px" data-slot="Buff图标_${t}"></div>
          <div class="t ${hot ? 'gold' : ''} abs" style="left:0;top:222px;width:280px;text-align:center;font-size:34px">${t}</div>
          <div class="t abs sm" style="left:16px;top:274px;width:248px;text-align:center;font-size:24px;color:#C8CDD4;line-height:1.4">${d}</div></div>`;
      inner = `<div class="abs" style="left:428px;top:210px;width:1004px;height:600px;background:#161013;border:3px solid #4C586A;border-radius:18px" ${L('L3 Buff池弹窗')}>
        <div class="t abs" style="left:0;top:34px;width:1004px;text-align:center;font-size:46px">入槽进度已满 · 三选一</div>
        <div class="t cyan abs sm" style="left:0;top:96px;width:1004px;text-align:center;font-size:26px">抽后进度重置，继续累计</div>
        ${card(0, '触发礼包', '限时只售高级弹珠<br>高 ROI', true)}
        ${card(1, '阶段积分', '直接获得一笔<br>额外进度条积分')}
        ${card(2, '弹珠返还', '返还随机数量弹珠')}</div>`;
    }

    if (D === 'pack') {
      inner = `<div class="abs" style="left:530px;top:190px;width:800px;height:640px;background:#161013;border:3px solid #FFC600;border-radius:18px" ${L('L3 触发礼包弹窗')}>
        <div class="t gold abs" style="left:0;top:30px;width:800px;text-align:center;font-size:46px">限时触发礼包</div>
        <div class="t cyan abs sm" style="left:0;top:92px;width:800px;text-align:center;font-size:28px">剩余 59:41　·　仅本次触发可购</div>
        <div class="slot abs" style="left:60px;top:150px;width:220px;height:220px" data-slot="高级弹珠礼包主视觉">高级弹珠<br>礼包主视觉</div>
        <div class="abs" style="left:312px;top:150px;width:428px" ${L('礼包内容')}>
          <div class="t abs sm" style="left:0;top:0;font-size:30px">高级弹珠 ×20</div>
          <div class="t green abs sm" style="left:0;top:48px;font-size:26px">本次发射得分 ×5，只出自礼包</div>
          <div class="abs" style="left:0;top:96px;width:94px;height:94px"><img style="position:absolute;left:0;top:0" width="94" height="94" src="${A}task/奖励格底_青.png"><img style="position:absolute;left:13px;top:13px" width="68" height="68" src="${A}task/道具图标B_IconRisingStarStone4.png"></div>
          <div class="t gold abs" style="left:120px;top:118px;font-size:44px">×20</div></div>
        <div class="t abs" style="left:60px;top:412px;width:220px;text-align:center;font-size:30px;color:#C8CDD4">ROI 标签位</div>
        <div class="abs" style="left:290px;top:470px" ${L('主按钮-购买')}>
          <img class="abs" style="left:0;top:0;width:280px;height:104px" src="${A}task/按钮_领取绿.png">
          <div class="t abs" style="left:0;top:0;width:280px;height:104px;display:flex;align-items:center;justify-content:center;font-size:40px">$ 4.99</div></div>
        <div class="t abs sm" style="left:0;top:590px;width:800px;text-align:center;font-size:24px;color:#8A929B">限购 1 次</div></div>`;
    }

    if (D === 'rank') {
      const row = (i, n, me) => `<div class="abs" style="left:30px;top:${190 + i * 92}px;width:940px;height:80px;background:${me ? 'rgba(255,198,0,.14)' : 'rgba(255,255,255,.04)'};border:${me ? '2px solid #FFC600' : '0'};border-radius:8px" ${L('榜行-' + n)}>
          <div class="t ${me ? 'gold' : ''} abs" style="left:24px;top:18px;font-size:34px">${n}</div>
          <div class="slot abs" style="left:110px;top:12px;width:56px;height:56px;border-width:2px"></div>
          <div class="t abs sm" style="left:186px;top:22px;font-size:30px;color:#C8CDD4">玩家名</div>
          <div class="t cyan abs sm" style="left:760px;top:22px;font-size:30px">弹珠消耗</div></div>`;
      inner = `<div class="abs" style="left:460px;top:150px;width:1000px;height:780px;background:#161013;border:3px solid #4C586A;border-radius:18px" ${L('L3 排行榜弹窗')}>
        <div class="t abs" style="left:0;top:30px;width:1000px;text-align:center;font-size:46px">跨服总榜</div>
        <div class="t cyan abs sm" style="left:0;top:96px;width:1000px;text-align:center;font-size:26px">按活动期累计弹珠消耗量排名</div>
        ${row(0, '1', false)}${row(1, '2', false)}${row(2, '3', false)}${row(3, '128', true)}
        <div class="abs" style="left:30px;top:566px;width:940px;height:150px;background:rgba(255,198,0,.08);border:2px solid #FFC600;border-radius:10px" ${L('名次奖励预览')}>
          <div class="slot abs" style="left:16px;top:16px;width:160px;height:118px" data-slot="限定主城皮肤_榜首大奖"></div>
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
          <div class="t gold abs" style="left:210px;top:24px;font-size:44px">128</div>
          <div class="t abs sm" style="left:400px;top:34px;font-size:28px;color:#C8CDD4">总积分 12,480</div></div>
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

  window.renderScreen = function (s) {
    return `<div class="screen abs" style="left:${s.x}px;top:${s.y}px" ${L(s.key)}>
      <div class="slot corner abs" style="left:0;top:0;width:1920px;height:1080px;padding:0 0 14px 1210px" data-slot="场景底_深空霓虹街机">场景底　·　深空霓虹街机（按档期替换）</div>
      ${nav()}
      <div class="t abs" style="left:398px;top:22px;font-size:74px;-webkit-text-stroke-width:7px" ${L('活动名')}>宇宙弹弹乐</div>
      <div class="t cyan abs sm" style="left:402px;top:112px;font-size:28px" ${L('活动描述')}>发射弹珠撞柱攒分，落槽翻倍　·　冲榜赢限定主城皮肤</div>
      <div class="abs" style="left:800px;top:34px;width:64px;height:64px;border-radius:50%;background:#1F2630;border:3px solid #4C586A;display:flex;align-items:center;justify-content:center" ${L('规则入口 ⓘ')}><div class="t gold" style="font-size:38px">i</div></div>
      ${assets(s)}${hud(s)}${board(s)}${fire(s)}${entries()}${panel(s)}${dialog(s)}
    </div>`;
  };
})();
