---
name: p2-festival-flash-sale
description: >-
  P2 节日限时抢购端到端配置 skill。覆盖 2 行 2112 主壳 + 2 行 2111 calendar + N 处 2013 节日道具替换。
  核心机制：限时抢购的 2135/2011/2013/2121/2115/2137 全部跨节日错峰共用同一套底层池（base_activity_id=21127385 情人节遗留 base），
  新节日上线只需新建 2 行 2112 + 2 行 2111 + 改 2013 里的节日专属道具。带 scripts/flash_sale.py 自动化（learn/plan/apply/verify）。
  触发：配 {节日} 限时抢购、写 {节日} 限抢、{节日}-限时抢购-S6/S3-5、限抢通用皮、提配置限抢、event flash sale。
---

# P2 节日限时抢购配置 Skill

## Scope 边界

**只处理**：限时抢购 S6 + S3-5 双 2112 主壳 + 节日道具切换。

**不在 scope**（碰到要切别的 skill）：
- 限时抢购的奖励数值平衡 / ROI 校验 → `p2-numerical-design`
- 节日累充活动配置（recharge_actv 链路） → 待 `iap-leichong-sync` skill
- 18 语翻译扩散（`LC_EVENT_flash_sale_*` 是模板共用 LC，新节日不需要新 LC） → 不需要走翻译
- 如果用户要"完全 fork 一份独立池"（不复用底层）→ 当前脚本不支持，需手动操作

## 关键事实：限抢是节日错峰共用底层（非常重要）

| 表 | 节日独立 | 节日共用 | 当前实例 ID |
|---|---|---|---|
| 2112 主壳 | ✅ 每节日 2 行 | — | 21127693/694 复活、21127716/717 科技、21127895/896 拓荒 |
| 2111 calendar | ✅ 每节日 2 行 | — | 节日区 21115xxx 段 |
| 2135 package | — | ✅ 16 个 | 21353311-21353326 |
| 2011 IAP | — | ✅ 14 个 | 2011400075-2011400088 |
| 2013 IAP 模板 | — | ✅ 14 个 | 2013500354-2013500367（**奖励道具会随当前激活节日改写**） |
| 2121 flash_sale_* | — | ✅ 8 个 | 21217182-21217189（duration/opentime/gacha S6+S35/popup S6+S35/raffle S6+S35）|
| 2115 task | — | ✅ 5 个 | 211572527-211572531 |
| 2137 retake | — | ✅ 1 个 | 21371262 |
| base_activity_id | — | ✅ 1 个 | **21127385**（情人节遗留 base，全节日共用）|

**含义**：上线新节日时，2013 里的奖励道具会被覆盖（上一节日的"自选宝箱"换成本节日的）。**老节日 2112 行虽然在 2111 calendar 留着，实际玩家看到的是当前激活节日的奖励**。这是 P2 限抢机制设计如此，不是 bug。

## 不变量模板（写到代码里强制）

`scripts/flash_sale.py` 顶部锁死：

| 字段 | 列 | 值 | 说明 |
|---|---|---|---|
| priority | E | 59999 | 全节日限抢统一 |
| base_activity_id | F | 21127385 | 情人节遗留 base，全节日共用 |
| filter | G | `{"op":"ge","typ":"building","id":111811,"val":5}` | 全统一（基地 lv5）|
| text | H | LC_EVENT_flash_sale_name (label/title) | 全统一 |
| description | J | `{"rule":"LC_EVENT_flash_sale_rule"}` | 全统一 |
| ui_template | K | 21191338 | 全统一 |
| rank_group | L | 1 | 全统一 |
| banner_obj | M | `""` 字面双引号 | 全统一 |
| banner_url | N | `assets/operation/P2dlcimg/activityImg/EventBanner_BG_425.png` | "通用皮"模板，节日有专属美术再换 |
| banner_v | O | 1 | 全统一 |
| calendar | S | 0 | 全统一 |
| calendar_reward | T | `[]` | 全统一 |
| display_flags | X | 96 | 全统一 |
| country_use_type | Y | 0 | 全统一 |

**S6 components**: packages 21353311-318 + tasks 211572527-531 + flash_sale_buy_opentime 21217189 + flash_sale_buy_duration 21217182 + flash_sale_gacha **21217183** + flash_sale_popup **21217184** + flash_sale_raffle **21217186** + retake 21371262

**S3-5 components**: packages 21353319-326 + 同 5 task + 同 buy_opentime/duration + flash_sale_gacha **21217188** + flash_sale_popup **21217185** + flash_sale_raffle **21217187** + retake 21371262

**节日专属（4 个）**：constant(C) / comment(B) / show_hud(R) / 节日道具替换。脚本只改这 4 个 + id(A)，其余 25 列照搬科技节 21127716/717 模板。

## 2112 命名规范

