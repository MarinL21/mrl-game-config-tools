// 运营策划工作台 · 外壳
// 职责只有三件：模块导航、公共 api/toast、把顶栏搜索转给当前模块。
// 加模块 = server.py 的 MODULES 加一行 + 写一个 static/mod_<key>.js（导出 mount/unmount/onSearch）。

export const $ = (s, r = document) => r.querySelector(s);
export const $$ = (s, r = document) => [...r.querySelectorAll(s)];
export const esc = (s) => String(s ?? '').replace(/[&<>"]/g, c =>
  ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

export async function api(path, opts = {}) {
  const o = { ...opts };
  if (o.body && !(o.body instanceof FormData)) {
    o.headers = { 'Content-Type': 'application/json', ...(o.headers || {}) };
    o.body = JSON.stringify(o.body);
  }
  const r = await fetch(path, o);
  if (!r.ok) {
    let d = await r.text();
    try { d = JSON.parse(d).detail || d; } catch { }
    throw new Error(`${r.status} ${d}`.slice(0, 300));
  }
  return r.status === 204 ? null : r.json();
}

export function toast(msg, type = '') {
  const el = document.createElement('div');
  el.className = 'toast ' + type;
  el.textContent = msg;
  $('#toasts').appendChild(el);
  setTimeout(() => { el.style.opacity = '0'; setTimeout(() => el.remove(), 200); }, type === 'err' ? 6000 : 2600);
}

const ctx = { api, toast, $, $$, esc };
let cur = null, curKey = '';

async function open(m) {
  if (m.ready === false) {
    if (m.href) window.open(m.href, '_blank');
    else toast(`${m.name} 还没做 —— ${m.desc || ''}`);
    return;
  }
  if (curKey === m.key) return;
  cur?.unmount?.();
  curKey = m.key;
  $$('.mtab').forEach(t => t.classList.toggle('on', t.dataset.k === m.key));
  const view = $('#view');
  view.innerHTML = '<div class="empty" style="margin:auto">加载中…</div>';
  cur = await import(`/static/mod_${m.key}.js`);
  await cur.mount(view, ctx);
}

(async function init() {
  const { modules } = await api('/api/modules');
  $('#mods').innerHTML = modules.map(m =>
    `<button class="mtab ${m.ready ? '' : 'soon'}" data-k="${m.key}" title="${esc(m.desc || '')}"
     ><i>${m.icon || '◇'}</i>${esc(m.name)}</button>`).join('');
  $('#mods').onclick = e => {
    const t = e.target.closest('.mtab');
    if (t) open(modules.find(m => m.key === t.dataset.k));
  };
  let timer;
  $('#q').oninput = e => {
    clearTimeout(timer);
    timer = setTimeout(() => cur?.onSearch?.(e.target.value.trim()), 260);
  };
  await open(modules.find(m => m.ready) || modules[0]);
})();
