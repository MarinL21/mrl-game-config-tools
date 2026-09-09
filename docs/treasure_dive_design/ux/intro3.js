/* ============================================================================
   深海探宝（2112 = 21129575，12 月节）· 活动开始介绍流程 三联图
   一屏 = 1920×1080；三屏并排在甲式黑板上，每屏都是活的 renderScreen(scr)

   机制口径来源：服务端 actvdom/treasuredivedom 通读结论 + 2121 / 2189 实配
     · 棋盘 6 列 × 8 行、10 米/行、单次下潜上限 32 行 —— 写死在服务端
     · 可挖 = 上下左右紧贴空格；最下一行出现空格 → 下潜一行
     · 水母：气泡 / 空气泡 / 海藻 1 只，石块 2 只，宝箱 0
     · 炸弹 13 格（九宫套十字）只卷气泡与石块；手电整列通吃
     · 海藻 3×3，中心格不可破、数字 = 周围 8 格中有奖的个数
   ========================================================================== */
'use strict';

const A = 'assets/';
/* 0909 换黑金 HOW TO PLAY 版式后，scene / nav / popBase / popBar / close / b* / info
   这几件已不在稿子里出现（旧 P2 蓝弹窗壳用的），留着方便回退，bundle 不会内联未引用的图 */
const IMG = {
  scene:    A + 'td/UI_场景全屏.jpg',
  nav:      A + 'common/导航条_母版整条_369x1080.png',
  popBase:  A + 'common/弹窗高_底板_1542x1027.png',
  popBar:   A + 'common/弹窗高_标题横条_1528x111.png',
  close:    A + 'common/弹窗_关闭红X_122x115.png',
  bBlue:    A + 'common/按钮_蓝通用_390x146.png',
  bGold:    A + 'common/按钮_金购买_390x146.png',
  bGray:    A + 'common/按钮_灰不可点击_390x146.png',
  info:     A + 'td/UI_钮_规则i.png',
  jelly:    A + 'td/道具_水母.png',
  gold:     A + 'td/道具_金海螺.png',
  silver:   A + 'td/道具_银海螺.png',
  bomb:     A + 'td/道具_炸弹.png',
  light:    A + 'td/道具_手电.png',
  chest:    A + 'td/UI_奖_宝箱.png',
  decor:    A + 'td/UI_奖_装饰件.png',
  shop:     A + 'td/UI_入口_兑换商店.png',
  rail:     A + 'td/UI_深度轨.png',
  btnBomb:  A + 'td/UI_钮_炸弹.png',
  btnLight: A + 'td/UI_钮_手电.png'
};
const CELL_ART = {
  b: A + 'td/格_气泡.png',
  x: A + 'td/格_空气泡.png',
  r: A + 'td/格_石块.png',
  s: A + 'td/格_海藻.png',
  c: A + 'td/格_海藻中心.png',
  e: A + 'td/格_空格.png',
  t: A + 'td/UI_奖_宝箱.png'
};
const PAGES = ['怎么下潜', '道具怎么用', '海螺换奖 + 深度奖励'];
const SUBCAP = ['点一格花多少 → 什么能点 → 怎么下潜', '炸弹 13 格 / 手电整列 / 落点限制', '海螺来源 / 兑换商店 / 深度奖励'];

/* ---------------------------------------------------------------- 小工具 */
const el = (h) => { const d = document.createElement('div'); d.innerHTML = h.trim(); return d.firstElementChild; };
const img = (src, w, h, cls, style) =>
  `<img${cls ? ` class="${cls}"` : ''} src="${src}"${w ? ` width="${w}"` : ''}${h ? ` height="${h}"` : ''}` +
  `${style ? ` style="${style}"` : ''} alt="">`;
const box = (l, t, w, h) => `left:${l}px;top:${t}px;width:${w}px;height:${h}px`;
const ph = (label, fs) => `<div class="slot" style="width:100%;height:100%;font-size:${fs || 16}px">${label}</div>`;

/* ---------------------------------------------------------------- 盘面 */
function cellHTML(cell, cls, size) {
  const t = cell.t;
  let inner = img(CELL_ART[t] || CELL_ART.e, size, size);
  if (t === 'c') inner += `<span class="num">${cell.n != null ? cell.n : ''}</span>`;
  if (t === 't' && cell.n != null) inner += `<span class="qty">×${cell.n}</span>`;
  return `<div class="cell${cls ? ' ' + cls : ''}" data-name="格_${t}">${inner}</div>`;
}
function boardHTML(grid, o) {
  const s = o.cell, g = o.gap == null ? 5 : o.gap, pad = o.pad == null ? 13 : o.pad;
  const cols = grid[0].length, rows = grid.length;
  const w = cols * s + (cols - 1) * g + pad * 2, h = rows * s + (rows - 1) * g + pad * 2;
  let cells = '';
  for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
    cells += `<div data-rc="${r},${c}" style="width:${s}px;height:${s}px">` +
             cellHTML(grid[r][c], o.mark ? o.mark(r, c, grid[r][c]) : '', s) + '</div>';
  }
  return `<div class="board" data-layer="盘面" data-name="盘面" style="${box(o.x, o.y, w, h)}">
    <div class="board-in" style="left:${pad}px;top:${pad}px;grid-template-columns:repeat(${cols},${s}px);gap:${g}px">
      ${cells}</div></div>`;
}

