// ====================== Code.gs ======================
/**
 * Base64 Encode Input
 * @param {any | Array<any[]>} input - Input cell, or range of cells
 * @param {boolean} [OPT_webSafe=true] - If should use websafe variant of base64
 * @param {boolean} [OPT_plainText=false] - If should treat input as plaintext instead of UTF-8
 */
function base64Encode(input, OPT_webSafe, OPT_plainText) {
  if (!input) return input;
  const charSet = OPT_plainText ? Utilities.Charset.US_ASCII : Utilities.Charset.UTF_8;
  const useWebSafe = OPT_webSafe !== false;
  const encoder = useWebSafe ? Utilities.base64EncodeWebSafe : Utilities.base64Encode;
  
  if (Array.isArray(input)) {
    return input.map(t => base64Encode(t, OPT_webSafe, OPT_plainText));
  }
  
  return encoder(input, charSet);
}

/**
 * Base64 Decode Input
 * @param {any | Array<any[]>} input - Input cell, or range of cells
 * @param {boolean} [OPT_webSafe=true] - If should use websafe variant of base64
 * @param {boolean} [OPT_plainText=false] - If should treat input as plaintext instead of UTF-8
 */
function base64Decode(input, OPT_webSafe, OPT_plainText) {
  if (!input) return input;
  const charSet = OPT_plainText ? Utilities.Charset.US_ASCII : Utilities.Charset.UTF_8;
  const useWebSafe = OPT_webSafe !== false;
  const decoder = useWebSafe ? Utilities.base64DecodeWebSafe : Utilities.base64Decode;
  
  if (Array.isArray(input)) {
    return input.map(t => base64Decode(t, OPT_webSafe, OPT_plainText));
  }
  
  return decoder(input, charSet);
}

/**
 * 获取当前文档中所有表格的信息（带缓存）
 * @returns {Object} 包含所有表格名称和当前表格的对象
 */
function getSheetInfo() {
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const activeSheet = ss.getActiveSheet();
    const activeSheetName = activeSheet.getName();
    
    // 只缓存表格列表，不缓存活动表格
    const cache = CacheService.getScriptCache();
    const cacheKey = 'sheet_list';
    let sheetList;
    
    const cached = cache.get(cacheKey);
    if (cached != null) {
      sheetList = JSON.parse(cached);
    } else {
      sheetList = ss.getSheets().map(sheet => sheet.getName());
      cache.put(cacheKey, JSON.stringify(sheetList), 120);
    }
    
    return {
      sheets: sheetList,
      activeSheet: activeSheetName // 总是获取最新的活动表格
    };
    
  } catch (error) {
    throw new Error("获取表格信息失败: " + error.toString());
  }
}

/**
 * 获取当前页签名称
 * @returns {string} 当前页签名称
 */
function getCurrentSheetName() {
  return SpreadsheetApp.getActiveSheet().getName();
}

/**
 * 获取当前页签A1单元格的注释
 * @returns {string} A1单元格的注释内容
 */
function getCurrentSheetA1Note() {
  try {
    const sheet = SpreadsheetApp.getActiveSheet();
    const a1Note = sheet.getRange("A1").getNote();
    return a1Note || '';
  } catch (error) {
    console.error('获取A1单元格注释失败:', error);
    return '';
  }
}

// ====================== Compare.gs ======================
// 显示配置对话框
function showCompareDialog() {
  // 每次打开对话框时清除缓存，确保获取最新数据
  var cache = CacheService.getScriptCache();
  cache.remove('sheet_info');
  
  var html = HtmlService.createHtmlOutputFromFile('CompareDialog')
    .setWidth(400)
    .setHeight(500);
  SpreadsheetApp.getUi().showModalDialog(html, '表格比较配置');
}

// 执行比较操作 - 优化数据处理
function compareSheets(config) {
  if (!config || !config.sheet1 || !config.sheet2) {
    return {
      success: false,
      message: "配置参数无效"
    };
  }

  // 检查当前表格是否为对比结果表
  var currentSheet = SpreadsheetApp.getActiveSheet();
  if (currentSheet.getName().includes(" vs ") && currentSheet.getName().endsWith("比较结果")) {
    return {
      success: false,
      message: "对比结果表不能作为对比的源表格，请切换到其他表格后再试"
    };
  }

  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet1 = ss.getSheetByName(config.sheet1);
  var sheet2 = ss.getSheetByName(config.sheet2);
  
  if (!sheet1 || !sheet2) {
    return {
      success: false,
      message: "未找到指定的表格，请检查表格名称"
    };
  }

  try {
    // 创建比较表格
    var previewName = `${config.sheet1} vs ${config.sheet2} 比较结果`;
    var previewSheet = createCompareSheet(previewName);

    // 批量获取数据以减少API调用
    var range1 = sheet1.getDataRange();
    var range2 = sheet2.getDataRange();
    
    var data1 = range1.getValues();
    var data2 = range2.getValues();
    
    // 获取表头数据
    var headers1 = data1[0];
    var headers2 = data2[0];
    
    // 使用对象来存储表头映射
    var headerMap = {};
    var unmatchedHeaders1 = [];
    var unmatchedHeaders2 = [];
    
    // 记录表头1中的列索引
    headers1.forEach((header, index) => {
      headerMap[header] = {sheet1Index: index, sheet2Index: -1};
    });
    
    // 查找表头2中对应的列索引
    headers2.forEach((header, index) => {
      if (headerMap[header]) {
        headerMap[header].sheet2Index = index;
      } else {
        unmatchedHeaders2.push({header: header, index: index});
      }
    });
    
    // 找出表头1中未匹配的列
    headers1.forEach((header, index) => {
      if (headerMap[header].sheet2Index === -1) {
        unmatchedHeaders1.push({header: header, index: index});
      }
    });

    // 找到ID列（使用常量定义的后缀）
    var idCol1 = headers1.findIndex(header => 
      header.toString().endsWith(ID_CHECKER_CONFIG.ID_COLUMN_SUFFIX));
    var idCol2 = headers2.findIndex(header => 
      header.toString().endsWith(ID_CHECKER_CONFIG.ID_COLUMN_SUFFIX));
    
    if (idCol1 === -1 || idCol2 === -1) {
      return {
        success: false,
        message: `未找到ID列（以'${ID_CHECKER_CONFIG.ID_COLUMN_SUFFIX}'结尾的列）`
      };
    }

    // 准备预览表数据
    var previewData = [headers1];
    var previewColors = [new Array(headers1.length).fill(null)];
    var previewNotes = [new Array(headers1.length).fill('')];

    // 使用Map存储表2的数据，以ID为键
    var data2Map = new Map();
    for (var i = 1; i < data2.length; i++) {
      var id = data2[i][idCol2].toString();
      if (!data2Map.has(id)) {
        data2Map.set(id, []);
      }
      data2Map.get(id).push({
        rowIndex: i,
        data: data2[i]
      });
    }

    var differences = {
      total: 0,
      modified: 0,
      added: 0,
      removed: 0,
      duplicate: 0,
      headerDiff: unmatchedHeaders1.length + unmatchedHeaders2.length
    };

    // 处理表1的数据行
    var processedIds = new Set();
    for (var i = 1; i < data1.length; i++) {
      var id = data1[i][idCol1].toString();
      var hasChanges = false;
      var rowColors = new Array(headers1.length).fill(null);
      var rowNotes = new Array(headers1.length).fill('');
      var rowData = [...data1[i]];

      var matchingRows = data2Map.get(id) || [];
      processedIds.add(id);

      if (matchingRows.length === 0) {
        // ID在表2中不存在，标记为新增行
        rowColors.fill(COMPARE_CONSTANTS.COLORS.ADDED);
        // 移除注释，只使用颜色标记
        hasChanges = true;
        differences.added++;
      } else if (matchingRows.length > 1) {
        // ID在表2中有重复
        rowColors.fill(COMPARE_CONSTANTS.COLORS.MODIFIED);
        rowNotes = rowNotes.map(note => 
          NoteManager.addSystemNote(note, NOTE_CONSTANTS.TYPES.VERSION, 
            `在对比表格中发现 ${matchingRows.length} 条重复记录`)
        );
        hasChanges = true;
        differences.duplicate++;
      } else {
        // 比较每个单元格
        for (var j = 0; j < headers1.length; j++) {
          var sheet2Col = headerMap[headers1[j]].sheet2Index;
          if (sheet2Col === -1) {
            rowColors[j] = COMPARE_CONSTANTS.COLORS.ADDED;
            rowNotes[j] = NoteManager.addSystemNote('', NOTE_CONSTANTS.TYPES.VERSION, 
              "此列在对比表格中不存在");
            hasChanges = true;
            differences.added++;
          } else {
            var value2 = matchingRows[0].data[sheet2Col];
            if (data1[i][j] !== value2) {
              rowColors[j] = COMPARE_CONSTANTS.COLORS.MODIFIED;
              rowNotes[j] = NoteManager.addSystemNote('', NOTE_CONSTANTS.TYPES.VERSION,
                `当前表格: ${data1[i][j]}\n对比表格: ${value2}`);
              hasChanges = true;
              differences.modified++;
            }
          }
        }
      }

      if (hasChanges) {
        previewData.push(rowData);
        previewColors.push(rowColors);
        previewNotes.push(rowNotes);
        differences.total++;
      }
    }

    // 检查表2中存在而表1中不存在的ID
    for (let [id, rows] of data2Map) {
      if (!processedIds.has(id)) {
        // 对于每个未处理的ID，添加一行到预览表
        var rowData = new Array(headers1.length).fill('');
        var rowColors = new Array(headers1.length).fill(COMPARE_CONSTANTS.COLORS.REMOVED);
        var rowNotes = new Array(headers1.length).fill('').map(note => 
          NoteManager.addSystemNote(note, NOTE_CONSTANTS.TYPES.VERSION, '此ID在基准表中不存在')
        );

        // 填充能对应的数据
        headers1.forEach((header, index) => {
          var sheet2Col = headerMap[header].sheet2Index;
          if (sheet2Col !== -1) {
            rowData[index] = rows[0].data[sheet2Col];
          }
        });

        if (rows.length > 1) {
          rowNotes = rowNotes.map(note => 
            NoteManager.addSystemNote(
              NoteManager.removeSystemNote(note, NOTE_CONSTANTS.TYPES.VERSION),
              NOTE_CONSTANTS.TYPES.VERSION,
              `此ID在基准表中不存在\n(在对比表格中有 ${rows.length} 条重复记录)`
            )
          );
        }

        previewData.push(rowData);
        previewColors.push(rowColors);
        previewNotes.push(rowNotes);
        differences.removed++;
        differences.total++;
      }
    }

    // 更新预览表
    var previewRange = previewSheet.getRange(1, 1, previewData.length, headers1.length);
    previewRange.setValues(previewData);
    previewRange.setBackgrounds(previewColors);
    previewRange.setNotes(previewNotes);

    // 添加比较信息到A1单元格
    var compareInfo = `对比表格: ${config.sheet2}\n` +
                     `差异总数: ${differences.total}\n` +
                     `└─ 值不同: ${differences.modified}\n` +
                     `└─ 新增项: ${differences.added}\n` +
                     `└─ 删除项: ${differences.removed}\n` +
                     `└─ 重复ID: ${differences.duplicate}\n` +
                     `└─ 表头差异: ${differences.headerDiff}\n` +
                     `比较时间: ${new Date().toLocaleString()}`;
    
    // 使用 NoteManager 添加系统注释
    var a1Cell = previewSheet.getRange(1, 1);
    var currentNote = a1Cell.getNote();
    var newNote = NoteManager.addSystemNote(
      currentNote,
      NOTE_CONSTANTS.TYPES.VERSION,
      compareInfo
    );
    a1Cell.setNote(newNote);

    // 激活预览表
    previewSheet.activate();

    // 记录比较完成的日志
    LogManager.addLog(
      LOG_CONSTANTS.TYPES.COMPARE,
      config.sheet1,
      "比较完成",
      `对比表格：${config.sheet2}\n` +
      `差异总数：${differences.total}\n` +
      `└─ 值不同：${differences.modified}\n` +
      `└─ 新增项：${differences.added}\n` +
      `└─ 删除项：${differences.removed}\n` +
      `└─ 重复ID：${differences.duplicate}\n` +
      `└─ 表头差异：${differences.headerDiff}`
    );

    return {
      success: true,
      message: `比较完成！\n发现 ${differences.total} 处差异\n${differences.modified} 处值不同\n${differences.added} 处新增\n${differences.removed} 处删除\n${differences.duplicate} 处重复ID\n${differences.headerDiff} 处表头差异`,
      differences: differences
    };
  } catch (error) {
    return {
      success: false,
      message: "发生错误: " + error.toString()
    };
  }
}

