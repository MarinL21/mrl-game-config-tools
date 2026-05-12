---
name: p2-wonder-egg-game
description: >-
  P2 节日 wonder 巨猿砸金蛋玩法端到端配置 skill。覆盖 5 表写入：
  2112 主表 + 2121(task_group + festival_wonder) + 2115(15 task) + 2111 calendar + 2011 IAP。
  默认按"复活节-2026-wonder巨猿-砸金蛋 21127698"模板克隆：
  112 components 中 110 项跨节日复用、2 项节日专属（task_group/festival_wonder）；
  15 task 节日各自一份；IAP 砸蛋锤礼包用 time_info.normal 数组多 actv_id 共享。
  带 scripts/wonder_egg.py 自动化（learn/plan/apply/verify），写前 ID 占用核查、写后 ID 回读。
  触发：配 {节日} wonder 巨猿砸金蛋、提配置 wonder 砸金蛋、{节日}wonder、festival_wonder、巨猿玩法。
---

# P2 节日 wonder 巨猿砸金蛋配置 Skill

## Scope 边界

**只处理**：节日 wonder 玩法的巨猿砸金蛋（priority=49982, base_activity_id=21121499, ui_template=21191534, filter 城堡≥8）。

**不在 scope**（碰到要切别的 skill 或问用户）：
- 跨服 wonder（21121260 主活动那一套）/ 太空争霸 wonder
- 节日签到 / BP / 累充 / 行军特效礼包 等其他玩法 → 切 `p2-festival-signin` 等
- 1111 表新建 BP 经验道具（脚本只复用已存在的节日 BP 道具）
- 1511 displaykey / 21680 show_hud / 21219xxx 共用 LC 的人工配置（脚本不动这些）
- 美术 / 18 语翻译 → 切 `p2-festival-art-brief` / `p2-translation-automatic`

## 玩法拓扑

```
2112 主行 (1 行)
├─ priority=49982, base_activity_id=21121499（拓荒节-2023-wonder巨猿，跨节日共用底子）
├─ ui_template=21191534, icon_displaykey=15116148
├─ banner=EventBanner_BG_162.png, calendar_banner=EventBanner_Timeline_168.png
├─ text.label=LC_EVENT_labor_wonder_event_title（拓荒节 LC，全节日共用）
├─ description.rule=LC_EVENT_2024_valentine_wonder_rules_1（情人节 LC，全节日共用）
├─ filter={"op":"ge","typ":"building","id":111811,"val":8}（城堡≥8）
└─ A_ARR_activity_components (112 项):
   ├─ 110 项跨节日复用：
   │  ├─ rank x1 (21222171)
   │  ├─ buff x3 (21211821-23)
   │  ├─ retake x2 (21371450-51)
   │  ├─ jump_link x2 (21219498-99)
   │  ├─ quest_reward_require x5 (21215311-15)
   │  ├─ task x7 (211586794-800) ← 框架级 task，跨节日共用
   │  ├─ create_entity x86 (21341186-272) ← 地图实体（巨猿/金蛋/营地）
   │  ├─ wonder_egg_drop x1 (21219500) ← 砸金蛋核心掉落
   │  ├─ wonder_hero_display x1 (21218353) ← 巨猿英雄展示
   │  ├─ task_group 通用 x1 (21218351) ← 联盟积分任务分组
   │  └─ package x1 (21359398) ← 砸蛋锤礼包 → 2135 → 2011500698
   └─ 2 项节日专属（每节日各一份）：
      ├─ task_group(节日积分任务) → 2121 表新行
      └─ festival_wonder(节日奖励) → 2121 表新行

2121 task_group (节日新行)
├─ A_STR_type=task_group, arg1=1
├─ comment="2026{节日}巨猿个人积分任务分组"
└─ A_ARR_array=[15 个 task id]  → 指向 2115 表 15 行新 task

2121 festival_wonder (节日新行)
├─ A_STR_type=festival_wonder, arg1=13330067, array=[3,10]
├─ comment="2026{节日}节巨猿奖励"
└─ A_ARR_reward=[{"asset":{"typ":"item","id":<节日 BP 道具>,"val":1}}]

2115 task (节日 15 行新 task)
├─ A_INT_group=284
├─ comment="{节日}节日活动-wonder巨猿-1-17"（前5）/-18-24（中5）/-25-35（后5）
├─ task_desc=LC_EVENT_2023_labor_wonder_task_score（拓荒节 LC，全节日共用）
├─ fincond.cat=10142127, fincond.arg.ids=[13330067]
├─ display_order 99766→99752 递减
└─ reward[5/6 项]: 4 通用道具 + 1 节日 BP 道具（11112xxx）

2111 calendar (节日新调度行)
├─ cal_id=新分配（21115xxx 段接续）
├─ activity_id=2112 主行 ID
├─ comment="{节日}-{年}-wonder巨猿-砸金蛋"
└─ server_info=[1,2,3,4,5,6,13,14,15,16,17,18]

2011 砸蛋锤礼包 2011500698（共享一行 IAP）
└─ time_info.normal[].actv_id 数组追加新节日的 2112 ID
```

