---
name: iap-jiji-fincond-replace
description: 机甲累充配置 fincond 替换工具 - 从累充规划表读取C列去重数据，按源 B 列 ID 升序整行复制 activity_task_QA 指定行，仅替换 A_MAP_fincond 中 arg.ids；行内容顺序不变；文案按页签将复活节改为目标节日。触发场景：机甲累充、机甲累充配置、机甲配置替换、机甲配置更新、机甲配置替换、机甲替换、机甲 fincond、机甲 ids。
---

# 机甲累充配置 fincond 替换工具

从累充规划表指定页签读取 C 列去重 ID，写入 `activity_task_QA` 中机甲累充任务行的 `A_MAP_fincond` 的 **`arg.ids` 数组**；**整行其它列原样复制且顺序与源表一致**，仅 B 列换新 ID、非 E 列文案按页签做节日名替换（如复活节→拓荒节）。

## 触发条件

当用户提到以下关键词时自动激活：

- 机甲累充 / 机甲配置 / 机甲替换 / 机甲 fincond / 机甲 ids
- 机甲累充配置替换 / 机甲累充配置更新
- fincond 替换 / A_MAP_fincond

## 核心概念

### 三张表关系

| 简称 | Spreadsheet ID | 用途 |
|------|---------------|------|
| activity_task_QA | `1K3-I4gCYKY-Zw5Ms05ozHtHKpOqYI-lp4kuuhqbWajY` | 目标配置表，含 A_MAP_fincond 字段 |
| 累充规划表 | `1RFAyBfpG3-8rm3ugNn3NHFdeDg8Erha0VttGzokIy6E` | 源数据表，含节日页签和 C 列礼包 ID |

### fincond 字段结构

`A_MAP_fincond`（E列）存储 JSON 格式的完成条件：

```json
{"cat":101412053,"arg":{"ids":[201130786,201130787,...]},"val":1250,"op":"ge"}
```

- `cat` / `op` / `val`：**不修改**
- `arg.ids`：**唯一替换块** — 用累充规划表当前页签 C 列去重后的 ID 列表整体替换
- 除上述 JSON 内 `ids` 数组外，**不要**改 E 列其它字段或键

### 行复制顺序（易错）

| 正确 | 错误 |
|------|------|
| 源 B 列 ID **升序**（如 211588136 → … → 211588145）依次对应输出第 1、2、… 行 | 按 ID **倒序**取源行，导致整行内容与源活动档位顺序不一致 |
| 新行 B 列 ID 从 `new_id_start` **连续递增**，与上面行顺序一致 | 把「倒序」用在整行复制上 |

**结论**：`211588136–211588145` 共 **10** 行，**行内容顺序与源表一致**；新 B 列 ID 为 `new_id_start` … `new_id_start+9`（示例：与截图一致时常用 `211589990` 起）。

### 文案与页签

复制到非 E 列的字符串中，若仍含「复活节」等旧节日名，按 `--src-tab` 解析出的节日简称替换（如页签 `26拓荒节` → 将「复活节」改为「拓荒节」），使展示与累充表一致（如 `2026拓荒节节日累充-1250`）。

## AI 执行指引

### 1. 确认参数

向用户确认以下信息（如用户已提供则跳过）：

| 参数 | 说明 | 示例 |
|------|------|------|
| **节日页签**（必填） | 累充规划表中页签名 | `26拓荒节` |
| 源 B 列 ID 范围（可选） | 要复制的源行，**默认 211588136–211588145（10 行）** | `211588136-211588145` |
| 新 B 列起始 ID（可选） | 插入行的首行 ID，**默认 211589990** | `211589990` |

> **节日页签速查**（累充规划表 `1RFAyBfpG3-8rm3ugNn3NHFdeDg8Erha0VttGzokIy6E`）：
>
> - 26拓荒节 → `26拓荒节`（sheetId=1728101054）
> - 26复活节 → `26复活节`（sheetId=1027326589）
> - 26科技节 → `26科技节`（sheetId=485738457）
> - 26情人节 → `26情人节`（sheetId=20976472）
> - 26春节 → `26春节`（sheetId=1334534091）

### 2. 执行脚本

脚本位于：`.agents/skills/iap-jiji-fincond-replace/scripts/replace_fincond.py`

```bash
# 仅预览（默认 --dry-run true，不写入）
python -X utf8 .agents/skills/iap-jiji-fincond-replace/scripts/replace_fincond.py --src-tab "26拓荒节"

# 实际写入（必须显式 --dry-run false）
python -X utf8 .agents/skills/iap-jiji-fincond-replace/scripts/replace_fincond.py --src-tab "26拓荒节" --dry-run false

# 验证表尾最近插入的 N 行（N 与当前 --src-id-start/end 区间行数一致）
python -X utf8 .agents/skills/iap-jiji-fincond-replace/scripts/replace_fincond.py --verify

# 删除表尾最近插入的 N 行（回退；与 --verify 一样依赖当前默认源区间行数 N）
python -X utf8 .agents/skills/iap-jiji-fincond-replace/scripts/replace_fincond.py --delete
```

**重要**：必须使用 `python -X utf8` 运行以避免 Windows 中文乱码。工作目录为项目根目录。

### 3. 确认并汇报结果

执行完成后，向用户汇报：

- 累充表 C 列去重后 ID 个数
- 插入行数、新 B 列 ID 区间
- 各档 `val` 是否与源行一致（仅 `ids` 来自累充表）
- 提示在表格中核对 A/B 列类型与描述是否已为拓荒节等目标文案

## 操作流程详解

```
1. 读取累充规划表指定页签 C 列 → 去重 → ids 列表
         ↓
2. 在 activity_task_QA 按 B 列查找源 ID 范围（升序：136…145）
         ↓
3. 按该升序逐行读取 E 列，仅替换 JSON 内 arg.ids，cat/val/op 不变
         ↓
4. 表末插入 N 行（N = 源行数）
         ↓
5. 按同一升序写入：除 B、E 外列从源行复制；非 E 列字符串中「复活节」→ 页签对应节日名；
   B 列 = 新 ID 连续递增；E 列 = 步骤 3 的 fincond
         ↓
6. 验证（可选）
```

## 注意事项

- **禁止**用 `reversed(源ID)` 遍历源行 — 会颠倒档位顺序，与「行内容顺序不变」冲突。
- **E 列**只改 `arg.ids` 数组元素，不改 `val`、不改 JSON 其它键。
- **RAW 模式写入**：E 列 JSON 使用 `valueInputOption="RAW"`，避免被表格改写格式。
- **表格扩展**：脚本在表末插入新行；`--delete` 删除**表尾最近 N 行**（N 与当前源 ID 区间行数一致），用于回退。
- 若还需 **第 11 行**（如每日充值、不同 A 列类型），需单独指定源 ID 或第二次执行，本技能默认仅处理连续 10 档 `211588136–211588145`。
