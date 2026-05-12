---
name: p2-festival-cityeffect-recharge
description: >-
  P2 节日主城特效累充三件套（个人/服务器/联盟）端到端配置 skill。一次配齐 2112 主表 + 2111 calendar +
  2122 rank（4 个）+ 2121 special（3 个）+ 2115 task（11 档）+ 1168 access_group（1 个），
  共 6 张表 25 行写入。默认按春节 2026 模板（21127582/583/703）patch，跨节日通用组件全沿用，节日专属
  字段（3 个 2112 ID + LC_Key + 美术 + 5 个累充范围 access_group args + 1312 city_skin + 累充统计
  rank）参数化。带 scripts/cityeffect_recharge.py 自动化（learn/plan/apply/verify），写前 ID 占用核查、
  写后 ID 回读、依赖图按 1168→2122→2121→2115→2112→2111 顺序写入。
  触发：配 {节日} 主城特效累充、写 {节日} 累充三件套、{节日}-主城特效累充-{个人/服务器/联盟}、
  累充个人/服务器/联盟、event city_effect accum_recharge、cityeffect 累充。
---

# P2 节日主城特效累充三件套配置 Skill

## Scope 边界

**只处理**：完整三件套版的"主城特效累充"——
- 个人版：iap_show + city_skin + 11×task + jump_link + 3×lucky_reward + lucky_cost + actv_show_rank + rank + countdown + retake
- 服务器版：package + jump_link + 6×progress + 2×progress_final + actv_show_rank + 2×rank + countdown
- 联盟版：iap_show + preview + package + jump_link + 4×progress + 2×progress_final + actv_show_rank + 2×rank + countdown + description

**不在 scope**（碰到要切别的 skill 或问用户）：
- 简化版主城皮肤累充（如 21127410 拓荒节2025 单 task 版） — 这不是三件套
- 累充范围 IAP 白名单的具体 ID 列表（用户后面通过 `iap-leichong-sync` 类 skill 统一改）
- 1312 city_skin 表的皮肤本身建立（套装最终皮肤、display_key、suit_id、buff 由美术/数值同事提前建好，本 skill 只引用）
- 2119 ui_template 表（联盟版每节日新建一个 21191xxx UI 模板由 UI 同事建，本 skill 只引用，不传则用占位）
- LC_Key 翻译扩散（走 `p2-translation-automatic`）
- gdconfig push（QA 配完后走 `p2-gdconfig-push`）

## 关键事实：三件套是"科技节首发 base + 跨节日组件复用"

| 维度 | 个人版 | 服务器版 | 联盟版 |
|------|------|------|------|
| base_activity_id | **21127335** 科技节2025 个人首发 | **21127336** 科技节2025 服务器首发 | **21127566** 星球套2025 联盟首发 |
| ui_template | **21191310** 跨节日固定 | **21191311** 跨节日固定 | **每节日新建**（春节 21191428 / 星球套 21191393）|
| priority | 49999 | 49998 | 49998 |
| calendar 标志 | 1（开 timeline） | 0 | 0 |

## 不变量模板（写到代码里强制）

`scripts/cityeffect_recharge.py` 顶部锁死，改前先改这里：

### 三版通用字段

| 字段 | 列 | 值 | 说明 |
|---|---|---|---|
| filter | G | `{"op":"ge","typ":"building","id":111811,"val":6}` | 民政厅 6 级 |
| description | J | `{"rule":"LC_EVENT_tech_cityeffect_actv_rule"}` | 跨节日通用 rule LC |
| rank_group | L | 1 | 全统一 |
| banner_obj | M | `""` 字面双引号 | 全统一 |
| banner_ver | O | 1 | 全统一 |
| default_dk | P | 0 | 全统一 |
| display_flags | X | 0 | 全统一 |
| country_use_type | Y | 0 | 全统一 |
| dependent | V | 0 | 全统一 |

### 个人版 components 通用 ID（不变）

- iap_show（无 id）
- 3×tech_lucky_reward: **21217083 / 21217084 / 21217085**
- tech_lucky_cost: **21217391**
- retake: **21371220**

### 服务器版 components 通用 ID（不变）

- package: **21357332**（跨节日复用同一个 IAP 礼包）
- 6×server_recharge_progress: **21217392-21217397**
- 2×server_recharge_progress_final: **21217398 / 21217399**
- actv_show_rank: **21215722**
- countdown: **21217099**

### 联盟版 components 通用 ID（不变）

- iap_show（无 id）
- preview: **21218445**
- package: **21357712**（跨节日复用同一个 IAP 礼包）
- jump_link: **21217390**（联盟版 jump_link **真的跨节日复用**，跟个人/服务器版每节日新建不同）
- 4×server_recharge_progress: **21218438-21218441**
- 2×server_recharge_progress_final: **21218442 / 21218443**
- actv_show_rank: **21218446**
- countdown: **21217099**
- description: **21219017**

### 11 档累充 task 模板（**新模板基线 = 拓荒节2026 211595001-011**，下次新节日从这套复制+换 3 个节日专属槽位）