## 跨节日变量 vs 不变量

### 节日变量（每节日必换）

| 表.字段 | 内容 | 来源 |
|---|---|---|
| **2112.A_INT_id** | 21127xxx 新号（用户预分配） | 用户给 |
| 2112.S_STR_comment | "{节日}-{年}-wonder巨猿-砸金蛋" | 拼 |
| 2112.A_STR_constant | `event_{slug}_festival_hegemony_{year}` | 命名规律 |
| 2112.A_INT_show_hud | 21680xxx（节日已建好的"系列活动"行） | 用户给 |
| 2112.components.task_group(节日专属) | 21219596(复)→212120001(拓荒)... | 新建 |
| 2112.components.festival_wonder | 21219597(复)→212120002(拓荒)... | 新建 |
| **2121.task_group 新行** | id + comment + array | 新建 |
| **2121.festival_wonder 新行** | id + comment + reward.item.id | 新建 |
| **2115.15 task 新行** | id + comment("复活节"→"{节日}") + reward[节日 BP] | 新建 |
| **2111.calendar 新调度行** | cal_id + activity_id + comment | 新建 |
| **2011.2011500698.time_info** | normal 数组追加新 actv_id | patch |

### 不变量（跨节日复用，禁改）

写到代码常量，不变。详见拓扑图里"110 项跨节日复用"段。

## 节日 BP 经验道具映射表（1111 表）

写 2121.festival_wonder.A_ARR_reward + 2115 task reward 替换关键道具时用。**已存在的节日 BP 道具直接引用，不新建**。

| 节日 | BP 道具 ID | 名称 | constant slug |
|---|---|---|---|
| 复活节 | **11112091** | 魔术棒 | easter |
| 科技节 | **11112127** | 聚能环 | tech |
| 拓荒节 | **11112150** | 纪念钻头 | labor |
| 春节 | 11112031 / 11112398 | 绣球（年专 / 通用） | spring |
| 情人节 | 11112060 / 11112408 | 夹心巧克力 | valen |
| 端午节 | 11112178 | 船桨 | dragon |
| 深海节 | 11112201 | 藏宝图碎片 | abyss |
| 周年庆 | 11112226 | 欢乐气筒 | anni |
| 登月节 | 11112293 | 纪念胶卷 | moon |
| 万圣节 | 11112306 | 南瓜币 | halloween |
| 感恩节 | 11112334 | 感恩食材盒 | thank |
| 圣诞节 | 11112001 / 11112356 | 幸运铃铛 | xmas |
| 沙滩节 | 11117166 / 11117473 | 沙滩铃鼓/摇铃 | beach |
| 音乐节 | 11119726 | （无名） | music |

未列节日：去 1111 表 grep `class=battle_pass_exp + comment 含{节日}/{slug}`。

## 2115 task reward 通用 vs 节日专属

15 行 task 每行 reward 是 5-6 道具数组，每行恰好 **1 个节日 BP 道具** + 其余通用。

**通用道具池**（跨节日不换，写死在脚本）：

| item id | 出现次数（15 行中） | 备注 |
|---|---|---|
| 11119980 | 15 | 全 15 行都给 |
| 11112498 | 15 | 漫游骰子-节日进度（虽叫节日进度但跨节日通用） |
| 11111156 | 15 | 通用资源 |
| 11116402 | 6 | 高级奖池抽奖券 |
| 11116111 | 6 | 通用 |
| 11111152 / 11111105 / 11111106 | 各 3 | 通用，分阶段 |

**节日专属（必换）**: 复活节 11112091 → 新节日的 BP 道具。脚本通过 "reward 中 item id == 复活节 BP 道具" 自动识别替换点，**不依赖 reward 数组下标**。

