#!/usr/bin/env python3
"""
P2 累充礼包归纳填写工具 — 本地 HTTP 服务器
读源表 1RFAyBfpG3-8rm3ugNn3NHFdeDg8Erha0VttGzokIy6E 各节日 tab，
对 271 条礼包数据：
  1) C 列 2011 IAP id 去重汇总
  2) 按 H 列价格分组归类
  3) 用户输入累充活动 id 列表 → 生成 K 列 recharge_actv JSON

用法：
  python3 server.py                     # 默认 26拓荒节 tab
  python3 server.py 26春节               # 切换 tab
  python3 server.py 26复活节 8800        # 自定义端口
"""
import http.server
import json
import subprocess
import urllib.parse
import sys
import webbrowser
from threading import Timer

SS_ID = "1RFAyBfpG3-8rm3ugNn3NHFdeDg8Erha0VttGzokIy6E"
IAP_2011_SS = "1yS_BehT_Rfcc3sXjDPsSaQRcjPh8YepucYTnUQDpEMc"
IAP_2011_TAB = "iap_config_QA"
DEFAULT_TAB = "26拓荒节"
DEFAULT_PORT = 8765

# in-memory cache: 2011 iap_config_QA preserved-fields lookup
_IAP_PRESERVED_CACHE = {"data": None}


def fetch_2011_data():
    """读 2011 iap_config_QA 全表 → {2011_id: {"preserved":[...], "row": int}}"""
    if _IAP_PRESERVED_CACHE["data"] is not None:
        return _IAP_PRESERVED_CACHE["data"]
    proc = subprocess.run(
        ["gws", "sheets", "+read", "--spreadsheet", IAP_2011_SS,
         "--range", f"{IAP_2011_TAB}!A:L"],
        capture_output=True, text=True, timeout=60,
    )
    out = proc.stdout
    if "{" not in out:
        raise RuntimeError(f"gws read 2011 failed: {proc.stderr or out}")
    raw = out[out.index("{"):]
    rows = json.loads(raw).get("values", [])
    cache = {}
    for i, r in enumerate(rows, start=1):
        if not r or not r[0]:
            continue
        a = str(r[0])
        if not (a.isdigit() and a.startswith("2011")):
            continue
        ias = r[11] if len(r) > 11 else ""
        preserved = []
        if ias:
            try:
                arr = json.loads(ias)
                if isinstance(arr, list):
                    preserved = [
                        o for o in arr
                        if isinstance(o, dict) and o.get("typ") and o.get("typ") != "recharge_actv"
                    ]
            except (ValueError, TypeError):
                pass
        cache[a] = {"preserved": preserved, "row": i}
    _IAP_PRESERVED_CACHE["data"] = cache
    return cache


def fetch_2011_preserved():
    """compat shim: returns {2011_id: [preserved_objs]}"""
    return {k: v["preserved"] for k, v in fetch_2011_data().items()}