/**
 * 创建比较表格
 * @param {string} previewName 预览表格名称
 * @returns {Sheet} 比较表格
 */
function createCompareSheet(previewName) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var existingSheet = ss.getSheetByName(previewName);
  
  if (existingSheet) {
    ss.deleteSheet(existingSheet);
  }
  
  return ss.insertSheet(previewName);
}

// 清除所有高亮和注释
function clearAllHighlights(showConfirm = true) {
  var ui = SpreadsheetApp.getUi();
  
  if (showConfirm) {
    var response = ui.alert(
      '确认清除',
      '是否要清除当前表格中所有的比较标记？',
      ui.ButtonSet.YES_NO
    );

    if (response !== ui.Button.YES) {
      return;
    }
  }
  
  var sheet = SpreadsheetApp.getActiveSheet();
  var range = sheet.getDataRange();
  var backgrounds = range.getBackgrounds();
  var notes = range.getNotes();
  var values = range.getValues();
  
  var newBackgrounds = [];
  var newNotes = [];
  var newValues = [];
  var rowsToKeep = [];
  
  // 检查每一行，标记需要保留的行
  for (var i = 0; i < backgrounds.length; i++) {
    var isDeletedRow = true;
    var hasHighlight = false;
    
    // 检查这一行是否是比较时新增的行（通过检查背景色和注释）
    for (var j = 0; j < backgrounds[i].length; j++) {
      var currentBg = backgrounds[i][j];
      var currentNote = notes[i][j];
      
      if (currentBg === COMPARE_CONSTANTS.COLORS.REMOVED) {
        hasHighlight = true;
      }
      
      if (currentNote && currentNote.includes("此行在基准表中不存在")) {
        hasHighlight = true;
      }
      
      // 如果这一行有任何非高亮的单元格，说明不是新增的行
      if (currentBg !== COMPARE_CONSTANTS.COLORS.REMOVED && 
          currentBg !== COMPARE_CONSTANTS.COLORS.MODIFIED && 
          currentBg !== COMPARE_CONSTANTS.COLORS.ADDED && 
          currentBg !== COMPARE_CONSTANTS.COLORS.HEADER_MODIFIED) {
        isDeletedRow = false;
      }
    }
    
    // 如果这一行不是新增的行，或者是第一行（表头），就保留它
    if (!isDeletedRow || !hasHighlight || i === 0) {
      rowsToKeep.push(i);
      
      var backgroundRow = [];
      var noteRow = [];
      
      for (var j = 0; j < backgrounds[i].length; j++) {
        var currentBg = backgrounds[i][j];
        var currentNote = notes[i][j];
        
        // 清除所有比较标记的背景色
        if (currentBg === COMPARE_CONSTANTS.COLORS.MODIFIED || 
            currentBg === COMPARE_CONSTANTS.COLORS.ADDED || 
            currentBg === COMPARE_CONSTANTS.COLORS.REMOVED || 
            currentBg === COMPARE_CONSTANTS.COLORS.HEADER_MODIFIED) {
          backgroundRow.push(null);
        } else {
          backgroundRow.push(currentBg);
        }
        
        // 清除所有比较相关的注释
        if (currentNote) {
          // 移除版本信息注释
          currentNote = NoteManager.removeSystemNote(currentNote, NOTE_CONSTANTS.TYPES.VERSION);
          noteRow.push(currentNote || '');
        } else {
          noteRow.push('');
        }
      }
      
      newBackgrounds.push(backgroundRow);
      newNotes.push(noteRow);
      newValues.push(values[i]);
    }
  }
  
  // 如果有行被删除，更新表格
  if (rowsToKeep.length < backgrounds.length) {
    var newRange = sheet.getRange(1, 1, newBackgrounds.length, backgrounds[0].length);
    newRange.setBackgrounds(newBackgrounds);
    newRange.setNotes(newNotes);
    newRange.setValues(newValues);
    
    // 删除多余的行
    if (backgrounds.length > newBackgrounds.length) {
      sheet.deleteRows(newBackgrounds.length + 1, backgrounds.length - newBackgrounds.length);
    }
  } else {
    // 如果没有行被删除，只更新背景色和注释
    range.setBackgrounds(newBackgrounds);
    range.setNotes(newNotes);
  }
}

/**
 * 基于当前表格创建新的页签
 */
function createNewSheetTab() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var currentSheet = ss.getActiveSheet();
  
  // 弹出对话框让用户输入新页签名称
  var ui = SpreadsheetApp.getUi();
  var response = ui.prompt(
    '新建页签',
    '请输入新页签名称：\n(将基于当前页签 "' + currentSheet.getName() + '" 创建)',
    ui.ButtonSet.OK_CANCEL
  );

  // 处理用户输入
  if (response.getSelectedButton() == ui.Button.OK) {
    var newSheetName = response.getResponseText().trim();
    
    // 验证输入的名称
    if (newSheetName === '') {
      ui.alert('错误', '页签名称不能为空', ui.ButtonSet.OK);
      return;
    }
    
    // 检查是否已存在同名页签
    if (ss.getSheetByName(newSheetName)) {
      ui.alert('错误', '已存在同名页签："' + newSheetName + '"', ui.ButtonSet.OK);
      return;
    }
    
    try {
      // 复制当前页签
      var newSheet = currentSheet.copyTo(ss);
      newSheet.setName(newSheetName);
      
      // 将新页签移动到当前页签后面
      var sheets = ss.getSheets();
      var currentIndex = sheets.findIndex(function(sheet) {
        return sheet.getName() === currentSheet.getName();
      });
      ss.setActiveSheet(newSheet);
      ss.moveActiveSheet(currentIndex + 2);
      
      // 清除所有标记和系统注释
      clearAllMarks(false);  // 传入 false 以跳过确认对话框
      
      // 创建用户友好的创建信息
      var creationInfo = {
        '创建者': Session.getActiveUser().getEmail(),
        '创建时间': new Date().toLocaleString(),
        '来源页签': currentSheet.getName()
      };
      
      var a1Cell = newSheet.getRange("A1");
      var currentNote = a1Cell.getNote() || '';
      var newNote = NoteManager.addSystemNote(
        currentNote,
        NOTE_CONSTANTS.TYPES.SHEET_CREATION,
        Object.entries(creationInfo)
          .map(([key, value]) => `${key}：${value}`)
          .join('\n')
      );
      a1Cell.setNote(newNote);
      
      // 清除缓存以确保getSheetInfo()返回最新数据
      var cache = CacheService.getScriptCache();
      cache.remove('sheet_info');
      
      // 记录创建成功日志
      LogManager.addLog(
        LOG_CONSTANTS.TYPES.SHEET_CREATE,
        newSheetName,
        "创建页签成功",
        `来源页签：${currentSheet.getName()}`
      );
      
      ui.alert('成功', '已创建新页签："' + newSheetName + '"', ui.ButtonSet.OK);
    } catch (error) {
      ui.alert('错误', '创建页签失败：' + error.toString(), ui.ButtonSet.OK);
    }
  }
}

// ====================== Constants.gs ======================
// --------------------- 常量 --------------------------------

// 表格相关常量
const SHEET_CONSTANTS = {
  COLORS: {
    MODIFIED: "#b3e5fc",  // 修改 - 浅蓝色
    ADDED: "#dcedc8",    // 新增 - 淡绿色
    HEADER_MODIFIED: "#fff9c4",  // 表头修改 - 浅黄色
    CONFLICT: "#f8bbd0"  // 冲突 - 粉色
  }
};

// 合并相关常量
const MERGE_CONSTANTS = {
  ID_SUFFIX: '_INT_id',
  CONFLICT_PREFIX: '冲突: ',
  PREVIEW_SUFFIX: '_预览',
  COLORS: {
    NEW: '#dcedc8',      // 浅绿色 - 新行
    CONFLICT: '#ffdce0', // 浅红色 - 冲突
    UPDATED: '#b3e5fc',  // 浅蓝色 - 已更新
    RESOLVED: "#e8f5e9", // 已解决 - 更浅的绿色
    MERGED: "#dfcd4d"    // 合并入表 - 橘色
  }
};