/* 盘面格子构造器：P('b') 气泡 / 'x' 空气泡 / 'r' 石块 / 's' 海藻 / 'c' 海藻中心 / 'e' 空格 / 't' 宝箱 */
const P = (t, n) => (n == null ? { t } : { t, n });

/* ================================================================ ①页
   2026-09-09 换版式：黑底金标题 HOW TO PLAY 三联分镜（参考竞品 HTP 弹窗）
   一页说清：① 点开格子要花水母 ② 只能挖紧贴空格的通路 ③ 挖穿底行=下潜10米
   底部横贯一条「点一格要花多少水母」把 5 类格子的 cost 全列出来
   cost 口径 = 2189 实配：气泡/空气泡/海藻 1，石块 2，宝箱 0（click_num 3~5）
   ============================================================== */
const SVG_ARROW = `<svg width="100" height="96" viewBox="0 0 100 96" fill="none">
  <path d="M8 72 C 26 26, 52 14, 80 30" stroke="#F2A93B" stroke-width="13"
        stroke-linecap="round" fill="none"/>
  <path d="M98 40 L62 20 L68 52 Z" fill="#F2A93B"/></svg>`;
const SVG_TAP = `<svg width="76" height="76" viewBox="0 0 76 76">
  <circle cx="38" cy="38" r="11" fill="#FFD34F"/>
  <circle cx="38" cy="38" r="21" fill="none" stroke="#FFD34F" stroke-width="4" opacity=".72"/>
  <circle cx="38" cy="38" r="32" fill="none" stroke="#FFD34F" stroke-width="3" opacity=".34"/></svg>`;
const SVG_DOWN = `<svg width="46" height="46" viewBox="0 0 46 46" fill="none">
  <path d="M23 5 L23 32 M11 23 L23 38 L35 23" stroke="#F8B32B" stroke-width="6"
        stroke-linecap="round" stroke-linejoin="round"/></svg>`;
const SVG_FRAME = `<svg width="46" height="46" viewBox="0 0 46 46" fill="none">
  <rect x="5" y="5" width="36" height="36" rx="5" stroke="#F8B32B" stroke-width="5"/>
  <rect x="15" y="15" width="16" height="16" rx="2" fill="#F8B32B" opacity=".55"/></svg>`;

const g4 = (rows) => rows.map((l) => l.split('').map((ch) => P(ch)));

/* 三格分镜：盘面 4 列 × 3 行，cell 82 */
const P1_SHOTS = [
  { rows: ['eeee', 'bbbb', 'bxsr'],
    mark: (r, c) => (r === 1 && c === 1 ? 'pick' : ''),
    deco: `<div style="position:absolute;left:150px;top:104px">${SVG_TAP}</div>
           <div class="htp-tag gold" style="left:236px;top:64px">−1 水母</div>`,
    icon: () => img(IMG.jelly, 46, 46, '', 'display:inline-block'),
    tt: '点开格子', 
    desc: '点一下就<b>破一格</b>，同时扣水母。<br>不同格子价钱不一样 —— 见下面那条。' },

  { rows: ['eeee', 'bbbb', 'bxsr'],
    mark: (r, c) => (r === 1 ? 'pick' : r === 2 ? 'nogo' : ''),
    deco: `<div class="htp-tag gold" style="left:74px;top:-52px">金框 = 现在点得动</div>
           <div class="htp-tag" style="left:112px;top:214px">挨不着空格 · 点不动</div>`,
    icon: () => SVG_FRAME,
    tt: '挨着空格才能点',
    desc: '格子要<b>上下左右挨着空格</b>才点得动。<br>下面几排现在<em>点不动</em>，<br>把上面挖开，就够得着了。' },

  /* 下潜口径按案子「下潜示意」：有空格就潜，**直到某一行没有空格才停**（32 行只是服务端保险丝，不进玩家文案） */
  { rows: ['ebee', 'bbeb', 'bbbb'],
    mark: (r, c) => (r === 2 ? 'nogo' : (r === 1 && c === 2 ? 'dug' : '')),
    deco: `<div class="htp-tag cyan" style="left:118px;top:-52px">每潜一行 +10 米</div>
           <div class="htp-tag gold" style="left:48px;top:116px">有空格 → 潜</div>
           <div class="htp-tag" style="left:48px;top:208px">没空格 → 停</div>`,
    icon: () => SVG_DOWN,
    tt: '会一直往下潜',
    desc: '底行有空格 → 往下潜一行，<b>+10 米</b>。<br>新补的一行还有空格 → 接着潜。<br><em>直到有一行没有空格才停。</em>' }
];

/* 底部消耗一览：k = CELL_ART 键；n = 水母数；free 时显示绿字 */
const P1_COST = [
  ['b', '气泡', 1, '开出奖励'],
  ['x', '空气泡', 1, '打破没奖励'],
  ['s', '海藻', 1, '中心格不可点'],
  ['r', '石块', 2, '纯路障'],
  ['t', '宝箱', 0, '可连点 3~5 次']
];