| 档 | val（累充$0.01）| reward 摘要 |
|---|---|---|
| 1 | 1250 | item 11119848×1 + 11116304×1 + material 19345004×2 + 11112498×30 + 11111105×2 |
| 2 | 2500 | 11118203×1 + 11116304×1 + 19345004×4 + 11114330×4 + 11111105×4 |
| 3 | 5000 | 11118203×1 + 11116304×1 + 19345004×6 + 11112498×30 + 11111105×6 |
| 4 | 12500 | 11118858×1 + 11116304×2 + 19345004×8 + 11112498×30 + 11111105×8 |
| 5 | 25000 | 11118203×5 + 11116304×4 + 19345004×10 + 11112498×30 + 11111105×10 |
| 6 | 50000 | 11118203×8 + 11116304×6 + 19345004×12 + 11112498×30 + 11111105×12 |
| 7 | 100000 | 11118203×10 + 11116304×8 + 19345004×14 + 11112498×30 + 11111105×14 |
| 8 | 175000 | 11118203×20 + 11116304×10 + 19345004×16 + 11112498×30 + 11111105×16 |
| 9 | 300000 | 11118203×25 + 11116304×12 + 19345004×18 + 11112498×30 + 11111105×18 |
| 10 | 500000 | 11119708×1 + 11116304×15 + 19345004×20 + 11112498×30 + 11111105×20 |
| 11 | 750000 | 11119844×1 + 11116304×90 + 19345004×450 + 11114330×450 + 11111105×40 |

数值需要改时改脚本顶部 `TASK_VALS` / `TASK_REWARDS`。

### 节日专属 vs 通用奖励道具识别（每节日必换 3 个槽位）

参考行 211572183-193 / 春节 211584133-142 的 reward 数组里，**只有 3 个 1111 id 是节日专属，每节日必换**：

| 槽位 | 模板 id | 含义 | 春节2026 用 | 拓荒节2026 用 |
|---|---|---|---|---|
| T1.slot1 | 11119848 | 节日个人累充抽奖票（class=event, effect.id=2112_personal_id）| 11119848（春节复用情人节）| **111110400 新建** |

⚠️ **新建抽奖票 1111 道具时，lc_name / lc_desc 直接复用老抽奖票（11119848）的 LC key**，**不要**自创 `LC_ITEM_{festival}_super_lotto_name`：
- lc_name = `{"typ":"lc","txt":"LC_ITEM_planet_super_lotto_name"}`
- lc_desc = `{"typ":"lc","txt":"LC_ITEM_planet_super_lotto_desc"}`

抽奖票名称/描述跨节日通用（"主城特效抽奖券"），不需要节日命名。display_key 才是每节日不同（拓荒节=151105008，由用户给）。
| T4.slot1 | 11118858 | 节日机甲喷漆（class=mecha_skin_colour）| 11118856 | **11118892** |
| T11.slot1 | 11119844 | 节日累充顶档主城特效/皮肤（class=city_effect / city_skin / city_suit_decoration）| 111110010 | **111111100**（用户预建的 item_select_box "高级主城特效自选宝箱"）|

其余 8 处道具（11118203 机甲芯片宝箱 / 11119708 2小时攻击buff / 11116304 万能英雄碎片橙 / 11112498 复活节漫游骰子 / 11111105 60min加速 / 11114330 高级资源宝箱10w / material 19345004）**全节日通用，不换**。

### 显示顺序 display_order（每档严格降序，最后 3 档共 99991）

```
T1=99999  T2=99998  T3=99997  T4=99996  T5=99995  T6=99994  T7=99993  T8=99992  T9=99991  T10=99991  T11=99991
```

**易踩坑**：之前脚本默认全填 99999，导致 11 档 task 在 UI 里乱序。必须按上面值降序写。

### 4011 mecha_colour 联动（**T4 喷漆道具的隐性依赖**）

T4 用机甲喷漆（如 11118892）时，必须去 `4011_p2_mecha_colour`（spreadsheetId `1nl7w3Vfm1Wgv2ih5xKcPdLaIwfxv-ArWztVUSBlPnKY`，tab `macha_colour`，注意 typo "macha"）找到对应的 `effect.mecha_colour.id`（如 401111005）的行，把 `A_INT_activity_select`（col R）从 `0` 改成 `1`，否则机甲喷漆在活动里不能选用。

### tech_lucky_cost 跨节日复用 21217086（**禁止每节日新建**）

2121 表 `21217086`（科技节累充-大乐透-消耗道具）是**跨节日错峰共用的"万年消耗道具行"**——每节日上线前只改这一行的 `A_INT_arg1`（消耗的抽奖票 1111 id）。
拓荒节 2026 改成 `arg1=111110400`。**禁止再每节日新建一行 21217xxx**——之前误建了 `21217391`（周年庆），现已废弃。
2112 主表 components 的 `tech_lucky_cost.id` 永远引用 `21217086`，不要再换。