// 比较相关常量
const COMPARE_CONSTANTS = {
  COLORS: {
    MODIFIED: "#ffcdd2",  // 修改 - 浅红色
    ADDED: "#dcedc8",    // 新增 - 浅绿色
    REMOVED: "#ffdce0",  // 删除 - Git风格浅红色
    HEADER_MODIFIED: "#fff9c4"  // 表头修改 - 浅黄色
  }
};

// ID检查器相关常量
const ID_CHECKER_CONFIG = {
  COLORS: {
    CONFLICT: '#ff0000',  // 冲突标记颜色 - 红色
  },
  ID_COLUMN_SUFFIX: '_INT_id',   // ID列的后缀
};

// 注释相关常量
const NOTE_CONSTANTS = {
  // 系统注释使用键值对格式
  SYSTEM_NOTE_START: '===== 系统信息开始 =====\n',
  SYSTEM_NOTE_END: '\n===== 系统信息结束 =====',
  
  TYPES: {
    BASE_VALUE: 'BASE',     // 基准值
    CONFLICT: 'CONFLICT',   // 冲突信息
    MERGE_INFO: 'MERGE',    // 合并信息
    VERSION: 'VERSION',     // 版本信息
    SHEET_CREATION: 'CREATION'  // 页签创建信息
  },

  // 添加分隔符常量
  KEY_VALUE_SEPARATOR: ': ',  // 键值分隔符
  LINE_SEPARATOR: '\n'        // 行分隔符
};

// 日志相关常量
const LOG_CONSTANTS = {
  SHEET_NAME: "配置表工具操作日志表",
  HEADERS: [
    "时间",
    "操作类型",
    "操作人",
    "操作表名",
    "操作内容",
    "详细信息"
  ],
  TYPES: {
    MERGE: "合并操作",
    COMPARE: "比较操作",
    CONFLICT_RESOLVE: "冲突解决",
    SHEET_CREATE: "创建表格",
    SHEET_UPDATE: "更新表格",
    SHEET_DELETE: "删除表格"
  },
  // 日志保留配置
  RETENTION: {
    MAX_ROWS: 10000,        // 最大保留行数
    CLEANUP_THRESHOLD: 0.9,  // 清理阈值（当达到最大行数的90%时触发清理）
    CLEANUP_TARGET: 0.7,     // 清理目标（清理后保留最大行数的70%）
    MIN_DAYS: 30            // 最小保留天数（无论行数多少，30天内的日志都保留）
  }
};

// --------------------- 常量 --------------------------------

// --------------------- NoteManager ------------------------ 

/**
 * 注释管理工具类
 */
class NoteManager {
  /**
   * 提取系统注释，自动合并多个系统注释块
   */
  static extractSystemNotes(note) {
    if (!note) return {};
    
    const systemNotes = {};
    let currentPosition = 0;
    let hasMultipleBlocks = false;
    
    // 查找所有系统注释块并合并
    while (true) {
      const start = note.indexOf(NOTE_CONSTANTS.SYSTEM_NOTE_START, currentPosition);
      if (start === -1) break;
      
      const end = note.indexOf(NOTE_CONSTANTS.SYSTEM_NOTE_END, start);
      if (end === -1) break;
      
      // 如果不是第一个块，标记存在多个块
      if (currentPosition > 0) {
        hasMultipleBlocks = true;
      }
      
      const notesSection = note.substring(
        start + NOTE_CONSTANTS.SYSTEM_NOTE_START.length,
        end
      );

      const noteRegex = /^(.+?):\s*\n([\s\S]*?)(?=\n\w+:|$)/gm;
      let match;
      
      while ((match = noteRegex.exec(notesSection)) !== null) {
        const [, key, value] = match;
        systemNotes[key.trim()] = value.trim();
      }
      
      currentPosition = end + NOTE_CONSTANTS.SYSTEM_NOTE_END.length;
    }
    
    // 如果发现多个块，自动清理并重写注释
    if (hasMultipleBlocks) {
      const cleanNote = this.removeAllSystemNotes(note);
      const systemPart = this.formatSystemNotes(systemNotes);
      const newNote = this.appendSystemNote(cleanNote, systemPart);
      
      // 如果是在单元格上下文中，尝试更新单元格注释
      try {
        const cell = SpreadsheetApp.getActiveRange();
        if (cell) {
          cell.setNote(newNote);
        }
      } catch (e) {
        // 忽略错误，因为可能不在单元格上下文中
      }
    }
    
    return systemNotes;
  }

  /**
   * 添加系统注释
   */
  static addSystemNote(originalNote, type, content) {
    // 添加参数验证
    if (!type || content === undefined) {
      throw new Error('Type and content are required');
    }
    
    // 直接使用 extractSystemNotes 进行合并处理
    const systemNotes = this.extractSystemNotes(originalNote);
    systemNotes[type] = content;
    
    const systemPart = this.formatSystemNotes(systemNotes);
    return this.appendSystemNote(this.removeAllSystemNotes(originalNote), systemPart);
  }
  
  /**
   * 获取系统注释内容
   * @param {string} note 完整注释
   * @param {string} type 注释类型
   * @returns {string|null} 系统注释内容
   */
  static getSystemNote(note, type) {
    const systemNotes = this.extractSystemNotes(note);
    return systemNotes[type] || null;
  }
  
  /**
   * 移除指定类型的系统注释
   * @param {string} note 完整注释
   * @param {string} type 注释类型
   * @returns {string} 清理后的注释
   */
  static removeSystemNote(note, type) {
    const systemNotes = this.extractSystemNotes(note);
    delete systemNotes[type];
    
    // 如果没有剩余的系统注释，返回清理后的原始注释
    if (Object.keys(systemNotes).length === 0) {
      return this.removeAllSystemNotes(note);
    }
    
    const systemPart = this.formatSystemNotes(systemNotes);
    return this.appendSystemNote(this.removeAllSystemNotes(note), systemPart);
  }
  
  /**
   * 格式化系统注释
   * @private
   * @param {Object} systemNotes 系统注释对象
   * @returns {string} 格式化后的系统注释
   */
  static formatSystemNotes(systemNotes) {
    if (Object.keys(systemNotes).length === 0) return '';
    
    const formattedNotes = Object.entries(systemNotes)
      .map(([key, value]) => `${key}${NOTE_CONSTANTS.KEY_VALUE_SEPARATOR}\n${value}`)
      .join(NOTE_CONSTANTS.LINE_SEPARATOR);
    
    return `${NOTE_CONSTANTS.SYSTEM_NOTE_START}${formattedNotes}${NOTE_CONSTANTS.SYSTEM_NOTE_END}`;
  }
  
  /**
   * 移除所有系统注释
   * @private
   * @param {string} note 完整注释
   * @returns {string} 移除系统注释后的原始注释
   */
  static removeAllSystemNotes(note) {
    if (!note) return '';
    
    const start = note.indexOf(NOTE_CONSTANTS.SYSTEM_NOTE_START);
    if (start === -1) return note;
    
    const end = note.indexOf(NOTE_CONSTANTS.SYSTEM_NOTE_END);
    if (end === -1) return note;
    
    return note.substring(0, start) + note.substring(end + NOTE_CONSTANTS.SYSTEM_NOTE_END.length);
  }
  
  /**
   * 在原始注释后追加系统注释
   * @private
   * @param {string} originalNote 原始注释
   * @param {string} systemNote 系统注释部分
   * @returns {string} 组合后的完整注释
   */
  static appendSystemNote(originalNote, systemNote) {
    if (!systemNote) return originalNote || '';
    if (!originalNote) return systemNote;
    
    return `${originalNote.trim()}\n${systemNote}`;
  }

  /**
   * 移除单元格中指定类型的标记
   * @param {Range} cell 目标单元格
   * @param {string} type 要移除的标记类型
   * @returns {boolean} 是否成功移除标记
   */
  static removeMarkFromCell(cell, type) {
    if (!cell) return false;
    
    const note = cell.getNote();
    if (!note) return false;
    
    const newNote = this.removeSystemNote(note, type);
    
    // 如果注释内容没有变化，说明没有找到对应类型的标记
    if (newNote === note) return false;
    
    // 如果新注释为空，则完全清除注释
    if (newNote.trim() === '') {
      cell.clearNote();
    } else {
      cell.setNote(newNote);
    }
    
    return true;
  }
} 

// --------------------- NoteManager ------------------------ 

// --------------------- LogManager ------------------------ 

/**
 * 日志管理工具类
 */
class LogManager {
  /**
   * 初始化日志表
   * @private
   * @returns {Sheet} 日志表对象
   */
  static _initLogSheet() {
    const ss = SpreadsheetApp.getActive();
    let sheet = ss.getSheetByName(LOG_CONSTANTS.SHEET_NAME);
    
    if (!sheet) {
      sheet = ss.insertSheet(LOG_CONSTANTS.SHEET_NAME);
      sheet.getRange(1, 1, 1, LOG_CONSTANTS.HEADERS.length)
        .setValues([LOG_CONSTANTS.HEADERS])
        .setFontWeight('bold');
      sheet.setFrozenRows(1);
    }
    
    return sheet;
  }

  /**
   * 添加日志记录
   * @param {string} type 操作类型（使用 LOG_CONSTANTS.TYPES 中的值）
   * @param {string} sheetName 操作的表名
   * @param {string} action 操作内容
   * @param {string} [details=''] 详细信息（可选）
   */
  static addLog(type, sheetName, action, details = '') {
    const sheet = this._initLogSheet();
    const user = Session.getActiveUser().getEmail();
    const timestamp = new Date().toLocaleString("zh-CN");
    
    const logRow = [
      timestamp,
      type,
      user,
      sheetName,
      action,
      details
    ];
    
    // 在第二行插入新日志（保持表头在第一行）
    sheet.insertRowAfter(1);
    sheet.getRange(2, 1, 1, logRow.length).setValues([logRow]);

    // 检查是否需要清理日志
    this._checkAndCleanupLogs(sheet);
  }

