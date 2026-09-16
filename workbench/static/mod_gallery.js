// 模块 · 竞品外观库
// 左栏筛（游戏/类别/状态）→ 网格看 → 点开灯箱改标签。多选可批量打标。
// 性能：只加载缩略图（600px jpg）+ 原生 lazy + 滚动分页；视频只在灯箱里播。

import { api, toast, esc } from '/static/app.js';

let ctx, root, meta = null;
const S = {
  f: { game: '', category: '', status: '', kind: '', q: '', tag: '' },
  items: [], total: 0, sel: new Set(), picking: false, lbIdx: -1, loading: false,
};

const TPL = `
<aside class="side">
  <div class="sgroup">
    <button class="btn" id="scan">扫描收件箱 <span id="ibn"></span></button>
    <div class="drop" id="drop">把图 / 视频拖到这里<br><span style="opacity:.7">或丢进 inbox/ 后点上面</span></div>
  </div>
  <div class="sgroup"><h4>快捷</h4><div id="fquick"></div></div>
  <div class="sgroup"><h4>游戏 <button id="addgame" title="新增游戏">＋</button></h4><div id="fgames"></div></div>
  <div class="sgroup"><h4>类别 <button id="addcat" title="新增类别">＋</button></h4><div id="fcats"></div></div>
</aside>
<div class="work">
  <div class="bar">
    <div class="crumb" id="crumb"></div>
    <div class="spacer"></div>
    <button class="tgl" id="pickbtn">多选</button>
    <input type="range" class="rng" id="cell" min="150" max="440" step="10" value="220" title="缩略图大小">
  </div>
  <div class="grid" id="grid"></div>
  <div class="bulk" id="bulk">
    <b id="bn">已选 0</b>
    <select id="bgame"><option value="">设为游戏…</option></select>
    <select id="bcat"><option value="">设为类别…</option></select>
    <input id="btag" placeholder="加标签后回车" style="width:130px">
    <button class="tgl" id="bdone">标为已完成</button>
    <button class="tgl x" id="bdel">删除</button>
    <button class="tgl" id="bclr">取消</button>
  </div>
</div>
<div class="lb" id="lb">
  <div class="lb-stage" id="lbstage"></div>
  <button class="lb-nav lb-prev" id="lbprev">‹</button>
  <button class="lb-nav lb-next" id="lbnext">›</button>
  <button class="lb-close" id="lbclose">✕</button>
  <aside class="lb-side" id="lbside"></aside>
</div>
<datalist id="dlgames"></datalist><datalist id="dlcats"></datalist>`;

// ── 小工具 ─────────────────────────────
const dur = s => s == null ? '' : `${Math.floor(s / 60)}:${String(Math.round(s % 60)).padStart(2, '0')}`;
const size = b => b > 1048576 ? (b / 1048576).toFixed(1) + ' MB' : Math.round(b / 1024) + ' KB';
const q = s => root.querySelector(s);

export async function mount(_root, _ctx) {
  ctx = _ctx; root = _root;
  root.innerHTML = TPL;
  bind();
  await reload(true);
  openFromHash();
  window.addEventListener('hashchange', openFromHash);
}

// #g/<id> 直接开到某一件 —— 方便把某个外观的链接存下来 / 发给别人
async function openFromHash() {
  const m = /^#g\/(\d+)$/.exec(location.hash);
  if (!m) return;
  const id = +m[1];
  let i = S.items.findIndex(a => a.id === id);
  if (i < 0) {                       // 不在当前筛选结果里就清筛选再找
    S.f = { game: '', category: '', status: '', kind: '', q: '', tag: '' };
    await reload(true);
    i = S.items.findIndex(a => a.id === id);
  }
  if (i >= 0) openLB(i); else toast(`找不到 #${id}`, 'err');
}
export function unmount() { document.removeEventListener('keydown', onKey); }
export function onSearch(v) { S.f.q = v; reload(); }

