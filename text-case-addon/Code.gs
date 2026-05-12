/**
 * Text Case Converter
 * 使用方式：
 *   1. 把下面全部内容追加到你现有脚本末尾
 *   2. 在你已有的 onOpen() 函数里加一行：  addTextCaseMenu(ui);
 *      示例：
 *        function onOpen() {
 *          var ui = SpreadsheetApp.getUi();
 *          // ...你原有的菜单代码...
 *          addTextCaseMenu(ui);   // ← 加这一行
 *        }
 */

// ── 菜单注册（在已有 onOpen 里调用此函数） ──────────────
function addTextCaseMenu(ui) {
  ui.createMenu('文本格式')
    .addItem('首字母大写（Title Case）', 'applyTitleCase')
    .addItem('全大写（UPPER CASE）',     'applyUpperCase')
    .addItem('全小写（lower case）',     'applyLowerCase')
    .addToUi();
}

// ── 三个转换函数 ─────────────────────────────────────────
function applyTitleCase() {
  _transformRange(function(str) {
    return str.replace(/\S+/g, function(word) {
      return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
    });
  });
}

function applyUpperCase() {
  _transformRange(function(str) { return str.toUpperCase(); });
}

function applyLowerCase() {
  _transformRange(function(str) { return str.toLowerCase(); });
}

// ── 内部辅助（加下划线前缀避免与现有函数名冲突） ─────────
function _transformRange(fn) {
  var range  = SpreadsheetApp.getActiveRange();
  var values = range.getValues();

  var result = values.map(function(row) {
    return row.map(function(cell) {
      return (typeof cell === 'string' && cell.length > 0) ? fn(cell) : cell;
    });
  });

  range.setValues(result);
}