### actv_show_rank 每节日必须新建 3 个（个人 / 服务器 / 联盟，**不要跨节日复用**）

2121.actv_show_rank 行的 `arg1` 直接指向本节日的 2122 rank ID（节日专属），所以**不能跨节日复用**——每节日 3 件套（个人/服务器/联盟）各自新建一条 actv_show_rank。
拓荒节 2026 实例（已落 QA）：
- `212120004` 个人 actv_show_rank → arg1=21223501（group=392 个人 rank）
- `212120006` 服务器 actv_show_rank → arg1=21223503（group=393 server rank）
- `212120007` 联盟 actv_show_rank → arg1=21223504（group=393 alliance rank）

⚠️ 易踩坑：`21215722`（春节-服务器）/ `21218446`（星球套-联盟）之类老行**不能跨节日复用**——arg1 锁死了上一节日的 rank。**每节日 3 件套上线必须新建 3 条 actv_show_rank**。

### 联盟 alliance jump_link 也要切到本节日 jump_link（**禁止继续用 21217390**）

历史 alliance 三件套（星球套/科技节/春节/拓荒）都把 `jump_link` 设成 `21217390`（comment "2025周年庆-节日累充跳转"，expr.id=11684589 即周年庆 access_group）—— 这个跨 4 节日的"alliance 共用 jump_link"实际是**死锁的周年庆 jump 配置**，跨节日复用会导致玩家点跳转跳到周年庆活动列表。

正确做法：alliance.jump_link 跟个人/服务器**共用本节日 jump_link**（拓荒节=212120003，expr.id=11684906 拓荒节 access_group）。**不要因为历史包袱留 21217390**。

### 联盟跨节日复用的真共用行（**行 ID 不动，但 reward 数组要改**）

下列 alliance components 是真"星球套2025 模板"跨节日错峰复用——**components.id 不换**（春节也是这么处理的），但里面的 reward/cost 数组**每节日要改**：
- `package=21357712`（components 顶层 + 6 progress.reward 都引）—— 星球套 alliance 折扣团购 IAP 礼包
- `server_recharge_progress` 6 行 `21218438-441` + `final 21218442` + `final_first 21218443` —— 团购档位（原价/折扣1/2/3/折扣4+BUFF + 首个折扣4BUFF）
- `description=21219017` —— 联盟团购礼包描述
- `server_recharge_countdown=21217099` —— 24h 倒计时
- `banner_url` —— EventBanner_BG_504.png 跨节日复用（拓荒节同春节）

具体礼包内部的"换节日道具"逻辑发生在 package 内部 IAP 配置（2135/2011/2013），而非 alliance 2112/2121 这一层。

### preview 也每节日新建（**跟 actv_show_rank 同模式，liusiyi 区间**）

`preview` 行的 reward[0] 是节日专属的"主城套装体验卡自选盒"，跟 actv_show_rank 一样**不能跨节日复用** —— 老 row（如 `21218445`）的 reward[0] 锁死了上一节日的体验卡 1111 道具，强行复用会让玩家在拓荒节看到战地套预览。

每节日上线 alliance 必走 2 步：
1. **新建本节日"主城套装体验卡自选盒" 1111 道具**（class=item_select_box，select_box 装本节日 14天体验版 city_skin/city_suit_decoration + 11118663 多成长线宝箱）。拓荒节 2026 = `111110401`（巨龙套2026 ×4 + 11118663）
2. **新建本节日 preview 2121 行**（liusiyi 区间内下一可用 ID），reward 数组 = [本节日体验卡, 11111218 4h扩编, 11111210 24h攻强, 11111212 24h防强]

拓荒节 2026 实例：preview = `212120008` reward[0]=111110401 buffs同春节 / actv_show_rank = `212120007` arg1=21223504

⚠️ 老 alliance preview 行别动：21218445.reward[0]=111110256（战地套）保持不变，**春节/科技节/星球套照旧复用 21218445**，只有拓荒节及之后新节日切到本节日新 preview 行。

⚠️ 易踩坑：春节 alliance 当前仍 components.preview.id=21218445 → 战地套预览 = 隐藏 bug（活动里看到的是战地套礼包预览不是春节）—— 历史遗留，理论上春节 alliance 也应该 backfill 一个 spring preview 但不属本次范围。

### 2137 retake 跨节日复用 21371220（**同 21217086 模式**）

2137 表 `21371220`（科技节累充-gacha 道具，spreadsheetId `1ctEGsAU053iaCCTJeIU1qnp9zfyuURt7k8EzHkKzv2Y`，tab `activity_asset_retake`）是**累充 gacha 抽奖回收行**——玩家用抽奖票兑换 gacha 实物时走这条 retake：
- `give_asset`（col C）= 跨节日固定 `{"typ":"item","id":11111001,"val":1}`（gacha 实物道具）
- `cost_asset`（col D）= 节日专属 = 当前节日抽奖票 1111 id

