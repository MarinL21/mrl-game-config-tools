---
name: p2-translation-automatic
description: >-
  游戏本地化翻译全流程工具。从UX截图或原始文本提取UI文本，自动查重、复用翻译记忆、生成18语言翻译、写入Google Sheet暂存区，
  用户review后一键提交到目标页签。触发场景：游戏多语言配置、本地化翻译表、i18n配置、UI文本提取、多语言扩散翻译、
  LC_Key生成、翻译存入表格、UX截图翻译。
---

# 游戏本地化翻译全流程工具

## 核心能力

从 **UX截图** 或 **原始文本** 出发，经过 Key查重 → 术语对齐 → 翻译记忆复用 → 18语言翻译 → 写入暂存区 → 用户Review → 提交目标页签的完整流程。

## 前置条件

| 依赖 | 说明 |
|------|------|
| Python 3 | `google-api-python-client`, `google-auth` |
| gws CLI | 已认证（`gws auth login`），用于获取 OAuth 凭据 |
| Google Sheet | 需有编辑权限 |
| Apps Script | 已部署 `localization_tool.gs`（见 [setup-apps-script.md](setup-apps-script.md)） |

### 目标表格

```
spreadsheetId: 11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY
链接: https://docs.google.com/spreadsheets/d/11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY
```

### 工作目录

所有脚本和缓存文件位于：`c:\Users\liusiyi\游戏运营策划工具\`

---

## 完整执行流程

收到用户的 UX 截图或文本后，**严格按以下步骤执行**：

### Step 1: 提取 UI 文本

- 截图：仔细识别所有可见的 UI 文本（按钮、标题、提示、Tab名等）
- 纯文本：直接使用用户提供的中文原文
- 输出一张表格列出所有提取到的文本

### Step 2: Key 重复检测

运行脚本检查新生成的 key 是否与现有 46000+ key 冲突：

```bash
cd "c:\Users\liusiyi\游戏运营策划工具"
python check_duplicates.py key1 key2 key3 ...
```

- **有冲突** → 告知用户该 key 已在哪个页签，建议换名或复用
- **无冲突** → 继续

> 索引文件 `all_existing_keys.json` 如过期，运行 `python scan_all_keys.py` 刷新

### Step 3: ⚠️ 术语规范库查询（最高优先级）

从每条中文文本中提取游戏术语（名词/物品名/建筑名/兵种名等），**先查规范库**：

```bash
python glossary_lookup.py "阶段" "运输车" "豪华宴会券" "加速" ...
```

- **✅ 命中** → 直接使用规范库的 18 语言翻译，**不再检索、不自行翻译**
- **❌ 未命中** → 进入 Step 4 检索

**术语规范库** (`glossary.json`) 存储已确认的标准翻译，解决"同一术语多种译法"问题（如"阶段"→Stage 而非 Phase）。规范库条目经过频率分析确认，优先级最高。

维护命令：
- 查看全部：`python glossary_lookup.py --list`
- 添加新词：`python glossary_lookup.py --add "术语" en=xxx fr=xxx source=TAB/key note="说明"`
- 发现新的不一致翻译时，用 `python analyze_term.py "术语" EVENT` 分析频率后添加

### Step 4: ⚠️ 术语在线检索（规范库未命中时）

对 Step 3 未命中的术语，直连 Google Sheet 实时检索（优先 ITEM 表）：

```bash
python search_terms.py "加速" "金币" ...
```

- **EXACT MATCHES** → 必须直接采用，不得自行翻译
- **No matches** → AI 自行翻译

**拆词方法**：
1. 从每条中文文本中提取所有 **名词性术语**
2. 将术语传给 `glossary_lookup.py`（先查规范库）
3. 未命中的传给 `search_terms.py`（在线检索）
4. 仍未命中的才允许 AI 自行翻译

**示例**：
- 输入文本："运输车护卫奖励" → 拆出："运输车"、"奖励"
- "运输车"→ 规范库命中 Convoy ✅ 直接用
- "奖励"→ 规范库未命中 → search_terms.py → Rewards
- 最终翻译："Convoy Escort Rewards"

**发现翻译不一致时的处理**：
1. 运行 `python analyze_term.py "术语" EVENT` 分析频率分布
2. 以频率最高的翻译为准
3. 运行 `python glossary_lookup.py --add "术语" en=xxx ...` 写入规范库
4. 后续所有翻译自动遵循，不再重复分析

### Step 5: 翻译记忆查询

查询 40000+ 条已有翻译，作为 Step 3/4 的补充（整句匹配）：

```bash
python lookup_tm.py "完整中文文本1" "完整中文文本2" ...
```

- **精确匹配** → 直接复用已有翻译的全部 18 语言，不重新翻译
- **部分匹配** → 参考已有词汇风格
- **无匹配** → AI 生成新翻译（但术语必须用 Step 3/4 的结果）

> 记忆库 `translation_memory.json` 如过期，运行 `python build_translation_memory.py` 刷新

### Step 6: 推断目标页签

根据文本内容自动推断目标页签，详见 [reference.md](reference.md) 的页签映射表。

### Step 7: 生成 ID

- **格式**：`[a-z0-9_]`，全小写，语义化命名
- **不加页签前缀**：如 `cool_treasure_title`，不是 `event_cool_treasure_title`
- **暂存区不填 ID_int**：提交到目标页签时由 Apps Script 自动顺延生成

### Step 8: 生成 18 语言翻译

翻译顺序：cn → en → fr → de → po → zh → id → th → sp → ru → tr → vi → it → pl → ar → jp → kr → cns

**翻译来源优先级（严格遵守）**：
1. **术语规范库**（Step 3 `glossary_lookup.py`）→ 命中即用，不可覆盖
2. **术语在线检索**（Step 4 `search_terms.py`）→ EXACT MATCH 必须采用
3. **翻译记忆整句匹配**（Step 5 `lookup_tm.py`）→ 精确匹配直接复用全部 18 语言
4. **翻译记忆部分匹配** → 沿用已有词汇风格
5. **AI 新翻译** → 仅当以上全部无匹配时，AI 才自行翻译

**其他规则**：
- `\n` 作为文本字面量保留在同一行，不拆成多行
- `cns` 列（简体中文备份）= `cn` 列内容

### Step 9: 写入暂存区

生成 Python 脚本写入 **"AI翻译暂存"** 页签。

**脚本模板**（每次根据实际数据修改 `ROWS`）：

```python
import json, subprocess
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = "11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY"
STAGING_SHEET = "AI翻译暂存"

