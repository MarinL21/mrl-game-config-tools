---
name: id-lookup-plugin
description: >-
  Google Sheets 内嵌 ID 跨表查询插件的管理与部署。支持：新表部署、TABLE_REGISTRY 更新、全量同步推送、插件功能迭代。
  覆盖 P2 全部配置表（2112/2111/2121/2135/2011/2013/1111/1180/1168/1511/2115/2122/2124），已部署 7 个 Spreadsheet。
  触发：ID查询插件、跨表查询、部署插件、clasp push、TABLE_REGISTRY、新增配置表、侧边栏插件。
---

# ID 跨表查询插件 Skill

## 1. 插件功能

选中或粘贴一个 ID → 侧边栏自动识别所属表 → 显示全部非空字段 → 识别 JSON 内外键引用（可点击跳转） → 反向查询谁引用了此 ID。

| 能力 | 说明 |
|---|---|
| ID 正查 | 根据前 4 位数字前缀路由到对应 Spreadsheet，全页签搜索 |
| 外键识别 | 自动解析 JSON 和数值字段中的 ID 引用，显示为可点击标签 |
| 跳转源表 | 一键在新标签打开源行所在 Spreadsheet |
| 反向查询 | 搜索其余已注册表，找出谁引用了这个 ID |
| 粘贴自动查询 | 粘贴 ID 后 300ms 自动触发查询 |
| 查询历史 | 记录最近 8 次查询，支持单条删除和清空 |

## 2. 源码位置

```
/Users/marinl/游戏运营策划工具/google_sheets_id_lookup/
├── IdLookup.js      # 核心逻辑 + TABLE_REGISTRY
├── Sidebar.html     # 侧边栏 UI
├── Code.js          # 原始表的已有代码（含 onOpen）
├── .clasp.json      # 绑定原始项目
├── appsscript.json  # Apps Script 配置
├── CompareDialog.html  # 原有插件（不动）
└── MergeDialog.html    # 原有插件（不动）
```

## 3. TABLE_REGISTRY（当前 13 张表）

| 前缀 | 中文名 | 英文名 | Spreadsheet ID | 页签名 |
|---|---|---|---|---|
| 2112 | 活动配置 | activity_config | `1IKUBw678b2PU1m0md1vR9GxcH2uTNyLbR7VWgyAJ57E` | activity_config_qa |
| 2111 | 活动日历 | activity_calendar | `1OaExug4AwwFlGH6LGbBiMnvQF41hYg0LsXiMQZ9XX6g` | activity_calendar_QA |
| 2121 | 活动组件 | activity_special | `1sicvhfxZhagLVmpEg4HDcaCnPWPgsWkhgZKC-HxCCuc` | activity_special_QA |
| 2135 | 活动礼包壳 | activity_event_pkg | `1KrcIA8jC4Aj6sFz44c_2lhtJ-lyD1OYu3QNpzaor8Mc` | activity_event_pkg |
| 2011 | IAP外壳 | iap_config | `1yS_BehT_Rfcc3sXjDPsSaQRcjPh8YepucYTnUQDpEMc` | iap_config_QA |
| 2013 | IAP模板 | iap_template | `1sJzacpa0CBp1B8LQX1TboSBOA4T80_t8lH8eEzqHLbY` | iap_template_QA |
| 1111 | 道具表 | item | `1FQqpeRfkXVwaEDSVi3oTaQNs2PLLDcsvQQmc-k0L3ws` | item |
| 1180 | 行军表情 | map_emoji | `1SloOHvSFrEJz7HaU8yur9Qt8dOzsmqa69DUBERkkBmw` | qa |
| 1168 | 准入组 | get_access_group | `1KwX1xWoHHcmOGTaasZmMii2Al-YR_VXV3yoSGn3tBbA` | get_access_group（杜绝手搓） |
| 1511 | 展示键 | display_key | `1Oks7yHCxYnWxo1QiNdO5EYNET68l_aCzZU-58zATlLY` | display_key |
| 2115 | 任务配置 | activity_task | `1K3-I4gCYKY-Zw5Ms05ozHtHKpOqYI-lp4kuuhqbWajY` | activity_task_QA |
| 2122 | 排行榜规则 | activity_rank_rule | `1zziy6nMR1DlhCykKBndwk6d6KNRrzj1PsOsFGbLYR4M` | activity_rank_rule（QA） |
| 2124 | 掉落配置 | activity_drop | `1V7xDriTe0hGW3SF7ZPtk71-sFGyzpbbO47V6gLoBqVA` | activity_drop |

## 4. 已部署 Spreadsheet 及 Script ID