每节日上线前**只改 D 列的 cost_asset.id** 为本节日抽奖票（拓荒节2026=111110400，科技节2025=11119444 是历史值）。
2112 主表 components 永远引用 `retake.id=21371220`，不新建 21371xxx。

⚠️ 2137 表还有一行 `21371255`（科技节套装 S2 累充 gacha）也用过 11119444，但那是**另一个节日**的累充 retake，跟主城特效累充无关——别误改。

### 累充统计机制（春节 2026 起）

- task fincond.cat = **10148028**（春节起换的新机制；星球套/科技节用旧 cat=101412053 + 大白名单）
- task fincond.arg.ids = `[<新建个人 rank ID>]`（指向 group=392 的 rank，由其 score_rule 累计 IAP）
- 2122 rank score_rule.cat：
  - group=392 / 353（个人累充统计）= **101425016**（按 IAP ID 列表统计）
  - group=393（服务器排名）= **101425015**（score_rule.ids = `[2112_server_id]`，按主活动 ID 统计）
  - group=393（联盟排名）= **101427041**（score_rule.ids = `[2112_alliance_id]`，按主活动 ID 统计）

## 节日专属字段（每次必须传）

| # | 字段 | 用途 | 拓荒节2026 实例值 |
|---|------|------|---|
| 1 | `--festival` slug | 英文标识 | labor |
| 2 | `--cn` 中文名 | 命名/comment | 拓荒节 |
| 3 | `--year` | 年份后缀 | 2026 |
| 4 | `--id-personal` | 2112 个人 ID | 21127892 |
| 5 | `--id-server` | 2112 服务器 ID | 21127893 |
| 6 | `--id-alliance` | 2112 联盟 ID | 21127894 |
| 7 | `--icon-dk` | 1511 display_key（**只用于 2112 主表 HUD icon，每节日不同**；2122 排行榜 4 行全部硬编码 `15112516` 不受此参数影响）| 15116147 |
| 8 | `--show-hud` | 2168 节日 HUD | 21680032 |
| 9 | `--banner-personal` | 个人版 banner_url 文件名 | EventBanner_BG_423.png |
| 10 | `--banner-server` | 服务器版 banner | EventBanner_BG_467.png |
| 11 | `--banner-alliance` | 联盟版 banner | EventBanner_BG_504.png |
| 12 | `--cal-banner` | 个人版 timeline banner | EventBanner_Timeline_157.png |
| 13 | `--city-skin` | 1312 表 套装最终皮肤 ID | 13121115 |
| 14 | `--access-group-args` | N 个 2112 ID（当季核心付费玩法跳转列表）| 21127899,21127808,21127806（节日挖孔/推币机/弹珠GACHA）|

可选：
- `--alliance-ui-template`：联盟版 UI 模板（默认 21191428 春节占位，UI 同事建好新版后用此覆盖）
- `--group-label-lc`：默认按节日年份生成。**拓荒节特例**：默认 `LC_EVENT_2024labor_accum_recharge_event`（跨年通用，21127097/411/410 都用）
- `--personal-lc-name`：个人版 label/title LC，默认 `LC_EVENT_{slug}_cityeffect_actv_name`
- `--score-rule-ids-source`：累充统计 rank 的 score_rule.ids 来源
  - `clone-spring`（默认）：复用春节 21222393 的 393 个 IAP ID 占位
  - `empty`：留空 `[]`（用户后面统一填）

## ID 段位规律（脚本自动选号）

| 表 | 自动选号策略 | 拓荒节2026 实例 |
|---|---|---|
| 2112 | 用户预分配 3 个连号 | 21127892/893/894 |
| 2111 | 紧贴 21116001 占位符之前，节日段当前 max+1 起 3 连号 | 21115776/777/778 |
| 2122 | 当前 max+1 起 4 连号（group 392/353/393/393）| 21223501-504 |
| **2121** | **必须落在 'liusiyi占用' 区间内**（21212xxxx 段，212120000 与 212130000 标记之间）| 212120006/007/008（拓荒节 2026 已用 003/004/005）|
| 2115 | **必须落在 'liusiyi占用' 区间内**（211595000 起、211510000 止），21158xxxx 春节段已占满，落 211595xxxx 段 | 211595001-010 |
| 1168 | 当前 max+1 单行 | 11684906 |

### ⚠️ 2121 / 2115 占位区间规则（**重要！**）

P2 的某些表用"liusiyi占用 / zhangting占用"行做**人员预留区间**：
- 2121 表：**21212xxxx** 段是 liusiyi 区间（row 标记 212120000/212130000 是 liusiyi 占用行）；**21219xxx / 21211xxxx 段是 zhangting 区间**（不能占）
- 2115 表：**211595000-211510000** 是 liusiyi 区间（带"liusiyi占用开头/末尾"comment 标记）

脚本通过 `find_liusiyi_range()` 函数扫表里 'liusiyi占用' 标记，自动取区间内 max ID + 1 作为新 ID。**绝不能直接用 max(全表) + 1**，否则会落到 zhangting 区间触发同事冲突。

## 写入依赖顺序（脚本固化）