## ID 段分配规则

| 表 | 节日 wonder 占用段 | 当前最大值（2026-05） | 取号策略 |
|---|---|---|---|
| 2112 主行 | 21127xxx | 21127698 复活/21127578 科技/21127897 拓荒 | 用户预分配 |
| 2121 task_group / festival_wonder | 21219xxx 旧/212120000-212130000 新 | 复活=21219596/97，科技=21219496/97，拓荒=212120001/02 | 默认在 [212120000, 212130000] 区间挑空号；老节日用 21219xxx 段 |
| 2115 task | 211584xxx 段每节日 15 连号 | 复活 211584103-117，科技 211584118-132，拓荒 211584088-102（用户分配前段） | 用户给起始 ID 或脚本找下个 15 连号空位 |
| 2111 calendar cal_id | 21115xxx 接续 | 拓荒 wonder=21115773 | 找现有最大 cal_id 加 1，且必须 < 21116001 占位符 |
| 2011 IAP 砸蛋锤 | **2011500698 一份共享** | 不新建，仅 time_info.normal 追加 | 不分配新 ID |

## ⚠️ 五大警示（这次踩过的坑）

### 1. ID 占用必须双查（21127898 撞过）

写 2112 之前不只查 ">ID 的最小后继"，**也要查 "==ID 自身是否已被占用"**。

复活节巨猿砸金蛋曾计划用 21127898，结果发现 21127898 早被分配给"拓荒节签到-2026"，最后改用 21127897。

`scripts/wonder_egg.py learn` 自动做双查并报错。

### 2. calendar 预留行陷阱

2111 表里看到 `activity_id=<目标新ID>` 的现成行**不一定是给你预留的**。可能是别的活动（如签到）的真实调度行。

判定方法：看 `S_STR_comment` 字段。如果 comment 是别的活动名（"{节日}签到-{年}"等），**不要盖**——必须新建调度行而不是复用。

### 3. 2011 IAP 跨节日共享是默认做法

砸蛋锤礼包 `2011500698`（desc 写"科技界 typo"）一份 IAP 行跨多个节日 wonder 共用，靠 `time_info.normal` 数组追加 `{actv_id:新ID}` 实现。

P2 支持 normal 数组多 actv_id（最强猴子礼包就是 4 个活动共用一行）。**不要每节日复制新 IAP 行**——会破坏既有运营。

### 4. 文案 LC 的混乱继承

- text.label=`LC_EVENT_labor_wonder_event_title` ← **拓荒节 LC，全节日共用**
- description.rule=`LC_EVENT_2024_valentine_wonder_rules_1` ← **情人节 LC，全节日共用**
- 2115 task_desc=`LC_EVENT_2023_labor_wonder_task_score` ← **拓荒节 LC，全节日共用**

这种"祖宗节日 LC 全节日共用"是 P2 wonder 模块的历史包袱。**不要改 LC，不要新建 LC**。

### 5. base_activity_id 是拓荒节 2023 的（21121499）

所有节日 wonder 巨猿砸金蛋的 `base_activity_id=21121499`（"拓荒节-2023-wonder巨猿"）。这是这个 wonder 玩法的祖宗，跨节日共用 base 配置（活动结构、入口、UI 框架）。**禁改**。

## 工作流（4 步）

### Step 0 — 自主学习（必做，禁绕过）

```bash
python3 scripts/wonder_egg.py learn
```

返回 JSON：
- `existing_wonders`: 当前 2112 已有的所有 wonder 巨猿砸金蛋（含 base_activity_id 反查、id 段、comment）
- `template_2112_row`: 25 列模板（自动选最新 ID 的 wonder 行）
- `template_2121_pair`: 复活节 task_group + festival_wonder 全字段
- `template_2115_15rows`: 复活节 15 行 task 全字段
- `template_iap_5029`: 砸蛋锤礼包 row 5029 当前 time_info
- `bp_item_map`: 14 个节日 BP 道具映射表
- `next_2115_task_window`: 自动算的 15 连号空位

### Step 1 — 收齐用户确认的 8 个变量（**触发即问，不替用户决定**）

按 `feedback_proactive_questions`/`feedback_signin_ask_inputs`，触发本 skill 后第一件事是列下面 8 项空表请用户填，不要先猜默认：