  /**
   * 检查并清理日志
   * @private
   * @param {Sheet} sheet 日志表对象
   */
  static _checkAndCleanupLogs(sheet) {
    const currentRows = sheet.getLastRow();
    const threshold = LOG_CONSTANTS.RETENTION.MAX_ROWS * LOG_CONSTANTS.RETENTION.CLEANUP_THRESHOLD;
    
    // 如果当前行数超过阈值，触发清理
    if (currentRows > threshold) {
      const targetRows = Math.floor(LOG_CONSTANTS.RETENTION.MAX_ROWS * LOG_CONSTANTS.RETENTION.CLEANUP_TARGET);
      const data = sheet.getDataRange().getValues();
      
      // 确保保留表头
      if (data.length <= 1) return;
      
      // 计算最小保留日期
      const minDate = new Date();
      minDate.setDate(minDate.getDate() - LOG_CONSTANTS.RETENTION.MIN_DAYS);
      
      // 从后往前查找需要保留的最后一行
      let deleteFromRow = data.length;
      let foundDeleteRow = false;
      
      for (let i = data.length - 1; i > 1; i--) {
        const logDate = new Date(data[i][0]);
        
        // 如果找到了一行需要删除的数据（在最小保留日期之前，且超出目标行数）
        if (logDate < minDate && i > targetRows) {
          deleteFromRow = i;
          foundDeleteRow = true;
          break;
        }
      }
      
      // 如果需要删除行
      if (deleteFromRow < data.length) {
        const rowsToDelete = data.length - deleteFromRow;
        sheet.deleteRows(deleteFromRow + 1, rowsToDelete);
        
        // 记录清理操作（插入到第二行）
        const newLog = [
          new Date().toLocaleString("zh-CN"),
          "系统维护",
          "系统",
          LOG_CONSTANTS.SHEET_NAME,
          "日志清理",
          `清理了 ${rowsToDelete} 条历史日志记录`
        ];
        sheet.insertRowAfter(1);
        sheet.getRange(2, 1, 1, newLog.length).setValues([newLog]);
      }
    }
  }

  /**
   * 手动触发日志清理
   * @param {number} [days=30] 保留天数
   */
  static manualCleanup(days = LOG_CONSTANTS.RETENTION.MIN_DAYS) {
    const sheet = this._initLogSheet();
    const data = sheet.getDataRange().getValues();
    
    if (data.length <= 1) return; // 只有表头或空表，直接返回
    
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);
    
    // 从后往前查找需要删除的行
    let deleteFromRow = data.length;
    for (let i = data.length - 1; i > 1; i--) {
      const logDate = new Date(data[i][0]);
      if (logDate < cutoffDate) {
        deleteFromRow = i;
        break;
      }
    }
    
    if (deleteFromRow < data.length) {
      const rowsToDelete = data.length - deleteFromRow;
      sheet.deleteRows(deleteFromRow + 1, rowsToDelete);
      
      // 记录清理操作（插入到第二行）
      const newLog = [
        new Date().toLocaleString("zh-CN"),
        "系统维护",
        "系统",
        LOG_CONSTANTS.SHEET_NAME,
        "手动日志清理",
        `清理了 ${rowsToDelete} 条${days}天前的历史日志记录`
      ];
      sheet.insertRowAfter(1);
      sheet.getRange(2, 1, 1, newLog.length).setValues([newLog]);
    }
  }
}

// --------------------- LogManager ------------------------ 

// ====================== IdChecker.gs ======================
/**
 * 检查指定ID是否与其他ID冲突
 */
function checkSingleIdConflict({ value, sheet: sheetName, row, column, columnName }) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // 遍历所有表格查找相同ID
  for (const sheet of ss.getSheets()) {
    const headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
    const columnIndex = headers.findIndex(header => header.toString() === columnName);
    if (columnIndex === -1 || sheet.getLastRow() <= 1) continue;
    
    // 获取列数据并检查冲突
    const data = sheet.getRange(2, columnIndex + 1, sheet.getLastRow() - 1, 1).getValues();
    for (let i = 0; i < data.length; i++) {
      const [id] = data[i];
      if (!id?.toString().trim()) continue;
      
      const isCurrentCell = sheet.getName() === sheetName && 
                          i + 2 === row && 
                          columnIndex + 1 === column;
      
      if (id.toString() === value.toString() && !isCurrentCell) {
        // 找到第一个冲突就返回
        return [{
          sheet: sheet.getName(),
          row: i + 2,
          column: columnIndex + 1
        }];
      }
    }
  }
  
  return [];
}

/**
 * 检查ID冲突并标记
 */
function checkIdConflicts(editedCell) {
  
  if (!editedCell) return;
  
  const { sheet, range } = editedCell;
  const value = range.getValue();
  if (!value) {
    range.setBackground(null);
    NoteManager.removeMarkFromCell(range, NOTE_CONSTANTS.TYPES.CONFLICT);
    return;
  }
  
  // 先移除历史标记
  NoteManager.removeMarkFromCell(range, NOTE_CONSTANTS.TYPES.CONFLICT);

  const headerValue = sheet.getRange(1, range.getColumn()).getValue();
  const conflicts = checkSingleIdConflict({
    value,
    sheet: sheet.getName(),
    row: range.getRow(),
    column: range.getColumn(),
    columnName: headerValue
  });
  
  if (conflicts.length > 0) {
    const conflictLocations = conflicts.map(loc => `${loc.sheet} 第${loc.row}行`).join('\n');
    const userNote = `在以下位置重复:\n${conflictLocations}`;
    
    range.setBackground(ID_CHECKER_CONFIG.COLORS.CONFLICT);
    range.setNote(NoteManager.addSystemNote(
      null,
      NOTE_CONSTANTS.TYPES.CONFLICT,  // 标记类型
      userNote
    ));
    
    SpreadsheetApp.getActiveSpreadsheet().toast('发现ID冲突，已用红色标记。', '警告', 3);
  }
}

// ====================== Merge.gs ======================
/**
 * 执行合并操作
 * @param {Object} config 合并配置
 * @param {Sheet} targetSheet 目标表格，如果不指定则使用config中的targetSheet
 * @returns {Object} 合并结果
 */