function renderP1(st) {
  const COLX = [170, 730, 1290], COLY = 176;

  const cols = P1_SHOTS.map((s, i) => {
    const grid = g4(s.rows);
    return `<div class="htp-col" style="left:${COLX[i]}px;top:${COLY}px" data-name="分镜${i + 1}">
      <div class="htp-stage">
        ${boardHTML(grid, { x: 41, y: 0, cell: 82, gap: 8, mark: s.mark })}
        ${s.deco}
      </div>
      <div class="htp-cap"><div class="ic">${s.icon()}</div><div class="tt">${s.tt}</div></div>
      <div class="htp-desc"><div>${s.desc}</div></div>
    </div>`;
  }).join('');

  const arrows = [645, 1205].map((x) =>
    `<div class="htp-ar" style="left:${x}px;top:${COLY + 108}px">${SVG_ARROW}</div>`).join('');

  const costs = P1_COST.map(([k, nm, n, note]) => `
    <div class="it">
      ${img(CELL_ART[k], 54, 54)}
      <div class="nm">${nm}</div>
      <div class="vl${n === 0 ? ' free' : ''}">${n === 0 ? '免费'
        : img(IMG.jelly, 28, 28) + ' ×' + n}</div>
      <div class="nm" style="color:#8B98A4;font-size:20px">${note}</div>
    </div>`).join('');

  return `${cols}${arrows}
  <div class="htp-cost" data-name="消耗一览">
    <div class="hd"><span>点一格要花多少水母</span></div>
    <div class="row">${costs}</div>
  </div>`;
}

/* ================================================================ ②页
   2026-09-09：黑金三联「道具怎么用」
   口径（服务端 htreasuredive/rule.go + dive.go 通读）：
     · 落点 toolTargetOk = 空格 or 海藻三种格 —— 0909 用户定版：稿子按实装画，海藻也是合法落点
     · 炸弹 inBombRange = 3x3 再加上下左右各远一格 = 13 格，且只卷【气泡与石块】
     · 手电 ColumnCells = 整列通吃，宝箱剩余次数一次用完、有奖海藻的奖全领
     · 先算范围再扣费：范围内一格都消不掉 → ErrCodeTreasureDiveToolTargetInvalid，不扣道具
   ============================================================== */
const SVG_NO = `<svg width="76" height="76" viewBox="0 0 76 76" fill="none">
  <circle cx="38" cy="38" r="30" fill="rgba(20,0,0,.55)" stroke="#FF4D4D" stroke-width="7"/>
  <path d="M20 20 L56 56" stroke="#FF4D4D" stroke-width="8" stroke-linecap="round"/></svg>`;

/* 5 列 × 5 行，cell 62 / gap 6 / pad 13 → 360×360，居中于 460 的 col 里 x=50 */
const SVG_OK = `<svg width="76" height="76" viewBox="0 0 76 76" fill="none">
  <circle cx="38" cy="38" r="30" fill="rgba(0,24,8,.55)" stroke="#5FE07A" stroke-width="7"/>
  <path d="M22 39 L34 51 L55 26" stroke="#5FE07A" stroke-width="8"
        stroke-linecap="round" stroke-linejoin="round"/></svg>`;

const P2_CELL = 62, P2_STEP = 68, P2_BX = 50;
const p2xy = (r, c, size) => `left:${P2_BX + 13 + c * P2_STEP + (P2_CELL - size) / 2}px;` +
                             `top:${13 + r * P2_STEP + (P2_CELL - size) / 2}px`;
const p2corner = (r, c) => `left:${P2_BX + 13 + c * P2_STEP + P2_CELL - 32}px;` +
                           `top:${13 + r * P2_STEP - 13}px`;      // 角标：压格子右上角，不盖住道具
const g5 = (rows) => rows.map((l) => l.split('').map((ch) => P(ch)));
const inBomb = (dr, dc) => {
  dr = Math.abs(dr); dc = Math.abs(dc);
  if (dr <= 1 && dc <= 1) return true;
  return (dr === 2 && dc === 0) || (dr === 0 && dc === 2);
};

