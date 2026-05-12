/**
 * P2 累充礼包归纳填写 - Google Sheets 侧边栏插件
 *
 * 绑定到礼包源表 (1RFAyBfpG3-8rm3ugNn3NHFdeDg8Erha0VttGzokIy6E) 的 Apps Script。
 * 跨表读 / 写 2011 iap_config_QA (1yS_BehT_Rfcc3sXjDPsSaQRcjPh8YepucYTnUQDpEMc).
 */

const SS_2011_ID = '1yS_BehT_Rfcc3sXjDPsSaQRcjPh8YepucYTnUQDpEMc';
const TAB_2011 = 'iap_config_QA';
const COL_2011_IAP_STATUS = 12; // L column

const SS_2112_ID = '1IKUBw678b2PU1m0md1vR9GxcH2uTNyLbR7VWgyAJ57E';
const TAB_2112 = 'activity_config_qa';
const COL_2112_COMPONENTS = 9; // I column

const SS_2115_ID = '1K3-I4gCYKY-Zw5Ms05ozHtHKpOqYI-lp4kuuhqbWajY';
const TAB_2115 = 'activity_task_QA';
const COL_2115_FINCOND = 5; // E column

const SS_2122_ID = '1zziy6nMR1DlhCykKBndwk6d6KNRrzj1PsOsFGbLYR4M';
const TAB_2122 = 'activity_rank_rule（QA）';
const COL_2122_SCORE_RULE = 4; // D column

// 只替换以下 cat 的 IAP 白名单；其他 cat 不动
const FINCOND_IAP_CATS = [101412053]; // 2115 task fincond cat（旧累充统计机制 IAP 大白名单）
const RANK_IAP_CATS = [101425016];    // 2122 rank score_rule cat（按 IAP 列表统计累充）

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('累充礼包归纳')
    .addItem('打开侧边栏', 'showSidebar')
    .addToUi();
}

function showSidebar() {
  const html = HtmlService.createHtmlOutputFromFile('Sidebar')
    .setTitle('累充礼包归纳');
  SpreadsheetApp.getUi().showSidebar(html);
}

function getActiveTabName() {
  return SpreadsheetApp.getActiveSheet().getName();
}

function getAllTabNames() {
  return SpreadsheetApp.getActiveSpreadsheet().getSheets().map(function (s) {
    return s.getName();
  });
}

/** Single bootstrap call for sidebar. */
function initSidebar() {
  return {
    activeTab: getActiveTabName(),
    allTabs: getAllTabNames(),
  };
}

/**
 * Read tab data + cross-read 2011 iap_config_QA preserved fields.
 * Returns the same shape as the local server's /api/data response.
 */
function loadData(tab) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(tab);
  if (!sheet) throw new Error('Tab not found: ' + tab);

  const lastRow = sheet.getLastRow();
  if (lastRow < 1) {
    return {
      tab: tab, total_packs: 0, unique_2011_count: 0,
      unique_2011: [], rows: [], by_price: [],
    };
  }
  const lastCol = Math.max(11, sheet.getLastColumn());
  const values = sheet.getRange(1, 1, lastRow, lastCol).getValues();

  const dataRows = [];
  values.forEach(function (r) {
    const a = String(r[0] || '');
    if (/^2013\d+$/.test(a)) {
      dataRows.push({
        id_2013: a,
        type: String(r[1] || ''),
        id_2011: String(r[2] || ''),
        id_2014: String(r[3] || ''),
        name: String(r[4] || ''),
        lc_name: String(r[5] || ''),
        lc_desc: String(r[6] || ''),
        price: String(r[7] || ''),
        k_existing: String(r[10] || ''),
        preserved: [],
      });
    }
  });

  const preservedMap = readPreservedMap_();
  dataRows.forEach(function (r) {
    r.preserved = preservedMap[r.id_2011] || [];
  });

  const seen = {};
  const unique2011 = [];
  dataRows.forEach(function (r) {
    if (r.id_2011 && !seen[r.id_2011]) {
      seen[r.id_2011] = 1;
      unique2011.push(r.id_2011);
    }
  });
  unique2011.sort();

  const byPriceMap = {};
  dataRows.forEach(function (r) {
    const p = r.price || '(空)';
    if (!byPriceMap[p]) byPriceMap[p] = [];
    byPriceMap[p].push(r);
  });
  const byPrice = Object.keys(byPriceMap).sort(function (a, b) {
    const fa = parseFloat(a); const fb = parseFloat(b);
    return (isFinite(fa) ? fa : -1) - (isFinite(fb) ? fb : -1);
  }).map(function (p) {
    return { price: p, count: byPriceMap[p].length, rows: byPriceMap[p] };
  });

  return {
    tab: tab,
    total_packs: dataRows.length,
    unique_2011_count: unique2011.length,
    unique_2011: unique2011,
    rows: dataRows,
    by_price: byPrice,
  };
}

