/* ===========================================================================
   marble3.js —— 宇宙弹弹乐 界面构件器 v3（定版）
   布局 1:1 复刻 P2 现有的「庆典弹弹乐」，色值与元件形态全部取自真机截图。
   ⛔ 不再自创排布。弹弹乐特有的三样东西挂进母版的既有位置：
      撞击计数 / 本发累计 → 盘顶提示条（母版那里写「点击任意洞口发射弹珠」）
      入槽进度 Buff       → 槽条右下角（母版那里是 0/8）
      高级弹珠 ×5         → 盘左上角圆按钮（母版那里是 ×5 倍数与道具圆钮）
   =========================================================================== */
(function () {
  const A = 'assets/';
  const MB = 'assets/marble/';
  const L = (n) => `data-layer="${n}" data-name="${n}"`;

  // 真机取色
  const C = {
    navBg: '#2E2E2E', navItem: '#3A3A3A', tabY: '#FFC61E', tabC: '#29C5F0',
    canopy: '#35C6F0', canopyDark: '#1B87B8', wood: '#C89A5A', woodDark: '#8A6A3A',
    boardBg: '#A8794C', green: '#5FD32A', greenDark: '#2E8A0C',
    gaugeFill: '#E040FB', gaugeBg: '#3A2A44', slotBg: '#5A4A94',
    ink: '#FFFFFF', dim: '#C8CDD4',
  };

  // ── 左侧导航条：一级黄页签(带尖角) + 二级青页签 + 未选中深灰底块 ──
  function nav() {
    const item = (y, txt, kind, dot, isNew, warn) => {
      const base = `left:0;top:${y}px;width:369px;height:${kind === 'sub' ? 88 : 104}px`;
      if (kind === 'main') {
        return `<div class="abs" style="${base}" ${L('页签-' + txt + ' 一级选中')}>
          <div class="abs" style="left:0;top:0;width:340px;height:104px;background:${C.tabY};border:4px solid #7A5A06;border-radius:14px"></div>
          <div class="abs" style="left:340px;top:30px;width:0;height:0;border-top:22px solid transparent;border-bottom:22px solid transparent;border-left:26px solid ${C.tabY}"></div>
          <div class="t dark abs" style="left:0;top:0;width:340px;height:104px;display:flex;align-items:center;justify-content:center;font-size:42px">${txt}</div>
          ${dot ? badge(-10, -10, dot) : ''}${isNew ? newTag(300, -12) : ''}</div>`;
      }
      if (kind === 'sub') {
        return `<div class="abs" style="${base}" ${L('页签-' + txt + ' 二级选中')}>
          <div class="abs" style="left:18px;top:0;width:304px;height:88px;background:${C.tabC};border:4px solid #0A5A78;border-radius:12px"></div>
          <div class="t abs" style="left:18px;top:0;width:304px;height:88px;display:flex;align-items:center;justify-content:center;font-size:36px">${txt}</div>
          ${dot ? badge(8, -10, dot) : ''}</div>`;
      }
      return `<div class="abs" style="${base}" ${L('页签-' + txt)}>
        <div class="abs" style="left:0;top:0;width:340px;height:104px;background:${C.navItem};border-bottom:2px solid #232323"></div>
        <div class="t abs" style="left:0;top:0;width:340px;height:104px;display:flex;align-items:center;justify-content:center;font-size:40px;color:#B6BCC4">${txt}</div>
        ${dot ? badge(-10, -10, dot) : ''}${isNew ? newTag(300, -12) : ''}${warn ? warnTag(150, 74) : ''}</div>`;
    };
    const badge = (x, y, n) => `<div class="abs" style="left:${x}px;top:${y}px;width:40px;height:40px;border-radius:50%;background:#E02020;border:3px solid #7A0C0C;display:flex;align-items:center;justify-content:center" ${L('红点')}><div class="t" style="font-size:24px">${n}</div></div>`;
    const newTag = (x, y) => `<div class="abs" style="left:${x}px;top:${y}px;width:56px;height:44px;background:#3EC81E;border:3px solid #1A6A0C;border-radius:8px;display:flex;align-items:center;justify-content:center" ${L('新角标')}><div class="t" style="font-size:22px">新</div></div>`;
    const warnTag = (x, y) => `<div class="abs" style="left:${x}px;top:${y}px;width:40px;height:40px;border-radius:50%;background:#E02020;border:3px solid #7A0C0C;display:flex;align-items:center;justify-content:center" ${L('待处理感叹号')}><div class="t" style="font-size:26px">!</div></div>`;

    return `<div class="abs" style="left:0;top:0;width:369px;height:1080px;background:${C.navBg}" ${L('左侧导航条')}>
      <div class="abs" style="left:14px;top:16px" ${L('返回按钮')}>
        <img class="abs" style="left:0;top:0" width="189" height="113" src="${A}nav/返回按钮底_189x113.png">
        <img class="abs" style="left:70px;top:22px" width="49" height="69" src="${A}nav/返回箭头_49x69.png"></div>
      ${item(150, '宇宙弹弹乐', 'main', 2, false)}
      ${item(266, '宇宙弹弹乐', 'sub', 2)}
      ${item(370, '惊喜加倍', 'off')}
      ${item(478, '充值豪礼', 'off')}
      ${item(600, '漫游奇遇', 'off', 1)}
      ${item(708, '节日派对', 'off', 5, false, true)}
      ${item(816, '庆典签到', 'off', 0, true)}
    </div>`;
  }

  // ── 右上资产条：黑半透明 + 绿方块【+】 ──
  function assets(s) {
    const chip = (icon, num, x, name) => `
      <div class="abs" style="left:${x}px;top:0;width:250px;height:66px" ${L(name)}>
        <div class="abs" style="left:0;top:0;width:196px;height:66px;background:rgba(8,10,14,.82);border-radius:12px"></div>
        <img class="abs" style="left:-8px;top:2px" width="62" height="62" src="${A}task/${icon}">
        <div class="t abs" style="left:62px;top:0;width:126px;height:66px;display:flex;align-items:center;justify-content:flex-end;font-size:34px">${num}</div>
        <div class="abs" style="left:200px;top:0;width:50px;height:66px;background:${C.green};border:3px solid ${C.greenDark};border-radius:12px;display:flex;align-items:center;justify-content:center" ${L('加号-跳礼包')}>
          <div class="t" style="font-size:40px">+</div></div></div>`;
    return `<div class="abs" style="left:1380px;top:16px;width:520px;height:66px" ${L('资产条')}>
      ${chip('../marble/弹珠_紫.png', s.balls, 0, '资产-弹珠')}
      ${chip('../marble/弹珠_金.png', s.adv, 270, '资产-高级弹珠')}</div>`;
  }

  // ── ① 弹珠机：顶棚 + 一关进度条 + 全同撞柱 + 倍数槽(含触发槽) ──
  //    撞柱全部一样，按撞中次数加分；积分满一关领奖后重置、场数+1。没有阶段奖励。
  function machine(s) {
    const MX = 500, MY = 112, MW = 840, MH = 906;
    const IX = MX + 36, IW = MW - 72;
    const PY = MY + 122;                 // 一关进度条
    const HY = MY + 192;                 // 实时读数条
    const IY = MY + 244, IH = 440;       // 盘面
    const live = s.hits > 0 || s.flying;
    const need = s.need || 120, cur = s.round || 0;

    const inlet = `<img class="abs" style="left:${MX + MW / 2 - 210}px;top:${MY + 40}px;width:420px;height:80px${s.flying ? ';filter:grayscale(.7) brightness(.75)' : ''}" src="${MB}顶棚发射横杆.png" ${L('入球口横杆' + (s.flying ? ' 出球中' : ''))}>`;

    // 一关进度条：撞柱得积分 → 满 need 领本关奖励 → 重置、场数+1
    const done = cur >= need;
    const roundBar = `<div class="abs" style="left:${IX}px;top:${PY}px;width:${IW}px;height:64px" ${L('一关进度条')}>
      <img class="abs" style="left:0;top:-6px;width:76px;height:76px" src="${MB}积分币.png" ${L('本关奖励图标(真切图)')}>
      <div class="abs" style="left:90px;top:8px;width:${IW - 220}px;height:48px;background:#241A10;border:5px solid #7A5A34;border-radius:24px"></div>
      <div class="abs" style="left:95px;top:13px;width:${(IW - 230) * Math.min(1, cur / need)}px;height:38px;background:linear-gradient(180deg,${done ? '#8CE84A,#3EAE12' : '#F06AFF,#E040FB'});border-radius:19px" ${L('本关进度填充')}></div>
      <div class="t abs" style="left:90px;top:8px;width:${IW - 220}px;height:48px;display:flex;align-items:center;justify-content:center;font-size:30px">${cur} / ${need}</div>
      <div class="abs" style="left:${IW - 116}px;top:-6px;width:116px;height:76px" ${L('场数')}>
        <img class="abs" style="left:12px;top:-8px;width:92px;height:92px" src="${MB}星_场数.png">
        <div class="t abs" style="left:12px;top:6px;width:92px;height:70px;display:flex;align-items:center;justify-content:center;font-size:36px;-webkit-text-stroke-width:5px">${s.stage || 1}</div>
        <div class="t abs sm" style="left:0;top:-30px;width:116px;text-align:center;font-size:22px;white-space:nowrap">场数</div></div></div>`;

    // 钉子 + 撞柱：撞柱全部一样，不带数字、不分高低
    let pegs = '';
    const POSTS = new Set(['1-3', '3-1', '3-5', '5-2', '5-4', '2-0', '2-6']);
    for (let r = 0; r < 7; r++) {
      const n = r % 2 === 0 ? 8 : 7;
      const y = IY + 40 + r * ((IH - 110) / 6);
      const gap = (IW - 110) / (n - 1 + (r % 2 === 0 ? 0 : 1));
      for (let c = 0; c < n; c++) {
        const x = IX + 55 + c * gap + (r % 2 ? gap / 2 : 0);
        if (POSTS.has(r + '-' + c)) {
          pegs += `<img class="abs" style="left:${x - 27}px;top:${y - 27}px;width:54px;height:54px${s.dead ? ';filter:grayscale(1) brightness(.6)' : ''}" src="${MB}圆钮_黄大.png" ${L('撞柱' + (s.dead ? ' 熄灭' : ''))}>`;
        } else {
          pegs += `<div class="abs" style="left:${x - 8}px;top:${y - 8}px;width:16px;height:16px;border-radius:50%;background:#F0E0C0;box-shadow:0 3px 0 #A88848"></div>`;
        }
      }
    }

    // 底部倍数槽 ×1 ×2 ×3 ×10 ×3 ×2 ×1；其中随机 1 个为触发槽（落入才累计，满则抽 Buff 后重随机）
    const vals = [1, 2, 3, 10, 3, 2, 1];
    const sy = MY + MH - 208;
    const trig = s.trigSlot === undefined ? 4 : s.trigSlot;
    const tFull = s.gauge[0] >= s.gauge[1];
    const slots = vals.map((v, i) => {
      const w = IW / 7, x = IX + i * w, hot = v === 10, hit = s.slot === i, isT = i === trig;
      return `<div class="abs" style="left:${x}px;top:${sy}px;width:${w}px;height:140px" ${L('槽' + (i + 1) + '-x' + v + (isT ? ' 触发槽' : '') + (hit ? ' 命中' : ''))}>
        ${isT ? `<div class="abs" style="left:${w / 2 - 44}px;top:-44px;width:88px;height:42px;background:${tFull ? '#FFC61E' : 'rgba(8,10,14,.86)'};border:4px solid #FFC61E;border-radius:21px;display:flex;align-items:center;justify-content:center" ${L('触发槽计数')}>
              <div class="t ${tFull ? 'dark' : 'gold'}" style="font-size:26px">${s.gauge[0]}/${s.gauge[1]}</div></div>` : ''}
        <div class="abs" style="left:${w / 2 - 34}px;top:0;width:68px;height:68px;border-radius:50%${isT ? ';box-shadow:0 0 0 5px rgba(255,198,30,.55),0 0 24px 6px rgba(255,198,30,.55)' : ''}${hit ? ';box-shadow:0 0 0 6px #FFFFFF' : ''}">
          <img class="abs" style="left:0;top:0;width:68px;height:68px" src="${MB}圆钮_${hot ? '黄大' : isT ? '紫大' : '蓝大'}.png">
          <div class="t abs" style="left:0;top:0;width:68px;height:68px;display:flex;align-items:center;justify-content:center;font-size:${hot ? 30 : 26}px">×${v}</div></div>
        <div class="t ${isT ? 'gold' : ''} abs sm" style="left:${w / 2 - 60}px;top:74px;width:120px;text-align:center;font-size:22px;white-space:nowrap;${isT ? '' : 'color:#C8CDD4'}">${isT ? '触发槽' : ''}</div></div>`;
    }).join('');
    const trigNote = `<div class="t cyan abs sm" style="left:${IX}px;top:${MY + MH - 46}px;width:${IW}px;text-align:center;font-size:22px;line-height:1.4" ${L('触发槽说明')}>落入<b>触发槽</b>才累计　·　满 ${s.gauge[1]} 次抽 Buff 后<b>重新随机</b>一个槽</div>`;

    return `
    <img class="abs" style="left:${MX - 30}px;top:${MY + 66}px;width:${MW + 60}px;height:${MH - 46}px" src="${MB}机身_空盘框.png" ${L('弹珠机身(真切图)')}>
    <img class="abs" style="left:${MX + MW / 2 - 330}px;top:${MY - 10}px;width:660px;height:130px" src="${MB}拱顶蓝盖.png" ${L('拱形顶棚(真切图)')}>
    ${inlet}${roundBar}
    <div class="abs" style="left:${IX}px;top:${HY}px;width:${IW}px;height:44px;background:${live ? 'rgba(8,10,16,.85)' : 'rgba(0,0,0,.42)'};border-radius:8px;display:flex;align-items:center;justify-content:center;gap:14px" ${L('⑨ ' + (live ? '本次发射实时信息' : '操作提示条'))}>
      ${live
        ? `<div class="t sm" style="font-size:26px">撞击</div><div class="t ${s.burst ? 'gold' : 'cyan'}" style="font-size:32px">${s.hits} / 11</div>
           <div class="t sm" style="font-size:26px;color:#8A929B">·</div>
           <div class="t sm" style="font-size:26px">本发累计</div><div class="t gold" style="font-size:32px">${s.acc.toLocaleString()}</div>`
        : `<div class="t sm" style="font-size:26px">撞柱按次数加分　·　满 ${need} 分领本关奖励，重置进下一场</div>`}</div>
    <div class="abs" style="left:${IX}px;top:${IY}px;width:${IW}px;height:${IH}px" ${L('盘面区')}></div>
    ${pegs}
    ${s.trail ? s.trail.map((p, i) => `<div class="abs" style="left:${IX + p[0] - 9}px;top:${IY + p[1] - 9}px;width:18px;height:18px;border-radius:50%;background:${s.advSel ? '#FFC61E' : '#EAF2FF'};opacity:${.16 + i * .14}"></div>`).join('') : ''}
    ${s.ball ? `<div class="abs" style="left:${IX + s.ball[0] - 22}px;top:${IY + s.ball[1] - 22}px;width:44px;height:44px;border-radius:50%;box-shadow:0 0 26px 8px ${s.advSel ? 'rgba(255,198,30,.8)' : 'rgba(190,120,255,.75)'}" ${L('弹珠')}><img style="position:absolute;left:0;top:0;width:44px;height:44px" src="${MB}弹珠_${s.advSel ? '金' : '紫'}.png"></div>` : ''}
    ${s.pop ? `<div class="t green abs" style="left:${IX + s.pop[0]}px;top:${IY + s.pop[1]}px;font-size:44px" ${L('命中飘字')}>+${s.pop[2]}</div>` : ''}
    ${s.burst ? `<div class="abs" style="left:${IX + IW / 2 - 220}px;top:${IY + IH / 2 - 80}px;width:440px;height:160px;border:5px solid #FFC61E;border-radius:16px;background:rgba(255,198,30,.22);display:flex;flex-direction:column;align-items:center;justify-content:center" ${L('第11次翻倍演出')}>
        <div class="t gold" style="font-size:58px">累计 ×2</div>
        <div class="t sm" style="font-size:24px;color:#FFE9A8">第 11 次撞击 · 翻倍并封顶</div></div>` : ''}
    ${slots}${trigNote}`;
  }

  // ── 右列：排行榜(右上) + 积分进度 + 成就/商店 + ②发射区(含消耗倍数) ──
  function rightCol(s) {
    const rank = `<div class="abs" style="left:1490px;top:96px;width:410px;height:150px" ${L('⑦ 排行榜卡')}>
      <div class="abs" style="left:0;top:0;width:280px;height:66px;background:linear-gradient(180deg,#D9484A,#8A1A1C);border:3px solid rgba(0,0,0,.45);border-radius:8px" ${L('榜行-跨服榜')}>
        <img class="abs" style="left:6px;top:5px;width:52px;height:52px;object-fit:contain" src="${MB}排行榜奖杯.png">
        <div class="t abs sm" style="left:66px;top:16px;font-size:26px;white-space:nowrap">跨服榜</div>
        <div class="t gold abs sm" style="right:10px;top:16px;font-size:26px">-</div></div>
      <div class="abs" style="left:0;top:76px;width:280px;height:66px;background:linear-gradient(180deg,#F0C24A,#B0821A);border:3px solid rgba(0,0,0,.45);border-radius:8px" ${L('榜行-每日榜')}>
        <img class="abs" style="left:6px;top:5px;width:52px;height:52px;object-fit:contain" src="${MB}星_场数.png">
        <div class="t abs sm" style="left:66px;top:16px;font-size:26px;white-space:nowrap">每日榜</div>
        <div class="t gold abs sm" style="right:10px;top:16px;font-size:26px;white-space:nowrap">${s.rank}th</div></div>
      <img class="abs" style="left:288px;top:2px;width:128px;height:120px;object-fit:contain" src="${MB}排行榜奖杯.png" ${L('排行榜按钮(真切图)')}></div>`;

    const ICONS = { '⑧ 成就': '成就图标', '兑换商店': '兑换商店图标' };
    const entry = (y, txt, name) => `<div class="abs" style="left:1668px;top:${y}px;width:200px;height:130px" ${L(name)}>
      <img class="abs" style="left:50px;top:-4px;width:100px;height:100px;object-fit:contain" src="${MB}${ICONS[name] || '成就图标'}.png">
      <div class="t abs" style="left:0;top:96px;width:200px;text-align:center;font-size:28px;white-space:nowrap">${txt}</div></div>`;

    const mult = (v, i) => `<div class="abs" style="left:${i * 116}px;top:0;width:104px;height:70px;background:${s.mult === v ? 'linear-gradient(180deg,#FFD24A,#D9840A)' : 'rgba(8,10,14,.78)'};border:4px solid ${s.mult === v ? '#7A5A06' : '#5A6270'};border-radius:12px;display:flex;align-items:center;justify-content:center" ${L('消耗倍数-x' + v)}>
      <div class="t ${s.mult === v ? 'dark' : ''}" style="font-size:32px">×${v}</div></div>`;

    const fire = `<div class="abs" style="left:1360px;top:722px;width:540px;height:274px" ${L('② 发射区')}>
      <div class="t abs sm" style="left:0;top:-4px;width:540px;text-align:center;font-size:22px;color:#C8CDD4;white-space:nowrap" ${L('倍数说明')}>③ 消耗弹珠数量　·　得分与消耗同步放大</div>
      <div class="abs" style="left:96px;top:28px;width:336px;height:70px" ${L('③ 倍数选择器')}>${mult(1, 0)}${mult(5, 1)}${mult(10, 2)}</div>
      <div class="abs" style="left:0;top:118px;width:150px;height:156px;background:rgba(8,10,14,.72);border:4px solid ${s.advSel ? '#FFC61E' : '#5A6270'};border-radius:14px" ${L('普通/高级弹珠切换')}>
        <div class="t abs sm" style="left:0;top:10px;width:150px;text-align:center;font-size:22px;color:#C8CDD4;white-space:nowrap">弹珠类型</div>
        <img class="abs" style="left:47px;top:42px" width="56" height="56" src="${MB}弹珠_${s.advSel ? '金' : '紫'}.png">
        <div class="t ${s.advSel ? 'gold' : ''} abs sm" style="left:0;top:106px;width:150px;text-align:center;font-size:26px;white-space:nowrap">${s.advSel ? '高级 ×5' : '普通'}</div></div>
      <div class="abs" style="left:170px;top:118px;width:370px;height:156px" ${L('主按钮-发射' + (s.fireOff || s.flying ? ' 置灰' : ''))}>
        <img class="abs" style="left:115px;top:-6px;width:132px;height:132px${s.fireOff || s.flying ? ';filter:grayscale(1) brightness(.65)' : ''}" src="${MB}绿大按钮.png">
        <div class="t abs" style="left:115px;top:32px;width:132px;text-align:center;font-size:38px">${s.flying ? '…' : (s.fireOff ? '✕' : '发射')}</div>
        <div class="t abs sm" style="left:0;top:126px;width:370px;text-align:center;font-size:24px;white-space:nowrap">${s.flying ? '发射中' : (s.fireLabel || '')}　消耗 弹珠 ×${s.mult}</div></div></div>`;

    const prize = `<div class="abs" style="left:1370px;top:300px;width:250px;height:330px;background:rgba(8,10,14,.6);border:4px solid #6A5A34;border-radius:14px" ${L('本关奖励预览')}>
      <div class="t abs sm" style="left:0;top:14px;width:250px;text-align:center;font-size:26px;white-space:nowrap">本场奖励</div>
      <div class="abs" style="left:35px;top:56px;width:180px;height:132px" ${L('本关奖励主图')}>
        <img class="abs" style="left:30px;top:0;width:120px;height:120px;object-fit:contain" src="${MB}积分币.png">
        <img class="abs" style="left:104px;top:64px;width:64px;height:64px" src="${MB}星_场数.png"></div>
      <div class="abs" style="left:35px;top:200px;width:82px;height:82px"><img style="position:absolute;left:0;top:0" width="82" height="82" src="${A}task/奖励格底_青.png"><img style="position:absolute;left:13px;top:13px;width:56px;height:56px;object-fit:contain" src="${MB}弹珠_紫.png"></div>
      <div class="abs" style="left:133px;top:200px;width:82px;height:82px"><img style="position:absolute;left:0;top:0" width="82" height="82" src="${A}task/奖励格底_黄.png"><img style="position:absolute;left:13px;top:13px;width:56px;height:56px;object-fit:contain" src="${MB}积分币.png"></div>
      <div class="t cyan abs sm" style="left:0;top:292px;width:250px;text-align:center;font-size:22px;white-space:nowrap">满 ${s.need || 120} 分自动进下一场</div></div>`;
    return rank + prize + entry(300, '成就', '⑧ 成就') + entry(458, '兑换商店', '兑换商店') + fire;
  }

  // ── 四角：倒计时（右下）+ ⓘ（左下） ──
  function corners(s) {
    return `
      <div class="abs" style="left:1560px;top:1000px;width:340px;height:56px;background:rgba(8,10,14,.85);border-radius:10px;display:flex;align-items:center;justify-content:center;gap:10px" ${L('活动倒计时')}>
        <div class="t sm" style="font-size:28px;white-space:nowrap">进行中</div>
        <div class="t gold" style="font-size:30px;white-space:nowrap">05天14时</div></div>
      <div class="abs" style="left:396px;top:990px;width:70px;height:70px;border-radius:50%;background:rgba(240,240,240,.9);border:4px solid #7A828C;display:flex;align-items:center;justify-content:center" ${L('规则入口 ⓘ')}>
        <div style="font-weight:900;font-size:42px;color:#3A3A3A">i</div></div>`;
  }

  // ── L3 弹窗（母版：灰白标题条 + 红 ✕ 外凸 + 文件夹页签） ──
  function dialog(s) {
    if (!s.dialog) return '';
    const shade = `<div class="abs" style="left:0;top:0;width:1920px;height:1080px;background:rgba(0,0,0,.6)" ${L('遮罩')}></div>`;
    const frame = (x, y, w, h, title, body, tabs) => `
      <div class="abs" style="left:${x}px;top:${y}px;width:${w}px;height:${h}px;background:#3A3A3A;border-radius:10px" ${L('L3 ' + title)}>
        <div class="abs" style="left:0;top:0;width:${w}px;height:88px;background:linear-gradient(180deg,#F2F2F2,#BFBFBF);border-radius:10px 10px 0 0"></div>
        <div style="position:absolute;left:0;top:0;width:${w}px;height:88px;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:44px;color:#3A3A3A">${title}</div>
        <div class="abs" style="left:${w - 62}px;top:-22px;width:104px;height:104px;background:#E02020;border:5px solid #7A0C0C;border-radius:14px;display:flex;align-items:center;justify-content:center" ${L('关闭')}>
          <div class="t" style="font-size:52px">✕</div></div>
        ${tabs || ''}${body}</div>`;

    if (s.dialog === 'rank') {
      const tabs = `<div class="abs" style="left:36px;top:96px;width:300px;height:70px;background:#4A4A4A;border-radius:10px 10px 0 0;display:flex;align-items:center;justify-content:center" ${L('页签-跨服榜 选中')}><div class="t" style="font-size:32px">跨服榜</div></div>
        <div class="abs" style="left:346px;top:104px;width:300px;height:62px;background:#2E2E2E;border-radius:10px 10px 0 0;display:flex;align-items:center;justify-content:center" ${L('页签-每日榜')}><div class="t" style="font-size:30px;color:#9AA0A8">每日榜</div></div>`;
      const row = (i, n, me) => `<div class="abs" style="left:36px;top:${240 + i * 96}px;width:1028px;height:84px;background:${me ? 'rgba(255,198,30,.18)' : (i % 2 ? '#333' : '#2C2C2C')};border-radius:8px${me ? ';border:3px solid #FFC61E' : ''}" ${L('榜行-' + n)}>
        <div class="t ${me ? 'gold' : ''} abs" style="left:26px;top:20px;font-size:34px">${n}</div>
        <div class="slot abs" style="left:120px;top:12px;width:60px;height:60px;border-width:2px"></div>
        <div class="t abs sm" style="left:200px;top:24px;font-size:30px;color:#C8CDD4">玩家名</div>
        <div class="t cyan abs sm" style="right:26px;top:24px;font-size:30px;white-space:nowrap">弹珠消耗</div></div>`;
      return shade + frame(410, 110, 1100, 860, '总排名',
        `<div class="abs" style="left:36px;top:176px;width:1028px;height:56px;background:#4A4A4A;border-radius:8px">
           <div class="t abs sm" style="left:40px;top:12px;font-size:28px;color:#B6BCC4">排名</div>
           <div class="t abs sm" style="left:480px;top:12px;font-size:28px;color:#B6BCC4">奖励</div></div>
         ${row(0, '1', false)}${row(1, '2', false)}${row(2, '3', false)}${row(3, s.rank, true)}
         <div class="t cyan abs sm" style="left:36px;top:640px;width:1028px;text-align:center;font-size:28px">按活动期累计弹珠消耗量排名　·　活动结束统一邮件发放</div>`, tabs);
    }
    if (s.dialog === 'buff') {
      const card = (i, t, d, hot) => `<div class="abs" style="left:${60 + i * 300}px;top:170px;width:260px;height:380px;background:${hot ? 'rgba(255,198,30,.14)' : '#2C2C2C'};border:4px solid ${hot ? '#FFC61E' : '#5A5A5A'};border-radius:14px" ${L('Buff卡-' + t)}>
        <img class="abs" style="left:50px;top:34px;width:160px;height:160px;object-fit:contain" src="${MB}${t === '触发礼包' ? '兑换商店图标' : t === '阶段积分' ? '积分币' : '弹珠_紫'}.png" ${L('Buff图标-' + t)}>
        <div class="t ${hot ? 'gold' : ''} abs" style="left:0;top:216px;width:260px;text-align:center;font-size:32px">${t}</div>
        <div class="t abs sm" style="left:14px;top:268px;width:232px;text-align:center;font-size:24px;color:#C8CDD4;line-height:1.4">${d}</div></div>`;
      return shade + frame(500, 190, 980, 620, '入槽进度已满',
        `<div class="t cyan abs sm" style="left:0;top:118px;width:980px;text-align:center;font-size:28px">三选一　·　抽后进度重置，继续累计</div>
         ${card(0, '触发礼包', '限时只售高级弹珠<br>高 ROI', true)}${card(1, '阶段积分', '直接获得一笔<br>额外进度积分')}${card(2, '弹珠返还', '返还随机数量弹珠')}`);
    }
    if (s.dialog === 'pack') {
      return shade + frame(560, 180, 800, 700, '限时触发礼包',
        `<div class="t gold abs" style="left:0;top:110px;width:800px;text-align:center;font-size:30px">剩余 59:41　·　仅本次触发可购</div>
         <div class="abs" style="left:60px;top:180px;width:220px;height:220px" ${L('高级弹珠礼包主视觉')}>
           <img class="abs" style="left:30px;top:20px;width:160px;height:160px;object-fit:contain" src="${MB}弹珠_金.png">
           <img class="abs" style="left:120px;top:110px;width:90px;height:90px;object-fit:contain" src="${MB}弹珠_金.png">
           <img class="abs" style="left:10px;top:120px;width:80px;height:80px;object-fit:contain" src="${MB}弹珠_金.png"></div>
         <div class="t abs" style="left:312px;top:190px;font-size:34px;white-space:nowrap">高级弹珠 ×20</div>
         <div class="t green abs sm" style="left:312px;top:244px;font-size:26px;white-space:nowrap">本次发射得分 ×5，只出自礼包</div>
         <div class="abs" style="left:312px;top:292px;width:94px;height:94px"><img style="position:absolute;left:0;top:0" width="94" height="94" src="${A}task/奖励格底_青.png"><img style="position:absolute;left:13px;top:13px" width="68" height="68" src="${A}task/道具图标B_IconRisingStarStone4.png"></div>
         <div class="t gold abs" style="left:432px;top:314px;font-size:44px">×20</div>
         <div class="abs" style="left:270px;top:470px;width:280px;height:96px;background:linear-gradient(180deg,#FFD24A,#D9840A);border:5px solid #7A4A06;border-radius:12px;display:flex;align-items:center;justify-content:center" ${L('主按钮-购买')}>
           <div class="t dark" style="font-size:42px">$ 4.99</div></div>
         <div class="t abs sm" style="left:0;top:596px;width:800px;text-align:center;font-size:26px;color:#9AA0A8">限购 1 次</div>`);
    }
    if (s.dialog === 'roundup') {
      return shade + frame(560, 180, 800, 700, '本关达成',
        `<div class="t cyan abs" style="left:0;top:110px;width:800px;text-align:center;font-size:28px">第 ${s.stage} 场积分已满 ${s.need || 120}</div>
         <div class="abs" style="left:80px;top:170px;width:250px;height:190px" ${L('本关奖励主图')}>
           <img class="abs" style="left:55px;top:0;width:140px;height:140px;object-fit:contain" src="${MB}积分币.png">
           <img class="abs" style="left:150px;top:86px;width:70px;height:70px" src="${MB}星_场数.png">
           <div class="t abs sm" style="left:0;top:152px;width:250px;text-align:center;font-size:24px;white-space:nowrap">第 ${s.stage} 场奖励</div></div>
         <div class="abs" style="left:370px;top:180px;width:94px;height:94px"><img style="position:absolute;left:0;top:0" width="94" height="94" src="${A}task/奖励格底_青.png"><img style="position:absolute;left:13px;top:13px" width="68" height="68" src="${A}task/道具图标B_IconRisingStarStone4.png"></div>
         <div class="abs" style="left:478px;top:180px;width:94px;height:94px"><img style="position:absolute;left:0;top:0" width="94" height="94" src="${A}task/奖励格底_黄.png"><img style="position:absolute;left:13px;top:13px" width="68" height="68" src="${A}task/道具图标A_UiItemsGoldAllPower.png"></div>
         <div class="t abs sm" style="left:370px;top:292px;width:300px;font-size:24px;color:#C8CDD4;line-height:1.5">领取后进度重置，<br>场数 +1、奖励升级</div>
         <div class="abs" style="left:220px;top:420px;width:360px;height:104px;background:linear-gradient(180deg,#7BE84A,#2E8A0C);border:6px solid #1A6A0C;border-radius:14px;display:flex;align-items:center;justify-content:center" ${L('主按钮-领取并进下一场')}>
           <div class="t" style="font-size:38px">领取 · 进入第 ${s.stage + 1} 场</div></div>
         <div class="t abs sm" style="left:0;top:560px;width:800px;text-align:center;font-size:24px;color:#9AA0A8">积分越高的场次，本场奖励越好</div>`);
    }
    if (s.dialog === 'end') {
      return shade + frame(600, 240, 720, 580, '活动已结束',
        `<div class="t cyan abs" style="left:0;top:112px;width:720px;text-align:center;font-size:28px">名次奖励将统一发放至邮件</div>
         <div class="abs" style="left:50px;top:174px;width:620px;height:110px;background:#2C2C2C;border-radius:10px" ${L('最终名次')}>
           <div class="t abs sm" style="left:26px;top:34px;font-size:30px;white-space:nowrap">最终名次</div>
           <div class="t gold abs" style="left:200px;top:24px;font-size:44px">${s.rank}</div>
           <div class="t abs sm" style="left:360px;top:34px;font-size:28px;color:#C8CDD4;white-space:nowrap">完成 ${s.stage} 场</div></div>
         <div class="abs" style="left:50px;top:302px;width:620px;height:110px;background:rgba(255,198,30,.1);border:3px solid #FFC61E;border-radius:10px" ${L('剩余弹珠折算')}>
           <div class="t gold abs sm" style="left:26px;top:16px;font-size:28px;white-space:nowrap">剩余弹珠折算金币</div>
           <div class="t abs sm" style="left:26px;top:58px;font-size:26px;color:#C8CDD4;white-space:nowrap">普通 ×12 + 高级 ×2　→　邮件发放</div></div>
         <div class="abs" style="left:220px;top:446px;width:280px;height:88px;background:linear-gradient(180deg,#7BE84A,#2E8A0C);border:5px solid #1A6A0C;border-radius:12px;display:flex;align-items:center;justify-content:center" ${L('主按钮-确定')}>
           <div class="t" style="font-size:38px">确定</div></div>`);
    }
    if (s.dialog === 'error') {
      return shade + frame(680, 340, 560, 400, '数据加载失败',
        `<div class="t abs sm" style="left:40px;top:130px;width:480px;text-align:center;font-size:28px;color:#C8CDD4;line-height:1.5">排行榜 / 积分数据拉取超时。<br>本次发射结果已保留，重试后刷新。</div>
         <div class="abs" style="left:140px;top:262px;width:280px;height:88px;background:linear-gradient(180deg,#8FE4FF,#2FA6D8);border:5px solid #0C5A7A;border-radius:12px;display:flex;align-items:center;justify-content:center" ${L('主按钮-重试')}>
           <div class="t" style="font-size:38px">重试</div></div>`);
    }
    return shade;
  }

  window.renderScreen3 = function (s) {
    return `<div class="screen abs" style="left:${s.x}px;top:${s.y}px" ${L(s.key)}>
      <img class="abs" style="left:0;top:0;width:1920px;height:1080px;object-fit:cover" src="${MB}场景底_街机厅.png" ${L('场景底(按档期替换)')}>
      <div class="abs" style="left:369px;top:0;width:1551px;height:1080px;background:rgba(6,10,18,.38)" ${L('场景压暗层')}></div>
      ${nav()}
      <div class="t abs" style="left:398px;top:14px;font-size:76px;-webkit-text-stroke-width:8px" ${L('活动名')}>宇宙弹弹乐</div>
      ${assets(s)}${machine(s)}${rightCol(s)}${corners(s)}
      ${s.lowHint ? `<div class="abs" style="left:1360px;top:668px;width:540px;height:50px;background:rgba(224,32,32,.22);border:3px solid #FF5A4E;border-radius:10px;display:flex;align-items:center;justify-content:center" ${L('弹珠不足提示')}><div class="t sm" style="font-size:26px;color:#FF9A90">${s.lowHint}</div></div>` : ''}
      ${dialog(s)}
    </div>`;
  };
})();