# 每行格式: [目标页签, ID, cn, en, fr, de, po, zh, id, th, sp, ru, tr, vi, it, pl, ar, jp, kr, cns]
ROWS = [
    ["EVENT", "explore_record", "探索记录", "EXPLORE LOG", ...其他16语言...],
]

def get_credentials():
    result = subprocess.run(
        ["gws", "auth", "export", "--unmasked"],
        capture_output=True, text=True, encoding="utf-8", shell=True,
    )
    creds_data = json.loads(result.stdout.strip())
    return Credentials(
        token=None,
        refresh_token=creds_data["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=creds_data["client_id"],
        client_secret=creds_data["client_secret"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )

def main():
    credentials = get_credentials()
    service = build("sheets", "v4", credentials=credentials)
    sheets_api = service.spreadsheets()

    # 获取暂存页签 sheetId
    spreadsheet = sheets_api.get(
        spreadsheetId=SPREADSHEET_ID, fields="sheets.properties"
    ).execute()
    staging_sheet_id = None
    for s in spreadsheet["sheets"]:
        if s["properties"]["title"] == STAGING_SHEET:
            staging_sheet_id = s["properties"]["sheetId"]
            break

    # 定位追加起始行
    result = sheets_api.values().get(
        spreadsheetId=SPREADSHEET_ID, range=f"'{STAGING_SHEET}'!A:A"
    ).execute()
    existing = result.get("values", [])
    next_row = max(len(existing) + 1, 2)
    end_row = next_row + len(ROWS) - 1

    # 写入数据到 B~U 列（A 列留给 checkbox）
    sheets_api.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{STAGING_SHEET}'!B{next_row}:U{end_row}",
        valueInputOption="RAW",
        body={"values": ROWS},
    ).execute()

    # 获取所有页签名（用于下拉菜单）
    tab_names = [
        s["properties"]["title"] for s in spreadsheet["sheets"]
        if s["properties"]["title"] not in (STAGING_SHEET, "回车检查", "本地化使用说明")
    ]

    # 为 A 列设置 checkbox + B 列设置目标页签下拉菜单
    sheets_api.batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={"requests": [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": staging_sheet_id,
                        "startRowIndex": next_row - 1, "endRowIndex": end_row,
                        "startColumnIndex": 0, "endColumnIndex": 1,
                    },
                    "cell": {
                        "dataValidation": {"condition": {"type": "BOOLEAN"}, "strict": True},
                        "userEnteredValue": {"boolValue": False},
                    },
                    "fields": "dataValidation,userEnteredValue",
                }
            },
            {
                "setDataValidation": {
                    "range": {
                        "sheetId": staging_sheet_id,
                        "startRowIndex": next_row - 1, "endRowIndex": end_row,
                        "startColumnIndex": 1, "endColumnIndex": 2,
                    },
                    "rule": {
                        "condition": {
                            "type": "ONE_OF_LIST",
                            "values": [{"userEnteredValue": t} for t in tab_names],
                        },
                        "showCustomUi": True,
                        "strict": False,
                    },
                }
            },
        ]},
    ).execute()
    print(f"Done! Wrote {len(ROWS)} rows (row {next_row}-{end_row})")