1. **2112 ID**（21127xxx，用户预分配，必须双查未占用）
2. **节日英文 slug**（labor / easter / tech / spring / xmas / halloween / thank / moon / anni / valen / abyss / dragon / beach / music）
3. **节日中文名**（拓荒节 / 复活节 / ...）
4. **年份**（2026 / 2027）
5. **show_hud**（21680xxx，节日已建好的"系列活动"行，不新建）
6. **节日 BP 道具 1111 id**（按 BP 映射表，找不到去 1111 grep `class=battle_pass_exp + comment 含{节日}`）
7. **2121 新 ID 段**（task_group + festival_wonder，默认 [212120000, 212130000] 取最低空号 2 个连号；老节日复用 21219xxx）
8. **2115 task 起始 ID**（用户给一个 15 连号区间起点，脚本验证空号）

### Step 2 — Plan dry-run

```bash
python3 scripts/wonder_egg.py plan \
  --festival labor --cn 拓荒节 --year 2026 \
  --id-2112 21127897 \
  --show-hud 21680032 \
  --bp-item 11112150 \
  --id-2121-task-group 212120001 --id-2121-festival-wonder 212120002 \
  --task-start 211584088
```

输出五表完整写入计划，**不动表**。让用户看一遍再 apply。

### Step 3 — Apply

```bash
python3 scripts/wonder_egg.py apply <相同参数>
```

脚本顺序（依赖优先）：
1. **2121 写前 ID 校对** → insertDimension → 写 task_group + festival_wonder 两行 → ID 回读
2. **2115 写前 ID 校对** → insertDimension 15 行 → 写 15 行 → ID 回读
3. **2112 写前 ID 双查（==自身 + >自身）** → insertDimension → 写主行 → ID 回读
4. **2111 calendar 新行** → 找现有 cal_id 最大 + 1（< 21116001）→ insertDimension → 写 → ID 回读
5. **2011 IAP time_info patch** → 读 row 5029 当前 time_info → JSON parse → 数组追加新 actv_id → 写回 → 回读校验包含

任一步失败抛 AssertionError，**不会留下脏数据**。

### Step 4 — Verify（独立可调）

```bash
python3 scripts/wonder_egg.py verify --id-2112 21127897
```

校核：
- 2112 行存在，priority/base_activity/components.110+2 全齐
- 2121 task_group + festival_wonder 行存在，相互引用对齐
- 2115 15 task 全在，reward[节日 BP 道具] 数量正确
- 2111 有指向该 2112 ID 的 calendar 行，且 cal_id < 21116001
- 2011 砸蛋锤礼包 time_info.normal 含新 actv_id

返回非 0 即有问题。

## 真实案例存档

**2026-05-06 拓荒节-2026-wonder巨猿-砸金蛋 21127897 落地**：

| 表 | 写入 | ID |
|---|---|---|
| 2112 | row 1782 新建 | 21127897 |
| 2121 | row 3311-3312 新建 | 212120001 task_group / 212120002 festival_wonder |
| 2115 | row 10885-10899 新建 15 行 | 211584088-102 |
| 2111 | row 1940 新建 | cal_id=21115773 |
| 2011 | row 5029 patch | 2011500698.time_info 追加 actv_id=21127897 |

**踩过的坑**：
- 21127898 误占用 → 改 21127897（21127898 是签到的）
- 2111 row 1939 cal_id=21115772 是签到调度行，曾误改 comment 已撤回
- 2115 task 起始号用户分配在复活节段前（211584088-102 在复活 211584103 之前），不是后段接续

**未做（用户决定不做）**：
- 1111.11112150.category_param={} 跟复活节 11112091 不一致（复活节有 actv_open 跳转），跨节日不一致是历史问题，不在本次 scope
- 2011500698.desc "2026科技界wonder巨猿砸蛋锤礼包" typo，不动

## 与其他 skill 的关系

- `p2-config-diagnosis`：bug 时跑这个先诊断
- `p2-numerical-design`：task reward 数值若需要重新设计走这个
- `p2-festival-signin`：节日签到走这个，跟 wonder 完全不同的拓扑
- `p2-festival-art-brief`：banner / icon 美需走这个
- `p2-translation-style` / `p2-translation-automatic`：本 skill 不动 LC（全部复用）
- `p2-gdconfig-push`：QA 配完后导到 gdconfig tsv 走这个