// ── 数据 ───────────────────────────────
async function loadMeta() {
  meta = await api('/api/gallery/meta');
  q('#ibn').textContent = meta.inbox ? `(${meta.inbox})` : '';
  q('#scan').classList.toggle('ghost', !meta.inbox);

  q('#fquick').innerHTML = [
    ['', '', '全部', meta.total],
    ['status', 'new', '⚠ 待标注', meta.pending],
    ['kind', 'image', '图片', meta.images],
    ['kind', 'video', '视频', meta.videos],
  ].map(([k, v, nm, n]) => {
    const on = k === '' ? (!S.f.status && !S.f.kind) : S.f[k] === v;
    return `<div class="fitem ${on ? 'on' : ''}" data-quick="${k}:${v}">
      <span class="nm">${nm}</span><span class="ct">${n}</span></div>`;
  }).join('');

  const list = (key, arr, loose) => arr.concat(loose.map(n => ({ name: n, count: -1, loose: 1 })))
    .map(t => `<div class="fitem ${S.f[key] === t.name ? 'on' : ''}" data-k="${key}" data-v="${esc(t.name)}"
       title="${esc(t.alias || '')}"><span class="nm">${esc(t.name)}</span>
       <span class="ct">${t.count < 0 ? '·' : t.count}</span>
       <button class="del" data-del="${key === 'game' ? 'game' : 'category'}" title="从分类池移除">✕</button></div>`).join('');
  q('#fgames').innerHTML = list('game', meta.games, meta.loose_games);
  q('#fcats').innerHTML = list('category', meta.categories, meta.loose_categories);

  const opts = a => a.map(t => `<option value="${esc(t.name)}">`).join('');
  root.querySelector('#dlgames').innerHTML = opts(meta.games);
  root.querySelector('#dlcats').innerHTML = opts(meta.categories);
  const sel = (el, a, ph) => el.innerHTML = `<option value="">${ph}</option>` +
    a.map(t => `<option>${esc(t.name)}</option>`).join('');
  sel(q('#bgame'), meta.games, '设为游戏…');
  sel(q('#bcat'), meta.categories, '设为类别…');
}

async function reload(withMeta = false, append = false) {
  if (S.loading) return;
  S.loading = true;
  try {
    if (withMeta) await loadMeta();
    const p = new URLSearchParams();
    for (const [k, v] of Object.entries(S.f)) if (v) p.set(k, v);
    p.set('offset', append ? S.items.length : 0);
    p.set('limit', 300);
    const r = await api('/api/gallery/assets?' + p);
    S.items = append ? S.items.concat(r.items) : r.items;
    S.total = r.total;
    draw();
  } catch (e) { toast(e.message, 'err'); }
  finally { S.loading = false; }
}

// ── 渲染 ───────────────────────────────
function card(a) {
  const sub = [a.game, a.category].filter(Boolean).map(esc).join(' · ') || '<em>待标注</em>';
  return `<article class="card${S.sel.has(a.id) ? ' sel' : ''}" data-id="${a.id}">
    <div class="tw">${a.thumb
      ? `<img loading="lazy" decoding="async" src="/${a.thumb}" alt="">`
      : '<span class="noimg">无预览</span>'}
      ${a.kind === 'video' ? `<span class="badge">▶ ${dur(a.duration) || '视频'}</span>` : ''}
      ${a.status === 'new' ? '<span class="newdot"></span>' : ''}
      <span class="pick"></span></div>
    <div class="cmeta"><div class="t">${esc(a.title || a.filename || '')}</div>
      <div class="s">${sub}</div></div></article>`;
}

function draw() {
  const g = q('#grid');
  g.classList.toggle('picking', S.picking);
  g.innerHTML = S.items.length ? S.items.map(card).join('')
    : `<div class="empty"><b>这里还是空的</b>
       把竞品截图 / 录屏拖进左边的方框，或丢进 <code>workbench/inbox/</code> 后点「扫描收件箱」。</div>`;
  const chips = [];
  for (const [k, label] of [['game', '游戏'], ['category', '类别'], ['tag', '标签'], ['q', '搜索']])
    if (S.f[k]) chips.push(`<span class="chip">${label}：${esc(S.f[k])}<button data-clr="${k}">✕</button></span>`);
  if (S.f.status === 'new') chips.push(`<span class="chip">待标注<button data-clr="status">✕</button></span>`);
  if (S.f.kind) chips.push(`<span class="chip">${S.f.kind === 'video' ? '视频' : '图片'}<button data-clr="kind">✕</button></span>`);
  q('#crumb').innerHTML = chips.join('') +
    `<b>${S.items.length}</b> / ${S.total} 件` + (meta ? `　库内共 ${meta.total}` : '');
  q('#bn').textContent = `已选 ${S.sel.size}`;
  q('#bulk').classList.toggle('on', S.sel.size > 0);
}

