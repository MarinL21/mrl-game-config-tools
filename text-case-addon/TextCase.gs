/**
 * TextCase.gs
 * 新建此文件即可，不要修改任何现有文件。
 *
 * 安装步骤（只做一次）：
 *   1. 在 Apps Script 编辑器新建文件，把此内容粘贴进去
 *   2. 顶部函数下拉框选 setupTextCaseMenu → 点运行
 *   3. 授权后，"文本格式"菜单会在每次打开表格时自动出现
 */

// ── 安装触发器（只运行一次）──────────────────────────────
function setupTextCaseMenu() {
  // 避免重复注册
  ScriptApp.getProjectTriggers().forEach(function(t) {
    if (t.getHandlerFunction() === '_textCaseOnOpen') {
      ScriptApp.deleteTrigger(t);
    }
  });

  ScriptApp.newTrigger('_textCaseOnOpen')
    .forSpreadsheet(SpreadsheetApp.getActive())
    .onOpen()
    .create();

  SpreadsheetApp.getUi().alert('文本格式菜单已安装，刷新页面后生效。');
}

// ── 菜单注册（由触发器自动调用，无需手动执行）────────────
function _textCaseOnOpen() {
  SpreadsheetApp.getUi()
    .createMenu('文本格式')
    .addItem('首字母大写（Title Case）', '_applyTitleCase')
    .addItem('全大写（UPPER CASE）',     '_applyUpperCase')
    .addItem('全小写（lower case）',     '_applyLowerCase')
    .addToUi();
}

// ── 三个转换函数 ─────────────────────────────────────────
function _applyTitleCase() {
  _textCaseTransform(function(str) {
    return str.replace(/\S+/g, function(word) {
      return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
    });
  });
}

function _applyUpperCase() {
  _textCaseTransform(function(str) { return str.toUpperCase(); });
}

function _applyLowerCase() {
  _textCaseTransform(function(str) { return str.toLowerCase(); });
}

// ── 内部辅助 ─────────────────────────────────────────────
function _textCaseTransform(fn) {
  var range  = SpreadsheetApp.getActiveRange();
  var values = range.getValues();

  var result = values.map(function(row) {
    return row.map(function(cell) {
      return (typeof cell === 'string' && cell.length > 0) ? fn(cell) : cell;
    });
  });

  range.setValues(result);
}
