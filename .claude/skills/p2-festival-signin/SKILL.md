---
name: p2-festival-signin-config
description: >-
  P2 节日签到端到端配置 skill。覆盖 2112 主表 + 2111 calendar + 2115 task pool 三表写入。
  默认按"2026 节日签到模板"复制：22 task + login_complement、priority 49991、base_activity 21121590 等共用，
  仅 4 字段节日专属（constant / ui_template / show_hud / banner_url）。带 scripts/signin.py 自动化（learn/plan/apply/verify），
  写前 ID-row 校对、写后 ID 回读。触发：配 {节日} 签到、写 {节日} 签到、{节日}签到-{年}、提配置签到、event sign-in。
---

# P2 节日签到配置 Skill

## Scope 边界

**只处理**：2026+ 节日的常规登录签到（priority=49991, base_activity=21121590, components 用通用 21 task pool）。

**不在 scope**（碰到要切别的 skill 或问用户）：
- BP 类七日活动（如 21127404 拓荒节2025-七日-新版，priority 49996，含 75 task + 7days_box）
- 周年庆专属签到（用 211551161-211551188 这套 28 task）
- 28 天版签到（211552251-211552257 那段）
- 回归签到 / 合服签到（schema 不一样）
- 1511 displaykey 表 / 21680 show_hud 表 / LC 文案的人工配置（脚本不动这些）

## 2026 签到模板不变量（写到代码里强制）

`scripts/signin.py` 顶部锁死，改前先改这里：

| 字段 | 列 | 值 | 说明 |
|---|---|---|---|
| priority | E | 49991 | 全 2026 签到统一 |
| base_activity_id | F | 21121590 | 全 2026 签到统一 |
| filter | G | `{"op":"ge","typ":"building","id":111811,"val":5}` | 全统一 |
| text | H | LC_EVENT_2024_anni_log_in_title (label/title) + LC_EVENT_moon_log_in_bp_title_desc (subtitle) | 全统一 |
| components | I | 21 task `211552230-211552250` + login_complement `21215260` | **全 2026 节日共用**（见 §警示） |
| description | J | `{"rule":"LC_EVENT_anni_log_in_actv_rule"}` | 全统一 |
| rank_group | L | 1 | 全统一 |
| banner_obj_url | M | `""` 字面双引号 | 全统一 |
| banner_version | O | 1 | 全统一 |
| calendar | S | 1 | flag bool 全统一 |
| calendar_reward | T | `[]` | 全统一 |
| calendar_banner_url | U | EventBanner_Timeline_145.png | 全统一 |
| mini_banner_url | W | EventBanner_Timeline_145.png | 全统一 |
| display_flags | X | 0 | 全统一 |
| country_use_type | Y | 0 | 全统一 |

**节日专属（4 个）**：constant(C) / ui_template(K) / show_hud(R) / banner_url(N)。
脚本只改这 4 个 + id(A) + comment(B)，其余 25 列照搬最新 2026 签到行。

## ⚠️ 2115 共用 task 警示（最易踩坑）

`211552230-211552250` 这 21 个 task 命名"节日通用1号签到-N"，**春节/科技节/复活节/拓荒节签到全部共用同一份 task id**——不是 item_select_box 节日内切，是**直接复用**。

**意味着**：直接改 2115 这 21 行的 reward 会**同时影响所有 2026 节日签到**。

**21 天奖励道具构成**（脚本自动盘点；通用池写死在 `COMMON_REWARD_ITEMS`）：

| 类型 | item id | 名称 | 出现位置 |
|---|---|---|---|
| **节日专属（要换）** | 11112091 / 11112150 / ... | BP 进度道具，每节日不同 | 第 1/5/8/12/15/19 天，共 6 处 |
| 通用 | 11112498 | 漫游骰子-节日进度活动 | 7 次 |
| 通用 | 11116258 | 碎片-艾玛 | 3 次 |
| 通用 | 11116604 | 收藏品-橙色升星 | 1 |
| 通用 | 11117068 | 军备零件箱 | 1 |
| 通用 | 19345004 | material | 1 |
| 通用 | 11114330 | 高级资源自选宝箱 | 1 |
| 通用 | 11116402 | 高级奖池抽奖券 | 1 |

脚本通过"reward 中 item id 不在通用池"自动识别 BP 进度行（不依赖 hardcode 行号），所以**模板首次新增天数 / BP 道具 id 变了都会自动跟上**。

**两种处理方案**：
- **方案 A**（不污染其他节日，推荐做未来上线节日）：在 2115 复制 21 行通用 task 到下一段空号（211552278+），改其中 6 处 BP 道具为新节日的，然后让 2112 components 引用新 task id。**脚本暂未自动化此模式**，需要手动复制 + 用 `--task-pool` 传入（待开发）。
- **方案 B**（直改通用 task，简单但污染）：直接改 211552230-211552250 的 6 处 BP 道具。当其他节日已结束 / 不会重开时可用。**脚本默认 mode B**。