function mergeSheets(config, targetSheet) {
  if (!config || !config.sourceSheet || (!config.targetSheet && !targetSheet)) {
    return {
      success: false,
      message: "配置参数无效"
    };
  }

  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sourceSheet = ss.getSheetByName(config.sourceSheet);
  var targetSheetName = targetSheet ? targetSheet.getName() : config.targetSheet;
  var targetSheet = targetSheet ? targetSheet : ss.getSheetByName(targetSheetName);
  
  if (!sourceSheet || !targetSheet) {
    return {
      success: false,
      message: "未找到指定的表格，请检查表格名称"
    };
  }

  try {
    // 获取三个表的数据：源表、目标表和基准表
    var sourceRange = sourceSheet.getDataRange();
    var targetRange = targetSheet.getDataRange();
    
    var sourceData = sourceRange.getValues();
    var targetData = targetRange.getValues();
    
    // 获取源表的注释（用于获取基准值）
    var sourceNotes = sourceRange.getNotes();
    var sourceBaseData = sourceNotes.map(row => 
      row.map(note => {
        var baseValue = NoteManager.getSystemNote(note, NOTE_CONSTANTS.TYPES.BASE_VALUE);
        return baseValue;
      })
    );
    
    // 获取表头
    var sourceHeaders = sourceData[0];
    var targetHeaders = targetData[0];
    
    // 找到ID列
    var sourceIdColIndex = -1;
    var targetIdColIndex = -1;
    
    sourceHeaders.forEach((header, index) => {
      if (header.toString().endsWith(MERGE_CONSTANTS.ID_SUFFIX)) {
        sourceIdColIndex = index;
      }
    });
    
    targetHeaders.forEach((header, index) => {
      if (header.toString().endsWith(MERGE_CONSTANTS.ID_SUFFIX)) {
        targetIdColIndex = index;
      }
    });
    
    if (sourceIdColIndex === -1 || targetIdColIndex === -1) {
      return {
        success: false,
        message: `未找到ID列（以${MERGE_CONSTANTS.ID_SUFFIX}结尾的列）`
      };
    }

    // 创建表头映射
    var headerMap = {};
    sourceHeaders.forEach((header, index) => {
      headerMap[header] = {sourceIndex: index, targetIndex: -1};
    });
    
    // 检查新增列
    var newColumns = [];
    sourceHeaders.forEach((header, index) => {
      if (!targetHeaders.includes(header) && !header.toString().endsWith(MERGE_CONSTANTS.ID_SUFFIX)) {
        newColumns.push({
          header: header,
          sourceIndex: index
        });
      }
    });

    // 如果有新增列，在目标表和预览表中添加这些列
    if (newColumns.length > 0) {
      // 在目标表最后添加新列
      targetHeaders = targetHeaders.concat(newColumns.map(col => col.header));
      targetSheet.getRange(1, targetHeaders.length - newColumns.length + 1, 1, newColumns.length)
        .setValues([newColumns.map(col => col.header)])
        .setBackground(MERGE_CONSTANTS.COLORS.NEW);
      
      // 更新headerMap
      newColumns.forEach((col, idx) => {
        headerMap[col.header].targetIndex = targetHeaders.length - newColumns.length + idx;
      });
      
      // 为新列添加空值
      var emptyColumns = Array(newColumns.length).fill('');
      for (var i = 1; i < targetData.length; i++) {
        targetSheet.getRange(i + 1, targetHeaders.length - newColumns.length + 1, 1, newColumns.length)
          .setValues([emptyColumns]);
      }
      
      // 更新targetData以包含新列
      targetData = targetSheet.getDataRange().getValues();
    }

    targetHeaders.forEach((header, index) => {
      if (headerMap[header]) {
        headerMap[header].targetIndex = index;
      }
    });

    // 将目标表数据转换为以ID为键的Map
    var targetDataMap = new Map();
    for (var i = 1; i < targetData.length; i++) {
      var id = targetData[i][targetIdColIndex];
      if (id) {
        targetDataMap.set(id.toString(), {
          rowIndex: i,
          data: targetData[i],
        });
      }
    }

    // 记录需要处理的变更
    var changes = {
      newRows: [],
      updates: [], // 新增：记录可以直接更新的行
      conflicts: []
    };

    // 处理源表数据
    for (var i = 1; i < sourceData.length; i++) {
      var sourceRow = sourceData[i];
      var id = sourceRow[sourceIdColIndex];
      
      if (!id) continue; // 跳过空ID行
      
      id = id.toString();
      var targetRow = targetDataMap.get(id);
      
      if (!targetRow) {
        // 新行，直接添加到新行列表
        changes.newRows.push(sourceRow);
      } else {
        // 检查修改情况
        var hasConflict = false;
        var conflictColumns = [];
        var updateColumns = [];
        
        for (var header in headerMap) {
          var sourceIndex = headerMap[header].sourceIndex;
          var targetIndex = headerMap[header].targetIndex;
          
          if (targetIndex === -1) continue; // 跳过目标表中不存在的列
          
          // 目标表中的当前值
          var currentValue = targetRow.data[targetIndex];
          // 当前表的当前值
          var sourceValue = sourceRow[sourceIndex];
          // 当前表中标记的 base
          var sourceBaseValue = sourceBaseData[i][sourceIndex];
          
          // 检查源表和目标表是否都进行了修改
          var sourceModified = sourceBaseValue && normalizeValue(sourceValue) !== normalizeValue(sourceBaseValue);
          if (sourceModified && normalizeValue(sourceBaseValue) !== normalizeValue(currentValue) && normalizeValue(sourceValue) !== normalizeValue(currentValue) ) {
            hasConflict = true;
            Logger.log('the value %s %s %s ', normalizeValue(sourceValue), normalizeValue(currentValue), normalizeValue(sourceBaseValue))
            conflictColumns.push({
              header: header,
              sourceValue: normalizeValue(sourceValue),
              targetValue: normalizeValue(currentValue),
              sourceBaseValue: normalizeValue(sourceBaseValue),
            });
          } else if (sourceModified) {
            updateColumns.push({
              header: header,
              sourceValue: sourceValue,
              baseValue: sourceValue // 更新基准值为新的源值
            });
          }
        }
        
        if (hasConflict) {
          changes.conflicts.push({
            id: id,
            sourceRowIndex: i,
            targetRowIndex: targetRow.rowIndex,
            columns: conflictColumns
          });
        } else if (updateColumns.length > 0) {
          changes.updates.push({
            id: id,
            sourceRowIndex: i,
            targetRowIndex: targetRow.rowIndex,
            columns: updateColumns
          });
        }
      }
    }

    // 处理变更
    // 1. 添加新行（按ID顺序插入）
    if (changes.newRows.length > 0) {
      const insertResult = batchInsertRowsInOrder(
        targetSheet,
        changes.newRows,
        targetIdColIndex,
        {
          newRowColor: MERGE_CONSTANTS.COLORS.NEW,
          addBaseNotes: true
        }
      );
      
      if (!insertResult.success) {
        throw new Error(`无法插入新行: ${insertResult.message}`);
      }
      
      // 插入新行后，重新获取目标表数据和ID映射
      // 因为排序可能改变了行的顺序
      var updatedTargetData = targetSheet.getDataRange().getValues();
      var updatedTargetMap = new Map();
      
      for (var i = 1; i < updatedTargetData.length; i++) {
        var id = updatedTargetData[i][targetIdColIndex];
        if (id) {
          updatedTargetMap.set(id.toString(), {
            rowIndex: i,
            data: updatedTargetData[i]
          });
        }
      }
      
      // 更新changes中的targetRowIndex
      changes.updates.forEach(update => {
        const mappedRow = updatedTargetMap.get(update.id);
        if (mappedRow) {
          update.targetRowIndex = mappedRow.rowIndex;
        }
      });
      
      changes.conflicts.forEach(conflict => {
        const mappedRow = updatedTargetMap.get(conflict.id);
        if (mappedRow) {
          conflict.targetRowIndex = mappedRow.rowIndex;
        }
      });
    }

    // 2. 处理可以直接更新的行
    changes.updates.forEach(update => {
      update.columns.forEach(col => {
        var targetIndex = headerMap[col.header].targetIndex;
        var range = targetSheet.getRange(update.targetRowIndex + 1, targetIndex + 1);
        range.setValue(col.sourceValue);
        range.setBackground(MERGE_CONSTANTS.COLORS.UPDATED);
        
        // 更新基准值注释 - 使用保留格式的方法
        const currentNote = range.getNote();
        const newNote = NoteManager.addSystemNote(
          NoteManager.removeSystemNote(currentNote, NOTE_CONSTANTS.TYPES.BASE_VALUE),
          NOTE_CONSTANTS.TYPES.BASE_VALUE,
          normalizeValue(col.sourceValue) // 使用新函数
        );
        range.setNote(newNote);
      });
    });

    // 3. 标记冲突
    changes.conflicts.forEach(conflict => {
      conflict.columns.forEach(col => {
        var targetIndex = headerMap[col.header].targetIndex;
        var range = targetSheet.getRange(conflict.targetRowIndex + 1, targetIndex + 1);
        range.setBackground(MERGE_CONSTANTS.COLORS.CONFLICT);
        
        Logger.log('targetValue %s', col.targetValue)
        const targetValueFormatted = normalizeValue(col.targetValue);
        const sourceValueFormatted = normalizeValue(col.sourceValue);
        
        const conflictInfo = `${config.targetSheet}: ${targetValueFormatted}\n${config.sourceSheet}: ${sourceValueFormatted}`;
        const currentNote = range.getNote();
        const newNote = NoteManager.addSystemNote(
          NoteManager.removeSystemNote(currentNote, NOTE_CONSTANTS.TYPES.CONFLICT),
          NOTE_CONSTANTS.TYPES.CONFLICT,
          conflictInfo
        );
        range.setNote(newNote);
      });
    });

    // 在合并成功后记录日志
    LogManager.addLog(
      LOG_CONSTANTS.TYPES.MERGE,
      config.sourceSheet,
      "生成合并预览成功",
      `目标表格：${targetSheetName}\n` +
      `新增行数：${changes.newRows.length}\n` +
      `更新行数：${changes.updates.length}\n` +
      `冲突行数：${changes.conflicts.length}`
    );

    return {
      success: true,
      message: `合并完成\n新增行数: ${changes.newRows.length}\n更新行数: ${changes.updates.length}\n冲突行数: ${changes.conflicts.length}`,
      changes: changes
    };
  } catch (error) {
    return {
      success: false,
      message: "合并过程中出错: " + error.toString()
    };
  }
}

/**
 * 从注释中提取基准值
 */
function extractBaseValue(note) {
  return NoteManager.getSystemNote(note, NOTE_CONSTANTS.TYPES.BASE_VALUE);
}

/**
 * 确认合并预览表到目标表
 * @param {string} sourceSheetName 源表格名称
 * @param {string} targetSheetName 目标表格名称
 * @param {string} previewSheetName 预览表格名称
 * @returns {Object} 合并结果
 */
function confirmMergeFromPreview(sourceSheetName, targetSheetName, previewSheetName) {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sourceSheet = ss.getSheetByName(sourceSheetName);
    var targetSheet = ss.getSheetByName(targetSheetName);
    var previewSheet = ss.getSheetByName(previewSheetName);
    
    if (!sourceSheet || !targetSheet || !previewSheet) {
      return {
        success: false,
        message: "未找到指定的表格，请检查表格名称"
      };
    }

    // 获取预览表的数据和注释
    var previewRange = previewSheet.getDataRange();
    var previewData = previewRange.getValues();
    var previewNotes = previewRange.getNotes();
    var previewBackgrounds = previewRange.getBackgrounds();
    
    // 检查是否存在未解决的冲突
    var hasUnresolvedConflicts = false;
    for (var i = 0; i < previewNotes.length; i++) {
      for (var j = 0; j < previewNotes[i].length; j++) {
        var note = previewNotes[i][j];
        var conflictInfo = NoteManager.getSystemNote(note, NOTE_CONSTANTS.TYPES.CONFLICT);
        if (conflictInfo) {
          hasUnresolvedConflicts = true;
          break;
        }
      }
      if (hasUnresolvedConflicts) break;
    }
    
    if (hasUnresolvedConflicts) {
      return {
        success: false,
        message: "存在未解决的冲突，请先解决所有冲突后再确认合并"
      };
    }

    // 找到ID列以识别新行
    var idColIndex = -1;
    var headers = previewData[0];
    headers.forEach((header, index) => {
      if (header.toString().endsWith(MERGE_CONSTANTS.ID_SUFFIX)) {
        idColIndex = index;
      }
    });
    
    if (idColIndex === -1) {
      return {
        success: false,
        message: `未找到ID列（以${MERGE_CONSTANTS.ID_SUFFIX}结尾的列）`
      };
    }

    // 获取变更行信息
    var rowsWithChanges = [];
    var newRowData = [];
    
    // 记录所有有变化的行
    for (var i = 0; i < previewData.length; i++) {
      var hasChanges = false;
      for (var j = 0; j < previewData[i].length; j++) {
        var background = previewBackgrounds[i][j];
        if (background === MERGE_CONSTANTS.COLORS.NEW || 
            background === MERGE_CONSTANTS.COLORS.UPDATED || 
            background === MERGE_CONSTANTS.COLORS.RESOLVED) {
          hasChanges = true;
        }
      }
      
      if (hasChanges) {
        if (i > 0 && previewBackgrounds[i][0] === MERGE_CONSTANTS.COLORS.NEW) {
          // 新行，需要在目标表中插入
          newRowData.push({
            rowIndex: i,
            id: previewData[i][idColIndex],
            data: previewData[i],
            notes: previewNotes[i]
          });
        } else {
          // 更新的现有行
          rowsWithChanges.push(i);
        }
      }
    }
    
    // 对目标表的修改
    Logger.log('current changes %s', rowsWithChanges)

    // 1. 先处理新行插入（会改变行数和可能改变行的顺序）
    if (newRowData.length > 0) {
      // 将newRowData格式转换为batchInsertRowsInOrder所需格式
      const formattedNewRows = newRowData.map(row => row.data);
      
      const insertResult = batchInsertRowsInOrder(
        targetSheet,
        formattedNewRows,
        idColIndex,
        {
          newRowColor: MERGE_CONSTANTS.COLORS.MERGED,
          addBaseNotes: true
        }
      );
      
      if (!insertResult.success) {
        throw new Error(`确认合并时无法插入新行: ${insertResult.message}`);
      }
      
      // 插入后重新获取目标表和预览表的行映射关系
      // 这步非常重要，因为行的顺序可能已经改变
      var targetData = targetSheet.getDataRange().getValues();
      var targetIdMap = new Map();
      
      // 建立ID到行索引的映射
      for (var i = 1; i < targetData.length; i++) {
        var id = targetData[i][idColIndex];
        if (id) {
          targetIdMap.set(id.toString(), i);
        }
      }
      
      // 更新rowsWithChanges中的行索引，使其与目标表一致
      var updatedRowsWithChanges = [];
      for (var i = 0; i < rowsWithChanges.length; i++) {
        var rowIndex = rowsWithChanges[i];
        if (rowIndex > 0) { // 跳过表头
          var id = previewData[rowIndex][idColIndex];
          if (id) {
            var targetRowIndex = targetIdMap.get(id.toString());
            if (targetRowIndex !== undefined) {
              updatedRowsWithChanges.push({
                previewIndex: rowIndex,
                targetIndex: targetRowIndex
              });
            }
          }
        }
      }
      
      // 2. 然后处理现有行的更新（使用更新后的行索引）
      for (var i = 0; i < updatedRowsWithChanges.length; i++) {
        var indices = updatedRowsWithChanges[i];
        var previewRowIndex = indices.previewIndex;
        var targetRowIndex = indices.targetIndex;
        
        for (var j = 0; j < previewData[previewRowIndex].length; j++) {
          var background = previewBackgrounds[previewRowIndex][j];
          // 检查单元格是否有变化
          if (background === MERGE_CONSTANTS.COLORS.UPDATED || 
              background === MERGE_CONSTANTS.COLORS.RESOLVED ||
              background === MERGE_CONSTANTS.COLORS.NEW) {
            var targetCell = targetSheet.getRange(targetRowIndex + 1, j + 1);
            targetCell.setValue(previewData[previewRowIndex][j]);
            targetCell.setNote(previewNotes[previewRowIndex][j]);
            targetCell.setBackground(MERGE_CONSTANTS.COLORS.MERGED);
          }
        }
      }
    } else {
      // 如果没有新行，可以直接处理更新（不需要重新映射）
      // 处理现有行的更新
      for (var i = 0; i < rowsWithChanges.length; i++) {
        var rowIndex = rowsWithChanges[i];
        for (var j = 0; j < previewData[rowIndex].length; j++) {
          var background = previewBackgrounds[rowIndex][j];
          // 检查单元格是否有变化
          if (background === MERGE_CONSTANTS.COLORS.UPDATED || 
              background === MERGE_CONSTANTS.COLORS.RESOLVED ||
              background === MERGE_CONSTANTS.COLORS.NEW) {
            var targetCell = targetSheet.getRange(rowIndex + 1, j + 1);
            targetCell.setValue(previewData[rowIndex][j]);
            targetCell.setNote(previewNotes[rowIndex][j]);
            targetCell.setBackground(MERGE_CONSTANTS.COLORS.MERGED);
          }
        }
      }
    }

    // 标记源表为已合并
    var headerRow = sourceSheet.getRange(1, 1, 1, sourceSheet.getLastColumn()).getValues()[0];
    var statusColIndex = -1;
    
    // 在源表格名称后添加"(已合并)"标记
    const newSourceSheetName = sourceSheetName.endsWith('(已合并)') 
      ? sourceSheetName 
      : `${sourceSheetName}(已合并)`;
    sourceSheet.setName(newSourceSheetName);
    
    // 删除预览表
    ss.deleteSheet(previewSheet);
    
    // 清除预览状态
    const cache = CacheService.getScriptCache();
    cache.remove('merge_preview_state');
    
    // 激活目标页签
    targetSheet.activate();
    
    // 记录确认合并成功的日志
    LogManager.addLog(
      LOG_CONSTANTS.TYPES.MERGE,
      sourceSheetName,
      "确认合并成功",
      `目标表格：${targetSheetName}`
    );
    
    return {
      success: true,
      message: "合并完成！只更新了变更的单元格。源表已标记为已合并状态。",
      newRowCount: newRowData.length
    };
    
  } catch (error) {
    console.error('确认合并失败:', error);
    return {
      success: false,
      message: "确认合并过程中出错: " + error.toString()
    };
  }
}

