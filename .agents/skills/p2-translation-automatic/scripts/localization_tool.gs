/**
 * 游戏本地化暂存工具 - Google Apps Script
 * 暂存区格式：✅提交 | 目标页签 | ID | cn | en | ... | cns（无 ID_int）
 * 提交时自动读取目标页签最后一行 ID_int 并顺延
 */

const STAGING_SHEET_NAME = 'AI翻译暂存';
const STAGING_HEADER = [
  '✅提交', '目标页签',
  'ID', 'cn', 'en', 'fr', 'de', 'po', 'zh',
  'id', 'th', 'sp', 'ru', 'tr', 'vi', 'it', 'pl', 'ar', 'jp', 'kr', 'cns'
];
const TARGET_HEADER = [
  'ID_int', 'ID', 'cn', 'en', 'fr', 'de', 'po', 'zh',
  'id', 'th', 'sp', 'ru', 'tr', 'vi', 'it', 'pl', 'ar', 'jp', 'kr', 'cns'
];
const PINK_COLOR = '#FFB6C1';

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('🌍 本地化工具')
    .addItem('✅ 提交选中行到对应页签', 'commitSelectedRows')
    .addSeparator()
    .addItem('☑️ 全选暂存区', 'selectAll')
    .addItem('⬜ 取消全选', 'deselectAll')
    .addSeparator()
    .addItem('🗑️ 清空暂存区', 'clearStaging')
    .addSeparator()
    .addItem('🔧 初始化暂存页签', 'initStagingSheet')
    .addToUi();
}

// ============================================================
// 初始化暂存页签
// ============================================================

function initStagingSheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(STAGING_SHEET_NAME);

  if (sheet) {
    const ui = SpreadsheetApp.getUi();
    const resp = ui.alert(
      '暂存页签已存在',
      `"${STAGING_SHEET_NAME}" 页签已存在，是否要重新初始化？\n（将清空所有内容）`,
      ui.ButtonSet.YES_NO
    );
    if (resp !== ui.Button.YES) return;
    sheet.clear();
  } else {
    sheet = ss.insertSheet(STAGING_SHEET_NAME, 0);
  }

  const headerRange = sheet.getRange(1, 1, 1, STAGING_HEADER.length);
  headerRange.setValues([STAGING_HEADER]);
  headerRange.setFontWeight('bold');
  headerRange.setBackground('#4A86C8');
  headerRange.setFontColor('#FFFFFF');

  sheet.setColumnWidth(1, 60);
  sheet.setColumnWidth(2, 100);
  sheet.setColumnWidth(3, 200);
  sheet.setColumnWidth(4, 200);
  sheet.setColumnWidth(5, 250);

  sheet.setFrozenRows(1);

  sheet.getRange(2, 1, 100, 1).insertCheckboxes();

  const tabNames = getExistingTabNames_();
  if (tabNames.length > 0) {
    const rule = SpreadsheetApp.newDataValidation()
      .requireValueInList(tabNames, true)
      .setAllowInvalid(true)
      .build();
    sheet.getRange(2, 2, 100, 1).setDataValidation(rule);
  }

  SpreadsheetApp.getUi().alert('初始化完成！暂存页签已就绪。');
}

// ============================================================
// 提交选中行到目标页签（自动生成 ID_int）
// ============================================================