const P2_SHOTS = [
  { /* ① 炸弹 */
    rows: ['bbbbr', 'brbbb', 'bberb', 'bbrbb', 'rbbbb'],
    tgt: [2, 2],
    mark(r, c, cell) {
      if (r === 2 && c === 2) return 'pick';
      if (!inBomb(r - 2, c - 2)) return '';
      return (cell.t === 'b' || cell.t === 'r') ? 'hot' : '';
    },
    over: `${img(IMG.bomb, 54, 54, 'htp-tool', p2xy(2, 2, 54))}`,
    icon: () => img(IMG.bomb, 46, 46, '', 'display:inline-block'),
    tt: '炸弹 · 炸掉 13 格',
    desc: '以落点为中心 <b>3×3</b>，上下左右再远一格。<br>只炸<b>气泡和石块</b>，宝箱海藻不收。' },

  { /* ② 手电 */
    rows: ['bbbbr', 'bsssb', 'bscsb', 'bsssb', 'rbtbb'],
    tgt: [2, 2],
    mark(r, c) { return (r === 2 && c === 2) ? 'pick' : (c === 2 ? 'hot' : ''); },   // 落点=海藻中心格
    over: `${img(IMG.light, 54, 54, 'htp-tool', p2xy(2, 2, 54))}`,
    icon: () => img(IMG.light, 46, 46, '', 'display:inline-block'),
    tt: '手电 · 通吃整列',
    desc: '落点那一<b>整列从头清到尾</b>。<br>宝箱剩余次数一次用光，海藻的奖全领。' },

  { /* ③ 落点限制：空格与海藻可放，其余不行（0909 用户定版，与服务端 toolTargetOk 一致） */
    rows: ['bbbbr', 'bsssb', 'bscsb', 'bsssb', 'rbbbb'],
    tgt: null,
    mark(r, c) { return (r === 2 && c === 4) ? 'bad' : (r === 1 && c === 1 ? 'pick' : ''); },
    over: `${img(IMG.bomb, 54, 54, 'htp-tool', p2xy(1, 1, 54))}
           <div class="htp-ok" style="${p2corner(1, 1)}">${SVG_OK.replace('76', '46').replace('76', '46')}</div>
           ${img(IMG.bomb, 54, 54, 'htp-tool', p2xy(2, 4, 54) + ';opacity:.5')}
           <div class="htp-no" style="${p2xy(2, 4, 76)}">${SVG_NO}</div>
           <div class="htp-tag gold" style="left:34px;top:-52px">海藻上也放得下</div>`,
    icon: () => SVG_OK.replace('width="76" height="76"', 'width="46" height="46"'),
    tt: '只能放空格或海藻',
    desc: '落点只有<b>空格和海藻</b>放得下。<br>气泡、石块、宝箱都不行。<br>范围内没东西可消也<em>拒绝</em>，不白扣道具。' }
];

function renderP2(st) {
  const COLX = [170, 730, 1290], COLY = 158, STAGE = 366;

  const cols = P2_SHOTS.map((s, i) => `
    <div class="htp-col" style="left:${COLX[i]}px;top:${COLY}px" data-name="分镜${i + 1}">
      <div class="htp-stage" style="height:${STAGE}px">
        ${boardHTML(g5(s.rows), { x: P2_BX, y: 0, cell: P2_CELL, gap: 6, mark: s.mark })}
        ${s.over}
      </div>
      <div class="htp-cap" style="top:${STAGE + 14}px">
        <div class="ic">${s.icon()}</div><div class="tt">${s.tt}</div></div>
      <div class="htp-desc" style="top:${STAGE + 126}px;height:140px;padding:16px 18px;font-size:22px"><div>${s.desc}</div></div>
    </div>`).join('');

  const arrows = [645, 1205].map((x) =>
    `<div class="htp-ar" style="left:${x}px;top:${COLY + 140}px">${SVG_ARROW}</div>`).join('');

  return `${cols}${arrows}
  <div class="htp-legend" data-name="图例">
    <span><i class="sw pick"></i>落点（空格或海藻）</span>
    <span><i class="sw hot"></i>这次会被清掉的格子</span>
    <span><b>道具从哪来</b>：气泡里开出 / 商店买</span>
    <span><em>用一次扣 1 个</em></span>
  </div>`;
}

/* ================================================================ ③页
   2026-09-09 换版式：黑金三联「海螺换奖 + 深度奖励」
   ① 海螺从哪来（气泡 / 宝箱 / 海藻三个来源，宝箱不花水母）
   ② 拿海螺换奖（2116 group58 共 17 位；金 = 稀有位 / 银 = 常规位，各有限购）
   ③ 潜得越深奖越大（2115 group10003 共 11 档 300→12000m，终档 = 节日装饰 ×13）
   底部横贯一条 11 档深度阶梯，点任意一档可切「已达成 / 下一档 / 未达成」三态
   ============================================================== */
const P3_SRC = [
  { k: 'b', lb: '气泡',  sub: '1 只水母',  out: ['g', 's'] },
  { k: 't', lb: '宝箱',  sub: '不花水母',  out: ['g'] },
  { k: 's', lb: '海藻',  sub: '1 只水母',  out: ['g', 's'] }
];
/* 深度轨只画「有档位、越深越厚」这件事 —— 奖励内容不进教学页（用户 0909 口径：
   功能介绍别本末倒置，玩家先玩懂；每档具体给什么去活动界面的深度轨上看） */
const P3_RAIL = [[12000, 1], [6000, 0], [3600, 0], [300, 0]];

