/**
 * P2 跨表 ID 查询插件
 *
 * 功能：选中一个 ID → 侧边栏显示来源表、全部字段、外键引用
 * 支持：2112/2111/2121/2135/2011/2013/1111/1180/1168/1511 共 10 张表
 *
 * 安装：
 *   1. Google Sheets → 扩展程序 → Apps Script
 *   2. 粘贴本文件到 Code.gs
 *   3. 新建 Sidebar.html，粘贴对应内容
 *   4. 保存 → 刷新表格 → 菜单栏出现「ID 查询」
 */

// ============================================================
//  表注册表 —— 新增表只需加一行，格式：
//  '前缀': { name: 中文名, full: 英文名, sid: SpreadsheetID, tab: 页签名, idCol: ID列名 }
// ============================================================

var TABLE_REGISTRY = {
  '2112': { name: '活动配置',   full: 'activity_config',    sid: '1IKUBw678b2PU1m0md1vR9GxcH2uTNyLbR7VWgyAJ57E', tab: 'activity_config_qa',           idCol: 'A_INT_id' },
  '2111': { name: '活动日历',   full: 'activity_calendar',  sid: '1OaExug4AwwFlGH6LGbBiMnvQF41hYg0LsXiMQZ9XX6g', tab: 'activity_calendar_QA',         idCol: 'A_INT_id' },
  '2121': { name: '活动组件',   full: 'activity_special',   sid: '1sicvhfxZhagLVmpEg4HDcaCnPWPgsWkhgZKC-HxCCuc', tab: 'activity_special_QA',          idCol: 'A_INT_id' },
  '2135': { name: '活动礼包壳', full: 'activity_event_pkg', sid: '1KrcIA8jC4Aj6sFz44c_2lhtJ-lyD1OYu3QNpzaor8Mc', tab: 'activity_event_pkg',           idCol: 'A_INT_id' },
  '2011': { name: 'IAP外壳',   full: 'iap_config',         sid: '1yS_BehT_Rfcc3sXjDPsSaQRcjPh8YepucYTnUQDpEMc', tab: 'iap_config_QA',                idCol: 'A_INT_id' },
  '2013': { name: 'IAP模板',   full: 'iap_template',       sid: '1sJzacpa0CBp1B8LQX1TboSBOA4T80_t8lH8eEzqHLbY', tab: 'iap_template_QA',              idCol: 'A_INT_id' },
  '1111': { name: '道具表',    full: 'item',               sid: '1FQqpeRfkXVwaEDSVi3oTaQNs2PLLDcsvQQmc-k0L3ws', tab: 'item',                         idCol: 'A_INT_id' },
  '1180': { name: '行军表情',   full: 'map_emoji',          sid: '1SloOHvSFrEJz7HaU8yur9Qt8dOzsmqa69DUBERkkBmw', tab: 'qa',                           idCol: 'A_INT_id' },
  '1168': { name: '准入组',    full: 'get_access_group',   sid: '1KwX1xWoHHcmOGTaasZmMii2Al-YR_VXV3yoSGn3tBbA', tab: 'get_access_group（杜绝手搓）',  idCol: 'A_INT_id' },
  '1511': { name: '展示键',    full: 'display_key',        sid: '1Oks7yHCxYnWxo1QiNdO5EYNET68l_aCzZU-58zATlLY', tab: 'display_key',                  idCol: 'A_INT_id' },
  '2115': { name: '任务配置',   full: 'activity_task',      sid: '1K3-I4gCYKY-Zw5Ms05ozHtHKpOqYI-lp4kuuhqbWajY', tab: 'activity_task_QA',             idCol: 'A_INT_id' },
  '2122': { name: '排行榜规则', full: 'activity_rank_rule', sid: '1zziy6nMR1DlhCykKBndwk6d6KNRrzj1PsOsFGbLYR4M', tab: 'activity_rank_rule（QA）',     idCol: 'A_INT_id' },
  '2124': { name: '掉落配置',   full: 'activity_drop',      sid: '1V7xDriTe0hGW3SF7ZPtk71-sFGyzpbbO47V6gLoBqVA', tab: 'activity_drop',                idCol: 'A_INT_id' }
};

// ============================================================
//  菜单 & 侧边栏
// ============================================================

// 如果原有代码已有 onOpen，请在原有 onOpen 末尾加一行: addIdLookupMenu();
function addIdLookupMenu() {
  SpreadsheetApp.getUi()
    .createMenu('ID 查询')
    .addItem('打开查询面板', 'showSidebar')
    .addToUi();
}