每次必须问用户选 A 还是 B。**默认不要替用户决定**。

## 2111 calendar 落位规则

- **新行 ID = 2111 当前最后一个节日 ID + 1**（自动从占位符 21116001 上一行算）
- **物理位置**：紧贴 21116001 占位符之前 = 节日段尾
- **9 列字段**全部按 2026 模板：`schema:[1,2,3,4,5,6]` / `typ:time, is_ark:1` / 其余 `{}` / data_cross=0 / country=0
- 21116001 是分隔行（"节日占位符-以上是节日"），它之后是非节日活动，**绝不能跨过它**

## 工作流（4 步）

### Step 0 — 自主学习（必做）

```bash
python3 scripts/signin.py learn
```

返回 JSON：
- `2026_signins`: 当前 2112 已有的所有 2026 签到
- `template_2112_row`: 25 列模板（自动选最新 ID 的签到行）
- `2115_bp_rows`: 自动识别出当前 BP 进度道具的 6 个 task 行
- `2111_next_id`: 自动算的 2111 新 ID
- `2111_placeholder_row`: 占位符位置

### Step 1 — 收齐用户确认的 6 个变量（**触发即问，不替用户决定**）

用户已在 2026-05-06 明确："每次让你配的时候询问我就可以"。触发本 skill 后第一件事是列下面 6 项空表请用户填，不要先猜默认：
1. **2112 ID**（用户预分配的实例 ID，21127XXX 段）
2. **节日英文 slug**（labor / easter / spring / tech / xmas / halloween / thank / moon / anni / sci / valen / abyss）
3. **节日中文名**（拓荒节 / 复活节 / ...）
4. **ui_template**（21191XXX，1511/UI 表配的）
5. **show_hud**（21680XXX）
6. **banner_url**（默认 BG_408.png；春节用过 BG_499 节日专版）
7. **BP 进度道具 1111 id**（按节日：复活=11112091 魔术棒 / 拓荒=11112150 纪念钻头 / 其他节日去 1111 表 grep "{节日}.*BP"）
8. **2115 mode**（A 新建 / B 直改） — **不要替用户选**

### Step 2 — Plan dry-run

```bash
python3 scripts/signin.py plan \
  --festival labor --cn 拓荒节 \
  --id-2112 21127898 \
  --ui-template 21191578 --show-hud 21680032 \
  --bp-item 11112150
```

输出三表完整写入计划，**不动表**。让用户看一遍再 apply。

### Step 3 — Apply

```bash
python3 scripts/signin.py apply <相同参数>
```

脚本顺序：
1. **2115 写前 ID 校对**：每个 G 列 cell 对应的 B 列 task id 必须吻合
2. 6 cell batchUpdate（BP 道具 → 新道具）
3. 6 cell **回读**确认含新 item / 不含旧 item
4. 2112 insertDimension 在数值前驱+1，写 25 列，ID 回读
5. 2111 insertDimension 在 21116001 占位符之前，写 9 列，ID 回读

任一步失败抛 AssertionError，**不会留下脏数据**。

### Step 4 — Verify（独立可调）

```bash
python3 scripts/signin.py verify --id-2112 21127898
```

校核：
- 2112 行存在，priority/base_activity/22 task/login_complement 全齐
- 2111 有指向该 2112 ID 的 calendar 行，且位于占位符之前
- 2115 21 task 全在

返回非 0 即有问题。

## 不做的事（明确边界）

- **1511 displaykey** ui_template 表：用户预先配好传 id 进来
- **21680 show_hud** 表：同上
- **LC 文案**（如 LC_EVENT_anni_log_in_actv_rule）：模板里全节日共用，不需要每节日新建
- **2011/2013 IAP**：签到不需要 IAP 挂钩
- **1011 翻译表**：签到 UI 文案是模板共用 LC，不走 18 语扩散（除非后续改文案）
- **修改通用 task 的非 BP 奖励**：脚本不会动通用池里的 7 种道具

## 真实案例存档

2026-05-06 拓荒节签到 21127898 落地（mode B）：
- 2112 row 1780 / 2111 row 1939 / 2115 6 cell（211552230/234/237/241/244/248）
- BP 道具 11112091 → 11112150（污染了春节/科技节/复活节签到的 6 处奖励，已知）
- ui_template 21191578 / show_hud 21680032 / banner=BG_408.png（同复活节）

## 与其他 skill 的关系

- `p2-config-diagnosis`：bug 时跑这个先诊断
- `p2-numerical-design`：签到道具数量/数值若需要重新设计走这个
- `p2-translation-style` + `p2-translation-automatic`：仅当签到 UI 文案改名（基本不改）才走
- `p2-gdconfig-push`：QA 配完后导到 gdconfig tsv 走这个