function renderP3(st) {
  const COLX = [170, 730, 1290], COLY = 150, STAGE = 330;

  /* —— 分镜① 海螺从哪来 —— */
  const srcs = P3_SRC.map((o, i) => `
    <div class="htp-src" style="left:${41 + i * 126}px;top:40px" data-name="来源_${o.lb}">
      <div style="margin:0 auto;width:82px;height:82px">${cellHTML(P(o.k), '', 82)}</div>
      <div style="margin:8px auto 0;width:46px">${SVG_DOWN}</div>
      <div class="out">${o.out.map((c) => img(c === 'g' ? IMG.gold : IMG.silver, 56, 56)).join('')}</div>
      <div class="lb">${o.lb}<small>${o.sub}</small></div>
    </div>`).join('');

  /* —— 分镜② 拿海螺换奖：只讲功能「去兑换商店换奖励」，不列货位（0909 用户口径）—— */
  const shop = `
    <div class="out" style="position:absolute;left:0;top:28px;width:460px;gap:22px"
         data-name="两种海螺">
      ${img(IMG.gold, 88, 88)}${img(IMG.silver, 88, 88)}
    </div>
    <div style="position:absolute;left:207px;top:126px;width:46px">${SVG_DOWN}</div>
    <div style="position:absolute;left:130px;top:182px;width:200px;text-align:center"
         data-name="兑换商店入口">
      ${img(IMG.shop, 200, 183, '', 'margin:0 auto;border-radius:10px')}
    </div>
    <div class="htp-tag gold" style="left:302px;top:196px">主界面右上角 ↗</div>`;

  /* —— 分镜③ 潜得越深奖越大 —— */
  const rail = `<div class="htp-rail" style="top:14px" data-name="深度轨">
    <div class="ln"></div>
    ${P3_RAIL.map(([m, top]) => {
      const got = st.depth >= m;
      return `<div class="nd${top ? ' top' : ''}${got ? ' got' : ''}" data-tier="${m}"
                   data-name="深度档_${m}m">
        <div class="m">${m}<small> 米</small></div><div class="pt"></div>
        <div class="ic">${img(IMG.chest, 48, 48)}</div>
        <div class="rw">${got ? '可领取' : (top ? '最终大奖' : '未达成')}</div>
      </div>`;
    }).join('')}
    <div style="position:absolute;left:156px;top:306px;font-size:20px;color:#8B98A4">一共 11 档，越深越厚</div>
  </div>`;

  const SHOTS = [
    { body: srcs, icon: img(IMG.gold, 46, 46, '', 'display:inline-block'), tt: '海螺从哪来',
      desc: '气泡、宝箱、海藻都能开出<b>金 / 银海螺</b>。<br>宝箱不花水母，刷到就是白赚。' },
    { body: shop, icon: img(IMG.shop, 50, 46, '', 'display:inline-block'), tt: '拿海螺换奖',
      desc: '攒到的<b>金 / 银海螺</b>，去主界面右上角的<br><b>兑换商店</b>换奖励。<br>换什么、什么价，进商店看。' },
    { body: rail, icon: SVG_DOWN, tt: '潜得越深奖越大',
      desc: '深度<b>只增不减</b>，到档就能领。<br>一共 <b>11 档</b>，<b>12000 米</b>拿最终大奖。<br>理论最深 18000 米。' }
  ];
  const cols = SHOTS.map((s, i) => `
    <div class="htp-col" style="left:${COLX[i]}px;top:${COLY}px" data-name="分镜${i + 1}">
      <div class="htp-stage" style="height:${STAGE}px">${s.body}</div>
      <div class="htp-cap" style="top:${STAGE + 14}px">
        <div class="ic">${s.icon}</div><div class="tt">${s.tt}</div></div>
      <div class="htp-desc" style="top:${STAGE + 140}px;height:136px;padding:14px 18px;font-size:22px">
        <div>${s.desc}</div></div>
    </div>`).join('');

  const arrows = [645, 1205].map((x) =>
    `<div class="htp-ar" style="left:${x}px;top:${COLY + 122}px">${SVG_ARROW}</div>`).join('');

  return `${cols}${arrows}
  <div class="htp-legend" data-name="图例">
    <span>深度<b>只增不减</b>，挖多深算多深</span>
    <span>到档<b>就能领</b>，不用抢</span>
    <span><b>12000 米</b>拿最终大奖</span>
    <span>奖励挂在<em>盘面左侧竖轨</em>，点开看</span>
  </div>`;
}

/* ---------------------------------------------------------------- 单屏壳 */
/* ---------------------------------------------------------------- ①页黑金外壳 */
function screenHTMLDark(st) {
  const dots = [0, 1, 2].map((i) =>
    `<div class="dot${i === st.page ? ' on' : ''}" data-page="${i}"></div>`).join('');
  return `
  <div class="htp-dim"></div>
  <div class="htp-bar" data-name="标题条"><span>HOW TO PLAY</span></div>
  <div class="htp-x" data-act="close" data-name="关闭">✕</div>
  <div class="htp-nav l${st.page === 0 ? ' off' : ''}"${st.page === 0 ? '' : ' data-act="prev"'}
       data-name="上一页">‹</div>
  <div class="htp-nav r${st.page === 2 ? ' off' : ''}"${st.page === 2 ? '' : ' data-act="next"'}
       data-name="下一页">›</div>
  <div class="htp-well" data-layer="内容井" data-name="内容井"></div>
  <div class="htp-dots">${dots}</div>`;
}
function renderScreen(scr) {
  const st = scr.__st;
  scr.innerHTML = screenHTMLDark(st);          // 三页统一黑金 HOW TO PLAY 壳
  scr.querySelector('.htp-well').innerHTML =
    st.page === 0 ? renderP1(st) : st.page === 1 ? renderP2(st) : renderP3(st);
  bind(scr);
}