- **id**: 用户预分配（21127XXX 段）
- **constant**: `event_{festival_slug}_flash_sale_s6` / `..._s3_5`
- **comment**: `{节日中文}-限时抢购-S6-通用皮（1、2期` / `..._S3-5-通用皮（3期`

`{festival_slug}`: pioneer / easter / spring / tech / xmas / halloween / thank / moon / anni / sci / valen / abyss

## 2111 calendar 落位规则（必须）

- **物理位置**：紧贴 21116001 占位符（"节日占位符-以上是节日"）之前
- **新行 ID**：节日区当前最大节日 ID + 1（自动从占位符上一行算）
- **段位**：21115XXX 段（**绝不能用 21117XXX，那是非节日区**）
- 9 列字段全按模板：`schema:[1,2,3,4,5,6]` / `typ:time, is_ark:1` / 其余 `{}` / data_cross=0 / country=0
- activity_id 指向新 2112 id（S6 → s6 ID，S3-5 → s3_5 ID）

## 2013 节日道具替换清单（必检）

每次新节日上线前，扫 14 个 2013 模板（500354-500367），按下面分类处理：

### 🔴 红色英雄相关（永远必须移除）

| item id | 名称 | 历史出现档位 |
|---|---|---|
| 11116272 | 碎片-艾里奥特（quality=15115983 红色） | S6-49.99 B / S6-99.99 A/B |
| 11116390 | 红色英雄-专属技能养成道具 | S6-99.99 A |
| 11116391 | 红色英雄-切换天赋页道具 | S6-99.99 B |

**用户硬约束**：拓荒节、感恩节、圣诞节等不投红色英雄的节日必须 0 容忍移除。脚本 verify 阶段会扫 14 个 2013，发现这 3 个 ID 直接抛 fail。

### 🎁 节日自选宝箱（必须按节日切换）

| item id | 名称 | 出现档位 |
|---|---|---|
| 111110264 | 2026复活节自选宝箱 | S6-19.99 A / S6-99.99 A / S3-5-19.99 A / S3-5-99.99 A |
| 111110325 | 2026拓荒节自选宝箱 | (拓荒节 2026 切换时用) |
| 111110256 | 2026科技节外显体验卡自选道具 | (科技节投放期) |

每个节日要在 1111 表 grep `class=item_select_box && comment ~ {年}{节日}.*自选宝箱` 找对应 ID，4 处槽位全替换（保留原数量 ×20 / ×100）。

### 🎲 节日玩法专属道具（按当季玩法决定换不换）

| item id | 名称 | 玩法窗口 |
|---|---|---|
| 11117305 / 11117019 | 战装大富翁-骰子 / 幸运币 | 大富翁玩法激活季 |
| 11117107 | 月度异族-穿甲弹 | 异族月活动季 |
| 11119084 | 收藏品盲盒抽奖币-飙车族 | 飙车族玩法季 |
| 11117479 / 11119694 | 行军特效-海滩拾贝-永久 / 周年庆蛋糕-行军特效自选宝箱 | 节日特效投放窗口 |

**判断规则**：当前节日如果有同类玩法（拓荒节有大富翁吗？），保留；没有就请用户给替换品 ID。**默认不擅自决定**。

### 🟢 跨节日通用（永远不换）

11114317-11114320 联盟礼物礼包 1-6 / 11116110 升星橙 / 11116304 万能英雄碎片橙 / 11116402 高级抽奖券 / 11119707 限抢皮肤随机宝箱 / 11119797 成长线宝箱自选 / 11112030 装饰券 / 11161002 XP 经验 / 19345xxx 材料

## 工作流（4 步）

### Step 0 — 自主学习（必做）

```bash
python3 scripts/flash_sale.py learn
```

返回 JSON：
- `2112_template`: 21127716/21127717 25 列模板
- `2111_placeholder_row` / `2111_last_festival_id` / `2111_next_id`
- `2013_reward_scan`: 14 个模板 R 列扫描，标识每档当前的节日道具
- `red_hero_items_present`: 红色英雄 3 个 ID 是否仍在 2013（应为空数组）

### Step 1 — 收齐用户确认的 5 个变量（**触发即问，不替用户决定**）

触发本 skill 后第一件事是列下面 5 项空表请用户填：
1. **2112 S6 ID**（21127XXX，用户预分配）
2. **2112 S3-5 ID**（21127XXX）
3. **节日英文 slug**（pioneer / easter / spring / tech / xmas / ...）
4. **节日中文名**（拓荒节 / 复活节 / ...）
5. **show_hud**（21680XXX，对应 2168 表节日入口图标）

可选：
- **节日自选宝箱 ID**（111110XXX，1111 表新节日 select_box）— 不给的话脚本只新建 2112+2111，不动 2013 道具
- **banner_url**（默认 BG_425.png 通用皮，节日专版需提供）

### Step 2 — Plan dry-run