function commitSelectedRows() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const staging = ss.getSheetByName(STAGING_SHEET_NAME);

  if (!staging) {
    SpreadsheetApp.getUi().alert('找不到暂存页签，请先运行"初始化暂存页签"');
    return;
  }

  const lastRow = staging.getLastRow();
  if (lastRow <= 1) {
    SpreadsheetApp.getUi().alert('暂存区为空，没有可提交的数据。');
    return;
  }

  const dataRange = staging.getRange(2, 1, lastRow - 1, STAGING_HEADER.length);
  const allData = dataRange.getValues();

  const groupedByTab = {};
  const submittedRowIndices = [];

  for (let i = 0; i < allData.length; i++) {
    const row = allData[i];
    const isChecked = row[0] === true;
    const targetTab = row[1];
    const id = row[2];

    if (!isChecked) continue;
    if (!targetTab) {
      SpreadsheetApp.getUi().alert(`第 ${i + 2} 行已勾选但未指定目标页签，请填写后重试。`);
      return;
    }
    if (!id) continue;

    const rowData = row.slice(2); // [ID, cn, en, fr, ...]
    if (!groupedByTab[targetTab]) {
      groupedByTab[targetTab] = [];
    }
    groupedByTab[targetTab].push(rowData);
    submittedRowIndices.push(i + 2);
  }

  if (submittedRowIndices.length === 0) {
    SpreadsheetApp.getUi().alert('没有勾选任何行，请先在 A 列勾选要提交的行。');
    return;
  }

  const tabSummary = Object.entries(groupedByTab)
    .map(([tab, rows]) => `  ${tab}: ${rows.length} 条`)
    .join('\n');

  const ui = SpreadsheetApp.getUi();
  const resp = ui.alert(
    '确认提交',
    `即将提交 ${submittedRowIndices.length} 条翻译：\n\n${tabSummary}\n\n确认提交？`,
    ui.ButtonSet.YES_NO
  );
  if (resp !== ui.Button.YES) return;

  const results = [];
  for (const [tabName, rows] of Object.entries(groupedByTab)) {
    let targetSheet = ss.getSheetByName(tabName);

    if (!targetSheet) {
      targetSheet = ss.insertSheet(tabName);
      targetSheet.getRange(1, 1, 1, TARGET_HEADER.length).setValues([TARGET_HEADER]);
      targetSheet.getRange(1, 1, 1, TARGET_HEADER.length).setFontWeight('bold');
    }

    // 读取目标页签最后一行的 ID_int，用于顺延
    const targetLastRow = targetSheet.getLastRow();
    let nextIdInt = 1;
    if (targetLastRow >= 2) {
      const lastIdIntValue = targetSheet.getRange(targetLastRow, 1).getValue();
      const parsed = parseInt(lastIdIntValue, 10);
      if (!isNaN(parsed)) {
        nextIdInt = parsed + 1;
      }
    }

    const startRow = targetLastRow + 1;
    const outputRows = [];
    for (const row of rows) {
      outputRows.push([nextIdInt, ...row]); // [ID_int, ID, cn, en, ...]
      nextIdInt++;
    }

    targetSheet.getRange(startRow, 1, outputRows.length, outputRows[0].length)
      .setValues(outputRows);

    targetSheet.getRange(startRow, 1, outputRows.length, outputRows[0].length)
      .setBackground(PINK_COLOR);

    const firstId = outputRows[0][0];
    const lastId = outputRows[outputRows.length - 1][0];
    results.push(`${tabName}: ${rows.length} 行 (ID_int: ${firstId} ~ ${lastId})`);
  }

  submittedRowIndices.sort((a, b) => b - a);
  for (const rowIdx of submittedRowIndices) {
    staging.deleteRow(rowIdx);
  }

  repairStagingCheckboxes_(staging);

  SpreadsheetApp.getUi().alert(
    `提交成功！已提交 ${submittedRowIndices.length} 条翻译：\n\n${results.join('\n')}\n\n已提交的行已从暂存区移除。`
  );
}

// ============================================================
// 全选 / 取消全选
// ============================================================

function selectAll() { toggleAll_(true); }
function deselectAll() { toggleAll_(false); }

function toggleAll_(value) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const staging = ss.getSheetByName(STAGING_SHEET_NAME);
  if (!staging) {
    SpreadsheetApp.getUi().alert('找不到暂存页签');
    return;
  }

  const lastRow = staging.getLastRow();
  if (lastRow <= 1) return;

  const data = staging.getRange(2, 1, lastRow - 1, 3).getValues();
  for (let i = 0; i < data.length; i++) {
    if (data[i][2]) { // ID 列有值
      staging.getRange(i + 2, 1).setValue(value);
    }
  }
}

// ============================================================
// 清空暂存区
// ============================================================

function clearStaging() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const staging = ss.getSheetByName(STAGING_SHEET_NAME);
  if (!staging) {
    SpreadsheetApp.getUi().alert('找不到暂存页签');
    return;
  }

  const ui = SpreadsheetApp.getUi();
  const resp = ui.alert(
    '清空暂存区',
    '确定要清空所有暂存数据吗？\n（表头会保留）',
    ui.ButtonSet.YES_NO
  );
  if (resp !== ui.Button.YES) return;

  const lastRow = staging.getLastRow();
  if (lastRow > 1) {
    staging.deleteRows(2, lastRow - 1);
  }

  repairStagingCheckboxes_(staging);
  ui.alert('暂存区已清空。');
}

// ============================================================
// 辅助函数
// ============================================================

function getExistingTabNames_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  return ss.getSheets()
    .map(s => s.getName())
    .filter(name => name !== STAGING_SHEET_NAME && name !== '回车检查' && name !== '本地化使用说明');
}

function repairStagingCheckboxes_(staging) {
  const lastRow = staging.getLastRow();
  const rowsNeeded = Math.max(20, lastRow + 10) - lastRow;

  if (rowsNeeded > 0 && lastRow < 101) {
    const startRow = lastRow + 1;
    const count = Math.min(rowsNeeded, 101 - lastRow);
    staging.getRange(startRow, 1, count, 1).insertCheckboxes();

    const tabNames = getExistingTabNames_();
    if (tabNames.length > 0) {
      const rule = SpreadsheetApp.newDataValidation()
        .requireValueInList(tabNames, true)
        .setAllowInvalid(true)
        .build();
      staging.getRange(startRow, 2, count, 1).setDataValidation(rule);
    }
  }
}