function showSidebar() {
  var html = HtmlService.createHtmlOutputFromFile('Sidebar')
    .setTitle('ID 跨表查询');
  SpreadsheetApp.getUi().showSidebar(html);
}

// ============================================================
//  读取当前选中单元格
// ============================================================

function getSelectedCellValue() {
  var cell = SpreadsheetApp.getActiveSpreadsheet().getActiveCell();
  if (!cell) return '';
  var v = cell.getValue();
  if (v === null || v === undefined || v === '') return '';
  // 数字可能带 .0，先转整数
  if (typeof v === 'number') return String(Math.floor(v));
  return String(v).trim();
}

// ============================================================
//  主查询入口
// ============================================================

function lookupId(idStr) {
  idStr = String(idStr).trim();

  // 处理可能的小数（如 21127576.0）
  var num = Number(idStr);
  if (!isNaN(num) && isFinite(num)) {
    idStr = String(Math.floor(num));
  }

  // 提取纯数字
  var numId = idStr.replace(/[^0-9]/g, '');
  if (!numId || numId.length < 5) {
    return { error: '请输入至少 5 位数字 ID（当前: "' + idStr + '"）' };
  }

  // 前 4 位 = 表前缀
  var prefix = numId.substring(0, 4);
  var cfg = TABLE_REGISTRY[prefix];
  if (!cfg) {
    return {
      error: '未知前缀 ' + prefix + '\n已支持: ' + Object.keys(TABLE_REGISTRY).join(', ')
    };
  }

  try {
    return _fetchRow(cfg, numId, prefix);
  } catch (e) {
    return { error: '查询出错: ' + e.message + '\n表: ' + cfg.name + ' (' + cfg.full + ')' };
  }
}

// ============================================================
//  从目标表读取一行
// ============================================================

function _fetchRow(cfg, idStr, prefix) {
  var ss = SpreadsheetApp.openById(cfg.sid);

  // 策略：先查配置的页签，找不到就扫描全部页签
  var result = _searchInSheet(ss, cfg.tab, cfg.idCol, idStr);

  if (!result.found) {
    // 扫描该 Spreadsheet 的所有页签
    var allSheets = ss.getSheets();
    for (var s = 0; s < allSheets.length; s++) {
      var sheetName = allSheets[s].getName();
      if (sheetName === cfg.tab) continue; // 已经搜过了
      result = _searchInSheet(ss, sheetName, cfg.idCol, idStr);
      if (result.found) break;
    }
  }

  if (!result.found) {
    return { found: false, error: '在「' + cfg.name + '」全部页签中未找到 ID: ' + idStr };
  }

  var sheet = result.sheet;
  var rowNum = result.rowNum;
  var headers = result.headers;
  var lastCol = headers.length;

  // 3. 读整行数据
  var rowData = sheet.getRange(rowNum, 1, 1, lastCol).getValues()[0];

  // 4. 构建跳转链接
  var sheetGid = sheet.getSheetId();
  var url = 'https://docs.google.com/spreadsheets/d/' + cfg.sid +
            '/edit#gid=' + sheetGid + '&range=A' + rowNum;

  // 5. 解析每个字段
  var fields = [];
  for (var j = 0; j < headers.length; j++) {
    var h = String(headers[j]).trim();
    var v = rowData[j];
    if (!h || v === '' || v === null || v === undefined) continue;

    var sv = (typeof v === 'number') ? String(v) : String(v);
    var f = { name: h, value: sv, isJson: false, refs: [] };

    // JSON 字段：解析并提取引用
    if (sv.charAt(0) === '[' || sv.charAt(0) === '{') {
      try {
        var parsed = JSON.parse(sv);
        f.value = JSON.stringify(parsed, null, 2);
        f.isJson = true;
        f.refs = _extractRefs(parsed);
      } catch (_) { /* 非法 JSON，原样显示 */ }
    }

    // 数字型外键：值 >= 7 位且前缀匹配已注册表
    if (!f.isJson && !isNaN(v) && String(Math.floor(Number(v))).length >= 7 && h !== cfg.idCol) {
      var vp = String(Math.floor(Number(v))).substring(0, 4);
      if (TABLE_REGISTRY[vp]) {
        f.refs.push({
          id: String(Math.floor(Number(v))),
          prefix: vp,
          tableName: TABLE_REGISTRY[vp].name
        });
      }
    }

    fields.push(f);
  }

  return {
    found: true,
    queriedId: idStr,
    prefix: prefix,
    tableName: cfg.name + ' (' + cfg.full + ') · ' + sheet.getName(),
    rowNumber: rowNum,
    sourceUrl: url,
    fields: fields
  };
}