`apply` 子命令按下面顺序串行执行：

1. **1168 access_group** — 拿到 jump_link.expr.id 引用
2. **2122 rank ×4** — 拿到 task fincond.arg.ids + components rank IDs
3. **2121 special ×3** — jump_link 引用 1168 ID，actv_show_rank 引用 2122 个人 rank
4. **2115 task ×11** — fincond.arg.ids 引用 2122 个人 rank
5. **2112 ×3** — components 引用 2121/2122/1168 全部 ID
6. **2111 calendar ×3** — activity_id 引用 2112 ID

任何一步失败抛 AssertionError，**已写的早段不会回滚**（业主决定要不要补救——通常是脚本修复后从失败处续写）。

## 工作流（4 步）

### Step 0 — 自主学习（必做）

```bash
python3 scripts/cityeffect_recharge.py learn
```

返回 JSON：
- `2112_template_personal/server/alliance`: 春节 21127582/583/703 三件套完整模板
- `1168_max_id` / `2121_max_id` / `2122_max_id` / `2115_max_id`：各表当前最大 ID
- `2111_placeholder_row`: 21116001 行号 + 节日段 next_id
- `spring_iap_ids`: 春节 21222393 的 393 个 IAP ID 数组（占位用）

### Step 1 — 收齐用户必填的 14 个变量（**触发即问，不替用户决定**）

触发本 skill 后第一件事是列上面"节日专属字段"的 14 项空表请用户填。**不能替用户假设**：
- 1312 city_skin ID（拓荒节 2026 已有 13121113/114/115 三档）必须用户告知用哪个
- access_group 的 5 个 2112 ID 必须用户给（"拓荒节当季有哪些核心付费玩法"是业务决策）
- 美术资源（icon_dk/show_hud/3×banner/cal_banner）必须用户给

### Step 2 — Plan dry-run

```bash
python3 scripts/cityeffect_recharge.py plan \
  --festival labor --cn 拓荒节 --year 2026 \
  --id-personal 21127892 --id-server 21127893 --id-alliance 21127894 \
  --icon-dk 15116147 --show-hud 21680032 \
  --banner-personal EventBanner_BG_423.png \
  --banner-server EventBanner_BG_467.png \
  --banner-alliance EventBanner_BG_504.png \
  --cal-banner EventBanner_Timeline_157.png \
  --city-skin 13121115 \
  --access-group-args 21127651,21127689,21127806,21127558,21127362
```

输出 6 表完整写入计划（**不动表**）：
- 1168: 1 行 access_group
- 2122: 4 行 rank
- 2121: 3 行 special
- 2115: 11 行 task
- 2112: 3 行 main
- 2111: 3 行 calendar

每行附带「插入位置（row）+ 列内容预览」。

### Step 3 — Apply

```bash
python3 scripts/cityeffect_recharge.py apply <相同参数>
```

按依赖顺序串行写入。每张表步骤：
1. 检查 ID 段空位，确认无碰撞
2. insertDimension（中间插入）或 appendDimension（表尾延伸）
3. values update 写入数据
4. **回读校验** ID 列匹配预期

### Step 4 — Verify（独立可调）

```bash
python3 scripts/cityeffect_recharge.py verify \
  --id-personal 21127892 --id-server 21127893 --id-alliance 21127894
```

校核：
- 6 张表对应 ID 全部存在
- 2112 三行 components 引用的所有 ID 在对应表能找到（依赖闭环）
- 2111 三行紧贴占位符之前
- task fincond.arg.ids 指向真实存在的 2122 rank
- 1168 access_group 列表非空（如果占位 0 会 fail）

返回非 0 即有问题。

## ⚠️ 警示（每次必读）

### 警示 1：联盟版 ui_template 是节日专属，不传就是春节占位

UI 同事每节日单独建一个 21191xxx 联盟版 UI 模板（春节 21191428 / 星球套 21191393 / 科技节 21191xxx）。
脚本 `--alliance-ui-template` 不传时使用 21191428 占位，**激活后联盟版 UI 会显示春节风格**，必须 UI 建好后用 `apply` 覆写或手动改这一格。

### 警示 2：累充统计 cat 春节起从 101412053 → 10148028

旧机制（科技节 / 星球套 task fincond.cat=101412053）需要在 fincond.arg.ids 维护几百个 IAP ID 白名单——每节日要追加。
**新机制（春节起 cat=10148028）通过引用一个 group=392 的 rank 来统计**，本 skill 强制用新机制。如果用户要保留旧机制要明确说，**默认不替用户决定**。

### 警示 3：access_group 列 2112 ID 是节日专属，**每次必须问用户**

参考春节 11684712 列了 5 个 args（钓鱼/挖孔×2/拓荒节BP/异族大富翁）；拓荒节 2026 改成 3 个（节日挖孔-新/推币机-新/弹珠GACHA）。
**每次新节日上线时这个清单都不一样**，由用户根据当季玩法清单给定。