/**
 * Cross-spreadsheet read 2011 iap_config_QA whole table.
 * Returns: { '<2011_id>': [preserved_non-recharge_actv_obj, ...] }
 */
function readPreservedMap_() {
  const ss2011 = SpreadsheetApp.openById(SS_2011_ID);
  const sheet2011 = ss2011.getSheetByName(TAB_2011);
  if (!sheet2011) throw new Error('2011 tab not found: ' + TAB_2011);
  const lastRow = sheet2011.getLastRow();
  if (lastRow < 1) return {};
  const v = sheet2011.getRange(1, 1, lastRow, COL_2011_IAP_STATUS).getValues();
  const map = {};
  v.forEach(function (r) {
    const a = String(r[0] || '');
    if (!/^2011\d+$/.test(a)) return;
    const ias = r[COL_2011_IAP_STATUS - 1] || '';
    let preserved = [];
    if (ias) {
      try {
        const arr = JSON.parse(String(ias));
        if (Array.isArray(arr)) {
          preserved = arr.filter(function (o) {
            return o && typeof o === 'object' && o.typ && o.typ !== 'recharge_actv';
          });
        }
      } catch (e) {
        // leave preserved as []
      }
    }
    map[a] = preserved;
  });
  return map;
}

/**
 * Read 2011 iap_config_QA: { '<2011_id>': { row: 1-indexed-row, preserved: [...] } }
 */
function readIapStatusMap_() {
  const ss2011 = SpreadsheetApp.openById(SS_2011_ID);
  const sheet2011 = ss2011.getSheetByName(TAB_2011);
  if (!sheet2011) throw new Error('2011 tab not found: ' + TAB_2011);
  const lastRow = sheet2011.getLastRow();
  const v = sheet2011.getRange(1, 1, lastRow, COL_2011_IAP_STATUS).getValues();
  const map = {};
  v.forEach(function (r, i) {
    const a = String(r[0] || '');
    if (!/^2011\d+$/.test(a)) return;
    const ias = r[COL_2011_IAP_STATUS - 1] || '';
    let preserved = [];
    if (ias) {
      try {
        const arr = JSON.parse(String(ias));
        if (Array.isArray(arr)) {
          preserved = arr.filter(function (o) {
            return o && typeof o === 'object' && o.typ && o.typ !== 'recharge_actv';
          });
        }
      } catch (e) {}
    }
    map[a] = { row: i + 1, preserved: preserved, sheet: sheet2011 };
  });
  return { map: map, sheet: sheet2011 };
}

/**
 * Write back: update each unique 2011 IAP's iap_status (col L) with preserved + new recharge_actv.
 * Returns: { updated, ranges, skipped, error? }
 */
function writeBack(tab, actvIds) {
  if (!actvIds || !actvIds.length) {
    return { error: 'actv_ids 为空' };
  }
  for (let i = 0; i < actvIds.length; i++) {
    if (!/^\d{8}$/.test(String(actvIds[i]))) {
      return { error: '非法 id (应是 8 位数字 2112xxxx): ' + actvIds[i] };
    }
  }
  const newRas = actvIds.map(function (id) {
    return { typ: 'recharge_actv', id: parseInt(id, 10), val: 1 };
  });

  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(tab);
  if (!sheet) return { error: 'Tab not found: ' + tab };

  const values = sheet.getRange(1, 1, sheet.getLastRow(), 3).getValues();
  const seen = {};
  const uniqueIds = [];
  values.forEach(function (r) {
    const a = String(r[0] || '');
    if (/^2013\d+$/.test(a)) {
      const id2011 = String(r[2] || '');
      if (id2011 && !seen[id2011]) {
        seen[id2011] = 1;
        uniqueIds.push(id2011);
      }
    }
  });

  const iap = readIapStatusMap_();
  const skipped = [];
  let updated = 0;
  // Sort by row number for sequential writes (slightly faster).
  uniqueIds.sort(function (a, b) {
    const ra = iap.map[a] ? iap.map[a].row : 0;
    const rb = iap.map[b] ? iap.map[b].row : 0;
    return ra - rb;
  });
  uniqueIds.forEach(function (id) {
    const info = iap.map[id];
    if (!info) {
      skipped.push({ id: id, reason: 'not_found_in_2011_table' });
      return;
    }
    const merged = info.preserved.concat(newRas);
    iap.sheet.getRange(info.row, COL_2011_IAP_STATUS).setValue(JSON.stringify(merged));
    updated++;
  });
  // Force flush so user sees result immediately.
  SpreadsheetApp.flush();

  return {
    updated: updated,
    ranges: updated,
    skipped: skipped,
  };
}