// ── 交互 ───────────────────────────────
function bind() {
  q('#scan').onclick = async (e) => {
    e.target.disabled = true; e.target.textContent = '扫描中…';
    try {
      const r = await api('/api/gallery/scan', { method: 'POST' });
      toast(`入库 ${r.added} 件${r.dups ? `，跳过重复 ${r.dups}` : ''}${r.failed.length ? `，失败 ${r.failed.length}` : ''}`,
        r.added ? 'ok' : '');
      if (r.failed.length) console.warn('失败：', r.failed);
    } catch (err) { toast(err.message, 'err'); }
    e.target.disabled = false; e.target.innerHTML = '扫描收件箱 <span id="ibn"></span>';
    S.f.status = 'new'; S.f.kind = '';
    await reload(true);
  };

  // 侧栏筛选
  root.querySelector('.side').onclick = async e => {
    const del = e.target.closest('[data-del]');
    if (del) {
      e.stopPropagation();
      const it = del.closest('.fitem');
      if (!confirm(`把「${it.dataset.v}」从分类池移除？（已标注的素材不受影响）`)) return;
      await api('/api/gallery/tax/delete', { method: 'POST', body: { kind: del.dataset.del, name: it.dataset.v } });
      return reload(true);
    }
    const qk = e.target.closest('[data-quick]');
    if (qk) {
      const [k, v] = qk.dataset.quick.split(':');
      S.f.status = ''; S.f.kind = '';
      if (k) S.f[k] = v;
      return reload(true);
    }
    const it = e.target.closest('[data-k]');
    if (it) { S.f[it.dataset.k] = S.f[it.dataset.k] === it.dataset.v ? '' : it.dataset.v; return reload(true); }
  };
  q('#addgame').onclick = e => { e.stopPropagation(); addTax('game', '游戏'); };
  q('#addcat').onclick = e => { e.stopPropagation(); addTax('category', '类别'); };

  // 网格
  q('#grid').onclick = e => {
    const c = e.target.closest('.card');
    if (!c) return;
    const id = +c.dataset.id;
    if (S.picking || e.target.classList.contains('pick') || e.metaKey || e.shiftKey) {
      S.sel.has(id) ? S.sel.delete(id) : S.sel.add(id);
      c.classList.toggle('sel', S.sel.has(id));
      q('#bn').textContent = `已选 ${S.sel.size}`;
      q('#bulk').classList.toggle('on', S.sel.size > 0);
      return;
    }
    openLB(S.items.findIndex(a => a.id === id));
  };
  q('#grid').onscroll = e => {
    const el = e.target;
    if (el.scrollTop + el.clientHeight > el.scrollHeight - 500 && S.items.length < S.total) reload(false, true);
  };
  q('#crumb').onclick = e => {
    const b = e.target.closest('[data-clr]');
    if (!b) return;
    S.f[b.dataset.clr] = '';
    if (b.dataset.clr === 'q') document.querySelector('#q').value = '';
    reload(true);
  };
  q('#pickbtn').onclick = e => {
    S.picking = !S.picking;
    e.target.classList.toggle('on', S.picking);
    q('#grid').classList.toggle('picking', S.picking);
  };
  q('#cell').oninput = e => root.style.setProperty('--cell', e.target.value + 'px');

  // 批量
  const doBulk = async fields => {
    const ids = [...S.sel];
    await api('/api/gallery/bulk', { method: 'POST', body: { ids, fields } });
    toast(`已更新 ${ids.length} 件`, 'ok');
    S.sel.clear();
    await reload(true);
  };
  q('#bgame').onchange = e => { if (e.target.value) doBulk({ game: e.target.value }); e.target.value = ''; };
  q('#bcat').onchange = e => { if (e.target.value) doBulk({ category: e.target.value }); e.target.value = ''; };
  q('#btag').onkeydown = e => {
    if (e.key !== 'Enter' || !e.target.value.trim()) return;
    const t = e.target.value.trim(); e.target.value = '';
    Promise.all([...S.sel].map(id => {
      const a = S.items.find(x => x.id === id);
      const tags = (a.tags ? a.tags.split(',').map(s => s.trim()).filter(Boolean) : []);
      if (!tags.includes(t)) tags.push(t);
      return api(`/api/gallery/asset/${id}`, { method: 'PATCH', body: { tags: tags.join(',') } });
    })).then(() => { toast(`加标签「${t}」`, 'ok'); S.sel.clear(); reload(true); });
  };
  q('#bdone').onclick = () => doBulk({ status: 'done' });
  q('#bclr').onclick = () => { S.sel.clear(); draw(); };
  q('#bdel').onclick = async () => {
    if (!confirm(`删除选中的 ${S.sel.size} 件？文件会一并删掉，不可撤销。`)) return;
    await api('/api/gallery/delete', { method: 'POST', body: { ids: [...S.sel] } });
    toast(`已删除 ${S.sel.size} 件`, 'ok');
    S.sel.clear(); reload(true);
  };

  // 灯箱
  q('#lbclose').onclick = closeLB;
  q('#lbprev').onclick = () => openLB(S.lbIdx - 1);
  q('#lbnext').onclick = () => openLB(S.lbIdx + 1);
  q('#lb').onclick = e => { if (e.target.id === 'lb' || e.target.id === 'lbstage') closeLB(); };
  document.addEventListener('keydown', onKey);

  // 拖拽上传
  const drop = q('#drop');
  const stop = e => { e.preventDefault(); e.stopPropagation(); };
  ['dragenter', 'dragover'].forEach(t => root.addEventListener(t, e => { stop(e); drop.classList.add('hot'); }));
  ['dragleave', 'drop'].forEach(t => root.addEventListener(t, e => { stop(e); if (t === 'dragleave') drop.classList.remove('hot'); }));
  root.addEventListener('drop', async e => {
    drop.classList.remove('hot');
    const files = [...(e.dataTransfer?.files || [])];
    if (!files.length) return;
    const fd = new FormData();
    files.forEach(f => fd.append('files', f));
    if (S.f.game) fd.append('game', S.f.game);
    if (S.f.category) fd.append('category', S.f.category);
    toast(`上传 ${files.length} 个文件…`);
    try {
      const r = await api('/api/gallery/upload', { method: 'POST', body: fd });
      toast(`入库 ${r.added} 件${r.dups ? `，重复 ${r.dups}` : ''}`, 'ok');
      if (r.failed.length) { toast(`失败 ${r.failed.length} 个，见控制台`, 'err'); console.warn(r.failed); }
      await reload(true);
    } catch (err) { toast(err.message, 'err'); }
  });
}