🚨 **触发本 skill 时必须明确问用户：『1168 access_group 跳转的活动 ID 列表是什么？』** 不要替用户选默认值（即使有上一节日清单可参考），不要从 2112 表自动 grep "节日相关"——这是产品层业务决策。

### 警示 4：score_rule.ids 占位 vs 真实 IAP

脚本默认 `--score-rule-ids-source clone-spring`，写春节 393 个 IAP 占位。
**激活前用户必须用 `iap-leichong-sync` 类工具批量把这 393 个 ID 替换为拓荒节专属的 IAP ID**，否则玩家充拓荒节 IAP 不计入累充。

### 警示 5：2122 rank score_rule.cat 三种不同

| group | cat | ids 含义 |
|---|---|---|
| 392 / 353（个人统计/共用）| 101425016 | IAP 2011 ID 数组 |
| 393（服务器排名）| 101425015 | 单元素 = 服务器 2112 ID |
| 393（联盟排名）| 101427041 | 单元素 = 联盟 2112 ID |

脚本自动按 group 选 cat，不要手动改。

### 警示 6：2111 calendar time_info 必须空 `{}`

主城特效累充活动的时间窗**不通过 2111.time_info 配置**，由 base_activity_id（21127335/336/566）的时间继承。
脚本写 2111 三行的 time_info 字段强制 `{}`，不接受用户传入起止时间。

### 警示 7：2122 rank A_INT_icon_display_key 全节日统一 15112516（**不要被 --icon-dk 串污**）

2122 排行榜 4 行（group 392/353/393/393）的 `A_INT_icon_display_key` **跨所有累充节日实例统一为 `15112516`**——这是排行榜列表的通用图标 ID。审计 group=392/353/393 全部历史行确认：除一处 `151104368` 例外（情人节单期特殊），全部累充三件套都是 `15112516`。

⚠️ 不要跟 2112 主表 HUD icon（A_INT_icon_displaykey）混淆：
- **2112 HUD icon** 每节日不同：拓荒节2024=15117636 / 拓荒节2025=15119925 / 春节2026=151101310 / 拓荒节2026=15116147 → 由 `--icon-dk` 参数传入
- **2122 rank icon** 跨节日相同：永远 `15112516` → 脚本 `build_2122_rows()` 4 行全部硬编码

🔥 2026-05-08 踩坑：`build_2122_rows()` group=392 第一行曾误用 `p["icon_dk"]`（即 2112 主表的 HUD icon 值），导致拓荒节2026 的 21223501 写成 15116147。已修正为硬编码 `"15112516"`。

## 真实案例存档

### 拓荒节 2026 主城特效累充三件套（已落 QA，2026-05-07~08 完整版）

| 表 | 个人 (21127892) | 服务器 (21127893) | 联盟 (21127894) |
|---|---|---|---|
| 2112 main | row 1780 | row 1781 | row 1782 (注：经一次 deletion 后实际 row 偏移) |
| 2111 calendar | 21115776 | 21115777 | 21115778（紧贴 21116001 占位符前 ✓）|
| 2122 rank slot 1 | 21223501（group 392 个人）| 21223502（group 353 共享累充统计）| 21223502（同 server）|
| 2122 rank slot 2 | — | 21223503（group 393 server）| 21223504（group 393 alliance）|
| 2122 icon_display_key | 全 4 行统一 **15112516** | 同 | 同 |
| 2121 jump_link | **212120003** expr.id=11684906 | 同（共用）| **同 212120003**（不再用 21217390 周年庆死锁）|
| 2121 actv_show_rank | **212120004** arg1=21223501 | **212120006** arg1=21223503 | **212120007** arg1=21223504 |
| 2121 server_recharge_countdown | **212120005** | 21217099（共用）| 21217099（共用）|
| 2121 preview | — | — | **212120008** reward[0]=111110401 + 3 通用 buff |
| 2121 tech_lucky_cost | 21217086 共用，arg1 改 111110400 | — | — |
| 2121 tech_lucky_reward | 21217083/084/085 共用 | — | — |
| 2115 task | 211595001-011（11 档，group 290）| 211595012-021（group 282 服务器，不归个人累充结构）| — |
| 2137 retake | 21371220 共用，cost.id 改 111110400 | — | — |
| 1168 access_group | 11684906 row 865 args=[21127899/808/806] | — | — |

**1111 新建 + 复用清单**：
- `111110400` 拓荒节累充抽奖票（class=event, effect.id=21127892）—— lc_name/desc 复用 `LC_ITEM_planet_super_lotto_*`（**抽奖票 LC 跨节日通用**）
- `111110401` 拓荒节体验卡自选盒（class=item_select_box, select_box=巨龙套2026 ×4 14天 + 11118663）—— lc_name/desc=`LC_ITEM_labor_2026_city_suit_select_box_*`（PM 已预译"苍龙引雷"+"猩球"）
- `111111100` 用户预建顶档奖励（class=item_select_box "高级主城特效自选宝箱"）—— 我曾误建 city_skin 版重复，事后 deleteDimension 修
- 复用项：T2 11118203 机甲芯片宝箱 / T4 11118892 蜘蛛粉色喷漆（**4011 row 93 activity_select 已开 1**）/ T10 11119708 2h攻击buff "不要投放" / T11 顶档槽 111111100