/**
 * 获取预览状态
 * @param {string} sourceSheet 源表格名称
 * @param {string} targetSheet 目标表格名称
 * @returns {Object|null} 预览状态对象，如果没有则返回null
 */
function getPreviewState(sourceSheet, targetSheet) {
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const previewSheetName = `${sourceSheet} -> ${targetSheet} 合并预览`;
    const previewSheet = ss.getSheetByName(previewSheetName);
    
    if (!previewSheet) {
      return null;
    }
    
    return {
      previewSheetName: previewSheetName,
      sourceSheet: sourceSheet,
      targetSheet: targetSheet
    };
  } catch (e) {
    console.error('获取预览状态失败:', e);
    return null;
  }
}

/**
 * 显示确认对话框
 */
function showConfirmDialog() {
  try {
    // 获取当前活动页签
    const activeSheet = SpreadsheetApp.getActiveSheet();
    const sheetName = activeSheet.getName();
    console.log('当前页签名称:', sheetName);
    
    // 从页签名称中解析源表和目标表
    // 预览页签的命名格式为: "sourceSheet -> targetSheet 合并预览"
    const match = sheetName.match(/^(.*?)\s*->\s*(.*?)\s*合并预览$/);
    console.log('页签名称匹配结果:', match);
    
    if (!match) {
      showAlert('请在合并预览页签中使用此功能');
      return;
    }
    
    const [_, sourceSheet, targetSheet] = match;
    console.log('解析出的源表和目标表:', { sourceSheet, targetSheet });
    
    // 检查预览状态
    const previewState = getPreviewState(sourceSheet.trim(), targetSheet.trim());
    console.log('获取到的预览状态:', previewState);
    
    if (!previewState) {
      showAlert('未找到有效的预览状态，请重新执行合并预览');
      return;
    }
    
    console.log('准备显示对话框');
    // 显示合并对话框
    const ui = SpreadsheetApp.getUi();
    const html = HtmlService.createHtmlOutputFromFile('MergeDialog')
      .setWidth(600)
      .setHeight(600)
      .setTitle('合并表格');
    
    ui.showModalDialog(html, '合并表格');
    console.log('对话框已显示');
  } catch (error) {
    console.error('显示确认对话框失败:', error);
    showAlert('显示确认对话框失败: ' + error.toString());
  }
}

/**
 * 预览合并结果
 * @param {Object} config 合并配置
 * @returns {Object} 预览结果
 */
function previewMerge(config) {
  if (!config || !config.sourceSheet || !config.targetSheet) {
    return {
      success: false,
      message: "配置参数无效"
    };
  }

  var ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // 检查是否已存在预览状态
  const existingPreview = getPreviewState(config.sourceSheet, config.targetSheet);
  if (existingPreview) {
    return {
      success: false,
      message: `已存在 "${config.sourceSheet} -> ${config.targetSheet}" 的预览，请先完成或取消现有预览`
    };
  }

  Logger.log('解析预合并参数: %s', config);
  var sourceSheet = ss.getSheetByName(config.sourceSheet);
  var targetSheet = ss.getSheetByName(config.targetSheet);
  
  if (!sourceSheet || !targetSheet) {
    return {
      success: false,
      message: "未找到指定的表格，请检查表格名称"
    };
  }

  try {
    // 创建预览表格
    var previewSheet = createPreviewSheet(config.targetSheet, config.sourceSheet);
    
    // 复制目标表格的数据到预览表格，但不包括背景色和系统注释
    var targetRange = targetSheet.getDataRange();
    var targetData = targetRange.getValues();
    
    // 只复制数据，不复制格式和注释
    previewSheet.getRange(1, 1, targetData.length, targetData[0].length).setNumberFormat("@")
    previewSheet.getRange(1, 1, targetData.length, targetData[0].length)
      .setValues(targetData);

    // 执行合并预览
    var result = mergeSheets(config, previewSheet);
    
    if (result.success) {
      return {
        success: true,
        previewSheetName: previewSheet.getName(),
        sourceSheet: config.sourceSheet,
        targetSheet: config.targetSheet,
        changes: result.changes,
        message: `预览已生成，请在"${previewSheet.getName()}"表格中查看\n${result.message}`
      };
    } else {
      // 如果预览失败，删除预览表格
      deletePreviewSheet(previewSheet.getName());
      return result;
    }
  } catch (error) {
    console.error('预览失败:', error);
    return {
      success: false,
      message: "预览生成失败：" + error.toString()
    };
  }
}

/**
 * 删除预览表格
 * @param {string} previewSheetName 预览表格名称
 * @returns {boolean} 是否成功删除
 */
function deletePreviewSheet(previewSheetName) {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName(previewSheetName);
    if (sheet) {
      ss.deleteSheet(sheet);
      return true;
    }
    return false;
  } catch (error) {
    console.error('删除预览表格失败:', error);
    return false;
  }
}

/**
 * 解决合并冲突
 * @param {Object} config 解决配置
 * @returns {Object} 操作结果
 */
function resolveConflict(config) {
  if (!config || !config.row || !config.header || config.value === undefined) {
    return {
      success: false,
      message: "参数无效"
    };
  }

  try {
    var sheet = SpreadsheetApp.getActiveSheet();
    var headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
    
    // 找到对应的列
    var colIndex = headers.findIndex(h => h === config.header);
    if (colIndex === -1) {
      return {
        success: false,
        message: "未找到指定列: " + config.header
      };
    }

    // 更新单元格值
    var cell = sheet.getRange(config.row + 1, colIndex + 1);
    cell.setValue(config.value);
    cell.setBackground(MERGE_CONSTANTS.COLORS.RESOLVED);
    
    // 更新注释：清除冲突信息，更新基准值
    const currentNote = cell.getNote();
    let newNote = NoteManager.removeSystemNote(currentNote, NOTE_CONSTANTS.TYPES.CONFLICT);
    newNote = NoteManager.addSystemNote(
      newNote,
      NOTE_CONSTANTS.TYPES.BASE_VALUE,
      normalizeValue(config.value) // 使用新函数
    );
    cell.setNote(newNote);

    return {
      success: true,
      message: "已更新单元格值"
    };
  } catch (error) {
    return {
      success: false,
      message: "更新失败: " + error.toString()
    };
  }
}

/**
 * 显示提示信息
 * @param {string} message 提示信息
 */
function showAlert(message) {
  SpreadsheetApp.getUi().alert(message);
}

/**
 * 显示对话框
 * @param {string} [dialogType='merge'] 对话框类型
 */
function showDialog(dialogType = 'merge') {
  // 创建新的对话框实例
  var html = HtmlService.createHtmlOutputFromFile('MergeDialog')
    .setWidth(600)
    .setHeight(600)
    .setTitle('合并表格');
  
  // 使用showModalDialog而不是showDialog以确保对话框总是在前面
  SpreadsheetApp.getUi().showModalDialog(html, '合并表格');
}

/**
 * 创建预览表格
 * @param {string} targetSheetName 目标表格名称
 * @param {string} sourceSheetName 源表格名称
 * @returns {Sheet} 预览表格
 */
function createPreviewSheet(targetSheetName, sourceSheetName) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var previewName = `${sourceSheetName} -> ${targetSheetName} 合并预览`;
  var existingSheet = ss.getSheetByName(previewName);
  if (existingSheet) {
    ss.deleteSheet(existingSheet);
  }
  return ss.insertSheet(previewName);
}