function onKey(e) {
  if (!q('#lb')?.classList.contains('on')) return;
  if (['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName)) {
    if (e.key === 'Escape') e.target.blur();
    return;
  }
  if (e.key === 'Escape') closeLB();
  if (e.key === 'ArrowLeft') openLB(S.lbIdx - 1);
  if (e.key === 'ArrowRight') openLB(S.lbIdx + 1);
}

async function addTax(kind, label) {
  const name = prompt(`新增${label}名称：`);
  if (!name?.trim()) return;
  await api('/api/gallery/tax', { method: 'POST', body: { kind, name: name.trim() } });
  await reload(true);
}

// ── 灯箱 ───────────────────────────────
function openLB(i) {
  if (i < 0 || i >= S.items.length) return;
  S.lbIdx = i;
  const a = S.items[i];
  history.replaceState(null, '', '#g/' + a.id);
  q('#lb').classList.add('on');
  const stage = q('#lbstage');
  stage.innerHTML = a.kind === 'video'
    ? `<video src="/${a.path}" controls autoplay loop playsinline></video>`
    : `<img src="/${a.path}" alt="">`;
  const im = stage.querySelector('img');
  if (im) im.onload = () => {          // 图标类小图默认会小得看不清，等比放大到舞台一半
    const sw = stage.clientWidth - 52, sh = stage.clientHeight - 52;
    if (im.naturalWidth < sw * .5 && im.naturalHeight < sh * .5) {
      const k = Math.min(4, sw * .5 / im.naturalWidth, sh * .7 / im.naturalHeight);
      im.style.width = Math.round(im.naturalWidth * k) + 'px';
    }
  };
  const opt = (v, cur) => `<option value="${esc(v)}"${v === cur ? ' selected' : ''}>${esc(v)}</option>`;
  q('#lbside').innerHTML = `
    <h3>${esc(a.title || a.filename || '未命名')}</h3>
    <div class="sub">${a.kind === 'video' ? '视频 ' + (dur(a.duration) || '') : '图片'} ·
      ${a.width ? a.width + '×' + a.height + ' · ' : ''}${size(a.bytes)} · ${esc(a.filename || '')}</div>
    <div class="fld"><label>游戏</label><input id="e_game" list="dlgames" value="${esc(a.game)}" placeholder="选或直接输入新的"></div>
    <div class="fld"><label>类别</label><input id="e_category" list="dlcats" value="${esc(a.category)}" placeholder="选或直接输入新的"></div>
    <div class="fld"><label>这件外观叫什么</label><input id="e_title" value="${esc(a.title)}" placeholder="如：极光主城皮肤 / 龙鳞行军特效"></div>
    <div class="fld"><label>标签（逗号分隔）</label><input id="e_tags" value="${esc(a.tags)}" placeholder="冰雪, 高级档, 可动特效"></div>
    <div class="fld"><label>备注 · 好在哪 / 想借鉴什么</label><textarea id="e_note">${esc(a.note)}</textarea></div>
    <div class="fld"><label>来源链接</label><input id="e_source_url" value="${esc(a.source_url)}" placeholder="https://"></div>
    <div class="fld"><label>评分</label><div class="stars" id="stars">${[1, 2, 3].map(n =>
      `<button data-n="${n}" class="${a.rating >= n ? 'on' : ''}">★</button>`).join('')}</div></div>
    <div class="fld" style="display:flex;gap:8px">
      <a class="btn ghost" style="flex:1;line-height:1.6" href="/${a.path}" target="_blank">原图新窗打开</a>
      <button class="btn ghost" id="e_del" style="flex:none;width:56px;color:#ff6b6b">删除</button>
    </div>
    <div style="color:#6d7688;font-size:11px;line-height:1.9;margin-top:4px">
      ← → 切换 · Esc 关闭 · 改完自动保存</div>`;

  const save = async (k, v) => {
    try {
      const r = await api(`/api/gallery/asset/${a.id}`, { method: 'PATCH', body: { [k]: v } });
      Object.assign(a, r.asset);
      const c = q(`.card[data-id="${a.id}"]`);
      if (c) c.outerHTML = card(a);
      if (['game', 'category'].includes(k)) loadMeta();
    } catch (e) { toast(e.message, 'err'); }
  };
  for (const k of ['game', 'category', 'title', 'tags', 'note', 'source_url']) {
    const el = q('#e_' + k);
    el.onchange = () => save(k, el.value.trim());
  }
  q('#stars').onclick = e => {
    const b = e.target.closest('[data-n]');
    if (!b) return;
    const n = a.rating === +b.dataset.n ? 0 : +b.dataset.n;
    save('rating', n);
    [...q('#stars').children].forEach(x => x.classList.toggle('on', +x.dataset.n <= n));
  };
  q('#e_del').onclick = async () => {
    if (!confirm('删除这一件？文件一并删掉。')) return;
    await api('/api/gallery/delete', { method: 'POST', body: { ids: [a.id] } });
    closeLB(); reload(true);
  };
}

function closeLB() {
  history.replaceState(null, '', location.pathname);
  q('#lb').classList.remove('on');
  q('#lbstage').innerHTML = '';   // 停掉视频播放
}