**节日参数终值**：
- icon_dk=15116147 / show_hud=21680032 / city_skin=13121115（巨龙套最终皮肤）
- banner: 个人=423.png / 服务器=467.png / 联盟=504.png（联盟跨节日复用 504）
- ui_template 联盟=21191428（春节占位，UI 同事未建拓荒节专版）
- group_label=`LC_EVENT_festival_accum_recharge_title`（情人节起跨节日通用，禁自创年份专属）
- 个人 label/title=`LC_EVENT_moon_cityeffect_actv_name`（带 moon 名字但跨节日通用）
- 个人 constant=`event_techFestival_2026_city_effect_personal_labor`（错误模板沿用，应 `event_labor_2026_city_effect_personal`）
- 联盟 constant=`event_labor_2026_city_effect_alliance`

### 拓荒节 2026 机甲累充（21127891，独立结构，待建 p2-festival-mecha-recharge skill）

- 2115 task: 211595012-022 row 12643-12653（11 档，group 290 个人；跟主城特效 server group 282 211595012-021 ID 段重叠是巧合，非同表）

  ⚠️ 注意：机甲累充 task ID 段（211595012-022 group=290）跟 主城特效累充 server task（211595012-021 group=282）**ID 段完全重叠** —— 是不同 group 的不同行，gws 读 col B 看不出来。要看 col A group 区分。

- gacha 道具（每节日必问用户）= **`11112649`**（周年弹珠 GACHA）—— 不是 `11112164`（拓荒节通用 GACHA, 表面看更"对应"但用户说错了），10 档全部用此 id 数量递增 5/12/25/50/200/200/450/450/500/550
- T2 第二槽通用 `11112163`（2024拓荒节犀牛染色自选）— 历史复用
- T5 第一槽通用 `11112280`（感恩节机甲自选假道具）— 跨节日复用
- T11（每日累充1500）：111110325（拓荒节自选宝箱）×3 + 11111152 + 11111002 通用加速

## 新节日累充三件套上线 12 步 cookbook（下次跑此清单即可）

收齐 14 项节日参数后（slug/cn/year/3 个 2112 ID/icon_dk/show_hud/3 个 banner/cal_banner/city_skin/access_group_args），按如下顺序执行：

1. **1168 access_group** 新建 1 行 + args 列表（用户给定，禁默认）
2. **2122 rank** 新建 4 行（group 392/353/393/393）—— icon_display_key 全部 **15112516** 硬编码（禁用 --icon-dk 参数）
3. **2121 jump_link** 新建 1 行（liusiyi 区间，expr.id=本节日 access_group）—— 个人/服务器/联盟全部共用此一条
4. **2121 actv_show_rank ×3** 新建（个人/服务器/联盟分别指 group=392/393server/393alliance rank）
5. **2121 server_recharge_countdown** 新建 1 行（个人用，跨节日实际共用 21217099 也行）
6. **2121 preview**（联盟用）新建 1 行 reward=[本节日体验卡, 11111218 4h扩编, 11111210 24h攻强, 11111212 24h防强]
7. **1111 抽奖票** 新建 1 行（lc 复用 `LC_ITEM_planet_super_lotto_*`，effect.id=本节日个人 2112 ID）
8. **1111 体验卡自选盒** 新建 1 行（select_box=本节日 14天体验项 + 11118663）—— **写前先 live 读 1011 ITEM tab 查 LC，PM 可能预译过禁重复**
9. **4011 mecha_skin_colour** 把 T4 喷漆道具的 mecha_colour 行 col R `activity_select` 改成 1
10. **2115 task** 新建 11 行（211595001-011 拓荒节版作模板，复制 reward 整段，只换 3 槽位：T1 抽奖票/T4 喷漆/T11 顶档主城特效），display_order 严格 99999→99991
11. **2137 retake 21371220** 改 cost_asset.id=本节日抽奖票（不新建）；**2121 21217086** 改 arg1=本节日抽奖票（不新建）
12. **2112 三件套 main** 新建 3 行 components 引用以上全部新建 ID + 联盟 components 还要引用真共用行（package 21357712 / 6 progress 21218438-443 / description 21219017）；**2111 三件套 calendar** 新建 3 行紧贴 21116001 占位符前

最后 verify：所有 components 引用 ID 全部能在对应表找到 + 2122 4 行 icon_display_key 都是 15112516 + 4011 喷漆行 activity_select=1 + 21217086.arg1 + 21371220.cost.id 都指本节日抽奖票 + 联盟三件套 actv_show_rank/preview/jump_link 是本节日新行不复用老行。