/**
 * 显示合并对话框
 */
function showMergeDialog() {
  // 检查当前表格是否已经标记为已合并
  var currentSheet = SpreadsheetApp.getActiveSheet();
  var currentSheetName = currentSheet.getName();
  
  if (currentSheetName.endsWith('(已合并)')) {
    SpreadsheetApp.getUi().alert(
      '无法合并',
      '当前表格已经标记为已合并状态，不能重复发起合并。',
      SpreadsheetApp.getUi().ButtonSet.OK
    );
    return;
  }

  var html = HtmlService.createHtmlOutputFromFile('MergeDialog')
    .setWidth(500)
    .setHeight(500);
  SpreadsheetApp.getUi().showModalDialog(html, '表格合并工具');
}

// 用于比较ID的辅助函数
function compareIds(idA, idB) {
  // 尝试将ID解析为数字进行比较
  const numA = parseFloat(idA);
  const numB = parseFloat(idB);
  
  // 如果都是有效数字，按数字大小排序
  if (!isNaN(numA) && !isNaN(numB)) {
    return numA - numB;
  }
  
  // 否则按字符串排序
  return idA.localeCompare(idB);
}

/**
 * 优化的ID排序和行插入函数 - 在预览和确认合并时共用
 * @param {Sheet} sheet 目标表格
 * @param {Array} newRows 要插入的新行
 * @param {number} idColIndex ID列索引
 * @param {Object} options 可选配置项
 * @returns {Object} 处理结果
 */
function batchInsertRowsInOrder(sheet, newRows, idColIndex, options = {}) {
  if (newRows.length === 0) return { success: true, message: "没有新行需要插入" };
  
  try {
    const defaults = {
      preserveFormatting: true,    // 是否保留现有格式
      newRowColor: MERGE_CONSTANTS.COLORS.NEW,  // 新行的背景色
      addBaseNotes: true,          // 是否添加基准值注释
      batchSize: 1000              // 批量处理的最大行数
    };
    
    const config = { ...defaults, ...options };
    
    // 获取当前表所有数据、注释和格式
    const currentData = sheet.getDataRange().getValues();
    const currentNotes = config.addBaseNotes ? sheet.getDataRange().getNotes() : null;
    const currentBackgrounds = config.preserveFormatting ? sheet.getDataRange().getBackgrounds() : null;
    
    const headerRow = currentData[0];
    const dataRows = currentData.slice(1); // 不包括表头
    
    // 计算所需的列数(取最大值)
    const maxColumns = Math.max(
      headerRow.length,
      ...newRows.map(row => row.length)
    );
    
    // 提取所有已有ID和对应整行数据
    const existingIds = new Map();
    dataRows.forEach((row, idx) => {
      const id = row[idColIndex]?.toString();
      if (id) {
        // 确保存储完整行数据
        existingIds.set(id, {
          data: [...row], // 复制整行数据
          index: idx + 1, // 实际行号(从1开始)，不包括表头
          notes: config.addBaseNotes ? currentNotes[idx + 1] : null,
          background: config.preserveFormatting ? currentBackgrounds[idx + 1] : null
        });
      }
    });
    
    // 准备新行数据和ID
    const newRowsMap = new Map();
    newRows.forEach((row, idx) => {
      const id = row[idColIndex]?.toString();
      if (id) {
        // 确保行长度一致并按需格式化每个值
        const paddedRow = [];
        for (let i = 0; i < row.length; i++) {
          // 检查对应的列名是否有特定前缀
          const columnHeader = i < headerRow.length ? headerRow[i] : '';
          
          // 如果列名以A_BOL_开头且值是布尔类型，则应用格式化
          if (columnHeader && columnHeader.toString().startsWith('A_BOL_')) {
            // 对布尔值应用normalizeValue
            Logger.log('bol init %s', row[i])
            paddedRow.push(normalizeValue(row[i]));
          } else {
            // 其他值保持原样
            paddedRow.push(row[i]);
          }
        }
        
        // 填充剩余列
        while (paddedRow.length < maxColumns) {
          paddedRow.push('');
        }
        
        newRowsMap.set(id, {
          data: paddedRow, // 存储处理后的完整行数据
          originalIndex: idx
        });
      }
    });
    
    // 合并所有唯一ID并排序
    const allIds = [...new Set([...existingIds.keys(), ...newRowsMap.keys()])];
    allIds.sort(compareIds);
    
    // 创建完整的排序数据集
    const sortedData = [headerRow]; // 先放入表头
    const sortedNotes = config.addBaseNotes ? [currentNotes[0]] : null; 
    const sortedBackgrounds = config.preserveFormatting ? [currentBackgrounds[0]] : null;
    const newRowIndices = [];
    
    allIds.forEach((id, idx) => {
      const rowIndex = idx + 1; // 实际行索引（从0开始，不包括表头）
      
      if (newRowsMap.has(id)) {
        // 这是一个新行 - 保持整行数据关联
        const newRow = newRowsMap.get(id);
        sortedData.push(newRow.data); // 插入完整行数据
        newRowIndices.push(rowIndex + 1); // +1 是因为包括表头
        
        if (config.addBaseNotes) {
          // 为新行创建基准值注释
          const rowNotes = [];
          for (let i = 0; i < newRow.data.length; i++) {
            const value = newRow.data[i];
            const columnHeader = i < headerRow.length ? headerRow[i] : '';
            
            let noteValue = value;
            // 如果列名以A_BOL_开头且值是布尔类型，则应用格式化
            if (columnHeader && columnHeader.toString().startsWith('A_BOL_') && 
                (typeof value === 'boolean' || 
                 (typeof value === 'string' && (value.toUpperCase() === 'TRUE' || value.toUpperCase() === 'FALSE')))) {
              noteValue = normalizeValue(value);
            }
            
            rowNotes.push(NoteManager.addSystemNote('', NOTE_CONSTANTS.TYPES.BASE_VALUE, 
              noteValue !== null && noteValue !== undefined ? String(noteValue) : ''));
          }
          sortedNotes.push(rowNotes);
        }
        
        if (config.preserveFormatting) {
          // 为新行准备背景色
          const rowBackground = Array(maxColumns).fill(config.newRowColor);
          sortedBackgrounds.push(rowBackground);
        }
      } else if (existingIds.has(id)) {
        // 这是现有行 - 同样保持整行数据关联
        const existingRow = existingIds.get(id);
        
        // 确保行长度一致并按需格式化值
        const paddedRow = [];
        for (let i = 0; i < existingRow.data.length; i++) {
          // 检查对应的列名是否有特定前缀
          const columnHeader = i < headerRow.length ? headerRow[i] : '';
          
          // 如果列名以A_BOL_开头且值是布尔类型，则应用格式化
          if (columnHeader && columnHeader.toString().startsWith('A_BOL_') && 
              (typeof existingRow.data[i] === 'boolean' || 
               (typeof existingRow.data[i] === 'string' && (existingRow.data[i].toUpperCase() === 'TRUE' || existingRow.data[i].toUpperCase() === 'FALSE')))) {
            // 对布尔值应用normalizeValue
            paddedRow.push(normalizeValue(existingRow.data[i]));
          } else {
            // 其他值保持原样
            paddedRow.push(existingRow.data[i]);
          }
        }
        
        // 填充剩余列
        while (paddedRow.length < maxColumns) {
          paddedRow.push('');
        }
        sortedData.push(paddedRow);
        
        if (config.addBaseNotes) {
          sortedNotes.push(existingRow.notes);
        }
        
        if (config.preserveFormatting) {
          sortedBackgrounds.push(existingRow.background);
        }
      }
    });
    
    // 清除并批量写入数据
    if (sortedData.length > config.batchSize) {
      // 对于大数据集，分批处理
      const batchCount = Math.ceil(sortedData.length / config.batchSize);
      
      // 先调整表格大小以适应所有数据
      sheet.clear();
      if (sheet.getMaxRows() < sortedData.length) {
        sheet.insertRows(1, sortedData.length - sheet.getMaxRows());
      }
      if (sheet.getMaxColumns() < maxColumns) {
        sheet.insertColumns(1, maxColumns - sheet.getMaxColumns());
      }
      
      // 分批写入数据
      for (let i = 0; i < batchCount; i++) {
        const startRow = i * config.batchSize + 1;
        const batchRowCount = Math.min(config.batchSize, sortedData.length - i * config.batchSize);
        
        if (batchRowCount <= 0) break;
        
        const batchData = sortedData.slice(startRow - 1, startRow - 1 + batchRowCount);
        sheet.getRange(startRow, 1, batchRowCount, maxColumns).setValues(batchData);
        
        if (config.addBaseNotes) {
          const batchNotes = sortedNotes.slice(startRow - 1, startRow - 1 + batchRowCount);
          sheet.getRange(startRow, 1, batchRowCount, maxColumns).setNotes(batchNotes);
        }
        
        if (config.preserveFormatting) {
          const batchBackgrounds = sortedBackgrounds.slice(startRow - 1, startRow - 1 + batchRowCount);
          sheet.getRange(startRow, 1, batchRowCount, maxColumns).setBackgrounds(batchBackgrounds);
        }
      }
    } else {
      // 对于小数据集，一次性处理
      sheet.clear();
      if (sheet.getMaxRows() < sortedData.length) {
        sheet.insertRows(1, sortedData.length - sheet.getMaxRows());
      }
      if (sheet.getMaxColumns() < maxColumns) {
        sheet.insertColumns(1, maxColumns - sheet.getMaxColumns());
      }
      
      sheet.getRange(1, 1, sortedData.length, maxColumns).setNumberFormat("@");
      sheet.getRange(1, 1, sortedData.length, maxColumns).setValues(sortedData);
      
      if (config.addBaseNotes) {
        sheet.getRange(1, 1, sortedData.length, maxColumns).setNotes(sortedNotes);
      }
      
      if (config.preserveFormatting) {
        sheet.getRange(1, 1, sortedData.length, maxColumns).setBackgrounds(sortedBackgrounds);
      }
    }
    
    return {
      success: true,
      message: `成功按ID顺序插入了 ${newRowIndices.length} 行`,
      newRowCount: newRowIndices.length,
      sortedData: sortedData,
      newRowIndices: newRowIndices
    };
  } catch (error) {
    console.error('批量插入行失败:', error);
    return {
      success: false,
      message: `批量插入行失败: ${error.toString()}`
    };
  }
}