```bash
python3 scripts/flash_sale.py plan \
  --festival pioneer --cn 拓荒节 \
  --id-2112-s6 21127895 --id-2112-s3-5 21127896 \
  --show-hud 21680032 \
  --festival-select-box 111110325
```

输出三表完整写入计划（**不动表**）：
- 2 行 2112 数据
- 2 行 2111 数据 + 落位 row（占位符之前）
- 4 处 2013 R 列改动（含旧值 vs 新值 diff）

### Step 3 — Apply

```bash
python3 scripts/flash_sale.py apply <相同参数>
```

脚本顺序：
1. **2013 写前 row 校对**：每个 R 列改前先 ID 校对（A 列 = 期望 2013 ID）
2. 4 cell batchUpdate（111110264 → 拓荒节自选宝箱 ID）
3. 4 cell **回读**确认含新 ID / 不含旧 ID
4. 2112 insertDimension 在数值前驱+1，写 25 列 ×2 行，ID 回读
5. 2111 insertDimension 在 21116001 占位符之前，写 9 列 ×2 行，ID 回读

任一步失败抛 AssertionError，**不会留下脏数据**。

### Step 4 — Verify（独立可调）

```bash
python3 scripts/flash_sale.py verify --id-2112-s6 21127895 --id-2112-s3-5 21127896
```

校核：
- 2 行 2112 存在，priority/base_activity/components 全齐
- 2111 有指向 S6 + S3-5 的 calendar 行，且都在占位符之前
- 14 个 2013 中无红色英雄 ID（11116272/11116390/11116391）

返回非 0 即有问题。

## ⚠️ 警示（每次必读）

### 警示 1：底层奖励是全节日共用，2013 改一动全节日变

修改 2013 的 R 列 = 切换全局奖励，会同时影响**所有 2112 限抢主行**（包括复活/科技节）。
**前提**：上一节日已结束，下一节日错峰激活。如果两节日同时在 2111 calendar 激活，奖励会出错。
触发本 skill 时先扫 2111 calendar 看哪些 2112 限抢行还在调度。

### 警示 2：2111 calendar 段位很容易踩坑

- 节日区 ID 段是 **21115XXX**（21115772 拓荒节签到 / 21115773 拓荒节巨猿 / ... 21115774-5 限抢）
- **21116001 = "节日占位符-以上是节日"** 是硬分隔线
- **绝不能放表尾**（21117XXX 段是非节日活动，违反约定）
- 数值前驱很容易撞 ID（巨猿砸金蛋 / 卡包BP 等已占了 21115773-21115774），插入前先 grep 占位符上一行的 ID

### 警示 3：show_hud 是必须节日专属的

复活=21680031 / 科技=21680027 / 拓荒=21680032，对应 2168 表节日入口图标。
用户如果没给 show_hud，必须暂停问。**不能用上一个节日的 show_hud**（玩家会看到错误的节日入口图标）。

## 真实案例存档

**2026-05-06 拓荒节限抢落地**：
- 2112: 21127895 (S6) row 1780 / 21127896 (S3-5) row 1781
- 2111: 21115774 row 1941 / 21115775 row 1942（紧贴 21115773 巨猿之后、21116001 占位符之前）
- show_hud: 21680032
- 2013 替换: 111110264 → 111110325（4 处：500355 / 500359 / 500362 / 500366）数量保持 ×20/×100
- 红色英雄已被用户预先从 2013 清掉（11116272/11116390/11116391 在 S6-49.99B/99.99A/99.99B 三档）
- iap_status 拓荒节 recharge_actv 由用户后续统一改

**踩坑记录**：
- 第一次 calendar 误用 21117155/156 段（非节日区），用户纠正改 21115774/775
- delete + appendDimension + insertDimension 序列易导致 row 残留（21117156 漏删 1 行），verify 阶段必须扫表尾
- 2111 grid 不够大时 insertDimension 会报错 "startIndex must be less than the grid size"，要先 appendDimension 扩 grid 或选 inheritFromBefore=true

## 不做的事（明确边界）

- **2168 show_hud** 表：用户预先配好传 id 进来
- **1111 节日自选宝箱**：用户预先在 1111 建好，传 id 进来
- **LC 文案**（如 LC_EVENT_flash_sale_name/rule）：模板里全节日共用，不需要每节日新建
- **2011 iap_status 追加 recharge_actv**：用户说"后面统一改"，本 skill 不动
- **gdconfig push**：QA 配完后导到 gdconfig tsv 走 `p2-gdconfig-push` skill

## 与其他 skill 的关系

- `p2-config-diagnosis`：限抢 bug 时跑这个先诊断
- `p2-numerical-design`：奖励数值/ROI 重新设计走这个
- `p2-festival-signin`：同节日签到配置走对应 skill（结构高度类似）
- `p2-gdconfig-push`：QA 配完后 push 到 gdconfig 仓库