/* ---------------------------------------------------------------- 交互 */
function bind(scr) {
  const st = scr.__st;
  scr.querySelectorAll('.dot').forEach((d) => { d.onclick = () => { st.page = +d.dataset.page; renderScreen(scr); }; });
  const nx = scr.querySelector('[data-act="next"]'), pv = scr.querySelector('[data-act="prev"]');
  if (nx) nx.onclick = () => { st.page = (st.page + 1) % 3; renderScreen(scr); };
  if (pv) pv.onclick = () => { if (st.page > 0) { st.page -= 1; renderScreen(scr); } };
  const xd = scr.querySelector('[data-act="close"]');
  if (xd) xd.onclick = () => {                  // 关掉 = 回主界面；稿子里给个「再看一次」把弹窗叫回来
    scr.querySelectorAll('.htp-well,.htp-bar,.htp-nav,.htp-dots,.htp-x').forEach((n) => { n.style.display = 'none'; });
    const back = el(`<div class="htp-tag gold" data-name="再看一次"
      style="left:832px;top:498px;font-size:30px;padding:14px 30px;cursor:pointer;z-index:9">再看一次</div>`);
    back.onclick = () => renderScreen(scr);
    scr.appendChild(back);
  };
  if (st.page === 2) scr.querySelectorAll('[data-tier]').forEach((n) => {
    n.onclick = () => {                         // 点一档 = 假装潜到这个深度，看「未达成 / 可领取」两种态
      st.depth = +n.dataset.tier;
      renderScreen(scr);
    };
  });
}

/* ---------------------------------------------------------------- 标注 */
const NOTES = [
  { h: '①页「怎么下潜」— 交互与判定',
    li: ['<b>触发时机</b>：活动首次进入自动弹出，一期只弹一次（客户端本地标记）；之后点界面左下角 <b>ⓘ</b> 重新打开',
         '<b>版式</b>：整屏 1920×1080 黑底 + 金色 HOW TO PLAY 横幅、左右圆钮翻页、底部页码点；三页同一个壳，只换中间三联分镜',
         '<b>可挖判定</b>：仅「上下左右挨着空格」的格子可点 —— 教学图必须画出「够得着 / 够不着」的对比，否则玩家会以为随便点',
         '<em>⚠ 文案别用「通路 / 绕开」</em>（0909 用户实测看不懂）：说人话 = 「挨不着空格就点不动，把上面挖开就够得着了」',
         '<b>下潜判定</b>：<b>最下一行出现空格</b>即下潜一行（+10 米），新补的一行若又含空格就继续 —— <b>玩家侧口径 = 「一直潜到某一行没有空格才停」</b>（照案子的「下潜示意」写，别说成「挖穿一行才下潜」）',
         '<span class="cfg">单次最多连潜 32 行（服务端 MaxDivePerAction 保险丝）—— 是兜底不是规则，不进玩家文案</span>',
         '<b>深度口径</b>：depth = 顶行行号 × 10，客户端自乘、服务端不落库；深度只增不减',
         '<em>三联是静态示意</em>：实装每联可各自 K 一小段循环动画（点破一格 / 通路高亮 / 整盘上移），别摆一张死图',
         '<span class="cfg">棋盘 6 列 × 8 行、10 米/行、32 行上限都写死在服务端；刷新权重在 2121·212140056</span>'] },
  { h: '②页「道具怎么用」— 规则硬约束',
    li: ['水母消耗按 2189 <b>A_ARR_cost</b> 给定：气泡 / 空气泡 / 海藻 1 只、石块 2 只、<b>宝箱 0</b>（刷到就是白赚）',
         '<b>炸弹 = 13 格</b>：九宫格再加上下左右各远一格；<b>只卷气泡与石块</b>，宝箱 / 海藻不吃',
         '<b>手电筒 = 整列通吃</b>：宝箱剩余次数一次用完、有奖海藻的奖全领，代价是只能沿一列',
         '两者<b>落点必须是空格或海藻格</b>（0909 定版：稿子按实装 <span class="cfg">toolTargetOk</span> 画，海藻是合法落点），先算范围再扣费 —— 范围内没有可清的格子就直接拒绝，道具不扣',
         '宝箱可点 <b>3~5 次</b>随机（2189 status <span class="cfg">click_num arg2=[3,5]</span>），每次各抽一份奖励',
         '海藻 <b>3×3 一片</b>：<b>中心格不可打破</b>，数字 = 周围 8 格里有奖的个数 ⇒ 可点的是 <b>8 格</b>不是 9 格；屏幕同时最多一片',
         '<b>示意口径</b>：金框 = 落点、红框 = 这次会被清掉的格子；炸弹那联 12 红 + 1 金 = 13 格，手电那联画的是 5 行示意（实装整列 8 行）',
         '<em>待程序确认：工具清出来的空格是否触发下潜</em>（数值 v12 按「触发」算，两种口径通顶差约 $50）',
         '<span class="cfg">中心格与工具图标此稿借现网切图占位，等 1511000093-097 正式图标</span>'] },
  { h: '③页「海螺换奖 + 深度奖励」— 版式与数据来源',
    li: ['<b>三联</b>：① 海螺从哪来（气泡 / 宝箱 / 海藻）→ ② 去兑换商店换奖励 → ③ 潜得越深奖越大；底部一条功能口径横条',
         '<em>⛔ 这页不列奖励详情</em>（用户 0909 口径：功能介绍别本末倒置，这页只为让玩家玩懂）—— 货位清单与每档奖励内容都不上教学页，玩家去活动界面自己看',
         '②联<b>只讲「去兑换商店换奖励」这个功能</b>，不列货位（用户 0909 口径：教学页是功能介绍，货架进商店自己看）',
         '货位实配在 2116 <b>group58 共 17 位</b>：<b>金海螺</b>换稀有位 / <b>银海螺</b>换常规位（v12 起 5 位改银），每位有限购 —— 这些只写在标注里，不进教学页',
         '深度奖励 = 2115 <b>group10003</b>，11 档 300 → 12000 米，计数走 fin_cond <span class=\"cfg\">cat=10149044</span>',
         '<em>⛔ 这 11 条深度任务不要补 arg.ids</em>：服务端正是不带 ID 投递才命中，补了进度会静默不动、也没有报错',
         '<b>12000 米终档</b> = 节日装饰 ×13（最终大奖外显，教学页只说「最终大奖」不写内容）；理论最深 <b>18000 米</b> = 1800 行 × 10 米',
         '①联特意标了<b>宝箱不花水母</b> —— 它是免费玩家唯一稳定的金海螺来源，教学里别漏',
         '③联深度轨在稿子里点一档 = 切「未达成 / 可领取」，给 GUI 看两种态；奖励格用通用宝箱图占位，实装按 2115 各档真实奖励出图',
         '<span class=\"cfg\">奖励现为「王庭君主」装饰占位，待 12 月节装饰件替换；v12 数值拟并为 10 档，若并档这页与阶梯要同步改</span>']
  }
];

