# Apps Script 安装部署说明

## 功能概述

Google Apps Script 实现暂存区到目标页签的提交功能，包含：
- **提交选中行**：将勾选的翻译行移入目标页签，自动生成 ID_int
- **全选/取消全选**：批量操作复选框
- **清空暂存区**：清除所有暂存数据
- **初始化暂存页签**：创建/重置暂存页签

## 安装步骤

### 1. 打开 Apps Script 编辑器

在目标 Google Sheet 中：**扩展程序 → Apps Script**

### 2. 粘贴代码

将 `localization_tool.gs` 的完整内容粘贴到编辑器中。

源文件位置：`c:\Users\liusiyi\游戏运营策划工具\localization_tool.gs`

### 3. 保存并授权

1. 点击保存（Ctrl+S）
2. 刷新 Google Sheet 页面
3. 菜单栏出现 **🌍 本地化工具**
4. 首次点击任意菜单项时会弹出授权请求，点击"允许"

### 4. 初始化暂存页签

点击菜单 **🌍 本地化工具 → 🔧 初始化暂存页签**

## 使用流程

1. AI 工具将翻译写入「AI翻译暂存」页签
2. 用户在 Sheet 中 review 翻译内容
3. 勾选满意的行（A列复选框）
4. 点击菜单 **🌍 本地化工具 → ✅ 提交选中行到对应页签**
5. 确认弹窗后，翻译自动移入对应页签

## 提交逻辑

- 读取目标页签最后一行的 `ID_int`，新行从 `ID_int + 1` 开始
- 新增行标记粉红色背景（`#FFB6C1`）
- 已提交行从暂存区自动删除
- 自动补充复选框和下拉列表

## 关键常量

```javascript
const STAGING_SHEET_NAME = 'AI翻译暂存';
const STAGING_HEADER = ['✅提交', '目标页签', 'ID', 'cn', 'en', 'fr', 'de', 'po', 'zh', 'id', 'th', 'sp', 'ru', 'tr', 'vi', 'it', 'pl', 'ar', 'jp', 'kr', 'cns'];
const TARGET_HEADER = ['ID_int', 'ID', 'cn', 'en', 'fr', 'de', 'po', 'zh', 'id', 'th', 'sp', 'ru', 'tr', 'vi', 'it', 'pl', 'ar', 'jp', 'kr', 'cns'];
```