**踩坑记录**：
- 第一次 group_label 自创了 `LC_EVENT_2026labor_accum_recharge_event`，后发现拓荒节累充已有通用 LC——后又改成情人节起最新模式 `LC_EVENT_festival_accum_recharge_title`（**全节日通用**，跟 label/title 同含义）
- **个人版 label/title 自创 `LC_EVENT_labor_cityeffect_actv_name` 是 bug**——所有节日个人版用通用 `LC_EVENT_moon_cityeffect_actv_name`（虽然名字带 moon 但跨节日通用，春节/情人节/拓荒节都用这个）。脚本默认值已修正
- task 数量误用 11 档（沿用星球套2025 顶档 750000）——情人节/春节起改成 10 档（最高 500000）。脚本默认改成 10 档
- 2121 写入时 ID 没按升序（先 act_show_rank 后 jump_link）—— 修正为按 ID 升序写
- 2122 / 2115 是表尾延伸（grid size 等于 max ID 行），insertDimension 会报错 "startIndex must be less than the grid size"，必须用 appendDimension 扩 grid 再 update
- 21222368（星球套2025联盟充值排名）看似跨节日复用但实际每季节修改 score_rule.ids（春节改成 [21127703]）—— 不能再被拓荒节安全复用，必须新建
- **🔥 2122 group=392 行 icon_display_key 串污**：第一次 `build_2122_rows()` 把 `p["icon_dk"]`（2112 HUD icon = 15116147）传给了 2122 的 group=392 行，导致 21223501 跟其它 3 行（502/503/504 全部 15112516）不一致。2122 4 行的 icon_display_key 跨节日全部统一 15112516，脚本已硬编码不再受 `--icon-dk` 影响
- **🔥 2115 task reward 全部乱写 + display_order 全 99999**：2026-05-08 拓荒节 2026 落地后用户审计发现 11 档 task 的 reward 数组都是脚本胡编的（不是从参考累充复制），display_order 全填 99999 导致 UI 乱序。修正：reward 必须从 211572183-193 整段复制，**只换 3 个节日专属槽位**（T1=抽奖票/T4=喷漆/T11=顶档主城特效），display_order 严格降序 99999→99991（T9-T11 共享 99991）
- **🔥 1111 写新道具前查 id 占用要包含 == 分支**：脚本 `for r in rows: if n < tid: prev_row=r; elif n > tid: print` 漏了 `n == tid` 分支，导致已存在的 id 被当成空号位重复写入。2026-05-08 拓荒节 111111100（用户预建的 item_select_box "高级主城特效自选宝箱"）被脚本误判空号位，重复写入了一行 city_skin 版本，事后用 deleteDimension 修。**写前 ID 占用核查**必须 `if n == target: raise AlreadyExists`
- **🔥 tech_lucky_cost 不要每节日新建**：第一次每节日新建一行 21217xxx（如 21217391 周年庆-大乐透-消耗道具）—— 错误。2121 21217086 是跨节日错峰复用的"万年消耗道具行"，每节日只改 arg1 不新增。components 永远 `tech_lucky_cost.id=21217086`
- **🔥 mecha 喷漆奖励必须开 4011 activity_select**：T4 用机甲喷漆（如 11118892）时若 4011 表对应行 `A_INT_activity_select=0`，活动里选不了。每次新喷漆首次进 累充 reward 前必须把 4011 row.R 改成 1
- **🔥 2121 ID 段位错位**：第一次用了 21219636/637/638 落在 zhangting 占用区间，被用户搜不到——P2 的 2121/2115 表有"liusiyi占用 / zhangting占用"行做人员预留区间隔离，新 ID 必须落在 liusiyi 区间（212120xxx 段，标记行 212120000/212130000 之间）。脚本已加 `find_liusiyi_range()` 自动选号

## 不做的事（明确边界）

- **1312 city_skin** 表：用户预先在 1312 建好套装最终皮肤（class=4 / suit_id），传 ID 进来
- **2168 show_hud** 表：用户预先配好传 ID 进来
- **2119 ui_template** 联盟版：UI 同事建好后传 ID（不传用春节占位）
- **1511 display_key** 表：节日图标 icon_dk 用户传 ID
- **LC 文案翻译扩散**：18 语翻译走 `p2-translation-automatic`
- **2011 iap_status 追加 recharge_actv**：用户后面通过 `iap-leichong-sync` 类 skill 统一改
- **gdconfig push**：QA 配完后导到 gdconfig tsv 走 `p2-gdconfig-push` skill

## 与其他 skill 的关系

- `p2-config-diagnosis`：累充活动 bug 时跑这个先诊断
- `p2-numerical-design`：11 档累充奖励数值/ROI 重新设计走这个
- `p2-festival-flash-sale`：限抢配置（结构高度类似的"三件套" 之兄弟 skill）
- `p2-festival-signin`：签到配置（同节日另一个三表 skill）
- `p2-translation-automatic`：节日 LC（group_label / 个人 label/title）翻译扩散
- `p2-gdconfig-push`：QA 配完后 push 到 gdconfig 仓库
- `iap-leichong-sync`：替换 score_rule.ids 为节日专属 IAP 白名单