/* ---------------------------------------------------------------- 组板 */
const X = [90, 2150, 4210], TOP = 300;
const initState = (i) => ({ page: i, depth: 120 });   // depth 只给③页阶梯的三态演示用

function build() {
  const cv = document.getElementById('canvas');
  // ?only=N 只出第 N 屏（1920×1080 裸屏），给截图脚本用
  const only = new URLSearchParams(location.search).get('only');
  if (only) {
    const i = Math.max(0, Math.min(2, (+only) - 1));
    cv.style.width = '1920px'; cv.style.height = '1080px'; cv.innerHTML = '';
    const s = el(`<div class="screen" data-layer="第${i + 1}页"
      style="left:0;top:0;width:1920px;height:1080px"></div>`);
    const ctl = document.getElementById('ctl'); if (ctl) ctl.style.display = 'none';
    s.__st = initState(i); cv.appendChild(s); renderScreen(s); audit(); return;
  }
  cv.innerHTML = `
    <div class="bd-title" data-name="板标题"><div class="bar"></div>
      <div class="txt">深海探宝 · 开局玩法介绍（三联）</div></div>
    <div class="bd-sub">活动开始时自动弹出的三页教学：<b>怎么下潜 → 道具怎么用 → 海螺换奖与深度奖励</b>。
      版式照竞品 HOW TO PLAY 弹窗：每页三联分镜 + 一条底部横条。
      翻页钮 / 页码点 / ③页深度阶梯（点一档看三态）都能点。</div>
    <div class="bd-meta">2112 = <b>21129575</b> · 12 月节<br>
      画布 1920×1080 / 屏 · 甲式流程板<br>切图：0901 真机截图<br>版式：竞品 HOW TO PLAY 弹窗</div>
    ${[0, 1, 2].map((i) => `<div class="scr-cap" style="left:${X[i]}px;top:236px">
        ${i + 1}页 · ${PAGES[i]}<span>${SUBCAP[i]}</span></div>`).join('')}
    ${[0, 1].map((i) => `<div class="flowar" style="left:${X[i] + 1964}px;top:${TOP + 510}px"></div>`).join('')}
    ${NOTES.map((n, i) => `<div class="note" data-layer="标注_${i + 1}页" data-note="1"
        style="left:${X[i]}px;top:${TOP + 1126}px">
        <h4>${n.h}</h4><ul>${n.li.map((s) => `<li>${s}</li>`).join('')}</ul></div>`).join('')}`;

  [0, 1, 2].forEach((i) => {
    const scr = el(`<div class="screen" data-layer="第${i + 1}页" data-name="第${i + 1}页_${PAGES[i]}"
      style="left:${X[i]}px;top:${TOP}px;width:1920px;height:1080px"></div>`);
    scr.__st = initState(i);
    cv.appendChild(scr);
    renderScreen(scr);
  });

  audit();
}