// ===== 分析依赖 + 替换关联组件 IAP 列表 =====

function readComponentsForActvs_(actvIds) {
  const ss2112 = SpreadsheetApp.openById(SS_2112_ID);
  const sheet = ss2112.getSheetByName(TAB_2112);
  if (!sheet) throw new Error('2112 tab not found: ' + TAB_2112);
  const last = sheet.getLastRow();
  const v = sheet.getRange(1, 1, last, COL_2112_COMPONENTS).getValues();
  const idToComps = {};
  const wantSet = {};
  actvIds.forEach(function (x) { wantSet[String(x)] = 1; });
  v.forEach(function (r) {
    const a = String(r[0] || '');
    if (wantSet[a]) {
      try {
        const comps = JSON.parse(String(r[COL_2112_COMPONENTS - 1] || '[]'));
        idToComps[a] = Array.isArray(comps) ? comps : [];
      } catch (e) {
        idToComps[a] = [];
      }
    }
  });
  return idToComps;
}

function readTaskFinconds_(taskIds) {
  if (!taskIds.length) return {};
  const ss = SpreadsheetApp.openById(SS_2115_ID);
  const sheet = ss.getSheetByName(TAB_2115);
  const last = sheet.getLastRow();
  const v = sheet.getRange(1, 1, last, COL_2115_FINCOND).getValues();
  const want = {};
  taskIds.forEach(function (x) { want[String(x)] = 1; });
  const out = {};
  v.forEach(function (r, i) {
    const a = String(r[1] || ''); // col B = id
    if (want[a]) {
      try {
        const fc = JSON.parse(String(r[COL_2115_FINCOND - 1] || '{}'));
        out[a] = { row: i + 1, fincond: fc, sheet: sheet };
      } catch (e) {
        out[a] = { row: i + 1, fincond: null, sheet: sheet };
      }
    }
  });
  return out;
}

function readRankScoreRules_(rankIds) {
  if (!rankIds.length) return {};
  const ss = SpreadsheetApp.openById(SS_2122_ID);
  const sheet = ss.getSheetByName(TAB_2122);
  const last = sheet.getLastRow();
  const v = sheet.getRange(1, 1, last, COL_2122_SCORE_RULE).getValues();
  const want = {};
  rankIds.forEach(function (x) { want[String(x)] = 1; });
  const out = {};
  v.forEach(function (r, i) {
    const a = String(r[1] || ''); // col B = id
    if (want[a]) {
      try {
        const sr = JSON.parse(String(r[COL_2122_SCORE_RULE - 1] || '[]'));
        out[a] = { row: i + 1, score_rule: Array.isArray(sr) ? sr : [], sheet: sheet, group: String(r[0] || '') };
      } catch (e) {
        out[a] = { row: i + 1, score_rule: [], sheet: sheet, group: String(r[0] || '') };
      }
    }
  });
  return out;
}

/**
 * 输入累充活动 ids，返回每个 id 路由结果 + 待写 cell 清单。
 * 不修改任何表。
 */