| 表 | Script ID | 部署目录 |
|---|---|---|
| 原始表 | `1LTcMPPpXO2pcbDX-Lk_1NumZqvsnJKvFVGl2zDM8nkm7TH3y_K8kBusK` | `google_sheets_id_lookup/` |
| 1111 | `1OfEsmbyDIBrCfaUo570MW4D_ZkL8PWkQTA5XBiRsP3fgRMwbuQ3zJtut` | `/tmp/id_lookup_deploy/t1111` |
| 2115 | `1Yzj-fYdMnOlrPYnZSNFPsqRsv7sC3weYXFU9mvjmHuBUcqeJqdxh7Kd_` | `/tmp/id_lookup_deploy/t2115` |
| 2121 | `182SwKczLBG9sQIkTqdquM2fpIyQ28__r3SGpxxtcQieNSK6WUzdymzAu` | `/tmp/id_lookup_deploy/t2121` |
| 2122 | `1anNpzc7Pcjw_dToFfvXfxIofvDU_Ih3bF3STkHGBP2-3wyNrsBxspLdb` | `/tmp/id_lookup_deploy/t2122` |
| 2124 | `1el_gNhGrqR942n6uA2sx0fy81YRpqUg2DsaApffOQLFYjr9FY3Wp4FQB` | `/tmp/id_lookup_deploy/t2124` |
| 2135 | `1UGiM4azvRdGaIrWhrZ-P5tOqmdy0j6zzz2n4NlqpapUEzaSf_RzwE1aO` | `/tmp/id_lookup_deploy/t2135` |

## 5. 操作指南

### 5.1 给新 Spreadsheet 部署插件

```bash
# 1. 创建绑定脚本（在 /tmp 下操作，避免 .clasp.json 冲突）
mkdir -p /tmp/id_lookup_deploy/tXXXX
cd /tmp/id_lookup_deploy/tXXXX
clasp create --title "ID查询插件" --parentId "<SPREADSHEET_ID>" --rootDir "."

# 2. 复制插件文件
SRC="/Users/marinl/游戏运营策划工具/google_sheets_id_lookup"
cp "$SRC/IdLookup.js" ./IdLookup.js
cp "$SRC/Sidebar.html" ./Sidebar.html
echo 'function onOpen() { addIdLookupMenu(); }' > Code.js

# 3. 推送
clasp push
```

**注意**：如果目标表已有 Apps Script 项目和 `onOpen`，不要新建项目。改为 `clasp clone <现有ScriptID>`，然后只添加 `IdLookup.js` + `Sidebar.html`，在原有 `onOpen` 末尾加 `addIdLookupMenu();`。

### 5.2 新增表到 TABLE_REGISTRY

编辑 `IdLookup.js` 的 `TABLE_REGISTRY` 对象，加一行：

```javascript
'XXXX': { name: '中文名', full: 'english_name', sid: 'SPREADSHEET_ID', tab: 'TAB_NAME', idCol: 'A_INT_id' },
```

### 5.3 全量同步推送（改了 IdLookup.js 或 Sidebar.html 后）

```bash
SRC="/Users/marinl/游戏运营策划工具/google_sheets_id_lookup"
for dir in /tmp/id_lookup_deploy/t*; do
  cp "$SRC/IdLookup.js" "$dir/IdLookup.js"
  cp "$SRC/Sidebar.html" "$dir/Sidebar.html"
  (cd "$dir" && clasp push)
done
cd "$SRC" && clasp push
```

### 5.4 注意事项

- `clasp create` 必须在 `/tmp/id_lookup_deploy/` 下操作，因为源码目录已有 `.clasp.json`，clasp 会向上查找导致冲突
- 新 Spreadsheet 首次打开插件需要 Google 授权（弹窗点允许）
- 部署目录在 `/tmp`，重启后丢失；但 `.clasp.json` 可通过 Script ID 重建：`echo '{"scriptId":"<ID>","rootDir":"."}' > .clasp.json`
- 查询逻辑：先查配置的页签名，找不到则自动扫描该 Spreadsheet 的所有页签
- 原始表的 `Code.js` 包含其他插件（配置表工具），更新时不要覆盖，只改 `IdLookup.js` 和 `Sidebar.html`

## 6. 技术架构

```
用户选中/粘贴 ID
       ↓
Sidebar.html (oninput 防抖 300ms)
       ↓
google.script.run.lookupId(id)
       ↓
IdLookup.js:lookupId()
  ├─ 前 4 位匹配 TABLE_REGISTRY
  ├─ SpreadsheetApp.openById(sid)
  ├─ _searchInSheet() → 先查指定页签，再扫全部页签
  ├─ TextFinder.matchEntireCell(true) 精确搜索
  ├─ _walkJson() 递归提取 JSON 内的 ID 引用
  └─ 返回 { fields[], refs[], sourceUrl }
       ↓
Sidebar.html 渲染结果卡片
  ├─ 引用标签可点击 → 递归 doLookup()
  └─ 反向查询 → reverseSearch() 搜索其余 12 张表
```