def write_back_iap_status(tab, actv_ids):
    """
    把每个 tab 中引用的 2011 IAP 在 iap_config_QA col L (A_ARR_iap_status) 写为
    [...preserved..., ...new_recharge_actv...]。
    返回 {"updated": N, "skipped": [...], "errors": [...]}.
    """
    # 验证 actv_ids 全是 8 位数字
    if not actv_ids:
        return {"error": "actv_ids 为空"}
    bad = [x for x in actv_ids if not (isinstance(x, int) and 10000000 <= x <= 99999999)]
    if bad:
        return {"error": f"非法 id (应是 8 位数字 2112xxxx): {bad}"}
    new_ras = [{"typ": "recharge_actv", "id": int(x), "val": 1} for x in actv_ids]

    # 读源表 tab 拿引用的 unique 2011 ids
    proc = subprocess.run(
        ["gws", "sheets", "+read", "--spreadsheet", SS_ID, "--range", f"{tab}!A:K"],
        capture_output=True, text=True, timeout=30,
    )
    out = proc.stdout
    if "{" not in out:
        return {"error": f"读源表失败: {proc.stderr or out}"}
    raw = out[out.index("{"):]
    rows = json.loads(raw).get("values", [])
    unique_2011 = set()
    for r in rows:
        if not r:
            continue
        a = str(r[0]) if r else ""
        if a.isdigit() and a.startswith("2013"):
            id_2011 = r[2] if len(r) > 2 else ""
            if id_2011:
                unique_2011.add(id_2011)

    iap_data = fetch_2011_data()
    update_data = []
    skipped = []
    for id_2011 in sorted(unique_2011):
        if id_2011 not in iap_data:
            skipped.append({"id": id_2011, "reason": "not_found_in_2011_table"})
            continue
        info = iap_data[id_2011]
        merged = info["preserved"] + new_ras
        update_data.append({
            "range": f"{IAP_2011_TAB}!L{info['row']}",
            "values": [[json.dumps(merged, separators=(",", ":"))]],
        })

    if not update_data:
        return {"error": "无可写入数据", "skipped": skipped}

    body = {"valueInputOption": "USER_ENTERED", "data": update_data}
    params = {"spreadsheetId": IAP_2011_SS}
    proc = subprocess.run(
        ["gws", "sheets", "spreadsheets", "values", "batchUpdate",
         "--params", json.dumps(params),
         "--json", json.dumps(body, ensure_ascii=False)],
        capture_output=True, text=True, timeout=120,
    )
    out = proc.stdout
    err = proc.stderr
    if proc.returncode != 0 or "error" in (out + err).lower()[:500]:
        # 尝试解析 batchUpdate 响应
        try:
            resp = json.loads(out[out.index("{"):]) if "{" in out else {}
        except (ValueError, IndexError):
            resp = {}
        return {"error": "batchUpdate 失败", "stderr": err[:500], "stdout": out[:500], "resp": resp, "skipped": skipped}

    try:
        resp = json.loads(out[out.index("{"):])
    except (ValueError, IndexError):
        resp = {}

    return {
        "updated": resp.get("totalUpdatedCells", len(update_data)),
        "ranges": len(update_data),
        "skipped": skipped,
    }

KNOWN_TABS = [
    "26拓荒节", "26复活节", "26科技节", "26情人节", "26春节",
    "25圣诞节", "25.11星球套装", "25万圣节", "25音乐节", "25周年庆",
    "25登月节", "深海节", "拓荒节", "复活节", "科技节", "情人节", "春节",
]


def fetch_sheet(tab):
    """gws 拉表 → 解析为 data dict"""
    proc = subprocess.run(
        ["gws", "sheets", "+read", "--spreadsheet", SS_ID, "--range", f"{tab}!A:K"],
        capture_output=True, text=True, timeout=30,
    )
    out = proc.stdout
    if "{" in out:
        # gws 前面会打印 "Using keyring backend: keyring"
        raw = out[out.index("{"):]
    else:
        raise RuntimeError(f"gws read failed: {proc.stderr or out}")
    data = json.loads(raw)
    rows = data.get("values", [])
    # Clear cache so refresh button always pulls latest 2011 iap_status
    _IAP_PRESERVED_CACHE["data"] = None
    preserved_lookup = fetch_2011_preserved()
    data_rows = []
    for r in rows:
        if not r:
            continue
        a = str(r[0]) if r else ""
        if a.isdigit() and a.startswith("2013"):
            id_2011 = r[2] if len(r) > 2 else ""
            preserved = preserved_lookup.get(id_2011, []) if id_2011 else []
            data_rows.append({
                "id_2013": a,
                "type": r[1] if len(r) > 1 else "",
                "id_2011": id_2011,
                "id_2014": r[3] if len(r) > 3 else "",
                "name": r[4] if len(r) > 4 else "",
                "lc_name": r[5] if len(r) > 5 else "",
                "lc_desc": r[6] if len(r) > 6 else "",
                "price": r[7] if len(r) > 7 else "",
                "k_existing": r[10] if len(r) > 10 else "",
                "preserved": preserved,
            })
    unique_2011 = sorted({r["id_2011"] for r in data_rows if r["id_2011"]})
    by_price = {}
    for r in data_rows:
        p = r["price"] or "(空)"
        by_price.setdefault(p, []).append(r)

    def _price_key(k):
        try:
            return float(k)
        except (TypeError, ValueError):
            return -1
    sorted_prices = sorted(by_price.keys(), key=_price_key)
    return {
        "tab": tab,
        "total_packs": len(data_rows),
        "unique_2011_count": len(unique_2011),
        "unique_2011": unique_2011,
        "rows": data_rows,
        "by_price": [
            {"price": p, "count": len(by_price[p]), "rows": by_price[p]}
            for p in sorted_prices
        ],
    }