function analyzeDependencies(actvIds) {
  if (!actvIds || !actvIds.length) return { error: 'actv_ids 为空' };
  const idToComps = readComponentsForActvs_(actvIds);
  const taskIds = {};
  const rankIds = {};
  const perActv = [];
  actvIds.forEach(function (id) {
    const a = String(id);
    const comps = idToComps[a] || [];
    const myTasks = []; const myRanks = [];
    comps.forEach(function (c) {
      if (c.typ === 'task' && c.id) {
        taskIds[String(c.id)] = 1; myTasks.push(c.id);
      } else if (c.typ === 'rank' && c.id) {
        rankIds[String(c.id)] = 1; myRanks.push(c.id);
      }
    });
    perActv.push({
      id: a, found_in_2112: !!idToComps[a], tasks: myTasks, ranks: myRanks
    });
  });

  const taskInfo = readTaskFinconds_(Object.keys(taskIds));
  const rankInfo = readRankScoreRules_(Object.keys(rankIds));

  const tasksToUpdate = []; const tasksSkipped = [];
  Object.keys(taskInfo).forEach(function (tid) {
    const info = taskInfo[tid];
    const fc = info.fincond;
    const cat = fc && fc.cat;
    const ids = (fc && fc.arg && fc.arg.ids) || [];
    if (cat && FINCOND_IAP_CATS.indexOf(cat) >= 0) {
      tasksToUpdate.push({ id: tid, row: info.row, cat: cat, val: fc.val, current_ids_count: ids.length });
    } else {
      tasksSkipped.push({ id: tid, row: info.row, cat: cat, reason: 'cat 不在 FINCOND_IAP_CATS 白名单' });
    }
  });
  const ranksToUpdate = []; const ranksSkipped = [];
  Object.keys(rankInfo).forEach(function (rid) {
    const info = rankInfo[rid];
    const sr0 = info.score_rule[0];
    const cat = sr0 && sr0.cat;
    const ids = (sr0 && sr0.ids) || [];
    if (cat && RANK_IAP_CATS.indexOf(cat) >= 0) {
      ranksToUpdate.push({ id: rid, row: info.row, group: info.group, cat: cat, current_ids_count: ids.length });
    } else {
      ranksSkipped.push({ id: rid, row: info.row, group: info.group, cat: cat, reason: 'cat 不在 RANK_IAP_CATS 白名单（server/alliance rank 用 2112 ID 不替换）' });
    }
  });

  return {
    perActv: perActv,
    tasks_to_update: tasksToUpdate,
    ranks_to_update: ranksToUpdate,
    tasks_skipped: tasksSkipped,
    ranks_skipped: ranksSkipped,
    summary: {
      n_tasks_update: tasksToUpdate.length,
      n_ranks_update: ranksToUpdate.length,
      n_tasks_skipped: tasksSkipped.length,
      n_ranks_skipped: ranksSkipped.length,
    },
  };
}

/**
 * 实际替换 2115 fincond.arg.ids + 2122 score_rule[0].ids
 * 替换源 = 当前 tab 的 unique 2011 ids
 */
function replaceComponentIds(tab, actvIds) {
  if (!actvIds || !actvIds.length) return { error: 'actv_ids 为空' };
  for (let i = 0; i < actvIds.length; i++) {
    if (!/^\d{8}$/.test(String(actvIds[i]))) {
      return { error: '非法 id (应是 8 位数字 2112xxxx): ' + actvIds[i] };
    }
  }

  // 1. 拉源表 unique 2011 ids
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(tab);
  if (!sheet) return { error: 'Tab not found: ' + tab };
  const v = sheet.getRange(1, 1, sheet.getLastRow(), 3).getValues();
  const seen = {}; const unique2011 = [];
  v.forEach(function (r) {
    const a = String(r[0] || '');
    if (/^2013\d+$/.test(a)) {
      const idA = String(r[2] || '');
      if (idA && !seen[idA]) { seen[idA] = 1; unique2011.push(parseInt(idA, 10)); }
    }
  });
  if (!unique2011.length) return { error: '当前 tab 没有 2011 IAP 数据' };
  unique2011.sort(function (a, b) { return a - b; });

  // 2. 分析
  const ana = analyzeDependencies(actvIds);
  if (ana.error) return ana;

  // 3. 写 2115 task fincond
  const taskInfo = readTaskFinconds_(ana.tasks_to_update.map(function (t) { return t.id; }));
  const taskUpdates = [];
  ana.tasks_to_update.forEach(function (t) {
    const info = taskInfo[t.id];
    if (!info || !info.fincond) return;
    const fc = info.fincond;
    fc.arg = fc.arg || {};
    fc.arg.ids = unique2011.slice(); // copy
    info.sheet.getRange(info.row, COL_2115_FINCOND).setValue(JSON.stringify(fc));
    taskUpdates.push({ id: t.id, row: info.row });
  });

  // 4. 写 2122 rank score_rule
  const rankInfo = readRankScoreRules_(ana.ranks_to_update.map(function (r) { return r.id; }));
  const rankUpdates = [];
  ana.ranks_to_update.forEach(function (rk) {
    const info = rankInfo[rk.id];
    if (!info || !info.score_rule.length) return;
    const newSr = info.score_rule.map(function (s) { return s; }); // shallow copy
    newSr[0] = Object.assign({}, newSr[0]);
    newSr[0].ids = unique2011.slice();
    info.sheet.getRange(info.row, COL_2122_SCORE_RULE).setValue(JSON.stringify(newSr));
    rankUpdates.push({ id: rk.id, row: info.row });
  });

  SpreadsheetApp.flush();

  return {
    iap_count: unique2011.length,
    tasks_updated: taskUpdates,
    ranks_updated: rankUpdates,
    tasks_skipped: ana.tasks_skipped,
    ranks_skipped: ana.ranks_skipped,
  };
}