// ============================================================
//  辅助：在单个页签中搜索 ID
// ============================================================

function _searchInSheet(ss, tabName, idColName, idStr) {
  var sheet = ss.getSheetByName(tabName);
  if (!sheet) return { found: false };

  var lastCol = sheet.getLastColumn();
  var lastRow = sheet.getLastRow();
  if (lastRow < 2 || lastCol < 1) return { found: false };

  var headers = sheet.getRange(1, 1, 1, lastCol).getValues()[0];
  var idIdx = _findIdCol(headers, idColName);

  // 如果指定列名找不到，尝试在整个页签全文搜索
  if (idIdx === -1) {
    var globalCell = sheet.createTextFinder(idStr).matchEntireCell(true).findNext();
    if (globalCell) {
      return { found: true, sheet: sheet, rowNum: globalCell.getRow(), headers: headers };
    }
    return { found: false };
  }

  var idRange = sheet.getRange(2, idIdx + 1, lastRow - 1, 1);
  var cell = idRange.createTextFinder(idStr).matchEntireCell(true).findNext();
  if (!cell) return { found: false };

  return { found: true, sheet: sheet, rowNum: cell.getRow(), headers: headers };
}

// ============================================================
//  辅助：查找 ID 列索引
// ============================================================

function _findIdCol(headers, target) {
  for (var i = 0; i < headers.length; i++) {
    if (String(headers[i]).trim() === target) return i;
  }
  // 回退：模糊匹配
  for (var i = 0; i < headers.length; i++) {
    var h = String(headers[i]).trim().toLowerCase();
    if (h === 'a_int_id' || h === 'id') return i;
  }
  return -1;
}

// ============================================================
//  辅助：从 JSON 递归提取 ID 引用
// ============================================================

function _extractRefs(obj) {
  var refs = [];
  _walkJson(obj, refs);
  // 去重
  var seen = {};
  var unique = [];
  for (var i = 0; i < refs.length; i++) {
    if (!seen[refs[i].id]) {
      seen[refs[i].id] = true;
      unique.push(refs[i]);
    }
  }
  return unique;
}

function _walkJson(obj, refs) {
  if (Array.isArray(obj)) {
    for (var i = 0; i < obj.length; i++) _walkJson(obj[i], refs);
    return;
  }
  if (!obj || typeof obj !== 'object') return;

  var keys = Object.keys(obj);
  for (var k = 0; k < keys.length; k++) {
    var key = keys[k];
    var val = obj[key];

    // 识别可能是 ID 的字段名
    if (/id$/i.test(key) || key === 'iap' || key === 'actv_id' || key === 'config_id') {
      if (typeof val === 'number' || (typeof val === 'string' && /^\d+$/.test(val))) {
        var ns = String(Math.floor(Number(val)));
        if (ns.length >= 5) {
          var p = ns.substring(0, 4);
          if (TABLE_REGISTRY[p]) {
            refs.push({ id: ns, prefix: p, tableName: TABLE_REGISTRY[p].name, key: key });
          }
        }
      }
    }

    // 递归
    if (typeof val === 'object' && val !== null) {
      _walkJson(val, refs);
    }
  }
}

// ============================================================
//  反向查询：哪些表引用了这个 ID
// ============================================================

function reverseSearch(idStr) {
  idStr = String(idStr).trim();
  var results = [];
  var ownPrefix = (idStr.length >= 4) ? idStr.substring(0, 4) : '';
  var prefixes = Object.keys(TABLE_REGISTRY);

  for (var p = 0; p < prefixes.length; p++) {
    var prefix = prefixes[p];
    if (prefix === ownPrefix) continue; // 跳过自身所在表
    var cfg = TABLE_REGISTRY[prefix];

    try {
      var ss = SpreadsheetApp.openById(cfg.sid);
      var sheet = ss.getSheetByName(cfg.tab);
      if (!sheet) continue;

      var matches = sheet.createTextFinder(idStr).findAll();
      if (matches.length === 0) continue;

      var locs = [];
      var limit = Math.min(matches.length, 10);
      for (var m = 0; m < limit; m++) {
        var r = matches[m];
        var colHeader = sheet.getRange(1, r.getColumn()).getValue();
        locs.push({
          row: r.getRow(),
          col: String(colHeader),
          cell: r.getA1Notation()
        });
      }

      results.push({
        prefix: prefix,
        tableName: cfg.name,
        tabName: cfg.tab,
        sid: cfg.sid,
        sheetGid: sheet.getSheetId(),
        count: matches.length,
        locations: locs
      });
    } catch (_) {
      // 无权限或表不存在 — 静默跳过
    }
  }

  return results;
}