/* ---------------------------------------------------------------- 自检 */
// 把「每屏像素 + 元素越界 + 文字被裁」打进隐藏 <pre>，交给 check_sizes.py 断言 —— 不靠肉眼对齐
// 换黑金版式后不再查「弹窗内容井」，改查「有没有元素跑出 1920×1080」——
// 分镜的 cap / desc 是绝对定位挂在 stage 下面的，按父盒高度算溢出全是假警报。
function audit() {
  const lines = [];
  document.querySelectorAll('.screen').forEach((s, i) => {
    lines.push(`screen${i + 1}=${s.offsetWidth}x${s.offsetHeight}`);
    const sb = s.getBoundingClientRect();
    s.querySelectorAll('.htp-well *').forEach((n) => {
      if (!n.offsetWidth && !n.offsetHeight) return;
      const r = n.getBoundingClientRect();
      const l = Math.round(r.left - sb.left), t = Math.round(r.top - sb.top);
      const rr = Math.round(l + r.width), bb = Math.round(t + r.height);
      if (l < -2 || t < -2 || rr > 1922 || bb > 1082) {
        lines.push(`OUTSIDE screen${i + 1} <${n.className || n.tagName}> ` +
                   `l=${l} t=${t} r=${rr} b=${bb} (screen 1920x1080)`);
      }
      if (getComputedStyle(n).overflow !== 'visible' &&
          (n.scrollHeight > n.offsetHeight + 2 || n.scrollWidth > n.offsetWidth + 2)) {
        lines.push(`CLIP screen${i + 1} <${n.className || n.tagName}> ` +
                   `box=${n.offsetWidth}x${n.offsetHeight} content=${n.scrollWidth}x${n.scrollHeight}`);
      }
    });
  });
  const probe = document.createElement('pre');
  probe.id = '__assert';
  probe.style.display = 'none';
  probe.textContent = lines.join('\n');
  document.body.appendChild(probe);
}

/* ---------------------------------------------------------------- 自动交互测试 */
// intro3.html?autotest → 脚本自己点一遍 + 按版式逐项数数，把结果写进探针；靠断言不靠肉眼
function autotest() {
  const log = [];
  window.onerror = (m) => log.push('JSERR ' + m);
  const S = [...document.querySelectorAll('.screen')];
  const eq = (tag, got, want) => log.push(`TEST ${tag}=${got} want=${want}${got === want ? '' : ' ✗'}`);

  // 版式：每屏 3 联 + 各自的底部横条
  S.forEach((s, i) => eq(`p${i + 1}.cols`, s.querySelectorAll('.htp-col').length, 3));
  eq('p1.cost', S[0].querySelectorAll('.htp-cost .it').length, 5);        // 5 类格子消耗
  eq('p1.nogo', S[0].querySelectorAll('.cell.nogo').length, 4 + 4);       // ②联够不到那行 + ③联满的那行
  eq('p1.dug', S[0].querySelectorAll('.cell.dug').length, 1);             // ③联指着的那个空格
  eq('p2.legend', S[1].querySelectorAll('.htp-legend span').length, 4);
  eq('p3.legend', S[2].querySelectorAll('.htp-legend span').length, 4);
  eq('p3.rail', S[2].querySelectorAll('.htp-rail .nd').length, 4);        // 只示意 4 档，不列清单

  // ②页范围：炸弹 12 红 + 1 金 = 13 格；手电整列 5 格；③联落点一可一不可
  eq('p2.hot', S[1].querySelectorAll('.cell.hot').length, 12 + 4);
  eq('p2.pick', S[1].querySelectorAll('.cell.pick').length, 3);
  eq('p2.bad', S[1].querySelectorAll('.cell.bad').length, 1);
  eq('p2.ok/no', S[1].querySelectorAll('.htp-ok, .htp-no').length, 2);

  // ③页深度轨两态：点 3600 → 3600 与 300 变「可领取」
  const s3 = S[2];
  s3.querySelector('[data-tier="3600"]').click();
  eq('p3.got', s3.querySelectorAll('.htp-rail .nd.got').length, 2);
  log.push(`TEST p3.depth=${s3.__st.depth}`);

  // 翻页：任意屏点页码点都能换页
  s3.querySelectorAll('.htp-dots .dot')[0].click();
  eq('p3.pageAfterDot', s3.__st.page, 0);
  eq('p3.colsAfterDot', s3.querySelectorAll('.htp-col').length, 3);

  document.getElementById('__assert').textContent += '\n' + log.join('\n');
}

function ctl() {
  const cv = document.getElementById('canvas');
  const fit = (k) => {
    cv.style.transformOrigin = '0 0';
    cv.style.transform = `scale(${k})`;
    document.body.style.width = (6220 * k) + 'px';
    document.body.style.height = (1940 * k) + 'px';
  };
  const b = (id, fn) => { const n = document.getElementById(id); if (n) n.onclick = fn; };
  b('c-fit', () => fit((window.innerWidth - 30) / 6220));
  b('c-100', () => fit(1));
  b('c-reset', () => document.querySelectorAll('.screen').forEach((s, i) => {
    s.__st = initState(i); renderScreen(s);
  }));
}

build();
ctl();
if (location.search.indexOf('autotest') >= 0) autotest();
