/* ===========================================================================
   svgbake.js —— 把 .canvas 的 DOM 布局结果「烘焙」成分组命名的 SVG
   目的：HTML 负责排版（flex 好用），SVG 负责交付（Figma 拖进去自动成图层树）

   规则：
     [data-layer]  → <g id="名字">，容器嵌套，图层名 = 属性值
     [data-slot]   → 美术槽位，出一个命名好的空框（后续贴 AI 图）
     [data-note]   → 标注，统一收进最外层 <g id="标注层">，Figma 里一键隐藏

   烘焙结果写进 <script type="text/plain" id="__svg__">，供 render_ux.py 用
   Chrome --dump-dom 取走。
   =========================================================================== */
(function () {
  const NS = 'http://www.w3.org/2000/svg';
  let origin = { x: 0, y: 0 };
  const defs = [];
  let gradSeq = 0;

  const esc = (s) => String(s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');

  const n = (v) => Math.round(v * 100) / 100;

  // —— 颜色：rgba(…) → {hex, opacity}；透明返回 null ——
  function color(css) {
    if (!css) return null;
    const m = css.match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const p = m[1].split(',').map((x) => parseFloat(x.trim()));
    const a = p.length > 3 ? p[3] : 1;
    if (a === 0) return null;
    const hex = '#' + p.slice(0, 3)
      .map((c) => Math.round(c).toString(16).padStart(2, '0')).join('');
    return { hex, opacity: a };
  }

  // —— linear-gradient(180deg, #A 0%, #B 100%) → <linearGradient> ——
  function gradient(bgImage) {
    if (!bgImage || bgImage.indexOf('linear-gradient') < 0) return null;
    if (bgImage.indexOf('repeating-linear-gradient') === 0) return null; // 斜纹底：走纯色回落
    // ⛔ radial-gradient 不支持 —— 用了会烘焙成「无填充」，元素变空心。
    //    kit 里一律用 linear-gradient 代替，别图省事写 radial。
    const inner = bgImage.slice(bgImage.indexOf('(') + 1, bgImage.lastIndexOf(')'));
    const parts = inner.split(/,(?![^(]*\))/).map((s) => s.trim());
    let deg = 180;
    if (/^-?[\d.]+deg$/.test(parts[0])) deg = parseFloat(parts.shift());
    else if (/^to /.test(parts[0])) { const d = parts.shift(); deg = /right/.test(d) ? 90 : 180; }
    const stops = [];
    parts.forEach((p, i) => {
      const c = color(p);
      if (!c) return;
      const pm = p.match(/([\d.]+)%\s*$/);
      const off = pm ? parseFloat(pm[1]) : (i / Math.max(1, parts.length - 1)) * 100;
      stops.push({ c, off });
    });
    if (stops.length < 2) return null;
    // deg: 0=向上, 90=向右, 180=向下（CSS 定义）
    const rad = (deg - 90) * Math.PI / 180;
    const x1 = n(50 - Math.cos(rad) * 50), y1 = n(50 - Math.sin(rad) * 50);
    const x2 = n(50 + Math.cos(rad) * 50), y2 = n(50 + Math.sin(rad) * 50);
    const id = 'g' + (++gradSeq);
    defs.push(
      `<linearGradient id="${id}" x1="${x1}%" y1="${y1}%" x2="${x2}%" y2="${y2}%">` +
      stops.map((s) => `<stop offset="${n(s.off)}%" stop-color="${s.c.hex}" stop-opacity="${s.c.opacity}"/>`).join('') +
      `</linearGradient>`
    );
    return `url(#${id})`;
  }

  function rectOf(el) {
    const r = el.getBoundingClientRect();
    return { x: r.left - origin.x, y: r.top - origin.y, w: r.width, h: r.height };
  }

  function radius(cs, r) {
    const v = cs.borderTopLeftRadius || '0px';
    if (v.indexOf('%') >= 0) return Math.min(r.w, r.h) / 2;
    return parseFloat(v) || 0;
  }

  // —— 元素自身的底板：背景 + 描边 ——
  function boxOf(el, cs, r) {
    const out = [];
    const rx = n(radius(cs, r));
    const grad = gradient(cs.backgroundImage);
    const bg = color(cs.backgroundColor);
    const fill = grad || (bg ? bg.hex : null);
    const fillOp = grad ? 1 : (bg ? bg.opacity : 0);

    const bw = parseFloat(cs.borderTopWidth) || 0;
    const bc = color(cs.borderTopColor);
    const dashed = cs.borderTopStyle === 'dashed';

    if (fill) {
      out.push(`<rect x="${n(r.x)}" y="${n(r.y)}" width="${n(r.w)}" height="${n(r.h)}"` +
        (rx ? ` rx="${rx}"` : '') + ` fill="${fill}"` +
        (fillOp < 1 ? ` fill-opacity="${n(fillOp)}"` : '') + `/>`);
    }
    if (bw > 0 && bc) {
      const i = bw / 2;
      out.push(`<rect x="${n(r.x + i)}" y="${n(r.y + i)}" width="${n(Math.max(0, r.w - bw))}"` +
        ` height="${n(Math.max(0, r.h - bw))}"` + (rx ? ` rx="${n(Math.max(0, rx - i))}"` : '') +
        ` fill="none" stroke="${bc.hex}" stroke-width="${n(bw)}"` +
        (bc.opacity < 1 ? ` stroke-opacity="${n(bc.opacity)}"` : '') +
        (dashed ? ` stroke-dasharray="5 4"` : '') + `/>`);
    }
    return out;
  }

  // —— 文字：用 Range 逐行量，位置与 Chrome 排版一致 ——
  function lineBoxes(node) {
    const s = node.textContent;
    const a = s.search(/\S/), b = s.search(/\s*$/);
    if (a < 0) return [];
    const rg = document.createRange();
    const out = [];
    let start = a;
    for (let i = a + 1; i <= b; i++) {
      rg.setStart(node, start); rg.setEnd(node, i);
      if (rg.getClientRects().length > 1) {
        rg.setStart(node, start); rg.setEnd(node, i - 1);
        out.push({ text: s.slice(start, i - 1), r: rg.getBoundingClientRect() });
        start = i - 1;
        while (start < b && /\s/.test(s[start])) start++;
      }
    }
    rg.setStart(node, start); rg.setEnd(node, b);
    out.push({ text: s.slice(start, b), r: rg.getBoundingClientRect() });
    return out.filter((o) => o.text.trim());
  }

  function textOf(el, cs) {
    const out = [];
    const fill = color(cs.color);
    if (!fill) return out;
    const fs = parseFloat(cs.fontSize) || 13;
    const fw = cs.fontWeight;
    const fam = 'PingFang SC, Noto Sans SC, sans-serif';
    for (const node of el.childNodes) {
      if (node.nodeType !== 3 || !node.textContent.trim()) continue;
      for (const ln of lineBoxes(node)) {
        const x = ln.r.left - origin.x;
        const y = ln.r.top - origin.y + ln.r.height * 0.765;   // 近似基线：实测对齐 Chrome 排版，别乱调
        const sw = parseFloat(cs.webkitTextStrokeWidth) || 0;
        const sc = sw > 0 ? color(cs.webkitTextStrokeColor) : null;
        out.push(`<text x="${n(x)}" y="${n(y)}" font-family="${fam}" font-size="${n(fs)}"` +
          (fw && fw !== '400' ? ` font-weight="${fw}"` : '') +
          ` fill="${fill.hex}"` + (fill.opacity < 1 ? ` fill-opacity="${n(fill.opacity)}"` : '') +
          (sc ? ` stroke="${sc.hex}" stroke-width="${n(sw * 2)}" paint-order="stroke"` +
                ` stroke-linejoin="round"` : '') +
          ` xml:space="preserve">${esc(ln.text.trim())}</text>`);
      }
    }
    return out;
  }

  // 图片转 data URI —— SVG 必须自包含，Figma 解析不了外链
  const uriCache = new Map();
  function dataURI(img) {
    const key = img.currentSrc || img.src;
    if (uriCache.has(key)) return uriCache.get(key);
    let out = key;
    try {
      const c = document.createElement('canvas');
      c.width = img.naturalWidth; c.height = img.naturalHeight;
      c.getContext('2d').drawImage(img, 0, 0);
      out = c.toDataURL('image/png');
    } catch (e) { /* 取不到就退回原始 src，至少 PNG 那一路还是对的 */ }
    uriCache.set(key, out);
    return out;
  }

  function imgOf(el, r) {
    if (el.tagName !== 'IMG' || !el.naturalWidth) return [];
    const fit = getComputedStyle(el).objectFit === 'fill' ? 'none' : 'xMidYMid meet';
    return [`<image x="${n(r.x)}" y="${n(r.y)}" width="${n(r.w)}" height="${n(r.h)}"` +
      ` preserveAspectRatio="${fit}" href="${dataURI(el)}"/>`];
  }

  const isNoteRoot = (el) =>
    el.hasAttribute('data-note') &&
    !(el.parentElement && el.parentElement.closest('[data-note]'));

  // —— 主遍历 ——
  function walk(el, skipNotes) {
    if (el.nodeType !== 1) return '';
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') return '';
    if (skipNotes && isNoteRoot(el)) return '';

    const r = rectOf(el);
    const body = [];
    if (r.w > 0 && r.h > 0) body.push(...boxOf(el, cs, r), ...imgOf(el, r));
    body.push(...textOf(el, cs));
    for (const kid of el.children) body.push(walk(kid, skipNotes));

    const inner = body.filter(Boolean).join('');
    if (!inner) return '';

    const name = el.getAttribute('data-layer') || el.getAttribute('data-slot');
    if (!name) return inner;
    const op = parseFloat(cs.opacity);
    return `<g id="${esc(name)}" data-name="${esc(name)}"` +
      (op < 1 ? ` opacity="${n(op)}"` : '') + `>${inner}</g>`;
  }

  function bake() {
    const canvas = document.querySelector('.canvas');
    const cr = canvas.getBoundingClientRect();
    origin = { x: cr.left, y: cr.top };
    const W = Math.round(cr.width), H = Math.round(cr.height);

    const main = walk(canvas, true);
    const notes = [...canvas.querySelectorAll('[data-note]')]
      .filter(isNoteRoot).map((el) => walk(el, false)).filter(Boolean).join('');

    const bg = color(getComputedStyle(canvas).backgroundColor);
    return `<svg xmlns="${NS}" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">` +
      (defs.length ? `<defs>${defs.join('')}</defs>` : '') +
      (bg ? `<rect width="${W}" height="${H}" fill="${bg.hex}"/>` : '') +
      main +
      (notes ? `<g id="标注层" data-name="标注层">${notes}</g>` : '') +
      `</svg>`;
  }

  function run() {
    const svg = bake();
    let holder = document.getElementById('__svg__');
    if (!holder) {
      holder = document.createElement('script');
      holder.type = 'text/plain'; holder.id = '__svg__';
      document.body.appendChild(holder);
    }
    holder.textContent = svg;
    // 上报每一屏的实测尺寸 —— 规范要求「出图后必须校验像素」，交给 render_ux.py 断言
    holder.setAttribute('data-screens', [...document.querySelectorAll('.screen')]
      .map((e) => { const r = e.getBoundingClientRect();
                    return Math.round(r.width) + 'x' + Math.round(r.height); }).join(','));
    document.documentElement.setAttribute('data-baked', '1');
  }

  if (document.readyState === 'complete') run();
  else window.addEventListener('load', () => setTimeout(run, 60));
})();
