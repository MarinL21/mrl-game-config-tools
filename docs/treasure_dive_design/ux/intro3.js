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
const IMG = {
  scene:    A + 'td/UI_场景全屏.jpg',   // 背景烘成 JPEG：单文件 bundle 里要内联 3 次
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
const COST = { b: 1, x: 1, s: 1, r: 2, t: 0 };          // c 中心格 / e 空格 不可点
const PAGES = ['怎么下潜', '道具怎么用', '海螺换奖 + 深度奖励'];
const SUBCAP = ['点击 → 挖穿一行 → 下潜 10 米', '水母 / 炸弹 / 手电 + 5 类格子', '17 个货位 + 11 档深度'];

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

/* ---------------------------------------------------------------- 演示盘 */
const P = (t, n) => (n == null ? { t } : { t, n });
function freshGrid() {
  const rows = ['eeeeee', 'eeeeee', 'eeeeee', 'bbrbbb', 'bbbsss', 'xbbscs', 'brbsss', 'bbtbbb']
    .map((line) => line.split('').map((ch) => P(ch)));
  rows[5][4] = P('c', 5);     // 海藻中心格：数字 = 周围 8 格里有奖的个数
  rows[7][2] = P('t', 4);     // 宝箱：可点 3~5 次
  return rows;
}
const POOL = 'bbbbbbbbbbbxxxxrrreet'.split('');
const newRow = () => Array.from({ length: 6 }, () => {
  const t = POOL[(Math.random() * POOL.length) | 0];
  return t === 't' ? P(t, 3 + ((Math.random() * 3) | 0)) : P(t);
});
const DROPS = [['+高级资源箱', 26], ['+普通奖池抽奖券', 14], ['+高级探测券', 10], ['+英雄升星石·橙', 8],
               ['+金海螺 ×1', 9], ['+银海螺 ×10', 13], ['+水母 ×3', 10], ['+炸弹 ×1', 5], ['+手电筒 ×1', 5]];
function rollDrop() {
  let k = Math.random() * DROPS.reduce((a, d) => a + d[1], 0);
  for (const d of DROPS) { k -= d[1]; if (k <= 0) return d[0]; }
  return DROPS[0][0];
}

/* ================================================================ ①页 */
const P1_RULES = [
  ['点一下 = 花水母', '气泡 / 空气泡 / 海藻各 <b>1 只</b>，石块 <b>2 只</b>，宝箱 <b>免费</b>'],
  ['只能挖「通路」', '格子要<b>上下左右紧贴空格</b>才点得动，够不到的先绕开'],
  ['挖穿最下一行 = 下潜', '底行只要出现空格，棋盘立刻<b>下潜一行</b>，深度 <b>+10 米</b>'],
  ['会连锁往下掉', '新补的一行若又带空格，<i>接着往下潜</i>，一次最多 32 行'],
  ['深度只增不减', '整期累计，越深档位越高，<b>12000 米</b>拿最终大奖']
];
function renderP1(st) {
  const grid = st.grid;
  const canDig = (r, c) => COST[grid[r][c].t] != null &&
    [[1, 0], [-1, 0], [0, 1], [0, -1]].some(([dr, dc]) =>
      grid[r + dr] && grid[r + dr][c + dc] && grid[r + dr][c + dc].t === 'e');

  return `
  <div class="well-h" data-name="页标题">① 怎么下潜<small>点气泡 → 挖穿最下一行 → 棋盘往下潜 10 米</small></div>
  <div class="rule-line"></div>
  <div class="chip" data-name="资源_水母" style="left:34px;top:100px">
    ${img(IMG.jelly, 44, 44)}<span class="k">水母</span><span class="v">${st.jelly}</span></div>
  <div class="chip" data-name="读数_深度" style="left:236px;top:100px">
    <span class="k" style="margin-left:10px">当前深度</span><span class="v">${st.depth}</span><span class="k">米</span></div>
  ${boardHTML(grid, { x: 34, y: 172, cell: 58, mark: (r, c) => (canDig(r, c) ? 'pick' : '') })}
  <div class="board-lbl" style="left:34px;top:706px">▲ 金框 = 现在点得动的格子 · <b>本稿可直接点着试</b></div>
  <div class="rules" style="${box(456, 104, 972, 460)}" data-name="规则条目">
    ${P1_RULES.map((it, i) => `<div class="ri"><div class="n">${i + 1}</div>
       <h5>${it[0]}</h5><p>${it[1]}</p></div>`).join('')}
  </div>
  <div class="side" style="${box(456, 578, 972, 132)}" data-name="下潜示意">
    <h6 style="margin:14px 0 4px 20px">下潜一次的完整过程</h6>
    <div style="position:absolute;left:20px;top:64px;display:flex;align-items:center;gap:16px;
                font-size:24px;color:#CBE6F2;white-space:nowrap">
      <span>挖开底行任意一格</span><span style="color:#4FE3F5;font-size:28px">➜</span>
      <span>整盘上移一行</span><span style="color:#4FE3F5;font-size:28px">➜</span>
      <span style="color:#FFC94A;font-weight:700">深度 +10 米</span><span style="color:#4FE3F5;font-size:28px">➜</span>
      <span>底部补一行新格子</span>
    </div>
  </div>`;
}

/* ================================================================ ②页 */
const TOOLS = [
  { k: 'jelly', name: '水母', icon: IMG.jelly, cost: '挖掘消耗品 · 礼包 / 盘面产出',
    cap: '水母：只清点中的那 1 格',
    note: ['气泡 · 空气泡 · 海藻：每格 1 只', '石块 2 只 · 宝箱不花水母',
           '空格与海藻中心格点不动，也不扣'], warn: '' },
  { k: 'bomb', name: '炸弹', icon: IMG.bomb, cost: '消耗 1 个 · 礼包 / 气泡掉落',
    cap: '炸弹：一次 13 格（九宫格 + 十字各远一格）',
    note: ['只卷气泡与石块，宝箱 / 海藻不吃', '落点必须是空格或海藻格',
           '先算范围再扣费：范围里没有可清的格子就用不掉，道具不扣'],
    warn: '斜角外圈那 4 格（±2,±1）不在范围内' },
  { k: 'light', name: '手电筒', icon: IMG.light, cost: '消耗 1 个 · 礼包 / 气泡掉落',
    cap: '手电筒：沿一列整列通吃（本列 8 格）',
    note: ['宝箱剩余次数一次用完、有奖海藻的奖全领', '落点必须是空格或海藻格',
           '范围最大但只能沿一列，拿来挖通深井最划算'], warn: '' }
];
const KINDS = [
  { k: 'b', name: '有奖气泡', art: CELL_ART.b, desc: '1 只水母<br>出海螺 / 道具',
    cap: '有奖气泡：破开直接拿奖励',
    note: ['奖励内容看得见，值不值得点由玩家自己判断', '盘面上最常见的一类格子'], warn: '' },
  { k: 'x', name: '空气泡', art: CELL_ART.x, desc: '1 只水母<br>没奖励，只为打路',
    cap: '空气泡：花 1 只水母打通道',
    note: ['敲开没有任何奖励，作用是把通路挖通', '开局倒数第二排整排都是空气泡'], warn: '' },
  { k: 'r', name: '石块', art: CELL_ART.r, desc: '2 只水母<br>盘面最贵的一格',
    cap: '石块：2 只水母，盘面上最贵的一格',
    note: ['能绕开就绕开，绕不开才砸', '炸弹和手电筒都能清掉它'], warn: '' },
  { k: 't', name: '宝箱', art: CELL_ART.t, desc: '不花水母<br>可点 3~5 次',
    cap: '宝箱：免费连点 3~5 次',
    note: ['不消耗水母，刷到就是白赚', '每点一次给一份奖励，点满次数箱子才消失',
           '手电筒扫到它，会把剩余次数一次用完'], warn: '' },
  { k: 's', name: '海藻', art: CELL_ART.s, desc: '3×3 一整片<br>中心格不可破',
    cap: '海藻：3×3 一片，可点的是外围 8 格',
    note: ['中心格打不破，上面的数字 = 周围 8 格里有奖的个数', '外围 8 格每格 1 只水母',
           '屏幕上同时最多出现一片海藻'], warn: '中心格不算奖励格，别按 9 格算收益' }
];
const CENTER = [3, 3];
function rangeGrid(kind) {          // 6 列 × 8 行 = 实装盘面尺寸
  const g = Array.from({ length: 8 }, () => Array.from({ length: 6 }, () => P('b')));
  g[0][1] = P('r'); g[1][4] = P('r'); g[5][0] = P('x'); g[6][3] = P('x');
  g[7][5] = P('t', 3); g[2][1] = P('e'); g[6][1] = P('e');
  if (kind === 's') {
    for (let r = 2; r <= 4; r++) for (let c = 2; c <= 4; c++) g[r][c] = P('s');
    g[3][3] = P('c', 5);
  }
  if (kind === 'x') g[3][3] = P('x');
  if (kind === 'r') g[3][3] = P('r');
  if (kind === 't') g[3][3] = P('t', 4);
  return g;
}
function hotSet(sel) {
  const [R, C] = CENTER, out = {};
  const put = (r, c) => { if (r >= 0 && r < 8 && c >= 0 && c < 6) out[r + ',' + c] = 1; };
  if (sel === 'bomb') {
    for (let dr = -1; dr <= 1; dr++) for (let dc = -1; dc <= 1; dc++) put(R + dr, C + dc);
    put(R - 2, C); put(R + 2, C); put(R, C - 2); put(R, C + 2);
  } else if (sel === 'light') {
    for (let r = 0; r < 8; r++) put(r, C);
  } else if (sel === 's') {
    for (let r = 2; r <= 4; r++) for (let c = 2; c <= 4; c++) if (!(r === 3 && c === 3)) put(r, c);
  } else put(R, C);
  return out;
}
function renderP2(st) {
  const sel = st.sel;
  const cur = TOOLS.find((t) => t.k === sel) || KINDS.find((c) => c.k === sel);
  const hot = hotSet(sel);
  const nHot = Object.keys(hot).length;

  const toolCards = TOOLS.map((t, i) => `
    <div class="card tool${sel === t.k ? ' on' : ''}" data-sel="${t.k}" data-name="道具卡_${t.name}"
         style="${box(34, 104 + i * 146, 552, 136)}">
      <div class="ic">${img(t.icon, 104, 104)}</div>
      <h5>${t.name}</h5><div class="cost" style="width:390px">${t.cost}</div>
      <div class="pin">${sel === t.k ? '● 正在看' : '点我看范围'}</div>
    </div>`).join('');

  const kindCards = KINDS.map((c, i) => `
    <div class="card kind${sel === c.k ? ' on' : ''}" data-sel="${c.k}" data-name="格子卡_${c.name}"
         style="${box(34 + i * 281, 574, 270, 108)}">
      <div class="ic">${img(c.art, 66, 66)}</div>
      <h6>${c.name}</h6><p>${c.desc}</p>
    </div>`).join('');

  return `
  <div class="well-h" data-name="页标题">② 道具怎么用<small>点左边任意一项，中间盘面会亮出它的作用范围</small></div>
  <div class="rule-line"></div>
  ${toolCards}
  ${boardHTML(rangeGrid(sel), { x: 620, y: 104, cell: 46, mark: (r, c) => (hot[r + ',' + c] ? 'hot' : '') })}
  <div class="board-lbl" style="left:620px;top:542px">红框 = 本次作用范围（<b>${nHot} 格</b>）· 盘面即实装尺寸 6 列 × 8 行</div>
  <div class="side" style="${box(1010, 104, 418, 429)}" data-name="规则说明">
    <h6>${cur.cap}</h6>
    <ul>${cur.note.map((s) => `<li>${s}</li>`).join('')}</ul>
    ${cur.warn ? `<div class="warn">⛔ ${cur.warn}</div>` : ''}
    <div style="position:absolute;left:20px;bottom:14px;width:378px" data-name="工具钮位置">
      <div style="display:flex;gap:12px">
        ${img(IMG.btnBomb, 178, 80, '', 'border-radius:8px')}
        ${img(IMG.btnLight, 178, 80, '', 'border-radius:8px')}
      </div>
      <div style="font-size:20px;color:#7FA8BC;line-height:1.35;margin-top:6px">
        ↑ 两个工具钮在主界面盘面右下角，数量为 0 时置灰、点了跳礼包</div>
    </div>
  </div>
  <div class="board-lbl" style="left:34px;top:542px">盘面上会遇到的 5 类格子（也可以点）</div>
  ${kindCards}`;
}

/* ================================================================ ③页 */
const SHELF = [
  { nm: '水母 ×5', pr: 1, cur: 'g', lim: 5, art: IMG.jelly },
  { nm: '四周年庆-白色保底卡包 ×1', pr: 1, cur: 'g', lim: 10, art: null },
  { nm: '万能英雄碎片-橙色 ×1', pr: 4, cur: 'g', lim: 10, art: null },
  { nm: '装饰券 ×5', pr: 10, cur: 's', lim: 20, art: IMG.decor },
  { nm: '60 分钟加速 ×1', pr: 10, cur: 's', lim: 30, art: null }
];
const TIERS = [
  [300, '自选宝箱 ×1', 'chest'], [600, '节日装饰 ×1', 'decor'], [1200, '自选宝箱 ×3', 'chest'],
  [1800, '装饰升级 ×1', 'decor'], [2400, '装饰升级 ×2', 'decor'], [3000, '装饰升级 ×3', 'decor'],
  [3600, '装饰升级 ×6', 'decor'], [4800, '涂饰道具 ×7', null], [6000, '装饰升级 ×8', 'decor'],
  [9000, '涂饰道具 ×7', null], [12000, '节日装饰 ×13', 'decor']
];
function renderP3(st) {
  const rows = SHELF.map((s) => `
    <div class="srow" data-name="货位_${s.nm}">
      <div class="s">${s.art ? img(s.art, 60, 60) : ph('道具<br>图标', 15)}</div>
      <div class="nm">${s.nm}</div><div class="lm">限购 ${s.lim} 次 · 活动内累计</div>
      <div class="pr${s.cur === 's' ? ' silver' : ''}">
        ${img(s.cur === 'g' ? IMG.gold : IMG.silver, 36, 36)}<b>${s.pr}</b></div>
    </div>`).join('');

  const tiers = TIERS.map((t) => {
    const state = st.depth >= t[0] ? 'done' : (t[0] === st.next ? 'now' : 'lock');
    const art = t[2] === 'chest' ? IMG.chest : (t[2] === 'decor' ? IMG.decor : null);
    const last = t[0] === 12000;
    return `<div class="tier ${state}" data-tier="${t[0]}" data-name="深度档_${t[0]}m">
      <div class="ln"></div><div class="pt"></div>
      <div class="m">${t[0]}<span> 米</span></div>
      <div class="sl">${art ? img(art, 46, 46) : ph('图标', 14)}</div>
      <div class="rw">${t[1]}</div>
      <div class="st"${last ? ' style="color:#FFC94A"' : ''}>${last ? '最终大奖'
        : state === 'done' ? '已达成' : state === 'now' ? '下一档' : '未达成'}</div>
    </div>`;
  }).join('');

  return `
  <div class="well-h" data-name="页标题">③ 海螺换奖 + 深度奖励<small>挖出来的海螺去商店换，潜下去的深度按档发奖</small></div>
  <div class="rule-line"></div>

  <div class="side" style="${box(34, 104, 700, 124)}" data-name="双币说明">
    <div style="position:absolute;left:18px;top:12px;display:flex;align-items:center;gap:12px">
      ${img(IMG.gold, 80, 80)}
      <div><div style="font-size:29px;font-weight:900;color:#FFC94A">金海螺</div>
           <div style="font-size:21px;color:#CBE6F2;line-height:1.35">换稀有货位<br>产量少，留给大件</div></div>
    </div>
    <div style="position:absolute;left:370px;top:12px;display:flex;align-items:center;gap:12px">
      ${img(IMG.silver, 80, 80)}
      <div><div style="font-size:29px;font-weight:900;color:#DCEAF3">银海螺</div>
           <div style="font-size:21px;color:#CBE6F2;line-height:1.35">换常规货位<br>产量大，日常消耗</div></div>
    </div>
  </div>
  ${img(IMG.shop, 54, 50, '', 'position:absolute;left:34px;top:238px;border-radius:6px')}
  <div class="board-lbl" style="left:98px;top:248px" data-name="商店入口">
    兑换商店货位（示意 5 个，实装共 <b>17</b> 个）· 入口在主界面右上角 ↗</div>
  <div class="shelf" style="${box(34, 282, 700, 418)}" data-name="商店货架">${rows}</div>

  <div style="position:absolute;left:800px;top:100px;font-size:30px;font-weight:900;color:#4FE3F5"
       data-name="深度奖励标题">深度奖励</div>
  ${img(IMG.rail, 112, 470, '', 'position:absolute;left:800px;top:150px;border-radius:8px;opacity:.92')}
  <div class="mark" style="left:794px;top:630px;width:124px;text-align:center">实装位置：<br>盘面左侧竖轨</div>
  <div class="rail" style="${box(930, 152, 498, 572)}" data-name="深度档位轨">${tiers}</div>
  <div class="mark" style="left:944px;top:108px;width:484px">
    潜多深发多深 · 点任意一档可切三态</div>
  <div class="mark" style="left:34px;top:702px;width:880px">
    深度只增不减 · 达到档位即可领 · 理论最深 <b>18000 米</b>（1800 行 × 10 米）</div>`;
}

/* ---------------------------------------------------------------- 单屏壳 */
function screenHTML(st) {
  const last = st.page === 2;
  const dots = [0, 1, 2].map((i) => `<div class="dot${i === st.page ? ' on' : ''}" data-page="${i}"></div>`).join('');
  const first = st.page === 0;
  return `
  ${img(IMG.scene, 0, 0, 'bgscene')}
  <div class="dim"></div>
  ${img(IMG.nav, 369, 1080, 'navbar')}
  <div class="pop" data-layer="弹窗_玩法介绍" data-name="弹窗_玩法介绍">
    ${img(IMG.popBase, 1542, 1027, 'pop-base')}
    ${img(IMG.popBar, 1528, 111, 'pop-bar')}
    <div class="pop-title">深海探宝 · 玩法介绍</div>
    <div class="pop-page">${st.page + 1} / 3</div>
    ${img(IMG.close, 122, 115, 'pop-x')}
    <div class="well" data-layer="内容井" data-name="内容井"></div>
    <div class="foot" data-name="页脚">
      ${first ? '' : `<div class="btn blue" data-act="prev" style="left:60px;top:16px">
        ${img(IMG.bBlue, 300, 112)}
        <div class="lbl" style="font-size:38px">上一页</div></div>`}
      <div class="btn ${last ? 'gold' : 'blue'}" data-act="next" style="left:1128px;top:6px">
        ${img(last ? IMG.bGold : IMG.bBlue, 354, 132)}
        <div class="lbl">${last ? '开始挖宝' : '下一页'}</div></div>
      <div class="dots">${dots}</div>
      <div class="foot-hint">${img(IMG.info, 40, 40)}关闭后点界面左下角 ⓘ 可以再看一次</div>
    </div>
  </div>`;
}
function renderScreen(scr) {
  const st = scr.__st;
  scr.innerHTML = screenHTML(st);
  scr.querySelector('.well').innerHTML =
    st.page === 0 ? renderP1(st) : st.page === 1 ? renderP2(st) : renderP3(st);
  bind(scr);
}

/* ---------------------------------------------------------------- 交互 */
function toast(scr, msg, cyan) {
  const t = el(`<div class="toast" style="top:${cyan ? 226 : 300}px${cyan ?
    ';background:rgba(8,64,88,.94);border-color:#4FE3F5;color:#CFF7FF' : ''}">${msg}</div>`);
  scr.querySelector('.well').appendChild(t);
  setTimeout(() => t.remove(), 1600);
}
function floatText(scr, node, msg, color) {
  const well = scr.querySelector('.well');
  const b = node.getBoundingClientRect(), w = well.getBoundingClientRect();
  const k = w.width / 1462 || 1;
  const f = el(`<div class="float" style="left:${(b.left - w.left) / k - 20}px;` +
               `top:${(b.top - w.top) / k - 8}px${color ? `;color:${color}` : ''}">${msg}</div>`);
  well.appendChild(f);
  setTimeout(() => f.remove(), 1000);
}
function dig(scr, r, c, node) {
  const st = scr.__st, grid = st.grid, cell = grid[r][c], cost = COST[cell.t];
  if (cell.t === 'c') return toast(scr, '海藻中心格打不破，它只显示周围有几格有奖');
  if (cost == null) return toast(scr, '空格不可点，也不消耗水母');
  const near = [[1, 0], [-1, 0], [0, 1], [0, -1]].some(([dr, dc]) =>
    grid[r + dr] && grid[r + dr][c + dc] && grid[r + dr][c + dc].t === 'e');
  if (!near) return toast(scr, '只能挖上下左右紧贴空格的格子');
  if (st.jelly < cost) return toast(scr, '水母不足，去礼包补一些');

  st.jelly -= cost;
  if (cell.t === 't') {                          // 宝箱：cost 0，点满次数才消失
    cell.n -= 1;
    floatText(scr, node, rollDrop());
    if (cell.n <= 0) grid[r][c] = P('e');
  } else {
    grid[r][c] = P('e');
    if (cell.t === 'x') floatText(scr, node, '空气泡 · 无奖励', '#9FC7D8');
    else if (cell.t === 'r') floatText(scr, node, '石块 · −2 只水母', '#9FC7D8');
    else floatText(scr, node, rollDrop());
  }
  // 下潜：最下一行出现空格 → 整盘上移一行、深度 +10；新行若又有空格则连锁
  let dives = 0;
  while (grid[grid.length - 1].some((x) => x.t === 'e') && dives < 8) {
    grid.shift(); grid.push(newRow()); st.depth += 10; dives++;
  }
  renderScreen(scr);
  if (dives) toast(scr, dives > 1 ? `连锁下潜 ${dives} 行 · 深度 +${dives * 10} 米`
                                  : '下潜一行 · 深度 +10 米', true);
}
function bind(scr) {
  const st = scr.__st;
  scr.querySelectorAll('.dot').forEach((d) => { d.onclick = () => { st.page = +d.dataset.page; renderScreen(scr); }; });
  const nx = scr.querySelector('[data-act="next"]'), pv = scr.querySelector('[data-act="prev"]');
  if (nx) nx.onclick = () => { st.page = (st.page + 1) % 3; renderScreen(scr); };
  if (pv) pv.onclick = () => { if (st.page > 0) { st.page -= 1; renderScreen(scr); } };
  scr.querySelector('.pop-x').onclick = () => {
    scr.querySelector('.pop').style.display = 'none';
    const back = el(`<div class="btn blue" style="left:1400px;top:880px;z-index:9">
      ${img(IMG.bBlue, 300, 112)}<div class="lbl" style="font-size:34px">再看一次</div></div>`);
    back.onclick = () => renderScreen(scr);
    scr.appendChild(back);
  };
  if (st.page === 0) scr.querySelectorAll('.board [data-rc]').forEach((n) => {
    const [r, c] = n.dataset.rc.split(',').map(Number);
    n.onclick = () => dig(scr, r, c, n);
  });
  if (st.page === 1) scr.querySelectorAll('[data-sel]').forEach((n) => {
    n.onclick = () => { st.sel = n.dataset.sel; renderScreen(scr); };
  });
  if (st.page === 2) scr.querySelectorAll('[data-tier]').forEach((n) => {
    n.onclick = () => {
      const m = +n.dataset.tier;
      st.depth = m;
      st.next = (TIERS.find((t) => t[0] > m) || [null])[0];
      renderScreen(scr);
    };
  });
}

/* ---------------------------------------------------------------- 标注 */
const NOTES = [
  { h: '①页「怎么下潜」— 交互与判定',
    li: ['<b>触发时机</b>：活动首次进入自动弹出，一期只弹一次（客户端本地标记）；之后点界面左下角 <b>ⓘ</b> 重新打开',
         '<b>弹窗母版</b>：高弹窗底板 1542×1027 + 浅灰标题条（标题字 #3A3A3A）；三页共用一个壳，只换中间内容井',
         '<b>可挖判定</b>：仅「上下左右紧贴空格」的格子可点 —— 教学图必须画出这条通路，否则玩家会以为随便点',
         '<b>下潜判定</b>：<b>最下一行出现空格</b>即下潜一行（+10 米）；新行若又含空格则连锁，服务端单次上限 32 行',
         '<b>深度口径</b>：depth = 顶行行号 × 10，客户端自乘、服务端不落库；深度只增不减',
         '<em>本页盘面在稿子里可直接点着试</em>；实装建议做成 2~3 秒一轮的循环动画，别用静态图',
         '<span class="cfg">棋盘 6 列 × 8 行、10 米/行、32 行上限都写死在服务端；刷新权重在 2121·212140056</span>'] },
  { h: '②页「道具怎么用」— 规则硬约束',
    li: ['水母消耗按 2189 <b>A_ARR_cost</b> 给定：气泡 / 空气泡 / 海藻 1 只、石块 2 只、<b>宝箱 0</b>（刷到就是白赚）',
         '<b>炸弹 = 13 格</b>：九宫格再加上下左右各远一格；<b>只卷气泡与石块</b>，宝箱 / 海藻不吃',
         '<b>手电筒 = 整列通吃</b>：宝箱剩余次数一次用完、有奖海藻的奖全领，代价是只能沿一列',
         '两者<b>落点必须是空格或海藻格</b>，且先算范围再扣费 —— 范围内没有可清的格子就直接拒绝，道具不扣',
         '宝箱可点 <b>3~5 次</b>随机（2189 status <span class="cfg">click_num arg2=[3,5]</span>），每次各抽一份奖励',
         '海藻 <b>3×3 一片</b>：<b>中心格不可打破</b>，数字 = 周围 8 格里有奖的个数 ⇒ 可点的是 <b>8 格</b>不是 9 格；屏幕同时最多一片',
         '<em>待程序确认：工具清出来的空格是否触发下潜</em>（数值 v12 按「触发」算，两种口径通顶差约 $50）',
         '<span class="cfg">中心格与工具图标此稿借现网切图占位，等 1511000093-097 正式图标</span>'] },
  { h: '③页「海螺换奖 + 深度奖励」— 数据来源',
    li: ['兑换商店 = 2116 <b>group58 共 17 个货位</b>，双币：<b>金海螺</b>（稀有位）/ <b>银海螺</b>（常规位，v12 起 5 个货位改银）',
         '商店入口在主界面右上角；本页只讲规则，<b>不是实装商店界面</b>',
         '深度奖励 = 2115 <b>group10003</b>，现配 11 档 300 → 12000 米，计数走 fin_cond <span class="cfg">cat=10149044</span>',
         '<em>⛔ 这 11 条深度任务不要补 arg.ids</em>：服务端正是不带 ID 投递才命中，补了进度会静默不动、也没有报错',
         '<b>12000 米终档</b> = 节日装饰 ×13（最终大奖外显）；理论最深 <b>18000 米</b> = 1800 行 × 10 米',
         '档位三态（已达成 / 下一档 / 未达成）在稿子里点档位即可切；可领态沿用通用绿「领取」钮',
         '<span class="cfg">奖励现为「王庭君主」装饰占位，待 12 月节装饰件替换；v12 数值拟并为 10 档</span>'] }
];

/* ---------------------------------------------------------------- 组板 */
const X = [90, 2150, 4210], TOP = 300;
const initState = (i) => ({ page: i, jelly: 20, depth: 120, sel: 'jelly', next: 300, grid: freshGrid() });

function build() {
  const cv = document.getElementById('canvas');
  cv.innerHTML = `
    <div class="bd-title" data-name="板标题"><div class="bar"></div>
      <div class="txt">深海探宝 · 开局玩法介绍（三联）</div></div>
    <div class="bd-sub">活动开始时自动弹出的三页教学：<b>怎么下潜 → 道具怎么用 → 海螺换奖与深度奖励</b>。
      三屏都是活的 —— 盘面能点、道具能切、深度档位能切三态。</div>
    <div class="bd-meta">2112 = <b>21129575</b> · 12 月节<br>
      画布 1920×1080 / 屏 · 甲式流程板<br>切图：真机截图 + 共享素材库母版</div>
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
// 把「每屏像素 + 内容溢出」打进隐藏 <pre>，交给 check_sizes.py 断言 —— 不靠肉眼对齐
function audit() {
  const lines = [];
  document.querySelectorAll('.screen').forEach((s, i) => {
    lines.push(`screen${i + 1}=${s.offsetWidth}x${s.offsetHeight}`);
    const wells = [['well', s.querySelector('.well'), 1462, 740],
                   ['pop', s.querySelector('.pop'), 1542, 1027]];
    wells.forEach(([tag, host, W, H]) => {
      if (!host) return;
      [...host.children].forEach((n) => {
        if (!n.offsetParent && n.offsetWidth === 0) return;
        if (n.classList.contains('pop-x')) return;   // 关闭钮挂在弹窗角外，是母版做法
        const r = n.offsetLeft + n.offsetWidth, b = n.offsetTop + n.offsetHeight;
        if (r > W + 1 || b > H + 1 || n.offsetLeft < -1 || n.offsetTop < -1) {
          lines.push(`OVERFLOW screen${i + 1}.${tag} <${n.className || n.tagName}> ` +
                     `l=${n.offsetLeft} t=${n.offsetTop} r=${r} b=${b} (max ${W}x${H})`);
        }
        if (n.scrollHeight > n.offsetHeight + 2 || n.scrollWidth > n.offsetWidth + 2) {
          lines.push(`CLIP screen${i + 1}.${tag} <${n.className || n.tagName}> ` +
                     `box=${n.offsetWidth}x${n.offsetHeight} content=${n.scrollWidth}x${n.scrollHeight}`);
        }
      });
    });
  });
  const probe = document.createElement('pre');
  probe.id = '__assert';
  probe.style.display = 'none';
  probe.textContent = lines.join('\n');
  document.body.appendChild(probe);
}

/* ---------------------------------------------------------------- 自动交互测试 */
// intro3.html?autotest → 脚本自己点一遍，把结果写进探针；靠断言不靠肉眼
function autotest() {
  const log = [];
  window.onerror = (m) => log.push('JSERR ' + m);
  const S = [...document.querySelectorAll('.screen')];
  const s1 = S[0];
  for (let i = 0; i < 4; i++) {
    const pick = s1.querySelector('.cell.pick');
    if (!pick) { log.push('TEST no-pick@' + i); break; }
    pick.parentElement.click();
  }
  log.push(`TEST p1 jelly=${s1.__st.jelly} depth=${s1.__st.depth}`);
  const s2 = S[1];
  [['bomb', 13], ['light', 8], ['s', 8], ['t', 1], ['jelly', 1]].forEach(([k, want]) => {
    const c = s2.querySelector(`[data-sel="${k}"]`);
    if (!c) return log.push('TEST no-sel ' + k);
    c.click();
    const got = s2.querySelectorAll('.cell.hot').length;
    log.push(`TEST range ${k}=${got} want=${want}${got === want ? '' : ' ✗'}`);
  });
  const s3 = S[2];
  s3.querySelector('[data-tier="3600"]').click();
  log.push(`TEST tier depth=${s3.__st.depth} done=${s3.querySelectorAll('.tier.done').length} now=${s3.querySelectorAll('.tier.now').length}`);
  s3.querySelectorAll('.dot')[0].click();
  log.push(`TEST page=${s3.__st.page} boards=${s3.querySelectorAll('.board').length}`);
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