if __name__ == "__main__":
    main()
```

### Step 10: 告知用户结果

输出提交概要表格：

| Key | 中文 | 英文 | 翻译策略 |
|-----|------|------|---------|
| `explore_record` | 探索记录 | EXPLORE LOG | 复用 TM |

提示用户：去 Google Sheet 的「AI翻译暂存」页签 review，确认后勾选 → 菜单 **"本地化工具 > 提交选中行"**。

---

## 暂存页签格式（21列）

| A | B | C | D | E~U |
|---|---|---|---|-----|
| ✅复选框 | 目标页签 | ID | cn | en, fr, de, po, zh, id, th, sp, ru, tr, vi, it, pl, ar, jp, kr, cns |

用户在 Sheet 中 review → 勾选 → 菜单提交 → Apps Script 自动：
1. 读取目标页签最后一行 ID_int 并顺延
2. 追加数据到目标页签（20列：ID_int + ID + 18语言）
3. 新增行标记粉红色背景
4. 从暂存区删除已提交行

---

## 目标页签格式（20列）

| A | B | C | D~T |
|---|---|---|-----|
| ID_int | ID | cn | en, fr, de, po, zh, id, th, sp, ru, tr, vi, it, pl, ar, jp, kr, cns |

---

## 工具脚本速查

| 脚本 | 功能 | 用法 |
|------|------|------|
| `glossary_lookup.py` | ⚠️ 术语规范库（最高优先级） | `python glossary_lookup.py "阶段" "运输车"` |
| `glossary_lookup.py --add` | 添加新规范术语 | `python glossary_lookup.py --add "术语" en=xxx` |
| `glossary_lookup.py --list` | 查看全部规范术语 | `python glossary_lookup.py --list` |
| `analyze_term.py` | 分析术语翻译频率 | `python analyze_term.py "阶段" EVENT` |
| `search_terms.py` | 术语在线检索（直连Sheet） | `python search_terms.py "加速" "金币"` |
| `check_duplicates.py` | 检查 key 是否重复 | `python check_duplicates.py key1 key2` |
| `lookup_tm.py` | 翻译记忆查询（本地缓存） | `python lookup_tm.py "中文1" "中文2"` |
| `scan_all_keys.py` | 刷新 key 索引 | `python scan_all_keys.py` |
| `build_translation_memory.py` | 刷新翻译记忆库 | `python build_translation_memory.py` |
| `fix_dropdown.py` | 修复暂存区下拉菜单 | `python fix_dropdown.py` |

所有脚本在 `c:\Users\liusiyi\游戏运营策划工具\` 目录下运行。

---

## 文本处理规范

| 规则 | 说明 |
|------|------|
| `\n` 处理 | 作为字面量保留，不拆行 |
| 参数格式 | `{0}`, `{1}`... 各语言参数数量一致 |
| 简体中文 | 全角标点（，！：？），禁英文字母 |
| 富文本标签 | `<color=#3ef742>` 闭合正确 |
| ID 格式 | `[a-z0-9_]` 全小写，语义化 |

---

## 自检清单

每次输出前完成以下检查：

- [ ] ⚠️ 已运行 `glossary_lookup.py` 查规范库，命中术语已采用
- [ ] ⚠️ 规范库未命中的术语已运行 `search_terms.py` 在线检索
- [ ] 已运行 `lookup_tm.py` 查询翻译记忆
- [ ] 发现不一致翻译时已用 `analyze_term.py` 分析频率并写入规范库
- [ ] 20列全部有值（暂存区21列含checkbox）
- [ ] ID 全小写，无页签前缀
- [ ] `\n` 未拆行
- [ ] 参数 `{0}` 各语言数量一致
- [ ] 富文本标签正确闭合
- [ ] Key 无重复

---

## 详细参考

- 页签映射表、语言列表、ID_int 编码规则：[reference.md](reference.md)
- Apps Script 安装部署说明：[setup-apps-script.md](setup-apps-script.md)