// 标准化值 - 只对数字进行标准化，保留其他类型的原始格式
function normalizeValue(value) {
  if (value === null || value === undefined) return '';
  
  // 将所有值转换为字符串并去除空格
  const strValue = String(value).trim();
  
  // 只对纯数字进行标准化处理
  const num = Number(value);
  if (!isNaN(num) && /^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$/.test(strValue)) {
    // 对于整数，返回整数字符串
    if (Number.isInteger(num)) {
      return String(num);
    }
    // 对于小数，统一格式化（去除末尾的0）
    return String(parseFloat(num.toFixed(10)));
  }
  
  // 对于所有其他类型（包括布尔值），保留原始值的字符串表示
  return strValue;
}

// ====================== Triggers.gs ======================
/**
 * 安装时触发，设置必要的触发器
 */
function onInstall(e) {
  onOpen(e);
  createEditTrigger(false);
}

/**
 * 卸载时触发，清理所有触发器
 */
function onUninstall(e) {
  try {
    const triggers = ScriptApp.getProjectTriggers();
    const scriptId = ScriptApp.getScriptId();
    
    triggers.forEach(trigger => {
      // 只删除由当前脚本创建的触发器
      if (trigger.getScriptId() === scriptId) {
        ScriptApp.deleteTrigger(trigger);
      }
    });
  } catch (error) {
    console.error('Error cleaning up triggers:', error);
  }
}

/**
 * 设置编辑触发器
 * @param {boolean} showToast 是否显示提示，默认为true
 */
function createEditTrigger(showToast = true) {
  try {
    // First try to get authorization
    try {
      ScriptApp.getProjectTriggers();
    } catch (authError) {
      // If we get a permissions error, show a more user-friendly message
      if (showToast) {
        SpreadsheetApp.getActive().toast(
          '需要额外授权来安装触发器。请重新运行此脚本并接受权限请求。',
          '需要授权',
          10
        );
      }
      return;
    }

    // Original trigger creation logic
    const triggers = ScriptApp.getProjectTriggers();
    let hasEditTrigger = false;
    
    triggers.forEach(trigger => {
      if (trigger.getHandlerFunction() === 'onEdit') {
        hasEditTrigger = true;
      }
    });

    if (!hasEditTrigger) {
      const ss = SpreadsheetApp.getActive();
      ScriptApp.newTrigger('onEdit')
        .forSpreadsheet(ss)
        .onEdit()
        .create();
      
      if (showToast) {
        SpreadsheetApp.getActive().toast('编辑触发器已安装', '提示', 3);
      }
    }
  } catch (error) {
    console.error('Error creating edit trigger:', error);
    if (showToast) {
      SpreadsheetApp.getActive().toast('触发器安装失败: ' + error.message, '错误', 5);
    }
  }
}

/**
 * 打开文档时的触发器
 */
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('配置表工具')
    .addItem('新建页签', 'createNewSheetTab')
    .addItem('比较差异', 'showCompareDialog')
    .addItem('合并表格', 'showMergeDialog')
    .addItem('清除所有标记', 'clearAllMarks')
    .addToUi();
  // ID 查询插件
  addIdLookupMenu();
}

/**
 * 当编辑表格时的触发器
 * @param {Object} e 编辑事件对象
 */
function onEdit(e) {
  try {
    // 检查表格是否包含ID列
    const sheet = e.range.getSheet();
    const headerRow = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
    const hasIdColumn = headerRow.some(header => 
      header && header.toString().endsWith(ID_CHECKER_CONFIG.ID_COLUMN_SUFFIX)
    );
    
    // 如果没有ID列，直接返回
    if (!hasIdColumn) return;

    // 1. 处理基准值记录和颜色标记
    const range = e.range;
    const oldValue = e.oldValue;
    const newValue = range.getValue();
    
    // 获取当前单元格的背景色和注释
    const currentBg = range.getBackground();
    let note = range.getNote();
    
    // 如果当前单元格已经是新增状态（绿色），则不做任何改变
    if (currentBg === SHEET_CONSTANTS.COLORS.ADDED) {
      return;
    }

    // 检查是否已经有修改记录（通过背景色判断）
    const isAlreadyModified = currentBg === SHEET_CONSTANTS.COLORS.MODIFIED;

    if (oldValue !== undefined) {  // 是修改操作
      // 设置为修改颜色（浅蓝色）
      range.setBackground(SHEET_CONSTANTS.COLORS.MODIFIED);
      
      // 只在首次修改时记录基准值
      if (!isAlreadyModified) {
        // 保持原始值的格式
        let baseValue = oldValue;
        // 如果是整数，确保以整数形式存储
        if (Number.isInteger(Number(oldValue))) {
          baseValue = parseInt(oldValue, 10);
        }
        
        // 添加基准值到系统注释，保留用户原有注释
        const newNote = NoteManager.addSystemNote(
          note,
          NOTE_CONSTANTS.TYPES.BASE_VALUE,
          baseValue.toString()
        );
        range.setNote(newNote);
      }
    } else if (newValue && newValue.toString().trim() !== '') {
      // 如果是新增值，设置为新增颜色（淡绿色）
      range.setBackground(SHEET_CONSTANTS.COLORS.ADDED);
    }

    // 2. 处理ID检查 - 无论是否有oldValue都需要检查
    const column = range.getColumn();
    const headerRange = sheet.getRange(1, column);
    const headerValue = headerRange.getValue();
    
    // 检查是否编辑的是 ID 列
    if (headerValue && headerValue.toString().endsWith(ID_CHECKER_CONFIG.ID_COLUMN_SUFFIX)) {
      // 设置一个短暂的延迟，确保值已经更新
      Utilities.sleep(100);
      // 只检查 ID 列的单元格
      const idRange = sheet.getRange(range.getRow(), column, range.getNumRows(), 1);
      checkIdConflicts({
        sheet: sheet,
        range: idRange
      });
    }
  } catch (error) {
    console.error('onEdit触发器出错:', error);
  }
}

/**
 * 清除所有标记和系统注释
 * @param {boolean} showConfirm 是否显示确认对话框
 * @returns {Object} 操作结果
 */
function clearAllMarks(showConfirm = true) {
  try {
    if (showConfirm) {
      const ui = SpreadsheetApp.getUi();
      const response = ui.alert(
        '确认清除',
        '是否要清除当前表格中所有的比较标记和系统注释？',
        ui.ButtonSet.YES_NO
      );

      if (response !== ui.Button.YES) {
        return { success: false, message: "操作已取消" };
      }
    }

    const sheet = SpreadsheetApp.getActiveSheet();
    const range = sheet.getDataRange();
    const [backgrounds, notes, values] = [
      range.getBackgrounds(),
      range.getNotes(),
      range.getValues()
    ];

    const newBackgrounds = [];
    const newNotes = [];
    const newValues = [];
    const rowsToKeep = [];

    // 检查每一行，标记需要保留的行
    for (let i = 0; i < backgrounds.length; i++) {
      let isDeletedRow = true;
      let hasHighlight = false;

      // 检查这一行是否是比较时新增的行
      for (let j = 0; j < backgrounds[i].length; j++) {
        const currentBg = backgrounds[i][j];
        const currentNote = notes[i][j];

        if (currentBg === COMPARE_CONSTANTS.COLORS.REMOVED) {
          hasHighlight = true;
        }

        if (currentNote && currentNote.includes("此行在基准表中不存在")) {
          hasHighlight = true;
        }

        // 如果这一行有任何非高亮的单元格，说明不是新增的行
        if (currentBg !== COMPARE_CONSTANTS.COLORS.REMOVED && 
            currentBg !== COMPARE_CONSTANTS.COLORS.MODIFIED && 
            currentBg !== COMPARE_CONSTANTS.COLORS.ADDED && 
            currentBg !== COMPARE_CONSTANTS.COLORS.HEADER_MODIFIED) {
          isDeletedRow = false;
        }
      }

      // 如果这一行不是新增的行，或者是第一行（表头），就保留它
      if (!isDeletedRow || !hasHighlight || i === 0) {
        rowsToKeep.push(i);

        const backgroundRow = [];
        const noteRow = [];

        for (let j = 0; j < backgrounds[i].length; j++) {
          const currentBg = backgrounds[i][j];
          let currentNote = notes[i][j];

          // 清除所有比较标记的背景色
          if (currentBg === COMPARE_CONSTANTS.COLORS.MODIFIED || 
              currentBg === COMPARE_CONSTANTS.COLORS.ADDED || 
              currentBg === COMPARE_CONSTANTS.COLORS.REMOVED || 
              currentBg === COMPARE_CONSTANTS.COLORS.HEADER_MODIFIED ||
              currentBg === SHEET_CONSTANTS.COLORS.MODIFIED ||
              currentBg === SHEET_CONSTANTS.COLORS.ADDED ||
              currentBg === MERGE_CONSTANTS.COLORS.NEW ||
              currentBg === MERGE_CONSTANTS.COLORS.CONFLICT ||
              currentBg === MERGE_CONSTANTS.COLORS.UPDATED ||
              currentBg === MERGE_CONSTANTS.COLORS.MERGED ||
              currentBg === MERGE_CONSTANTS.COLORS.RESOLVED) {
            backgroundRow.push(null);
          } else {
            backgroundRow.push(currentBg);
          }

          // 清除系统注释
          if (currentNote) {
            currentNote = NoteManager.removeAllSystemNotes(currentNote);
            noteRow.push(currentNote || '');
          } else {
            noteRow.push('');
          }
        }

        newBackgrounds.push(backgroundRow);
        newNotes.push(noteRow);
        newValues.push(values[i]);
      }
    }

    // 更新表格
    if (rowsToKeep.length < backgrounds.length) {
      // 如果有行被删除，更新表格并删除多余的行
      const newRange = sheet.getRange(1, 1, newBackgrounds.length, backgrounds[0].length);
      newRange.setBackgrounds(newBackgrounds);
      newRange.setNotes(newNotes);
      newRange.setValues(newValues);

      if (backgrounds.length > newBackgrounds.length) {
        sheet.deleteRows(newBackgrounds.length + 1, backgrounds.length - newBackgrounds.length);
      }
    } else {
      // 如果没有行被删除，只更新背景色和注释
      range.setBackgrounds(newBackgrounds);
      range.setNotes(newNotes);
    }

    return {
      success: true,
      message: "已清除所有标记和系统注释"
    };
  } catch (error) {
    console.error('清除标记和注释失败:', error);
    return {
      success: false,
      message: "清除失败: " + error.toString()
    };
  }
}