INDEX_HTML = r"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>累充礼包归纳工具</title>
<style>
  * { box-sizing: border-box; }
  body { font-family: -apple-system, "Helvetica Neue", "PingFang SC", sans-serif; margin: 0; padding: 0; background: #f6f7f9; color: #222; }
  header { background: #1f2937; color: white; padding: 14px 24px; position: sticky; top: 0; z-index: 10; box-shadow: 0 2px 6px rgba(0,0,0,.1); }
  header h1 { margin: 0; font-size: 18px; font-weight: 600; }
  header .meta { font-size: 12px; opacity: .8; margin-top: 4px; }
  main { padding: 20px 24px 60px; max-width: 1280px; margin: 0 auto; }
  section { background: white; border-radius: 8px; padding: 16px 20px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,.06); }
  section h2 { margin: 0 0 12px; font-size: 15px; font-weight: 600; color: #111; border-left: 3px solid #4f46e5; padding-left: 8px; }
  .row { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
  select, input[type=text], textarea { font: inherit; padding: 6px 10px; border: 1px solid #cbd5e1; border-radius: 6px; background: white; }
  textarea { min-height: 60px; min-width: 380px; font-family: ui-monospace, Menlo, Consolas, monospace; }
  button { font: inherit; padding: 6px 14px; border: none; border-radius: 6px; background: #4f46e5; color: white; cursor: pointer; transition: background .15s; }
  button:hover { background: #4338ca; }
  button.ghost { background: #e5e7eb; color: #1f2937; }
  button.ghost:hover { background: #d1d5db; }
  button.copy { padding: 2px 8px; font-size: 11px; background: #6b7280; }
  button.copy:hover { background: #4b5563; }
  .stats { display: flex; gap: 24px; flex-wrap: wrap; margin-bottom: 12px; }
  .stat { font-size: 13px; }
  .stat b { color: #4f46e5; font-size: 16px; margin-right: 4px; }
  .id-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); gap: 4px; max-height: 320px; overflow-y: auto; padding: 4px; background: #f9fafb; border-radius: 4px; }
  .id-grid span { font: 12px ui-monospace, Menlo, monospace; padding: 2px 6px; background: white; border: 1px solid #e5e7eb; border-radius: 3px; user-select: all; }
  details { background: #f9fafb; border-radius: 4px; padding: 8px 12px; margin-bottom: 6px; border: 1px solid #e5e7eb; }
  details > summary { cursor: pointer; font-weight: 500; font-size: 13px; user-select: none; }
  details > summary .pill { display: inline-block; min-width: 28px; text-align: center; background: #4f46e5; color: white; border-radius: 12px; padding: 1px 8px; font-size: 11px; margin-left: 8px; }
  details[open] > summary { color: #4f46e5; }
  table { width: 100%; border-collapse: collapse; margin-top: 8px; font-size: 12px; }
  table th { background: #f1f5f9; padding: 6px 8px; text-align: left; font-weight: 600; color: #475569; border-bottom: 1px solid #cbd5e1; position: sticky; top: 0; }
  table td { padding: 4px 8px; border-bottom: 1px solid #f1f5f9; vertical-align: top; }
  table td.mono { font-family: ui-monospace, Menlo, monospace; }
  .out { background: #1e293b; color: #f1f5f9; padding: 12px 14px; border-radius: 6px; font: 13px ui-monospace, Menlo, monospace; word-break: break-all; max-height: 200px; overflow-y: auto; white-space: pre-wrap; }
  .hint { font-size: 12px; color: #64748b; margin-top: 6px; }
  .err { color: #dc2626; font-size: 12px; margin-top: 6px; }
  .loading { color: #64748b; font-size: 13px; }
  .badge { display: inline-block; padding: 1px 6px; background: #fef3c7; color: #92400e; border-radius: 3px; font-size: 11px; }
  .badge.r { background: #fee2e2; color: #991b1b; }
  .badge.n { background: #d1fae5; color: #065f46; }
</style>
</head>
<body>
<header>
  <div class="row" style="justify-content: space-between;">
    <div>
      <h1>累充礼包归纳填写工具</h1>
      <div class="meta">源表 <code>1RFAyBfpG3-8rm3ugNn3NHFdeDg8Erha0VttGzokIy6E</code></div>
    </div>
    <div class="row">
      <label>节日 tab:
        <select id="tabSelect">__TABS_OPTIONS__</select>
      </label>
      <button id="reloadBtn">🔄 刷新数据</button>
      <span id="lastUpdated" class="meta"></span>
    </div>
  </div>
</header>

<main>
  <section>
    <h2>① 累充活动 id 输入 → 生成 K 列 recharge_actv JSON</h2>
    <div class="row">
      <textarea id="actvIds" placeholder="累充活动 2112 id 列表，逗号/换行/空格分隔。例如：&#10;21127892,21127893,21127894,21127891"></textarea>
      <div>
        <button id="genBtn">生成 K 列 JSON</button>
        <div class="hint">所有礼包 K 列将贴同一段 JSON（用户选择"全局生效"模式）</div>
      </div>
    </div>
    <div id="genErr" class="err"></div>
    <div id="genWrap" style="display:none; margin-top:12px;">
      <div style="margin-bottom: 16px;">
        <div class="row" style="justify-content: space-between; margin-bottom: 6px;">
          <b style="font-size: 13px;">① 全局 recharge_actv 数组（适用 2011.iap_status 当前为空的礼包）：</b>
          <button class="copy" id="copyOutBtn">复制</button>
        </div>
        <div class="out" id="genOutput"></div>
      </div>
      <div>
        <div class="row" style="justify-content: space-between; margin-bottom: 6px;">
          <b style="font-size: 13px;">② 按行合并版（保留 2011 现有非-recharge_actv 字段 + 拼新 recharge_actv，<span id="genStats" style="color:#dc2626;"></span>）：</b>
          <button class="copy" id="copyMergedBtn">复制全列（按行序）</button>
        </div>
        <div class="hint">每行一个 JSON，从 sheet 第一行数据（第 14 行）开始按 sheet 行序排列。整列复制粘贴回源表 K 列。</div>
        <textarea id="genMerged" readonly style="width:100%; min-height:160px; margin-top:6px; font-family:ui-monospace,Menlo,Consolas,monospace; font-size:11px;"></textarea>
      </div>
      <div style="margin-top: 16px; padding: 12px 14px; background: #fef3c7; border: 1px solid #fcd34d; border-radius: 6px;">
        <div style="font-weight: 600; color: #92400e; margin-bottom: 4px;">⚡ 一键写回 2011 表 iap_status</div>
        <div class="hint" style="color:#78350f;">直接通过 gws 写回 <code>iap_config_QA</code> 的 <code>A_ARR_iap_status</code> 列，每个 unique 2011 IAP 写一次（preserved + 新 recharge_actv）。会修改活表，请先 review 上方结果。</div>
        <div class="row" style="margin-top:8px;">
          <button id="writeBackBtn" style="background:#dc2626;">⚡ 写回 2011 iap_status</button>
          <span id="writeBackStatus" class="hint"></span>
        </div>
        <div id="writeBackResult" class="out" style="display:none; margin-top:8px; max-height:160px;"></div>
      </div>
      <div id="preservedSummary" style="margin-top:12px;"></div>
    </div>
  </section>

  <section>
    <h2>② 数据概览</h2>
    <div class="stats" id="stats"></div>
  </section>

  <section>
    <h2 style="display:flex; align-items:center; gap:10px;">
      ③ C 列 2011 IAP id 去重汇总
      <span id="uniqueIdsCount" style="font-weight:400; color:#64748b; font-size:13px;"></span>
      <button class="ghost" id="copyAllIdsBtn" style="margin-left:auto;">复制全部 id（逗号分隔）</button>
    </h2>
    <div class="id-grid" id="uniqueIds"><div class="loading">加载中…</div></div>
  </section>

  <section>
    <h2>④ A 列礼包按 H 列价格归类</h2>
    <div id="byPrice"><div class="loading">加载中…</div></div>
  </section>
</main>

<script>
let DATA = null;

async function load(tab) {
  const grid = document.getElementById('uniqueIds');
  const byPrice = document.getElementById('byPrice');
  grid.innerHTML = '<div class="loading">加载中…</div>';
  byPrice.innerHTML = '<div class="loading">加载中…</div>';
  document.getElementById('lastUpdated').textContent = '加载中...';
  try {
    const r = await fetch('/api/data?tab=' + encodeURIComponent(tab));
    if (!r.ok) throw new Error('HTTP ' + r.status + ': ' + await r.text());
    DATA = await r.json();
    render();
    document.getElementById('lastUpdated').textContent = '更新于 ' + new Date().toLocaleTimeString();
  } catch (e) {
    grid.innerHTML = '<div class="err">加载失败：' + e.message + '</div>';
    byPrice.innerHTML = '';
    document.getElementById('lastUpdated').textContent = '加载失败';
  }
}

function render() {
  if (!DATA) return;
  // stats
  document.getElementById('stats').innerHTML = `
    <div class="stat"><b>${DATA.total_packs}</b>条礼包数据</div>
    <div class="stat"><b>${DATA.unique_2011_count}</b>个唯一 2011 IAP</div>
    <div class="stat"><b>${DATA.by_price.length}</b>档价格</div>
    <div class="stat">tab: <code>${DATA.tab}</code></div>
  `;
  // unique 2011 ids
  document.getElementById('uniqueIdsCount').textContent = `（共 ${DATA.unique_2011_count} 个）`;
  const grid = document.getElementById('uniqueIds');
  grid.innerHTML = DATA.unique_2011.map(id => `<span>${id}</span>`).join('');
  // by price
  const bp = document.getElementById('byPrice');
  bp.innerHTML = DATA.by_price.map((g, gi) => {
    const tierUnique = [...new Set(g.rows.map(r => r.id_2011).filter(Boolean))];
    return `
    <details>
      <summary>
        $${g.price}<span class="pill">${g.count}</span>
        <span style="font-weight:400; color:#64748b; font-size:12px; margin-left:8px;">${tierUnique.length} 个唯一 2011 IAP</span>
        <button class="copy" data-tier-idx="${gi}" style="margin-left:8px;">复制本价位 2011 id（${tierUnique.length} 个）</button>
      </summary>
      <table>
        <thead>
          <tr>
            <th>2013 ID</th><th>类型</th><th>2011 IAP</th><th>礼包名</th><th>K 列现有</th>
          </tr>
        </thead>
        <tbody>${g.rows.map(r => `
          <tr>
            <td class="mono">${r.id_2013}</td>
            <td><span class="badge ${r.type === 'random' ? 'r' : (r.type === 'normal' ? 'n' : '')}">${r.type || '—'}</span></td>
            <td class="mono">${r.id_2011}</td>
            <td>${escapeHtml(r.name)}</td>
            <td class="mono" style="max-width: 320px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${escapeAttr(r.k_existing)}">${escapeHtml(r.k_existing || '—').slice(0,80)}</td>
          </tr>`).join('')}
        </tbody>
      </table>
    </details>
  `;
  }).join('');

  // bind copy buttons per tier
  bp.querySelectorAll('button.copy[data-tier-idx]').forEach(btn => {
    btn.addEventListener('click', e => {
      e.preventDefault();
      e.stopPropagation();
      const idx = parseInt(btn.dataset.tierIdx, 10);
      const g = DATA.by_price[idx];
      const tierUnique = [...new Set(g.rows.map(r => r.id_2011).filter(Boolean))];
      navigator.clipboard.writeText(tierUnique.join(',')).then(() => {
        const orig = btn.textContent;
        btn.textContent = `✓ 已复制 ${tierUnique.length} 个`;
        setTimeout(() => btn.textContent = orig, 1500);
      });
    });
  });
}

function escapeHtml(s) {
  return String(s ?? '').replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
}
function escapeAttr(s) {
  return escapeHtml(s).replace(/"/g, '&quot;');
}

document.getElementById('reloadBtn').addEventListener('click', () => {
  load(document.getElementById('tabSelect').value);
});
document.getElementById('tabSelect').addEventListener('change', e => load(e.target.value));

document.getElementById('genBtn').addEventListener('click', () => {
  const raw = document.getElementById('actvIds').value;
  const errEl = document.getElementById('genErr');
  errEl.textContent = '';
  const ids = raw.split(/[\s,，;；]+/).map(s => s.trim()).filter(Boolean);
  if (!ids.length) {
    errEl.textContent = '请输入至少一个 2112 累充活动 id';
    document.getElementById('genWrap').style.display = 'none';
    return;
  }
  for (const id of ids) {
    if (!/^\d{8}$/.test(id)) {
      errEl.textContent = `非法 id "${id}"（应是 8 位数字 2112xxxx）`;
      document.getElementById('genWrap').style.display = 'none';
      return;
    }
  }
  if (!DATA) {
    errEl.textContent = '数据未加载';
    return;
  }
  const newRas = ids.map(id => ({typ: 'recharge_actv', id: parseInt(id, 10), val: 1}));
  const globalJson = JSON.stringify(newRas);
  document.getElementById('genOutput').textContent = globalJson;

  // per-row merged: preserved + new recharge_actv
  const preservedTypeCount = {};
  let nWithPreserved = 0;
  const lines = DATA.rows.map(r => {
    const merged = (r.preserved || []).concat(newRas);
    if (r.preserved && r.preserved.length) {
      nWithPreserved++;
      for (const o of r.preserved) {
        const t = o.typ || '?';
        preservedTypeCount[t] = (preservedTypeCount[t] || 0) + 1;
      }
    }
    return JSON.stringify(merged);
  });
  document.getElementById('genMerged').value = lines.join('\n');
  document.getElementById('genStats').textContent =
    `${nWithPreserved}/${DATA.rows.length} 行有保留字段`;

  // preserved summary table
  const sumDiv = document.getElementById('preservedSummary');
  if (nWithPreserved === 0) {
    sumDiv.innerHTML = '<div class="hint">所有行的 2011.iap_status 都没有非-recharge_actv 字段，按行合并版 = 全局数组重复 ' + DATA.rows.length + ' 次。</div>';
  } else {
    const typeRows = Object.entries(preservedTypeCount)
      .sort((a, b) => b[1] - a[1])
      .map(([t, n]) => `<tr><td class="mono">${escapeHtml(t)}</td><td>${n}</td></tr>`)
      .join('');
    const detailRows = DATA.rows
      .map((r, idx) => ({...r, idx}))
      .filter(r => r.preserved && r.preserved.length)
      .slice(0, 30)
      .map(r => `<tr>
        <td class="mono">${r.id_2013}</td>
        <td class="mono">${r.id_2011}</td>
        <td>${escapeHtml(r.name).slice(0,30)}</td>
        <td class="mono" style="font-size:11px;">${escapeHtml(JSON.stringify(r.preserved)).slice(0,200)}</td>
      </tr>`).join('');
    const moreNote = nWithPreserved > 30 ? `<div class="hint">仅展示前 30 行，共 ${nWithPreserved} 行有保留字段。</div>` : '';
    sumDiv.innerHTML = `
      <details open>
        <summary><b>保留字段类型统计</b><span class="pill">${Object.keys(preservedTypeCount).length} 种</span></summary>
        <table style="margin-top:8px; max-width:400px;">
          <thead><tr><th>typ</th><th>出现次数</th></tr></thead>
          <tbody>${typeRows}</tbody>
        </table>
      </details>
      <details style="margin-top:8px;">
        <summary><b>有保留字段的行明细</b><span class="pill">${nWithPreserved}</span></summary>
        <table style="margin-top:8px;">
          <thead><tr><th>2013 ID</th><th>2011 IAP</th><th>礼包名</th><th>preserved</th></tr></thead>
          <tbody>${detailRows}</tbody>
        </table>
        ${moreNote}
      </details>
    `;
  }

  document.getElementById('genWrap').style.display = 'block';
});

document.getElementById('copyMergedBtn').addEventListener('click', () => {
  const ta = document.getElementById('genMerged');
  navigator.clipboard.writeText(ta.value).then(() => {
    const btn = document.getElementById('copyMergedBtn');
    const orig = btn.textContent;
    const lineCount = ta.value.split('\n').length;
    btn.textContent = `✓ 已复制 ${lineCount} 行`;
    setTimeout(() => btn.textContent = orig, 1500);
  });
});

document.getElementById('writeBackBtn').addEventListener('click', async () => {
  const raw = document.getElementById('actvIds').value;
  const ids = raw.split(/[\s,，;；]+/).map(s => s.trim()).filter(Boolean);
  if (!ids.length) {
    alert('先在上方输入累充活动 id 并点"生成 K 列 JSON"。');
    return;
  }
  for (const id of ids) {
    if (!/^\d{8}$/.test(id)) { alert(`非法 id "${id}"`); return; }
  }
  const uniq2011 = new Set(DATA.rows.map(r => r.id_2011).filter(Boolean));
  const conf = `即将写回 2011 iap_config_QA 的 ${uniq2011.size} 行 iap_status 列。\n\n累充 id: ${ids.join(', ')}\n\n每行 = 该 IAP 现有非-recharge_actv 字段 + 上述新 recharge_actv 数组\n\n确认写入？`;
  if (!confirm(conf)) return;

  const btn = document.getElementById('writeBackBtn');
  const status = document.getElementById('writeBackStatus');
  const resultEl = document.getElementById('writeBackResult');
  btn.disabled = true;
  btn.textContent = '⏳ 写入中...';
  status.textContent = '';
  resultEl.style.display = 'none';

  try {
    const r = await fetch('/api/write', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({tab: DATA.tab, actv_ids: ids.map(x => parseInt(x, 10))}),
    });
    const data = await r.json();
    resultEl.style.display = 'block';
    resultEl.textContent = JSON.stringify(data, null, 2);
    if (r.ok && !data.error) {
      status.innerHTML = `<span style="color:#15803d;">✓ 已写入 ${data.updated} 个 cell（${data.ranges} 行）${data.skipped && data.skipped.length ? '，跳过 ' + data.skipped.length : ''}</span>`;
      btn.textContent = '✓ 写入完成';
    } else {
      status.innerHTML = `<span style="color:#dc2626;">✗ 失败: ${data.error || 'HTTP ' + r.status}</span>`;
      btn.textContent = '⚡ 写回 2011 iap_status';
    }
  } catch (e) {
    status.innerHTML = `<span style="color:#dc2626;">✗ 异常: ${e.message}</span>`;
    btn.textContent = '⚡ 写回 2011 iap_status';
  } finally {
    btn.disabled = false;
    setTimeout(() => { btn.textContent = '⚡ 写回 2011 iap_status'; }, 3000);
  }
});

document.getElementById('copyOutBtn').addEventListener('click', () => {
  const txt = document.getElementById('genOutput').textContent;
  navigator.clipboard.writeText(txt).then(() => {
    const btn = document.getElementById('copyOutBtn');
    const orig = btn.textContent;
    btn.textContent = '✓ 已复制';
    setTimeout(() => btn.textContent = orig, 1500);
  });
});

document.getElementById('copyAllIdsBtn').addEventListener('click', () => {
  if (!DATA) return;
  navigator.clipboard.writeText(DATA.unique_2011.join(',')).then(() => {
    const btn = document.getElementById('copyAllIdsBtn');
    const orig = btn.textContent;
    btn.textContent = '✓ 已复制 ' + DATA.unique_2011.length + ' 个';
    setTimeout(() => btn.textContent = orig, 1500);
  });
});

// init
load(document.getElementById('tabSelect').value);
</script>
</body>
</html>
"""


def render_index(default_tab):
    opts = "".join(
        f'<option value="{t}"{" selected" if t == default_tab else ""}>{t}</option>'
        for t in KNOWN_TABS
    )
    return INDEX_HTML.replace("__TABS_OPTIONS__", opts)


class Handler(http.server.BaseHTTPRequestHandler):
    default_tab = DEFAULT_TAB

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path == "/":
            body = render_index(self.default_tab).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif u.path == "/api/data":
            qs = urllib.parse.parse_qs(u.query)
            tab = qs.get("tab", [self.default_tab])[0]
            try:
                data = fetch_sheet(tab)
                body = json.dumps(data, ensure_ascii=False).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(str(e).encode("utf-8"))
        else:
            self.send_error(404)

    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        if u.path == "/api/write":
            length = int(self.headers.get("Content-Length", 0))
            try:
                body_raw = self.rfile.read(length).decode("utf-8")
                body = json.loads(body_raw) if body_raw else {}
                tab = body.get("tab", self.default_tab)
                actv_ids = body.get("actv_ids", [])
                result = write_back_iap_status(tab, actv_ids)
                resp_body = json.dumps(result, ensure_ascii=False).encode("utf-8")
                code = 200 if "error" not in result else 400
                self.send_response(code)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(resp_body)))
                self.end_headers()
                self.wfile.write(resp_body)
            except Exception as e:
                err = {"error": str(e)}
                resp_body = json.dumps(err, ensure_ascii=False).encode("utf-8")
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(resp_body)
        else:
            self.send_error(404)

    def log_message(self, *a):
        pass


def main():
    args = sys.argv[1:]
    tab = args[0] if args else DEFAULT_TAB
    port = int(args[1]) if len(args) >= 2 else DEFAULT_PORT
    Handler.default_tab = tab
    srv = http.server.HTTPServer(("127.0.0.1", port), Handler)
    url = f"http://127.0.0.1:{port}/"
    print(f"\n累充礼包归纳工具 启动")
    print(f"  默认 tab: {tab}")
    print(f"  地址:    {url}")
    print(f"  Ctrl+C  退出\n")
    Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n再见。")


if __name__ == "__main__":
    main()
