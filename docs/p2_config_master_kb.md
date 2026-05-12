# 游戏运营配置表自动化 — 知识库

> 本文档从配置逻辑和字段规范两个维度，系统记录活动配置体系的通用规则，使任何活动都能套用。

---

## 一、基础信息

### 1.1 配置表目录

- **名称**：p2_gsheet_config
- **Google Sheets ID**：`1wYJQoPcdmlw4HcjmR2QP41WP4Gb4k8Rd7iCJJX7H_8c`
- **作用**：所有配置表的目录索引，B列=表名，D列=文档ID

### 1.2 表编号命名规则

- 每张配置表有一个 **4 位数字编号**（如 2112、1224）
- 目录表 B 列格式：`{编号}_{表名缩写} - 中文说明`
- 目录表 D 列：Google Sheets 文档 ID
- 引用时直接说编号，如"2124 表"

### 1.3 常用表速查


| 编号   | 表名                           | 用途          | 文档ID                                         | 主页签                          |
| ---- | ---------------------------- | ----------- | -------------------------------------------- | ---------------------------- |
| 2112 | activity_config              | 活动配置总表（入口）  | 1IKUBw678b2PU1m0md1vR9GxcH2uTNyLbR7VWgyAJ57E | activity_config_qa           |
| 2124 | activity_drop                | 掉落配置        | 1V7xDriTe0hGW3SF7ZPtk71-sFGyzpbbO47V6gLoBqVA | activity_drop                |
| 2115 | activity_task                | 任务配置        | 1K3-I4gCYKY-Zw5Ms05ozHtHKpOqYI-lp4kuuhqbWajY | activity_task_QA             |
| 2135 | activity_package             | 活动礼包（桥接表）   | 1KrcIA8jC4Aj6sFz44c_2lhtJ-lyD1OYu3QNpzaor8Mc | activity_event_pkg           |
| 2011 | iap_config                   | 礼包条件配置      | 1yS_BehT_Rfcc3sXjDPsSaQRcjPh8YepucYTnUQDpEMc | iap_config_QA                |
| 2013 | iap_template                 | 礼包内容/价格     | 1sJzacpa0CBp1B8LQX1TboSBOA4T80_t8lH8eEzqHLbY | iap_template_QA              |
| 2121 | activity_special             | 活动特殊组件（万能表） | 1sicvhfxZhagLVmpEg4HDcaCnPWPgsWkhgZKC-HxCCuc | activity_special_QA          |
| 2122 | activity_rank_rule           | 排行榜规则       | 1zziy6nMR1DlhCykKBndwk6d6KNRrzj1PsOsFGbLYR4M | activity_rank_rule（QA）       |
| 2118 | activity_rank_rewards        | 排名奖励配置      | 1Nb23s9iVOiDzWGQlpHSRW5O0gIqd1ZiYNx9kYrDps2M | activity_rank_rewards        |
| 2168 | p2_activity_hud_entries      | 活动HUD图标     | 1PL868MbZ4vL60c3C9wImrciDr1xm0Kz_GlYIXnkACOg | （待记录）                        |
| 1168 | get_access_group             | 获取途径组合（跳转表） | 1KwX1xWoHHcmOGTaasZmMii2Al-YR_VXV3yoSGn3tBbA | get_access_group（杜绝手搓）       |
| 2116 | activity_item_exchange       | 道具兑换模块配置    | 14IDttHNuHx1U2I1kHinkMLIA6Q4cKmZ8MLoMkgdTGfY | activity_item_exchange       |
| 2130 | activity_battle_pass         | BP通行证总配置    | 1qe9RsX7P5bl_O2iLwh_eCJ62KtUkn_RaJiJ4uTRQS8M | activity_battle_pass         |
| 2131 | activity_battle_pass_level   | BP通行证等级奖励   | 1sbMG-3NHEGUgmpW5-kEzwnCkWoi94aeNSk50Zsu_Dcs | activity_battle_pass_level   |
| 2137 | activity_asset_retake        | 活动道具回收      | 1ctEGsAU053iaCCTJeIU1qnp9zfyuURt7k8EzHkKzv2Y | activity_asset_retake        |
| 2123 | activity_accumulate          | 累计配置        | （待记录）                                        | —                            |
| 1111 | item                         | 道具表         | 1FQqpeRfkXVwaEDSVi3oTaQNs2PLLDcsvQQmc-k0L3ws | —                            |
| 1116 | xp                           | 经验值/资产表     | 1FS5iz67L6bsXnvyyXzH5CJIxiMiiVyvZrfHfWfv-EqE | —                            |
| 1013 | const_config                 | 常量杂项配置      | 1WKAxQDf0-7UZADWxef1wDQaN0chqPJNa3zEB81W9fho | const_config                 |
| 2024 | iap_custom_chest             | 自选礼包配置      | 1jQSZKXz25Xl1Xps9o0x9SbkxKHkySb7mFr2pETGgF7c | iap_custom_chest             |
| 1142 | avatar_frame                 | 头像框配置       | 1jBsZOuoMz3uwYHN-Tcotn8QPBgX5LYDpUHXVu2LzpiQ | avatar_frame                 |
| 1511 | display_key                  | 美术资源配置      | 1Oks7yHCxYnWxo1QiNdO5EYNET68l_aCzZU-58zATlLY | display_key                  |
| 1011 | i18n                         | 客户端本地化文本    | 11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY | 无主页签，按类别分页签                  |
| 2111 | activity_calendar            | 活动日历（后台开启用） | 1OaExug4AwwFlGH6LGbBiMnvQF41hYg0LsXiMQZ9XX6g | activity_calendar_QA         |
| 2119 | activity_ui_template         | 活动UI模板      | 1_o6R4_vPcl9PACt_-5RZUqG5mYnWTTN7aA_sruSXGeM | activity_ui_template（qa）     |
| 2120 | activity_ui_module           | 活动UI模块      | 1b8aDEJWh4cmWKqrrg_5ZAkk3VdTj9k_6SBFbEt0P9-0 | （待记录）                        |
| 2154 | activity_without_gacha_floor | 爬塔层数配置      | 1XfENodZsKFH-hit2TWrxt8mmJSPqnn8qM2Cv2iIl2vo | activity_without_gacha_floor |
| 2169 | activity_hud_entry_style     | HUD入口样式配置   | （待记录）                                        | （待记录）                        |
| 1118 | building                     | 建筑表（含装饰本体）  | 1ES3syKlMbqqmZezWFCzwL0elIdrgvisiUTnBwJNRHrk | building（不要直接修改）             |
| 1127 | building_build               | 建筑建造入口      | 1Dlyk6JRGOYoVsSohfwXzbwN8wUvwlk1fGgBTzaDKtNw | building_build               |
| 2148 | event_decroation_level       | 活动装饰升级功能    | 1tI-J-BkIw7-NsoTN1yY-ZXJMW-edn7aK1GLsfVaeiVw | event_decroation_level       |
| 2171 | event_decroation_skill       | 装饰物技能表      | 1YJW39MBGg7aya62_hkhI1uRmyMknjZQV226Dqsksis4 | 装饰技能                         |


---

## 二、gws 工具操作

### 2.1 认证

```bash
gws auth status
```

- 用户：`sunminghao@nibirutech.com`，项目：`email-sent-dsy-2`

### 2.2 读取

```bash
gws sheets +read --spreadsheet "<文档ID>" --range "<页签>!<范围>" --format table|json
```

- `--format json` 适合管道给 Python 做数据处理
- 搜索关键词：管道接 `grep`
- 用 `2>&1 | grep -v "Using keyring"` 过滤认证日志后再 JSON 解析

### 2.3 写入（覆盖）

```bash
gws sheets spreadsheets values update \
  --params '{"spreadsheetId":"<文档ID>","range":"<页签>!<单元格>","valueInputOption":"RAW"}' \
  --json '{"values":[["<内容>"]]}'
```

> `+write` 不存在，必须用 `sheets spreadsheets values update`。中文页签名需转义单引号。

### 2.4 追加

```bash
gws sheets +append --spreadsheet "<文档ID>" --range "<页签>" --values '<JSON数组>'
```

### 2.5 range 格式

- 普通：`Sheet1!A1:E10`
- 中文页签：`'数据表'!A1:E10`（需加单引号）
- 仅页签名：`activity_config_qa`（默认从 A1 开始）

---

## 三、配置体系 — 表间关联逻辑

### 3.1 总入口：2112 活动配置表

**每行 = 一个活动**。核心字段是 I 列 `A_ARR_activity_components`，它以 JSON 数组列出该活动所有子模块：

```json
[
  {"typ": "drop",    "id": 21241882},
  {"typ": "task",    "id": 211562054},
  {"typ": "package", "id": 21353092},
  {"typ": "rank",    "id": 21222104}
]
```

### 3.2 组件 ID 定位规则（通用）

**规则：组件 ID 的前 4 位 = 子配置表的编号**


| 组件 typ                                                    | 前4位 → 表编号 | 目标表                                   |
| --------------------------------------------------------- | --------- | ------------------------------------- |
| drop                                                      | 2124      | activity_drop                         |
| task                                                      | 2115      | activity_task                         |
| package                                                   | 2135      | activity_package                      |
| battle_pass                                               | 2130      | activity_battle_pass                  |
| item_exchange                                             | —         | 2116（按 group 关联）                      |
| rank                                                      | 2122      | activity_rank_rule（排名规则，绑定 2118 排名奖励） |
| retake                                                    | 2137      | activity_retake                       |
| accumulate                                                | 2123      | activity_accumulate                   |
| jump_link / new_progress / cost / buff / actv_show_rank 等 | 2121      | activity_special（万能特殊组件表，297种type）    |
| **discount**                                              | **2121**  | **activity_special（本质是礼包，见下方说明）**     |
| cross_progress                                            | 2011      | iap_config（直接引用 2011 表 ID，非 2121）     |
| fes_module                                                | 2143      | 节日模块                                  |
| bp_rank_item                                              | 1111      | BP 排行榜展示道具                            |


> **注意**：`cross_progress`、`bp_rank_item` 的 ID **不遵循前4位规则**，它们直接引用 2011 和 1111 表的 ID。

> **注意**：`discount` 组件虽然在 2121 万能表中，但本质上是礼包组件。它通过 `A_ARR_status` 字段中的 `[{"typ":"iap","id":2011xxxxxx}]` 关联到 2011 礼包配置表，链路为 `2121.A_ARR_status → 2011 → 2013`，与 package 的 `2135 → 2011 → 2013` 链路殊途同归。**追踪活动关联礼包时，不能只看 package 组件，discount 等中转组件也会关联礼包。**

**通用定位步骤：**

1. 在 2112 表中找到目标活动（按 A 列 ID 或 B 列名称搜索）
2. 解析 I 列 JSON，提取目标 typ 的组件 id
3. 取 id 前 4 位 → 在"常用表速查"中找到文档ID和主页签
4. 在对应表中按 id 搜索具体配置行

### 3.3 配置追踪链总览

```
2112 activity_config（活动总配置，入口）
 ├── 2111 activity_calendar（活动日历，控制后台能否开启该活动）
 ├── 2115 activity_task（任务配置）
 ├── 2116 activity_item_exchange（道具兑换商店）
 ├── 2121 activity_special（特殊组件，万能表）
 ├── 2124 activity_drop（掉落配置）
 ├── 2135 activity_package → 2011 → 2013（礼包链路）
 ├── 2130 activity_battle_pass → 2131（BP 通行证）
 ├── 2122 activity_rank_rule → 2118（排行榜）
 ├── 2137 activity_asset_retake（道具回收）
 ├── 2119/2120 activity_ui_template/module（UI 模板）
 └── 2154 activity_without_gacha_floor（爬塔层数）

1111 item（道具表）
 ├── C_INT_display_key → 1511 图标资源
 ├── A_MAP_lc_name → 1011 翻译 key
 ├── C_ARR_display_labels → 背包分类显示
 ├── A_ARR_use_labels → 背包使用标签
 └── S_INT_use_now → 获得即用（1=是）

装饰物（四表联动）
2148 event_decroation_level（活动装饰升级，按星级一行）
 ├── A_INT_building      → 1118 的 A_INT_building_id（家族ID）
 ├── A_INT_unlock_item   → 1111 解锁道具（class=statue_decorate）
 └── A_ARR_upgrade_cost  → 1111 升级材料（class=event）
           │
           ↓
1118 building（按"家族 ID + 星级"展开，每星一行；type=2）
 └── A_INT_building_id 聚合同家族的所有星级；A_INT_lvl 指当前星
           ↑
1127 building_build（建造菜单入口；display_labels=["decoration"]）
 └── A_ARR_building_ids = [1118.A_INT_building_id]；A_ARR_unlock_cost=解锁道具
```

**2111 activity_calendar 说明**：活动能否在后台开启取决于此表是否有对应行（`A_INT_activity_id` 指向 2112 的活动 ID）。如果缺行，后台无法开启该活动。

### 3.4 各组件链路图

#### drop 链路（直接关联）

```
2112.A_ARR_activity_components → {"typ":"drop","id":2124xxxx}
    ↓
2124.A_INT_id = 2124xxxx （直接匹配，一步到位）
```

一个活动可包含多个 drop 组件（如强消耗活动有 4 个 drop，分免费/付费 × 阶段1/阶段2）。

#### task 链路（直接关联 + group 分组）

```
2112.A_ARR_activity_components → {"typ":"task","id":2115xxxx}
    ↓
2115.A_INT_id (B列) = 2115xxxx （直接匹配）
2115.A_INT_group (A列) = 同活动的所有 task 共享同一 group 编号
```

一个活动通常包含多个 task（如 15 个阶梯任务），它们共享相同的 `A_INT_group`。

#### package 链路（四表线性链路）

```
2112.A_ARR_activity_components → {"typ":"package","id":2135xxxx}
    ↓
2135.A_INT_id = 2135xxxx
2135.A_INT_iap (C列) = 2011xxxx       ← 指向 2011 的 ID
    ↓
2011.A_INT_id (A列) = 2011xxxx        ← 礼包条件配置
    ↓
2013.A_INT_config_id (C列) = 2011xxxx  ← 自动绑定，1对多
```

**关键要点：**

- **严格线性**：`2112 → 2135 → 2011 → 2013`，无分叉
- **2135 是桥接表**：仅通过 `A_INT_iap` 字段指向 2011ID
- **2013 自动绑定 2011**：通过 `A_INT_config_id` 匹配
- **1 个 2011 → 1 个或多个 2013**：同一个礼包可拆成多个价格档位

#### 随机礼包（random_pkg）

随机礼包是一种特殊礼包类型，玩家购买后获得的奖励不是固定内容，而是从关联的 drop 奖池中随机抽取。

**与普通礼包的配置差异：**


| 字段                      | 普通礼包                      | 随机礼包                                                 |
| ----------------------- | ------------------------- | ---------------------------------------------------- |
| 2011.`A_STR_function`   | `event_pkg` / `scene_pkg` | `random_pkg`                                         |
| 2011.`A_STR_pkg_type`   | `normal`                  | `random`                                             |
| 2011.`A_ARR_iap_status` | 仅含 `recharge_actv` 条目     | **额外包含 `{"typ":"drop","id":2124xxxx}`**，指向 2124 表的奖池 |
| 2013.`A_STR_temp_type`  | `normal`                  | `random`                                             |


**完整链路：**

```
2112 → 2135 → 2011（random_pkg）
                 ├─ → 2013（奖励模板，random 类型）
                 └─ A_ARR_iap_status → {"typ":"drop","id":2124xxxx}
                                          ↓
                                       2124（drop 奖池，action=random_pkg）
```

**操作要点：**

- 复制随机礼包时，必须同时复制关联的 drop 奖池并分配新 ID
- 修改随机礼包奖励时，需要同时修改 2013 模板和 2124 奖池
- drop 奖池的 `A_STR_action` 固定为 `random_pkg`，`S_STR_type` 固定为 `bag`

#### discount 链路（2121 中转到礼包）

```
2112.A_ARR_activity_components → {"typ":"discount","id":2121xxxx}
    ↓
2121.A_INT_id = 2121xxxx, A_STR_type = "discount"
2121.A_ARR_status = [{"typ":"iap","id":2011xxxxxx}]   ← 关联 2011 礼包
    ↓
2011.A_INT_id = 2011xxxxxx
    ↓
2013.A_INT_config_id = 2011xxxxxx（1对多）
```

**与 package 的区别**：package 经由 2135 桥接表到 2011，discount 经由 2121 的 `A_ARR_status` 字段直接引用 2011 ID。两者最终都到达 `2011 → 2013` 链路。

**关键规则**：追踪一个活动的所有礼包时，必须检查 `A_ARR_activity_components` 中**所有组件类型**（不只是 package），任何组件的字段中出现 `{"typ":"iap","id":2011xxx}` 或 `{"typ":"package","id":2135xxx}` 都意味着关联了礼包。

**已知会关联礼包的非 package 组件：**

| 组件类型 | 关联路径 | 关键字段 |
|---------|---------|---------|
| `package` | 组件 ID = 2135 ID → `2135.A_INT_iap` → 2011 → 2013 | 直接链路 |
| `discount` | 2121 表 `A_ARR_status` → `[{"typ":"iap","id":2011xxx}]` → 2013 | `A_ARR_status` |
| `monopoly_piggy_bank` | 2121 表 `A_ARR_reward` → `[{"typ":"package","id":2135xxx}]` → 2011 → 2013 | `A_ARR_reward` |
| `cross_progress` | 组件 ID 直接就是 2011 ID → 2013 | 直接链路 |

**完整追踪流程**：遍历活动所有组件 → 对每个组件检查其在对应表中的所有字段 → 发现 2011/2135 引用就追踪到 2013 → 同时用 2011 表 `A_MAP_time_info` 反查绑定该活动 ID 的礼包 → 取并集。

### 3.5 奖励资产类型体系


| 资产 typ | 含义       | ID前4位对应表   | 示例               |
| ------ | -------- | ---------- | ---------------- |
| item   | 道具       | 1111 item  | 11119279（抽奖券）    |
| xp     | 经验/资产    | 1116 xp    | 11161002（VIP点数）  |
| CD     | 光碟（通用货币） | 无独立表，直接填数量 | A_INT_CDs = 1250 |


**1116 xp 表常用资产：**


| ID       | 名称        | constant                   |
| -------- | --------- | -------------------------- |
| 11161001 | 经验-玩家经验   | —                          |
| 11161002 | 经验-VIP点数  | vip_xp                     |
| 11161003 | 香蕉建材-香蕉芯片 | banana_building_upgrade_xp |
| 11161004 | 经验-军功     | military_merit_xp          |


### 3.6 通用奖励 JSON 格式

以下格式在 2013（other_items）、2115（reward）、2124（drop args）等多张表中通用：

```json
{
  "asset": {"typ": "item", "id": 11119279, "val": 20},
  "setting": {"serial_number": 99, "ishighlight": true}
}
```

- `asset.typ`：资产类型（item / xp）
- `asset.id`：资产ID（前4位可定位来源表）
- `asset.val`：数量
- `setting.serial_number`：前端排序序号（数字越大越靠前）
- `setting.ishighlight`：是否高亮展示

### 3.7 通用条件表达式格式

以下 JSON 条件表达式在 2112（filter）、2115（showcond/fincond）、2011（filters/triggers）等多张表中通用：

**单条件：**

```json
{"op": "ge", "typ": "building", "id": 111811, "val": 6}
```


| 字段  | 含义                                        |
| --- | ----------------------------------------- |
| op  | 运算符：ge(≥) / le(≤) / eq(=) / ne(≠) / lt(<) |
| typ | 条件类型                                      |
| id  | 目标实体ID（部分 typ 不需要）                        |
| val | 阈值                                        |


**复合条件（and/or）：**

```json
{"op": "and", "args": [
  {"op": "ge", "typ": "building", "id": 111811, "val": 5},
  {"op": "ge", "typ": "actvtask", "id": 211562067, "val": 1}
]}
```

**已知条件 typ 速查：**


| typ                      | 含义            | 示例                            |
| ------------------------ | ------------- | ----------------------------- |
| building                 | 建筑等级          | `"id":111811,"val":6` = 要塞≥6级 |
| actvstarttime            | 活动已开始         | `"val":0`                     |
| actvtask                 | 活动任务完成        | `"id":任务ID,"val":1`           |
| iap_actvtask             | 礼包关联任务完成      | `"id":任务ID,"val":1`           |
| abtest                   | AB测试分组        | `"id":测试ID,"val":1`           |
| schema                   | 服务器生命周期       | `"id":schema编号`               |
| hero_extra_talent_unlock | 英雄额外天赋解锁      | `"id":天赋ID,"val":1`           |
| function_unlock          | 功能解锁          | `"id":功能ID,"val":1`           |
| iap_purchases            | 已购买礼包         | `"id":礼包ID,"val":1`           |
| client_version           | 客户端版本         | `"arg2":"0.25.0"`             |
| tank_unlock              | 载具解锁          | `"val":1`                     |
| in_ubattle_war           | 在跨服战中         | `"val":1`                     |
| total_pay                | 累计付费          | —                             |
| research                 | 科研等级          | `"id":科研ID,"val":等级`          |
| building_start           | 开始建造（触发用）     | —                             |
| situation_start          | 事件开始（触发用）     | —                             |
| metro_small_level_event  | 地铁小关卡（触发用）    | —                             |
| bi_kvk_heal_speed        | KVK治疗加速（BI触发） | —                             |
| bi_kvk_train_speed       | KVK训练加速（BI触发） | —                             |


---

## 四、各表字段规范与填写指南

### 4.1 2112 活动配置表

每行 = 一个活动。


| 列     | 字段名                           | 类型         | 说明            | 填写规范                 |
| ----- | ----------------------------- | ---------- | ------------- | -------------------- |
| A     | A_INT_id                      | int        | 活动ID（主键）      | 格式 `2112xxxx`，不可重复   |
| B     | S_STR_comment                 | string     | 活动名称/备注       | 含"弃用"的不要修改           |
| C     | A_STR_constant                | string     | 常量标识          | 程序引用的唯一英文标识          |
| E     | S_INT_priority                | int        | 优先级           | 数字越大越优先              |
| G     | A_MAP_filter                  | JSON       | 参与条件          | 通用条件表达式（见3.7节）       |
| H     | A_MAP_text                    | JSON       | 显示文本          | 值为 i18n 键，需配合 1011 表 |
| **I** | **A_ARR_activity_components** | **JSON数组** | **子模块列表（核心）** | 见 3.1 节格式            |
| J     | A_MAP_description             | JSON       | 规则说明          | 含 rule、note 等        |
| K     | A_INT_ui_template             | int        | UI模板ID        | —                    |
| V     | A_INT_dependent               | int        | 前置活动ID        | 0=无前置                |


### 4.2 2124 掉落配置表

每行 = 一个掉落配置。2112 的 drop 组件直接指向此表。


| 列     | 字段名               | 类型       | 说明           | 填写规范                      |
| ----- | ----------------- | -------- | ------------ | ------------------------- |
| A     | A_INT_id          | int      | 掉落ID（主键）     | 格式 `2124xxxx`             |
| B     | N_STR_comment     | string   | 名称/备注        | —                         |
| D     | A_STR_action      | string   | 动作标识         | 如 `strong_consume_free_1` |
| **G** | **A_MAP_drop**    | **JSON** | **掉落内容（核心）** | 见下方详细格式                   |
| H     | A_ARR_action_time | JSON     | 生效区间         | `[起始次数, 结束次数]`            |


**A_MAP_drop 格式（G列）：**

#### 顶层 drop 规则类型


| typ             | 含义      | 说明                                    |
| --------------- | ------- | ------------------------------------- |
| `single_random` | 按权重随机抽取 | 从 args 中按 wgt 权重随机选 `num` 个，最常见（688条） |
| `single_all`    | 全部给予    | args 中所有元素都发放，不做随机（541条）              |


#### args 子元素类型


| typ               | 含义                 | 使用位置                              |
| ----------------- | ------------------ | --------------------------------- |
| `item`            | 普通道具，id 指向 1111 表  | single_random / single_all 的 args |
| `material`        | 材料类资产              | 同上                                |
| `xp`              | 经验值资产，id 指向 1116 表 | 同上                                |
| `empty`           | 空掉落（什么都不给）         | single_random 的 args，用于实现"有概率不掉落" |
| `single_random`   | 嵌套随机池              | single_all 的 args，多个子池各抽一次全部给予    |
| `single_all`      | 嵌套全给               | single_all 的 args                 |
| `noreturn_random` | 不放回随机抽取            | single_all 的 args，从池中抽 num 个不重复   |


#### 典型结构示例

**single_random（随机抽取）：**

```json
{
  "typ": "single_random",
  "num": 1,
  "args": [
    {"typ": "item", "id": 11112127, "num": 2, "wgt": 60, "serial_number": 8, "is_highlight": false},
    {"typ": "item", "id": 11111105, "num": 1, "wgt": 40}
  ]
}
```

**single_all + 嵌套 single_random（多池各抽一次全给）：**

```json
{
  "typ": "single_all",
  "num": 1,
  "args": [
    {"typ": "single_random", "num": 1, "args": [...]},
    {"typ": "single_random", "num": 1, "args": [...]},
    {"typ": "item", "id": 11116004, "num": 2, "wgt": 1}
  ]
}
```

#### 保底规则 drop_rule

`drop_rule` 是挂在 `single_random` 上的可选附加字段，用于保底机制：

```json
{
  "typ": "single_random",
  "num": 1,
  "drop_rule": {
    "typ": "noget",
    "id": 11117396,
    "num": 15,
    "args": [{"typ": "item", "id": 11117396, "num": 1, "wgt": 1}]
  },
  "args": [
    {"typ": "item", "id": 11117396, "num": 1, "wgt": 0},
    {"typ": "item", "id": 111110264, "num": 10, "wgt": 10}
  ]
}
```


| 字段               | 含义                      |
| ---------------- | ----------------------- |
| `drop_rule.typ`  | 保底类型，`noget` = 连续未获得则保底 |
| `drop_rule.id`   | 监控的目标道具 ID              |
| `drop_rule.num`  | 保底触发阈值（连续多少次未抽到则触发）     |
| `drop_rule.args` | 保底触发时给予的奖励              |


配合使用时，目标道具在主 args 中通常 `wgt=0`（不参与正常随机），完全依赖保底发放。

#### args 通用字段


| 字段                   | 含义      | 填写规范                |
| -------------------- | ------- | ------------------- |
| args[].typ           | 奖励类型    | 见上方子元素类型表           |
| args[].id            | 道具/资产ID | 前4位对应 1111 或 1116 表 |
| args[].num           | 奖励数量    | 正整数                 |
| args[].wgt           | 权重      | 概率 = wgt / 奖池总wgt   |
| args[].serial_number | 排序序号    | 正整数（可选）             |
| args[].is_highlight  | 高亮显示    | true / false（可选）    |


**概率计算：** `某道具概率 = 该道具wgt / Σ(所有args的wgt)`

### 4.3 2115 任务配置表

每行 = 一个任务。2112 的 task 组件直接指向此表。


| 列     | 字段名               | 类型         | 说明           | 填写规范                 |
| ----- | ----------------- | ---------- | ------------ | -------------------- |
| A     | A_INT_group       | int        | 任务组号         | 同活动的 task 共享同一 group |
| **B** | **A_INT_id**      | **int**    | **任务ID（主键）** | 与2112组件id匹配          |
| C     | N_STR_comment     | string     | 名称/备注        | —                    |
| D     | A_MAP_showcond    | JSON       | 显示条件         | 通用条件表达式（见3.7节）       |
| **E** | **A_MAP_fincond** | **JSON**   | **完成条件（核心）** | 见下方格式                |
| F     | A_INT_pretrace    | int        | 前置任务ID       | 0=无前置                |
| **G** | **A_ARR_reward**  | **JSON数组** | **任务奖励**     | 通用奖励格式（见3.6节）        |


**A_MAP_fincond 格式：**

```json
{"cat": 10148028, "arg": {"ids": [21222104]}, "val": 5000, "op": "ge"}
```


| 字段      | 含义                         |
| ------- | -------------------------- |
| cat     | 条件类别ID（如 10148028 = 排行积分类） |
| arg.ids | 关联组件ID（通常为同活动的 rank 组件）    |
| val     | 目标数值                       |
| op      | 运算符（ge/le/eq）              |


### 4.4 2135 活动礼包表（桥接表）


| 列     | 字段名           | 类型      | 说明                  | 填写规范               |
| ----- | ------------- | ------- | ------------------- | ------------------ |
| A     | A_INT_id      | int     | 活动礼包ID（主键）          | 格式 `2135xxxx`      |
| B     | N_STR_comment | string  | 名称/备注               | —                  |
| **C** | **A_INT_iap** | **int** | **关联的 2011 ID（核心）** | 填 2011 表的 A_INT_id |


### 4.5 2011 礼包条件配置表

定义礼包的触发条件、优先级、生效时间等规格参数。不含具体奖励（奖励在 2013）。

**完整字段（列索引 0~19）：**


| 列索引        | 字段名                    | 类型       | 说明           | 填写规范                                   |
| ---------- | ---------------------- | -------- | ------------ | -------------------------------------- |
| 0 (A)      | A_INT_id               | int      | 礼包配置ID（主键）   | 格式 `2011xxxxxx`                        |
| 1 (B)      | N_STR_pkg_desc         | string   | 名称/备注        | —                                      |
| 2 (C)      | A_STR_function         | string   | 客户端礼包类型      | 默认 `normal_pkg`                        |
| 3 (D)      | A_STR_pkg_type         | string   | 服务器礼包类型      | 默认 `normal`，需与 2013.A_STR_temp_type 一致 |
| 4 (E)      | A_STR_paywall_tab      | string   | 付费墙页签        | —                                      |
| 5 (F)      | A_BOL_pirce_display    | bool     | 价格显示         | —                                      |
| 6 (G)      | S_MAP_server_info      | JSON     | 服务器生命周期      | 见下方                                    |
| 7 (H)      | A_INT_priority         | int      | 优先级          | 数字越大越优先                                |
| **8 (I)**  | **A_MAP_time_info**    | **JSON** | **生效时间（核心）** | 见下方                                    |
| **9 (J)**  | **S_MAP_filters**      | **JSON** | **生效条件**     | 通用条件表达式（见3.7节），空/`{}` = 无条件            |
| **10 (K)** | **A_MAP_triggers**     | **JSON** | **触发条件**     | 同 filters 格式，空/`{}` = 无触发限制            |
| 11 (L)     | A_ARR_iap_status       | JSON     | 礼包状态         | —                                      |
| 12 (M)     | A_INT_iap_new          | int      | 新礼包标记        | —                                      |
| 13 (N)     | S_MAP_group_limit      | JSON     | 组限制          | —                                      |
| 14 (O)     | A_STR_apply_scene      | string   | 应用场景         | —                                      |
| 15 (P)     | A_INT_close_sell_out   | int      | 售罄关闭         | —                                      |
| 16 (Q)     | A_STR_sub_scene        | string   | 子场景          | —                                      |
| 17 (R)     | A_INT_country_use_type | int      | 国家使用类型       | —                                      |
| 18 (S)     | A_STR_sub_tab          | string   | 子页签          | —                                      |
| 19 (T)     | A_INT_double_coupon    | int      | 双倍券          | —                                      |


**礼包类型规则：**

- `2011.A_STR_pkg_type` 和 `2013.A_STR_temp_type` **必须保持一致**，都由服务器使用
- `2011.A_STR_function` 由客户端使用，控制礼包在前端的调用逻辑
- 未特别说明时，默认值为 `pkg_type = normal`，`function = normal_pkg`

**S_MAP_filters 与 A_MAP_triggers：**

- `filters`：礼包生效的**前置条件**，玩家必须满足才能看到该礼包
- `triggers`：礼包的**触发条件**，当玩家行为满足时触发礼包出现
- 两者格式完全相同，都使用通用条件表达式（见3.7节）
- 空值或 `{}` 表示无限制
- 具体条件由运营指定，常见 typ 见 3.7 节速查表

**S_MAP_server_info（服务器生命周期）：**

控制礼包在哪些 schema 阶段生效。未特别说明时，默认全 schema 覆盖：

```json
{"typ":"schema","id":[1,2,3,4,5,6,13,14,15,16,17,18,55]}
```

**Schema 生命周期对照：**


| Schema ID | 含义        | 服务器天数      |
| --------- | --------- | ---------- |
| 1         | schema1   | 第1~13天     |
| 2         | schema2   | 第14~43天    |
| 3         | schema3   | 第24~86天    |
| 4         | schema4   | 第87~170天   |
| 5         | schema5   | 第171~299天  |
| 6         | schema6   | 第300天以上    |
| 13~18     | KVK1~KVK6 | 王国战争第1~6赛季 |
| 55        | 巅峰领土战     | —          |


**A_MAP_time_info（生效时间）：**

控制礼包何时对玩家可见/可购买。顶层 key 决定时间模式：

**模式一：normal（最常用）**

```json
// 绑定活动ID（活动期间生效）—— 活动礼包最常用
{"normal": [{"actv_id": 21127364}]}

// 绑定活动base_id
{"normal": [{"actv_base_id": 21121559}]}

// 永久生效（start_time=0 + duration≈100年）
{"normal": [{"start_time": 0, "duration": 3153600000}]}

// 绑定活动 + 指定天数后开始 + 持续时长
{"normal": [{"actv_id": 21121141, "day": 4, "duration": 259200}]}
```


| 子字段          | 含义                      |
| ------------ | ----------------------- |
| actv_id      | 绑定的活动ID（2112表），活动期间礼包生效 |
| actv_base_id | 绑定的基础活动ID               |
| start_time   | 起始时间偏移（0=立即）            |
| duration     | 持续时长（秒）                 |
| day          | 从活动第N天开始                |


**模式二：scene（触发场景型）**

```json
{"scene": {"duration": 43200, "refresh_time": 43200}}
{"scene": {"duration": 3600, "refresh_time": 3600, "buy_refresh": 1}}
```

**模式三：cycle（周期型）**

```json
{"cycle": [{"range": "day", "hour": 0, "duration": 86400}]}
```

**模式四：time（绝对时间型）**

```json
{"time": [{"start_time": "2025-10-30 00:00:00", "duration": 345600}]}
```

**模式五：time_card（周卡/月卡型）**

```json
{"time_card": {"duration": 604800}}
```

**常用 duration 速查：**


| 秒数         | 时长        |
| ---------- | --------- |
| 3600       | 1小时       |
| 43200      | 12小时      |
| 86400      | 1天        |
| 172800     | 2天        |
| 259200     | 3天        |
| 604800     | 7天        |
| 2592000    | 30天       |
| 3153600000 | ≈100年（永久） |


> **活动礼包默认用法**：如果礼包跟随某活动生效，填 `{"normal":[{"actv_id":活动ID}]}`。

### 4.6 2013 礼包内容/价格表

定义每个价格档位的具体售价和奖励内容。通过 `A_INT_config_id` 自动绑定到 2011。


| 列          | 字段名                   | 类型         | 说明                   | 填写规范                                  |
| ---------- | --------------------- | ---------- | -------------------- | ------------------------------------- |
| A (0)      | A_INT_id              | int        | 2013 唯一ID            | 格式 `2013xxxxxx`                       |
| B (1)      | A_STR_temp_type       | string     | 服务器礼包类型              | 默认 `normal`，需与 2011.A_STR_pkg_type 一致 |
| **C (2)**  | **A_INT_config_id**   | **int**    | **关联 2011.A_INT_id** | 自动绑定，不可随意改                            |
| E (4)      | N_STR_comment         | string     | 名称/备注                | —                                     |
| F (5)      | A_STR_pkg_title       | string     | 礼包名称                 | 本地化键，如 `LC_IAP_xxx`                   |
| G (6)      | A_STR_pkg_desc        | string     | 礼包描述                 | 本地化键                                  |
| **H (7)**  | **A_FLT_price**       | **float**  | **售价（USD）**          | 如 4.99、9.99                           |
| I (8)      | A_ARR_price_info      | JSON       | 各渠道 product_id 映射    | 由价格决定，见 4.6.2                         |
| **L (11)** | **A_INT_CDs**         | **int**    | **光碟（CD）数量**         | 直接填数字，查映射表                            |
| N (13)     | A_ARR_CD_items        | JSON       | CD相关道具               | 通常为空 `[]`                             |
| O (14)     | A_ARR_speedup_items   | JSON       | 加速道具                 | 空则忽略                                  |
| P (15)     | A_ARR_resource_items  | JSON       | 资源道具                 | 空则忽略                                  |
| Q (16)     | A_ARR_pvp_items       | JSON       | PVP道具                | 空则忽略                                  |
| **R (17)** | **A_ARR_other_items** | **JSON数组** | **综合奖励（主要奖励字段）**     | 通用奖励格式（见3.6节）                         |
| S (18)     | A_ARR_card_items      | JSON       | 卡牌道具                 | 空则忽略                                  |


**奖励字段规则：** `speedup_items`、`resource_items`、`pvp_items`、`other_items` 四个字段都是礼包内奖励，值为空（`[]`）就忽略。实际奖励通常集中在 `A_ARR_other_items` 中。

**A_INT_CDs（光碟/CD）说明：**

- CD = 光碟，游戏的**通用货币**（相当于金币/钻石）
- 直接填数量，非 JSON 格式
- 完整礼包奖励 = CD + speedup + resource + pvp + other + card 中所有非空项

#### 4.6.1 价格档位标准映射表

每个价格档位对应固定的 CD、VIP经验、联盟礼物级别。新建礼包时直接查表填写。


| 价格(USD) | CD（光碟） | VIP经验  | 联盟礼物  | 联盟礼物ID   |
| ------- | ------ | ------ | ----- | -------- |
| $0.99   | 250    | 250    | 联盟礼物1 | 11114303 |
| $1.99   | 500    | 500    | 联盟礼物1 | 11114303 |
| $2.99   | 750    | 750    | 联盟礼物2 | 11114316 |
| $3.99   | 1,000  | 1,000  | 联盟礼物1 | 11114303 |
| $4.99   | 1,250  | 1,250  | 联盟礼物2 | 11114316 |
| $6.99   | 1,750  | 1,750  | 联盟礼物1 | 11114303 |
| $9.99   | 2,500  | 2,500  | 联盟礼物3 | 11114317 |
| $11.99  | 3,000  | 3,000  | 联盟礼物3 | 11114317 |
| $14.99  | 3,750  | 3,750  | 联盟礼物3 | 11114317 |
| $19.99  | 5,000  | 5,000  | 联盟礼物4 | 11114318 |
| $24.99  | 6,250  | 6,250  | 联盟礼物4 | 11114318 |
| $29.99  | 7,500  | 7,500  | 联盟礼物5 | 11114319 |
| $49.99  | 12,500 | 12,500 | 联盟礼物5 | 11114319 |
| $99.99  | 25,000 | 25,000 | 联盟礼物6 | 11114320 |


**规律：**

- **CD = VIP经验**：始终 1:1
- **$1 ≈ 250 CD**：基准换算，受苹果商店价格影响不绝对精确
- **联盟礼物分6级**：低价(≤$6.99)给1-2级，中价($9.99~$14.99)给3级，高价($19.99+)给4-6级

**联盟礼物道具速查：**


| ID       | 名称          | 对应价格区间           |
| -------- | ----------- | ---------------- |
| 11114303 | 联盟礼物(触发)礼包1 | $0.99~$6.99（低价档） |
| 11114316 | 联盟礼物(触发)礼包2 | $2.99~$4.99      |
| 11114317 | 联盟礼物(触发)礼包3 | $9.99~$14.99     |
| 11114318 | 联盟礼物(触发)礼包4 | $19.99~$24.99    |
| 11114319 | 联盟礼物(触发)礼包5 | $29.99~$49.99    |
| 11114320 | 联盟礼物(触发)礼包6 | $99.99           |


#### 4.6.2 A_ARR_price_info 生成规则

price_info 完全由价格决定。将价格转为去小数点的4位编码，套入模板：

```json
[
  {"pay_type":"gplay",             "product_id":"ape_{CODE}_cd_an"},
  {"pay_type":"ios",               "product_id":"ape_{CODE}_cd_ios"},
  {"pay_type":"alipayv2",          "product_id":"ape_{CODE}_cd_ali"},
  {"pay_type":"weixin",            "product_id":"ape_{CODE}_cd_weixin"},
  {"pay_type":"huaweihms",         "product_id":"ape_{CODE}_cd_huawei"},
  {"pay_type":"weixinh5",          "product_id":"ape_{CODE}_cd_weixinh5"},
  {"pay_type":"xiaomi",            "product_id":"ape_{CODE}_cd_xiaomi"},
  {"pay_type":"oppo",              "product_id":"ape_{CODE}_cd_oppo"},
  {"pay_type":"ninegame",          "product_id":"ape_{CODE}_cd_ninegame"},
  {"pay_type":"main",              "product_id":"ape_{CODE}_cd_cn_group_main"},
  {"pay_type":"flexion",           "product_id":"ape_{CODE}_cd_an"},
  {"pay_type":"aggregate",         "product_id":"ape_{CODE}_cd_aggregate"},
  {"pay_type":"huaweihms_oversea", "product_id":"ape_{CODE}_cd_huaweihms_oversea"},
  {"pay_type":"catappult",         "product_id":"ape_{CODE}_cd_an"}
]
```

**价格编码对照：**


| 价格    | {CODE} | 价格     | {CODE} |
| ----- | ------ | ------ | ------ |
| $0.99 | 0099   | $11.99 | 1199   |
| $1.99 | 0199   | $14.99 | 1499   |
| $2.99 | 0299   | $19.99 | 1999   |
| $3.99 | 0399   | $24.99 | 2499   |
| $4.99 | 0499   | $29.99 | 2999   |
| $6.99 | 0699   | $49.99 | 4999   |
| $9.99 | 0999   | $99.99 | 9999   |


### 4.7 1111 道具表 / 1116 经验值表

资产数据源，按 ID 查询名称，一般不直接修改。

- **1111 道具表**：如 `11119279` = 复活节强消耗抽奖券
- **1116 经验值表**：如 `11161002` = VIP点数

**1111 关键字段补充：**


| 字段                     | 类型     | 说明                                                            |
| ---------------------- | ------ | ------------------------------------------------------------- |
| `A_STR_class`          | string | 道具大类（如 `item_general`, `item_subscription`, `avatar_frame` 等） |
| `C_ARR_display_labels` | JSON   | **背包分类标签**（控制道具在背包哪些 tab 下显示），如 `["all","speedup"]`           |
| `A_ARR_use_labels`     | JSON   | **背包使用标签**（控制道具使用按钮/行为），如 `["use_direct"]`                    |
| `S_INT_use_now`        | int    | **获得即用**：1 = 获得后立即自动使用，不进入背包                                  |
| `C_INT_display_key`    | int    | 道具图标，指向 1511 display_key 表                                    |
| `A_MAP_lc_name`        | JSON   | 道具名称本地化 key                                                   |
| `A_MAP_category_param` | JSON   | 道具分类参数，`item_subscription` 类含 `effect` 字段指向 2013              |


**背包控制规则：**

- `C_ARR_display_labels` 和 `A_ARR_use_labels` 共同决定道具在背包中的显示和交互方式
- 若道具**不应出现在背包**中（如纯数值类资产），需确保两个字段都为空 `[]`
- `S_INT_use_now = 1` 的道具获得后立即消耗，玩家不会在背包中看到

### 4.8 1011 本地化表（i18n）

多语言文本字典。**无主页签**，不同页签 = 不同类别的本地化内容。

- **文档ID**：`11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY`

**配置相关页签：**


| 页签    | 内容类别                                                                                                                                                                                                            | 常见用途      |
| ----- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| IAP   | 礼包相关                                                                                                                                                                                                            | 礼包名称、描述   |
| EVENT | 活动相关                                                                                                                                                                                                            | 活动名称、规则文本 |
| ITEM  | 道具相关                                                                                                                                                                                                            | 道具名称、描述   |
| MAIL  | 邮件相关                                                                                                                                                                                                            | 邮件标题、正文   |
| 其他    | HERO/BUILDING/QUEST/MENU/BUFF/SOLDIER/UNION/ARENA/ART/ASSET/CHINA/ERRCODE/FTE/HORDE/KVK/LEADERBOARD/MAP/NEWS/NPC/PLAYER/PUSH/RESEARCH/RSS/SATELLITE/SITUATION/SOCIAL/STORY/TIP/TRIGGER/METRO/minigame/checkncwj | 各自领域      |


**跳过的页签**：AI翻译暂存、回车检查、本地化使用说明、AI翻译页签、Operation Mail

**表结构**：A列=ID_int（数字ID），B列=ID（文本key），C~T列=20种语言（cn/en/fr/de/po/zh/id/th/sp/ru/tr/vi/it/pl/ar/jp/kr/cns）

**LC Key 命名规则：**

```
LC_{页签名}_{B列ID}
```

示例：IAP 页签中 B 列 `platform_pkg` → 引用写 `LC_IAP_platform_pkg`

**页签推断规则**：拿到一个 LC key 后，可通过前缀反推来源页签：


| LC Key 前缀      | 来源页签     | 内容类别 |
| -------------- | -------- | ---- |
| `LC_IAP_`      | IAP      | 礼包相关 |
| `LC_EVENT_`    | EVENT    | 活动相关 |
| `LC_ITEM_`     | ITEM     | 道具相关 |
| `LC_MAIL_`     | MAIL     | 邮件相关 |
| `LC_HERO_`     | HERO     | 英雄相关 |
| `LC_BUILDING_` | BUILDING | 建筑相关 |
| `LC_BUFF_`     | BUFF     | 增益相关 |


操作时先从 key 前缀定位页签，再到对应页签的 B 列搜索 key 名称。

**使用场景：**

- 2013 的 `A_STR_pkg_title`：礼包名称用 `LC_IAP_xxx` 或 `LC_ITEM_xxx`
- 2112 的 `A_MAP_text`：活动标题用 `LC_EVENT_xxx`
- 2115 的奖励描述、2121 的 `A_STR_desc`：常用 `LC_EVENT_xxx`

### 4.9 1173 聊天铭牌配置表（chat_skin）

定义聊天铭牌/气泡的样式、颜色、关联道具。每行 = 一个铭牌。

- **文档ID**：`1mKaHyDbToHVIV9iyOQPFbJ88pwnjGy5-GeiUvRZHPBg`
- **主页签**：`chat_skin`

| 字段 | 类型 | 说明 |
|------|------|------|
| `A_INT_id` | int | 唯一 ID（`1173xxxx`） |
| `C_STR_comment` | string | 备注（如"26拓荒节铭牌"） |
| `A_STR_constant` | string | 常量标识（近期铭牌通常为空） |
| `C_INT_display_key_chat` | int | **聊天框主体资源**，指向 1511 表（铭牌在聊天中的气泡背景） |
| `C_INT_display_key_show` | int | **道具图标资源**，指向 1511 表（铭牌在背包中的图标） |
| `C_INT_display_order` | int | 显示排序，数字越大越靠前（新增时 -1 递减） |
| `A_MAP_lc_name` | JSON | 铭牌名称，`{"typ":"lc","txt":"LC_ITEM_xxx"}` 指向 1011 表 |
| `C_MAP_lc_desc` | JSON | 铭牌描述，格式同上 |
| `A_ARR_status_active` | JSON | 激活条件，通常为 `[]` |
| `A_ARR_items` | JSON | **关联的 1111 道具 ID 列表**，如 `[111111037]` |
| `C_STR_color_quote_name` | string | 引用框-名字颜色（HEX，如 `#E8701A`） |
| `C_STR_color_quote_txt` | string | 引用框-文字颜色 |
| `C_STR_color_split_line` | string | 分割线颜色 |
| `C_STR_color_dialogue_name` | string | 对话框-名字颜色 |
| `C_STR_color_dialogue_txt` | string | 对话框-文字颜色 |
| `C_STR_user_labels` | string | 用户标签，通常填 1173 ID 本身 |
| `A_BOL_preview` | bool | 是否可预览，通常 `True` |

**新增铭牌完整流程（4 张表联动）：**

```
Step 1: 1511 display_key — 新增 2 条
  ├─ 道具图标（仅道具图标）→ 给 1173.C_INT_display_key_show + 1111.C_INT_display_key
  └─ 聊天框主体（聊天框，铭牌资源）→ 给 1173.C_INT_display_key_chat
  备注命名格式参考："26拓荒节铭牌道具图标（仅道具图标）"、"26拓荒节铭牌聊天框-主体（聊天框，铭牌资源）"
  所有资源字段填 "0"，C_MAP_text_image 填 "{}"（美术后续按 ID 提交资源）

Step 2: 1111 item — 新增 1 条铭牌道具
  ├─ A_STR_class = "chat_skin"
  ├─ A_INT_quest_class = 30
  ├─ C_INT_display_key = Step1 的道具图标 ID
  ├─ C_INT_display_quality = 沿用近期铭牌的品质 ID（如 15112564）
  ├─ A_MAP_lc_name / C_MAP_lc_desc = 指向 1011 的 LC key
  ├─ C_MAP_lc_usetip = {"typ":"lc","txt":"LC_ITEM_season_extra_reward_usedtip"}（通用）
  ├─ A_FLT_value = 2500
  └─ A_INT_max_own=9999999, A_INT_max_get=1, A_INT_max_use=1

Step 3: 1173 chat_skin — 新增 1 条
  ├─ C_INT_display_key_chat = Step1 的聊天框主体 ID
  ├─ C_INT_display_key_show = Step1 的道具图标 ID
  ├─ A_ARR_items = [Step2 的 1111 道具 ID]
  ├─ C_INT_display_order = 上一条 -1
  ├─ 5 个颜色字段根据铭牌美术风格配色
  └─ C_STR_user_labels = 本条 1173 ID

Step 4: 1011 i18n（ITEM 页签）— 新增 2 条
  ├─ name key：铭牌名称（中/英）
  └─ desc key：铭牌描述（中/英），描述风格参考同类铭牌
```

**颜色配色要点：**
- `quote_name` 和 `dialogue_name`：通常用铭牌主色（较亮），确保名字醒目
- `quote_txt` 和 `dialogue_txt`：通常用深色/暗色，确保文字在铭牌背景上清晰可读
- `split_line`：取铭牌边框或装饰元素的颜色
- 5 个颜色需要和铭牌美术风格统一，同时保证在浅色/深色背景下都有足够对比度

**LC Key 命名规则：**
- name：`LC_ITEM_{节日缩写}{年份}_nameplate_name`，如 `LC_ITEM_labor26_nameplate_name`
- desc：`LC_ITEM_{节日缩写}{年份}_nameplate_desc`

### 4.10 2116 道具兑换模块配置表

定义活动内的「以物换物」兑换商店。每行 = 一条兑换规则。

- **文档ID**：`14IDttHNuHx1U2I1kHinkMLIA6Q4cKmZ8MLoMkgdTGfY`
- **主页签**：`activity_item_exchange`
- 2112 的 `item_exchange` 组件 ID 对应本表的 `**A_INT_group`**（非 A_INT_id），同 group 的多条规则构成一个兑换商店。


| 字段                       | 类型     | 说明                                                         |
| ------------------------ | ------ | ---------------------------------------------------------- |
| `A_INT_group`            | int    | 分组编号，同组 = 同一个兑换商店                                          |
| `A_INT_id`               | int    | 唯一行 ID                                                     |
| `N_STR_comment`          | string | 注释                                                         |
| `A_ARR_item_give`        | JSON   | 消耗道具（代价），`[{asset:{typ,id,val}, setting:{serial_number}}]` |
| `A_ARR_item_get`         | JSON   | 获得道具（奖励），格式同上                                              |
| `A_INT_display_order`    | int    | 显示排序，数值越大越靠前                                               |
| `A_INT_limit_num`        | int    | 兑换次数上限                                                     |
| `A_INT_if_remind`        | int    | 是否提醒（1=是，0=否）                                              |
| `A_INT_display`          | int    | 显示控制                                                       |
| `A_MAP_requirement`      | JSON   | 兑换前置条件，通用条件表达式格式                                           |
| `S_MAP_show_requirement` | JSON   | 显示前置条件                                                     |
| `S_ARR_bargain_count`    | JSON   | 砍价幅度范围                                                     |
| `S_MAP_bargain_limit`    | JSON   | 砍价价格上下限                                                    |
| `C_INT_discount`         | int    | 折扣                                                         |
| `A_STR_pkg_title`        | string | 本地化 key                                                    |


### 4.11 2130 BP 通行证总配置表

定义 Battle Pass 活动的总体参数。每行 = 一个 BP 活动。

- **文档ID**：`1qe9RsX7P5bl_O2iLwh_eCJ62KtUkn_RaJiJ4uTRQS8M`
- **主页签**：`activity_battle_pass`
- 2112 的 `battle_pass` 组件直接指向 `A_INT_id`。


| 字段                          | 类型     | 说明                                                                                |
| --------------------------- | ------ | --------------------------------------------------------------------------------- |
| `A_INT_id`                  | int    | BP ID（主键），格式 `2130xxxx`                                                           |
| `N_STR_comment`             | string | 注释                                                                                |
| `A_INT_exp`                 | int    | 每级所需经验                                                                            |
| `A_INT_start_level`         | int    | 起始等级，通常 0                                                                         |
| `A_ARR_daily_taskids`       | JSON   | 每日任务 ID 列表，指向 2115 表                                                              |
| `A_ARR_achivement_taskids`  | JSON   | 成就任务 ID 列表，指向 2115 表                                                              |
| `A_ARR_weekly_taskids`      | JSON   | 每周任务 ID 列表，指向 2115 表                                                              |
| `A_ARR_limit_taskids`       | JSON   | 限时任务 ID 列表，指向 2115 表                                                              |
| `A_MAP_pkg`                 | JSON   | 购买 BP 的 IAP 配置，`args` 通过 `typ:iap` 引用 IAP ID                                      |
| `A_ARR_max_levelup_rewards` | JSON   | 满级后继续升级的奖励                                                                        |
| `S_ARR_quality_up_item`     | JSON   | 品质提升道具                                                                            |
| `A_ARR_level_up_item`       | JSON   | 手动升级 BP 等级的道具                                                                     |
| `S_ARR_crit`                | JSON   | 暴击倍率，如 `[{num:1,weight:70},{num:2,weight:25},{num:3,weight:10},{num:5,weight:5}]` |
| `A_INT_max_levelup_can_use` | int    | 升级道具单次最大使用量                                                                       |
| `A_ARR_reward_buff`         | JSON   | 奖励加成 buff                                                                         |
| `A_INT_type`                | int    | BP 类型，1=常规，2=特殊                                                                   |


### 4.12 2131 BP 通行证等级奖励表

定义每个 BP 每一级的三轨道奖励。通过 `A_INT_bp_id` 绑定 2130 表。

- **文档ID**：`1sbMG-3NHEGUgmpW5-kEzwnCkWoi94aeNSk50Zsu_Dcs`
- **主页签**：`activity_battle_pass_level`
- 一个 BP 通常 30~40 级，一级一行。


| 字段                    | 类型     | 说明                              |
| --------------------- | ------ | ------------------------------- |
| `A_INT_id`            | int    | 唯一行 ID                          |
| `A_INT_bp_id`         | int    | 关联 BP ID，**指向 2130 表 A_INT_id** |
| `N_STR_comment`       | string | 注释                              |
| `A_INT_level`         | int    | 等级编号，从 1 递增                     |
| `A_ARR_free_rewards`  | JSON   | 免费轨道奖励                          |
| `A_ARR_pay_rewards`   | JSON   | 付费轨道奖励（基础通行证）                   |
| `A_ARR_pay_rewards_2` | JSON   | 高级付费轨道奖励（豪华通行证），空数组表示无          |
| `A_INT_exp`           | int    | 本级所需经验，可逐级不同                    |
| `A_INT_show_type`     | int    | 显示类型（-1/0/1）                    |


**关联链路：**

```
2112 → battle_pass 组件(2130xxxx) → 2130.A_INT_id
                                      ↓
                              2131.A_INT_bp_id = 2130xxxx（每级奖励）
```

### 4.13 2121 活动特殊组件表

万能适配表，没有专属配置表的自定义组件都放在这里。通过 `A_STR_type` 区分组件类型。

- **文档ID**：`1sicvhfxZhagLVmpEg4HDcaCnPWPgsWkhgZKC-HxCCuc`
- **主页签**：`activity_special_QA`
- **数据量**：3291 条，297 种 type
- 2112 组件列表中 `{"typ":"new_progress","id":21215565}` → 本表 `A_INT_id=21215565, A_STR_type=new_progress`


| 字段                     | 类型     | 说明                      |
| ---------------------- | ------ | ----------------------- |
| `A_INT_id`             | int    | 唯一 ID                   |
| `C_STR_comment`        | string | 注释                      |
| `A_STR_type`           | string | **组件类型（核心字段）**，决定其他字段含义 |
| `A_ARR_reward`         | JSON   | 奖励（部分 type 使用）          |
| `A_MAP_expr`           | JSON   | 表达式/参数（含义随 type 变化）     |
| `A_INT_arg1/arg2/arg3` | int    | 通用参数（含义随 type 变化）       |
| `A_ARR_reward_expr`    | JSON   | 附加奖励                    |
| `A_STR_desc`           | string | 描述，常为本地化 key            |
| `A_ARR_array`          | JSON   | 通用数组                    |
| `A_ARR_status`         | JSON   | 状态/关联配置                 |
| `S_MAP_condition`      | JSON   | 前置条件，通用条件表达式格式          |
| `S_ARR_score_rule`     | JSON   | 积分规则                    |


**高频 type**：`progress`(464) / `new_progress`(430) / `7days_happy`(230) / `jump_link`(136) / `actv_show_rank`(115) / `buff`(85) / `discount`(83) / `cost`(46)

**特点**：同一字段在不同 type 下含义不同，修改时需参考同 type 历史配置。

#### 4.12.1 new_progress 组件（集结奖励）

全服/跨服集结类阶段奖励组件。常用于 BP 活动中的「集结礼包」（BP 中套 BP），也用于其他集结类活动。

**字段含义：**


| 字段                  | 含义                      | 说明                                                                 |
| ------------------- | ----------------------- | ------------------------------------------------------------------ |
| `A_INT_arg1`        | **人数阈值**                | 达到该人数即解锁本阶段奖励                                                      |
| `A_INT_arg2`        | **追踪的 IAP 包 ID**（2011表） | 统计购买该商品的玩家数量；`0` = 不追踪特定IAP（通用集结）                                  |
| `A_INT_arg3`        | **进度追踪维度**              | 见下表                                                                |
| `A_ARR_reward`      | **免费奖励**                | 阈值达成后所有玩家可领取                                                       |
| `A_ARR_reward_expr` | **付费奖励**                | 需满足 `S_MAP_condition` 才可领取；通用集结时通常为空 `[]`                          |
| `S_MAP_condition`   | **付费奖励领取条件**            | 通用条件表达式，常见 `{"op":"ge","typ":"iap_purchases","id":2013ID,"val":1}` |
| `A_MAP_expr`        | 显示配置                    | 通用集结时可能含 `{"op":"displaykey","id":displaykey_id}`                  |


**arg3 进度维度（来自单元格备注）：**


| arg3 值 | 含义    | 场景                |
| ------ | ----- | ----------------- |
| `1`    | 个人奖励  | 个人维度进度追踪（默认）      |
| `2`    | 联盟奖励  | 联盟维度进度追踪          |
| `4`    | 服务器进度 | 单服维度追踪            |
| `5`    | 跨服进度  | 跨服维度计算人数（BP 集结礼包） |


**BP 集结礼包的典型用法：**

10个 `new_progress` 组件构成10个阶段，配合 `cross_progress` 组件使用：

- `arg1` = 梯度阈值（如 1→10→50→100→200→300→400→600→800→1000），**每次可调整**
- `arg2` = 初级通行证的 2011 ID（追踪全服购买人数）
- `arg3` = `5`（跨服计算）
- `A_ARR_reward` = 免费奖励（所有人达阈值可领）
- `A_ARR_reward_expr` = 付费奖励
- `S_MAP_condition` = 需购买「集结奖励解锁礼包」（2013 模板 ID）
- 阶段数量和阈值梯度不固定，每次可根据需求调整

### 4.14 1168 获取途径组合表（跳转表）

定义道具/资源的获取途径，玩家点击"如何获取"时展示的跳转入口来自此表。

- **文档ID**：`1KwX1xWoHHcmOGTaasZmMii2Al-YR_VXV3yoSGn3tBbA`
- **主页签**：`get_access_group（杜绝手搓）`
- **同文档内含 1153 表**（`1153表` 页签）= 跳转类型定义


| 字段                   | 类型     | 说明                                  |
| -------------------- | ------ | ----------------------------------- |
| `A_INT_id`           | int    | 唯一 ID（`1168xxxx`）                   |
| `S_STR_comment`      | string | 注释                                  |
| `C_STR_item_label`   | string | 道具分类标签，`non_item` = 活动道具            |
| `C_ARR_access_group` | JSON   | **核心字段**：获取途径列表，每个元素引用 1153 表的跳转 ID |
| `C_MAP_lc_name`      | JSON   | 名称本地化                               |
| `C_MAP_label_name`   | JSON   | 标签名称本地化                             |


**常用 1153 跳转 ID**：


| ID         | 含义                   |
| ---------- | -------------------- |
| `11531001` | 活动跳转（通用），args 带活动 ID |
| `11531017` | 付费墙跳转（通用）            |
| `11531196` | 节日 BP 跳转到礼包界面        |
| `11531005` | Gacha 抽卡跳转           |


**关联链路**：

```
2112 组件 → {"typ":"jump_link","id":2121xxxx}
    ↓
2121.A_MAP_expr.id = 1168xxxx
    ↓
1168.C_ARR_access_group = [{id:1153xxxx, args:[...]}]
    ↓
1153 = 具体跳转定义
```

### 4.15 2122 排行榜规则表 + 2118 排名奖励表

#### 2122 排行榜规则表（activity_rank_rule）

定义活动排行榜的积分规则、排名范围、奖励关联。

- **文档ID**：`1zziy6nMR1DlhCykKBndwk6d6KNRrzj1PsOsFGbLYR4M`
- **主页签**：`activity_rank_rule（QA）`
- 同 `A_INT_group` 下包含 1 个**主排名行** + 多个**积分子规则行**


| 字段                        | 类型     | 说明（来自单元格备注）                                                                                |
| ------------------------- | ------ | ------------------------------------------------------------------------------------------ |
| `A_INT_group`             | int    | 分组号，同活动共享，与 2112 组件中的 rank ID 配合使用                                                         |
| `A_INT_id`                | int    | 唯一 ID（`2122xxxx`）                                                                          |
| `N_STR_comment`           | string | 注释                                                                                         |
| `A_ARR_score_rule`        | JSON   | 积分规则，`cat` 引用 1014 表，`val`/`score` 定义换算比。主排名行可引用子规则 ID                                     |
| `A_MAP_start_time`        | JSON   | 时间模式：`overall`=全程 / `section`(arg,dur)=分段 / `cycle`(arg1,dur)=周期 / `day_cycle`(arg,dur)=按天 |
| `A_INT_rank_unit`         | int    | 排名单位：1=个人 / 2=联盟 / 3=部落 / 4=服务器 / 5=服务器组                                                   |
| `A_INT_rank_scope`        | int    | 排名范围：同上，**必须 > rank_unit**。跑马灯需填 5                                                         |
| `A_INT_rank_components`   | int    | **关联 2118 表的 group 字段**（排名奖励）                                                              |
| `A_STR_section_lc`        | string | 奖励邮件中的阶段描述 LC key                                                                          |
| `A_STR_rank_title`        | string | 排行榜标题 LC key                                                                               |
| `A_INT_icon_display_key`  | int    | 排行榜图标                                                                                      |
| `A_INT_min_score`         | int    | 参与排名的最低分数要求                                                                                |
| `A_ARR_rule_desc`         | JSON   | 积分规则描述 LC key 列表                                                                           |
| `A_INT_retain_rank`       | int    | 1=永久保留排名 / 0=不保留                                                                           |
| `A_MAP_score_req`         | JSON   | 获得积分的前置条件                                                                                  |
| `A_INT_score_change_tips` | int    | 积分变化跑马灯模板 ID（跨服个人排行需 rank_unit=1, rank_scope=5）                                            |


**分组结构示例（group=243，强消耗活动 schema6）：**

- 21222098~21222103：6 个积分子规则（斗士/收藏品/军备/机甲/战装/加速）
- 21222104：主排名行，`score_rule` 引用上方 6 个 ID 汇总积分，`rank_components=272` 指向 2118

#### 2118 排名奖励表（activity_rank_rewards）

定义各名次段的奖励。通过 `A_INT_group` 与 2122 的 `A_INT_rank_components` 绑定。

- **文档ID**：`1Nb23s9iVOiDzWGQlpHSRW5O0gIqd1ZiYNx9kYrDps2M`
- **主页签**：`activity_rank_rewards`
- 每组通常 12 行，覆盖名次 1-1, 2-2, 3-3, 4-4, 5-5, 6-6, 7-7, 8-10, 11-15, 16-25, 26-50, 51-100


| 字段                 | 类型     | 说明                                    |
| ------------------ | ------ | ------------------------------------- |
| `A_INT_group`      | int    | 分组号，对应 2122 的 `A_INT_rank_components` |
| `N_STR_comment`    | string | 注释                                    |
| `A_INT_id`         | int    | 唯一 ID（`2118xxxx`）                     |
| `A_INT_rank_start` | int    | 名次范围起始                                |
| `A_INT_rank_end`   | int    | 名次范围结束                                |
| `A_ARR_reward`     | JSON   | 该名次段的奖励，通用奖励格式                        |


#### actv_show_rank 组件（2121 表）

在活动界面展示排行榜 UI 入口。


| 字段           | 含义               |
| ------------ | ---------------- |
| `A_STR_type` | `actv_show_rank` |
| `A_INT_arg1` | 指向 2122 的主排名行 ID |


#### 关联链路

```
2112 组件 → {"typ":"rank","id":21222104}
               ↓
          2122.A_INT_id = 21222104（主排名行）
          2122.A_INT_rank_components = 272
               ↓
          2118.A_INT_group = 272（12 行排名奖励）

2112 组件 → {"typ":"actv_show_rank","id":21215080}
               ↓
          2121.A_INT_arg1 = 21222104（指向同一个排名 ID）
```

#### 跑马灯图标规则

节日活动排行榜的跑马灯图标来自 2112 表的 `A_INT_icon_displaykey` 字段，该字段引用 **2168 表**（`p2_activity_hud_entries`）中的图标 key。

### 4.16 2137 活动道具回收表（activity_asset_retake）

活动结束后，系统自动回收玩家持有的活动专属道具，按换算比返还通用道具。

- **文档ID**：`1ctEGsAU053iaCCTJeIU1qnp9zfyuURt7k8EzHkKzv2Y`
- **主页签**：`activity_asset_retake`


| 字段                 | 类型     | 说明                                                |
| ------------------ | ------ | ------------------------------------------------- |
| `A_INT_id`         | int    | 唯一 ID（`2137xxxx`），**一个 ID 不能对应多个活动**              |
| `C_STR_comment`    | string | 注释                                                |
| `A_MAP_give_asset` | JSON   | 返还的资产（玩家收到的），格式 `{"typ":"item","id":xxx,"val":n}` |
| `A_MAP_cost_asset` | JSON   | 回收的资产（从玩家扣除的），格式同上                                |


**换算规则**：每 `cost_asset.val` 个活动道具 → 返还 `give_asset.val` 个通用道具。不能整除时**向上取整**。

**示例**（21127364 强消耗活动）：

- 21371226：回收扭蛋币(11119278) → 返还通用道具(11111001)，1:1
- 21371227：回收抽奖券(11119279) → 返还通用道具(11111104)，1:1

**注意**：活动结束后会记录结束状态，即使活动再次开启，之前的活动道具依然会被回收。

### 4.17 1013 常量配置表（const_config）

存储游戏中各种杂项常量参数。程序通过 `A_STR_constant` 字段名映射读取。

- **文档ID**：`1WKAxQDf0-7UZADWxef1wDQaN0chqPJNa3zEB81W9fho`
- **主页签**：`const_config`
- 其他页签均为版本分支或临时副本


| 字段                       | 类型     | 说明                                            |
| ------------------------ | ------ | --------------------------------------------- |
| `A_INT_id`               | int    | 唯一 ID（`1013xxxx`）                             |
| `S_STR_comment`          | string | 注释                                            |
| `A_STR_constant`         | string | **常量名（程序映射用）**，与 ID 一一对应，唯一，不能以数字开头           |
| `A_FLT_val`              | float  | 数值参数（不能超过 2^24 = 16777216，否则溢出）               |
| `A_ARR_array`            | JSON   | int 数组参数（含义由具体常量定义）                           |
| `A_ARR_quintuple`        | JSON   | 对象数组参数（含义由具体常量定义）                             |
| `A_MAP_requirement`      | JSON   | 条件 map                                        |
| `A_INT_use_type`         | int    | KVK 分支：0=公用 / 1=原服 / 2=KVK1 / 3=KVK2 / 4=KVK3 |
| `A_INT_country_use_type` | int    | 地区：0=公用 / 1=海外 / 2=国服                         |


**use_type 规则**：只出现1次的常量必须配 `0`（公用）。配 1/2/3/4 用于区分原服和各 KVK 赛季下的不同参数值。

**与活动配置的关联**：部分常量通过 `A_STR_constant` 与其他表的 action/constant 字段匹配绑定。例如 BP 循环宝箱中，1013 的 `fes_actv_bp_extra` 与 2124 drop 的 `A_STR_action` 同名绑定。

### 4.18 2024 自选礼包配置表（iap_custom_chest）

- **文档 ID**：`1jQSZKXz25Xl1Xps9o0x9SbkxKHkySb7mFr2pETGgF7c`
- **主页签**：`iap_custom_chest`

用于配置「自选奖励」——玩家购买礼包后，每日可从若干选项中选择一部分领取。


| 列   | 字段名                                       | 类型      | 说明                        |
| --- | ----------------------------------------- | ------- | ------------------------- |
| A   | A_INT_id                                  | int     | 主键，格式 `2024xxxx`          |
| B   | **A_INT_template_id**                     | **int** | **关联的 2013 ID（核心）**       |
| C   | N_STR_desc                                | string  | 备注                        |
| D   | A_MAP_path                                | json    | UI 位置，`{"col":N,"row":N}` |
| E-I | A_MAP_CD/speedup/resource/pvp/other_items | json    | 各类自选奖励内容                  |
| J   | A_INT_max                                 | int     | 每日最多选几个（通常 1）             |


**关联方式**：`A_INT_template_id` = 2013 表的 `A_INT_id`，1 个 2013 → 多个 2024（每个 2024 = 一个可选奖励坑位）。

**重要**：2024 与 1111 解锁道具是**各自独立、单向绑定** 2013 的关系，互不依赖：

- 2024.`A_INT_template_id` → 2013（定义自选坑位内容）
- 1111.`effect.id` → 2013（定义解锁哪套自选奖励）
- 两者可以指向同一个 2013，也可以指向不同的 2013
- 新增/复制 1111 解锁道具时**不需要**同步新增 2024 坑位，只要 effect 指向的 2013 已有 2024 坑位即可

### 4.19 解锁道具机制（item_subscription 类型）


| 字段                            | 说明                                            | 示例           |
| ----------------------------- | --------------------------------------------- | ------------ |
| `A_STR_class`                 | `item_subscription`（订阅解锁类）                    | —            |
| `A_MAP_category_param.effect` | `[{"typ":"item_subscription","id":2013xxxx}]` | `2013400161` |


- effect 中 `typ` = `item_subscription`，`id` 指向一个 **2013 模板 ID**
- 玩家使用该道具后，解锁对应 2013 关联的自选奖励（2024 表），在周卡期间每日可领

**自选周卡完整链路：**

```
2112 活动
  └─ package (2135) → 2011 (fes_weekly_card) → 2013（直售层）
       │
       ├─ 路径A：直接购买
       │    2013 本身同时关联 2024 自选坑位
       │    玩家购买后直接获得自选奖励资格
       │
       ├─ 路径B：全选包解锁
       │    2013 奖励中包含解锁道具 (1111, class=item_subscription)
       │         └─ effect.id → 某个 2013 ID（可以是路径A的同一个2013）
       │              └─ 2024 自选奖励 (N个坑位，通过 template_id 关联)
       │
       └─ 2013 自身的固定奖励 (CDs, VIP 等)

关键：2024 和 1111 各自独立绑定 2013，不互相依赖
```

**两种实际模式：**

1. **直售模式**（个别档位周卡）：玩家购买 → 获得 2013 → 2024 直接通过 `template_id` 绑定该 2013 → 自选奖励生效
2. **解锁道具模式**（全选包）：玩家购买全选包 → 获得多个解锁道具 → 使用道具 → effect 指向 2013 → 2024 通过 `template_id` 绑定同一个 2013 → 自选奖励生效

**操作要点：**

- 轮换活动需要分离解锁道具时，只需新建 1111 道具并让 `effect.id` 指向已有的 2013，无需新建 2024 坑位
- 2024 坑位只在自选奖励内容变化时才需要修改
- 2024 表中每个 `A_MAP_path` 的 col/row 决定 UI 布局位置
- 全选包的 2011 `S_MAP_filters` 会检查其他档位的 2013 ID 是否未购买（互斥逻辑）

### 4.20 装饰物配置（2148 + 1118 + 1127 + 1111）

**定位**：节日/活动装饰物在游戏里本质是一类"可升级星级的建筑"。一个装饰物的完整配置会同时出现在 4 张表里，缺一会导致无法建造、无法升级、或升级后没视觉/buff 变化。

#### 四张表的角色分工

| 表    | 名称                     | 作用                        | 粒度                          |
| ---- | ---------------------- | ------------------------- | --------------------------- |
| 2148 | event_decroation_level | 活动装饰升级规则：每星级 buff、升级消耗、回收 | 每个星级 1 行                    |
| 1118 | building               | 装饰"建筑本体"：美术、市容度、占地、功能     | 每个星级 1 行（type=2）            |
| 1127 | building_build         | 装饰在建造菜单里的入口：解锁消耗、分类       | 一个装饰家族 1 行                  |
| 1111 | item                   | 解锁道具 + 升级材料（同家族可多种材料）     | 1~N 行（解锁道具必有，升级材料按星级难度拆分）   |

#### 跨表 ID 关联链路

```
1111 item (解锁道具，如 11111340 感恩节装饰升级2022)
  │ A_MAP_category_param.effect = [{"typ":"holiday_statue","id":21480101}]
  ↓
2148 event_decroation_level (group_id=214801，3 行：1星/2星/3星)
  │ A_INT_building    = 1118107                       ← 建筑家族
  │ A_INT_unlock_item = 11111340（回指解锁道具）
  │ A_ARR_upgrade_cost = [{"typ":"item","id":11117248,"val":5}]  ← 升级材料
  ↓
1118 building (A_INT_building_id=1118107，3 行：111810701/02/03)
  ↑
1127 building_build (11271061)
  │ A_ARR_building_ids = [1118107]
  │ A_ARR_unlock_cost  = [{"typ":"item","id":11111340,"val":1}]（同解锁道具）
```

> **ID 编号约定**：1118 家族 ID 是 7 位（`1118xxx`），家族下每个星级 = `家族ID * 100 + 星级序号`（`111810701` / `111810702` / `111810703`）。2148 的 group_id（6 位，`214801`）和 1118 家族 ID 是平行编号，不是直接拼接关系。

#### 2148 关键字段

| 字段                         | 含义                                                                                      |
| -------------------------- | --------------------------------------------------------------------------------------- |
| `A_INT_id`                 | 主键（`2148` + group + 星级）                                                                 |
| `A_INT_group_id`           | 装饰分组 ID，同一装饰的所有星级行共享                                                                    |
| `A_INT_building`           | → 1118 的 `A_INT_building_id`（家族 ID）                                                     |
| `A_INT_unlock_item`        | → 1111 解锁道具 ID（用一次就能开图）                                                                 |
| `A_INT_star` / `_star_max` | 当前星级 / 最大星级                                                                             |
| `C_INT_display_key`        | 图标资源（1511）；每星级一般不同                                                                      |
| `C_INT_model_display_key`  | 3D 模型资源（同家族各星级可共用，也可分开）                                                                 |
| `A_MAP_lc_name`            | 名称 i18n key                                                                             |
| `C_MAP_lc_desc`            | 当前星级描述                                                                                  |
| `C_MAP_lc_desc_get`        | 获得/未升级描述                                                                                |
| `A_ARR_BUFF`               | 该星级提供的所有 buff。固定含 `{"typ":"citybeauty","id":12230001,"val":N}` 市容度；其余为 `typ=buff` 具体 id |
| `A_ARR_upgrade_cost`       | 升级到下一星的消耗（最高星级填空）；1 星一般填空                                                               |
| `S_ARR_retake`             | 回收返还（通常只在最高星级填）                                                                         |
| `C_STR_upitem_get_access`  | 升级材料的获取途径（1168 get_access_group 的 id）                                                   |
| `A_INT_year_group`         | 年度分组（轮换活动按年分组）                                                                          |

#### 1118 装饰建筑关键字段

| 字段                         | 典型值/说明                                                          |
| -------------------------- | --------------------------------------------------------------- |
| `A_INT_id`                 | `家族ID*100+星级`                                                   |
| `A_INT_building_id`        | 家族 ID（同家族所有星级共用）                                                |
| `A_INT_type`               | 固定 `2`（装饰类）                                                     |
| `A_INT_collision_class`    | 碰撞体积类型                                                          |
| `C_INT_display_key`        | 美术资源（1511）                                                      |
| `A_MAP_lc_name` / `C_MAP_lc_desc` | 名称 / 描述 i18n key                                         |
| `A_INT_lvl` / `A_INT_max_lvl` | 当前星级 / 最大星级                                                  |
| `A_ARR_cost_asset`         | 建造瞬时消耗（通常一份小资源，不是升级材料）                                          |
| `A_ARR_status`             | 建筑自身 buff（含 `citybeauty` 市容度）                                   |
| `A_ARR_function`           | 拥有的 function ID 列表（11301xxx）                                    |
| `A_ARR_citylayout_function`| 布局编辑时可用的 function                                               |
| `A_MAP_size`               | 占地大小 `{"x":3,"z":3}`                                            |
| `A_INT_remove`             | 是否可拆除（`1`=是）                                                    |
| `A_ARR_remove_rebate`      | 拆除返还                                                            |

> **buff 归属铁律**：1118.`A_ARR_status` 对活动装饰只放 1 条 citybeauty（全表 775 行 type=2 装饰统计 0 行出现过非 citybeauty 条目）；2148.`A_ARR_BUFF` 才是全部 buff 的权威来源。改属性只改 2148；1118 的 citybeauty 与 2148 的 citybeauty 值保持一致（冗余但必须同步）。

#### 1127 建造入口关键字段

| 字段                       | 典型值/说明                                                             |
| ------------------------ | ------------------------------------------------------------------ |
| `A_INT_id`               | `11271xxx`                                                         |
| `A_ARR_building_ids`     | `[1118家族ID]`（1 个元素）                                                |
| `C_ARR_display_labels`   | `["decoration"]`（固定）                                               |
| `A_ARR_unlock_cost`      | `[{"typ":"item","id":1111解锁道具,"val":1}]`（与 2148.A_INT_unlock_item 一致） |
| `C_ARR_unlock_desc`      | 解锁说明 i18n key                                                      |
| `A_INT_count` / `_count_max` | 可同时拥有数量                                                          |
| `A_INT_redoverlap`       | 是否允许重复建造                                                           |
| `C_INT_subtab`           | 建造菜单子分类（装饰通常 `4`）                                                  |
| `C_INT_display_order`    | 建造菜单内排序                                                            |

#### 1111 装饰相关道具

**解锁道具**（一张图纸性质）

| 字段                        | 典型值                                                                       |
| ------------------------- | ------------------------------------------------------------------------- |
| `A_STR_class`             | `statue_decorate`                                                         |
| `A_INT_quest_class`       | `23`                                                                      |
| `A_MAP_category_param`    | `{"effect":[{"typ":"holiday_statue","id":2148一星ID}, ...附带升级材料]}`           |
| `S_INT_use_now`           | `1`（获得即用，自动解锁并放置）                                                         |
| `A_INT_max_own`           | 通常 `=最大星级`，防止重复获取                                                         |
| `A_ARR_use_labels`        | `["bag"]`                                                                 |

> `A_MAP_category_param.effect` 除了 holiday_statue，还可以附带 item 条目（如"解锁后赠送 5 个升级材料"）。

**升级材料**（多次消耗）

| 字段                     | 典型值                |
| ---------------------- | ------------------ |
| `A_STR_class`          | `event`            |
| `C_ARR_display_labels` | `["bag_other"]`    |
| `S_INT_use_now`        | `0`                |
| `A_INT_max_own`        | `999999999`（大上限）   |

#### 配置一个新装饰物的标准步骤

1. **规划 ID**
   - 确定 1118 家族 ID（7 位，如 `1118107`）；按家族 ID 派生每星级 ID = `家族*100+星`。
   - 确定 2148 group_id（6 位）和每星级 ID。
   - 确定 1127 入口 ID、1111 解锁道具和升级材料 ID。
2. **1111 新增解锁道具**：`class=statue_decorate`、`effect` 指向 2148 **一星 ID**、`use_now=1`、`max_own=最大星级`。
3. **1111 新增升级材料**：`class=event`、`display_labels=["bag_other"]`。多个难度可拆多条。
4. **2148 按星级展开**：group_id 同值；每行 `A_INT_building` 指向 1118 家族 ID，`A_INT_unlock_item` 回指步骤 2；`upgrade_cost` 指向步骤 3 的升级材料；最高星级通常填 `S_ARR_retake`；`A_ARR_BUFF` 写该星级合计 buff（citybeauty 市容 + 其他 buff）。
5. **1118 按星级展开**：`A_INT_building_id` 同值；`type=2`；`A_INT_lvl / max_lvl` 对应星级；美术 `display_key`、`lc_name`、`size`、`function`、`remove/remove_rebate` 按家族配。
6. **1127 新增建造入口**：`A_ARR_building_ids=[1118家族ID]`、`display_labels=["decoration"]`、`A_ARR_unlock_cost` = 步骤 2 解锁道具、`subtab / display_order` 决定菜单位置。
7. **i18n（1011）**：补齐 `A_MAP_lc_name / C_MAP_lc_desc / C_MAP_lc_desc_get / C_ARR_unlock_desc` 涉及的所有 key。
8. **美术（1511 display_key）**：确认 `C_INT_display_key`、`C_INT_model_display_key`（2148）、1118 的 `C_INT_display_key` 都已在 1511 注册。
9. **获取途径（1168 get_access_group）**：为升级材料配好入口（对应 2148 的 `C_STR_upitem_get_access`），玩家才能点问号跳转到礼包/活动。
10. **活动联动**：解锁道具和升级材料通常作为 2124 drop 的奖励、或 2013 礼包内容；在对应活动里挂好掉落/礼包。

#### buff 规律（基于 46 组活动装饰 222 行样本）

1. **归属**：`2148.A_ARR_BUFF` 是唯一权威，结构是 `[{typ, id, val}, ...]`；两种 typ：
   - `citybeauty`（id 固定 `12230001`）= 市容度
   - `buff`（id 段 `12117xxx`，少量 `121141xxx`）= 具体属性加成

2. **星数框架**：star_max 分布 = 3（72 行）/ 5（55 行）/ 6（24 行）/ 10（70 行）。老节日用 3 星，大富翁系列 5 星，新节日（2024+ 复活节/春节）主流 10 星。

3. **citybeauty 标准递增**：

   | star_max | 1星 | 2星 | 3星 | 4星 | 5星 | 6星 | ... | 末星 |
   | -------- | --- | --- | --- | --- | --- | --- | --- | ---- |
   | 3        | 200 | 2000 | 4000 | — | — | — | | 4000 |
   | 5        | 200 | 1000 | 2000 | 4000 | 8000 | | | 8000 |
   | 10（线性档） | 200 | 2000 | 4000 | 5000 | 6000 | 7000 | → +1000 | 11000 |
   | 10（倍增档） | 500 | 2000 | 4000 | 6000 | 8000 | 10000 | → +2000 | 18000 |

4. **buff 条数递增（100% 累积、零重置）**：46 组全部"高星 buff id 集合 ⊇ 低星"，未出现覆盖/替换。
   - star_max=3：0 → 1 → 2（最常见形态）
   - star_max=10：1 星 0 条，2 星 1 条，3 星 2 条；**3 星后 id 集合常稳定，仅递增 val**（或 4 星再追加 1 条变 3 条）

5. **buff val 两种增长模式**：
   - **恒定型**：id 的 val 全程 200 不变，靠"加 id + 加市容度"拉升（2025 春节雕像 12117015 全程 200）
   - **阶梯型**：val 逐星 +100（2024 复活节 12117002：200→300→400→...→1000）
   - 老 3 星装饰多为恒定型；10 星装饰多为阶梯型

6. **1 星 buff 的版本演进**：
   - **老版本（≤2024）**：1 星只给 citybeauty，不给 buff（营造"升级感"）— 这是多数
   - **新版本（2025+ 大富翁系列、科林探索；2026 春节/情人节/复活节/科技节）**：1 星就送 1 条 buff，解锁即有收益（体验优化趋势）
   - 新配装饰默认选"老版本"写法；若要跟 2026 新风格，参考大富翁雕像（group 21483x 段）

7. **高数值特例**：
   - 前期装饰物-飞碟（214826）：val 跨度 20000~500000（挖矿产量类），不套用百位节奏
   - "涂饰"系列（军功丰碑 214829、竞技之王 214830）：1 星即 100，3 星档位，独立节奏

8. **双表 citybeauty 冗余一致**：
   - 1118.`A_ARR_status` 的 citybeauty 与 2148.`A_ARR_BUFF` 的 citybeauty **必须同值**（同家族 2022 感恩节 200/2000/4000 双表完全一致）
   - 改市容度要**两个表都改**，否则客户端/服务端读到不一致
   - 1118 永远只放 citybeauty 一条，**不要往 1118 加 `typ=buff` 条目**，所有属性加成都走 2148

9. **热门 buff id 速查**（可直接沿用同题材活动）：

   | id        | 出现   | 常见搭配节日/活动 |
   | --------- | ---- | --------- |
   | 12117002  | 34 次 | 热门主属性，多节日 |
   | 12117009  | 34 次 | 热门主属性      |
   | 12117005  | 31 次 |           |
   | 12117015  | 21 次 | 春节 / 复活节系 |
   | 12117004  | 20 次 |           |
   | 12117006  | 20 次 |           |
   | 12117013  | 18 次 | 感恩节 / 周年  |
   | 12117010  | 18 次 |           |
   | 12117011  | 17 次 | 葛列格 / 竞技  |
   | 12117017  | 15 次 | 周年 / 圣诞   |

   新装饰配 buff 时先找同题材历史雕像（如"春节装饰"去看 21482x 段），沿用已上线的 buff id 组合最安全。

#### 涂饰 & 技能机制（paint / decroation_paint_skill）

**核心认知**：部分装饰（47 组里 24 组，约 51%）支持"涂饰"——玩家消耗一个涂饰道具给装饰"上色 24 小时"，期间获得**额外 buff + 可触发主动技能**。所有 10 星装饰 100% 支持涂饰；老 3 星装饰只有 5/22 支持。

##### 五表联动（在装饰四表基础上增补 1 张）

```
2148.A_INT_paint = 1                                 ← 标记"支持涂饰"
2148.C_ARR_paint_item = [1111涂饰道具id]              ← 绑定哪个涂饰道具
2148.A_ARR_paint_buff = [{...}]                      ← 涂饰期间额外 buff（逐星递增）
2148.A_INT_decroation_paint_skill = 2171技能id       ← 某星解锁的技能（0=无）
    │
    ├─→ 1111 item (class=decorate_paint)            涂饰道具本体
    │     A_MAP_category_param.effect:
    │       [{"typ":"decorate_paint","id":2148.group_id,"val":86400000},
    │        {"typ":"item","id":自身,"val":1}]
    │     A_ARR_use_labels = ["bag", "<group_id>"]   按 group_id 绑定装饰
    │     S_INT_use_now = 0                          手动使用
    │     C_ARR_display_labels = ["bag_other"]
    │
    └─→ 2171 event_decroation_skill（装饰技能表）
          文档 1YJW39MBGg7aya62_hkhI1uRmyMknjZQV226Dqsksis4 / 页签「装饰技能」
          每行 = 一个技能组的一个等级
```

##### 2171 技能表关键字段

| 字段                   | 说明                                                               |
| -------------------- | ---------------------------------------------------------------- |
| `A_INT_id`           | 技能 ID（2148 回填用）                                                  |
| `A_INT_group`        | 技能组（一组 = 一个技能的多个等级，同组 ID 前 7 位相同）                                |
| `A_STR_class`        | 固定 `decroation_paint_skill`                                      |
| `A_INT_lv / _max_lv` | 技能等级 / 最大等级                                                      |
| `A_INT_cd`           | 冷却，样本全是 `4320`                                                   |
| `A_STR_target_troops`| 目标（`self_troop`=自军）                                              |
| `A_ARR_status`       | `[{"typ":"buff","id":<bufid>,"val":<时长ms>,"arg1":<数值千分位>}]` |

> 示例：`{"typ":"buff","id":12117001,"val":7200000,"arg1":500}` = 给自军上 12117001 这个 buff，持续 7200000ms（2 小时），数值 500（千分位 = 5%）。

##### 涂饰机制规律（基于 24 组涂饰装饰 144 行样本）

1. **道具消耗模型**：玩家用 1 个涂饰道具 → 激活该 group 涂饰状态 86400000ms（24 小时）→ 期间 `A_ARR_paint_buff` 生效、技能可释放 → 到期后退回"未涂饰"只剩 `A_ARR_BUFF`。需要续用道具保持效果。
2. **paint_item 1:1**：24 组中 22 组（92%）同家族只绑 1 种涂饰道具；另 2 组可能是轮换版本多绑。
3. **paint_buff 恒定 1 条**：144 行 100% 是单条 buff，结构 `[{"typ":"buff","id":<bufid>,"val":<数值>}]`，val 逐星线性递增。
4. **paint_buff 从 1 星起就有**（和主 BUFF 不一样！主 BUFF 老版 1 星只给 citybeauty）。这是"鼓励玩家购买涂饰道具"的设计。
5. **技能从第 3 星解锁（主流）**：6 组 10 星装饰 100% 从 star 3 起配技能；6 星装饰 3/4 从 star 3、1 个从 star 2；5 星/3 星装饰不统一（star 1-3 都有）。
6. **技能等级与星级对齐**：10 星装饰搭配 8 级技能组（star 3~10 → skill lv 1~8）；6 星装饰搭配 4 级技能组（star 3~6 → lv 1~4）。这是"解锁星数 = 技能组 max_lv"的严格对应。
7. **skill ID 同组内连续 +1**：2171 里一个 group 下的各等级 ID 就是 group 号×10 + 等级（如 2171011 组下就是 21710111/21710112/…）。回填 2148 时按此规律直接数。
8. **技能 status 两种持续时间**：主流 `val=7200000ms`（2 小时战斗类 buff）和 `val=28800000ms`（8 小时集结类 buff）；少量 `3600000ms`（1 小时）。
9. **arg1 = 千分位数值**：`arg1=500` 表示 5%、`arg1=1000` 表示 10%、`arg1=2000` 表示 20%。技能升级就是拉 arg1（500→1000→1500→2000），buff id 和 val 保持不变。
10. **一个装饰一个技能组**：24 组装饰对应 2171 里 17 个技能组（部分组被多个装饰复用）。复用常见于同一主题跨年（例如两个登月节装饰都用 group 2171005）。

##### 配置带涂饰装饰的增量步骤（在四表基础上追加）

1. **1111 新增涂饰道具**（class=`decorate_paint`，display_labels=`["bag_other"]`，use_now=0）：
   - `effect = [{"typ":"decorate_paint","id":<2148 group_id>,"val":86400000}, {"typ":"item","id":自身,"val":1}]`
   - `use_labels = ["bag","<group_id>"]`
2. **2171 新增技能组**（N 级一次配齐）：
   - ID 段按 `2171GGGL`（GGG=group 序号，L=等级），同组 +1 递增
   - `A_ARR_status` 的 val（持续时间）和 arg1（数值）按档位确定；arg1 常见 500/1000/1500/2000…
3. **回填 2148**：每星级行追加
   - `A_INT_paint=1`
   - `C_ARR_paint_item=[步骤1道具id]`
   - `A_ARR_paint_buff=[{"typ":"buff","id":<bufid>,"val":<数值>}]`（1 星起就填，val 逐星递增）
   - `A_INT_decroation_paint_skill`：主流从 3 星起填 `2171GGG1/2/3…`；1-2 星填 `0`
4. **i18n（1011）**：技能 `C_MAP_lc_name/lc_desc/lc_data` 的 3 组 key 都要翻译。
5. **美术（1511）**：技能 `C_INT_display_key` 图标。

#### 常见坑

- **星级数量不对齐**：2148、1118 的星级行必须一一对应；1118 少一行会导致最高星无建筑模型；2148 少一行会导致点升级无反应。
- **解锁道具 effect 必须指向一星**：`holiday_statue` 的 id 是 2148 里 star=1 的那行。指向其他星级 = 一次性升到目标星。
- **2148.A_INT_unlock_item 与 1127.A_ARR_unlock_cost 不一致**：会出现"建造菜单用 A 道具解锁，但活动逻辑期望 B 道具"的错位。改解锁道具时两个位置都要改。
- **buff 归属错放**：属性 buff（`typ=buff`）只写 2148；1118.`A_ARR_status` 只放 citybeauty。往 1118 放 `typ=buff` 会导致双重生效或客户端/服务端不一致。
- **缺 get_access_group**：问号按钮点了没反应，玩家不知道去哪拿升级材料。
- **轮换活动年度分组**：同一个"装饰系列"跨年复用时，用 `A_INT_year_group` 区分，老年份别直接覆盖，避免老号玩家数据错乱。
- **涂饰道具 use_labels 漏填 group_id**：`A_ARR_use_labels` 第二项必须是 2148 的 `A_INT_group_id`，否则道具不会绑定到装饰，玩家点了"使用"没反应。
- **技能等级数与装饰星数不匹配**：如 10 星装饰配了 6 级技能组，会出现"8-10 星点技能无效"；正确做法是 star_max - (首次解锁星 - 1) = 技能 max_lv。
- **paint_buff 与 A_ARR_BUFF 混配**：这两个字段互不覆盖——`A_ARR_BUFF` 始终生效、`A_ARR_paint_buff` 仅涂饰期间生效。不要把同一条 buff 同时放两个字段，会叠加。

#### 4.20.A 大富翁 5 星装饰标准模板（2025+ 节日常用）

**适用场景**：节日主题 + 大富翁活动容器（活动 id = 21127362 = "漫游奇遇"）。
**对标样本**：214834 2025周年庆、214839 2025圣诞、214841 2026春节、214842 2026情人节、214848 2026复活节、214849 2026拓荒节（本次新配）。

##### 数值档位（可直接套）

| 字段 | 1 星 | 2 星 | 3 星 | 4 星 | 5 星 |
|---|---|---|---|---|---|
| citybeauty val | 200 | 1000 | 2000 | 4000 | 8000 |
| 主 BUFF buff id 条数 | 1 | 2 | 2 | 2 | 2 |
| 主 BUFF val（buff 条） | 200 | 200 | 400 | 600 | 800 |
| paint_buff val | 200 | 400 | 600 | 800 | 1000 |
| upgrade_cost 升级材料数 | — | 6 | 12 | 15 | 20 |
| skill（方案 A：2 星起解锁 4 级） | 0 | lv1 | lv2 | lv3 | lv4 |
| S_ARR_retake | — | — | — | — | `[{item,11111021,1}]` = 200 CDs |

> **技能等级方案**：5 星 + 4 级技能组 = 2 星起解锁（参考春节 214841）；5 星 + 3 级技能组 = 3 星起解锁（参考情人节 214842）。首选 4 级组 + 2 星起。

##### 单模型 / 多模型

- **老版 3 星装饰**（感恩节/复活节等 smax=3）：每星一个模型（display_key 三档）
- **2026 春节大富翁**：3 个模型（1 星 / 2 星 / 3-5 星共用）
- **2026 深海节/拓荒节大富翁（最新趋势）**：**5 星全部共用 1 个模型** display_key（美术只给 1 张图）
- 1511 里对应资源命名：`<主题>2026-大富翁装饰建筑-1星` + `-道具icon` + `<主题>大富翁涂饰-<物件名>`

##### i18n key 复用策略（省翻译）

- `2148.C_MAP_lc_desc` + `1127.C_ARR_unlock_desc` **复用已有 EVENT key** `LC_EVENT_3anni_decoration_get_desc_1`（= "通过活动'漫游奇遇'获得"，多节日大富翁都共享）
- `2148.C_MAP_lc_name` + `C_MAP_lc_desc_get` + 1111 道具 name/desc → 新建 ITEM 段 key（每装饰一套）
- 涂饰道具新建 `LC_ITEM_<主题>_paint_decoration_paint_name/desc`（命名遵循春节/情人节风格）
- **不需要新建 BUILDING 段 key**（大富翁装饰全复用 EVENT）

##### 1168 标准配置模式（6 行）

每个大富翁装饰配 **5 + 1 = 6 条 1168 行**：
- 5 行：每星 1 条，`C_STR_item_label` = 2148 **行 id**（如 `21484901~05`），`access_group = [{"id":11531001,"args":["<活动 id>"]}]`
- 1 行：涂饰道具，`C_STR_item_label` = 2148 **group_id**（如 `214849`），同样指向活动 id
- 6 条 1168 的 ID 连续 `+1`，**2148 的 `C_STR_upitem_get_access` 按星升序依次映射前 5 条**；涂饰道具的 1168 id 写到 **1111 涂饰道具的 `A_INT_get_access_group`**（不是 2148）

##### ID 分配节奏（截至 2026-04）

| 表 | 最新已用 | 下一空位 |
|---|---|---|
| 2148 group_id | 214849（拓荒节）| 214850 |
| 1118 building_id | 1118220（拓荒节）| 1118221（之后是 kvk6 大号段 1118924+，装饰可安全 +1） |
| 1127 A_INT_id | 11275234 | 11275235 |
| 1111 8 位段 11111xxx | 11111361 | 11111362 |
| 1111 8 位段 11112xxx | 11112954 | 11112955 |
| 1168 A_INT_id | 11684890 | 11684891 |
| 2171 group | 2171018 之后空（2171017 已用）| 按需新建或复用热门组 |

#### 4.20.B 配置落表实操（Google Sheets → git）

##### 写入 Sheet 的 range 陷阱

`gws sheets +read` 默认 range（如 `A:R`）**会按指定结束列截断**，即使 Sheet 实际列更宽。**写入前验证完整列**时必须用宽范围：

```bash
gws sheets +read --spreadsheet <id> --range "<tab>!A<row>:AZ<row>"
```

**教训**：2026 大富翁系列装饰的 1118 行看起来只有 18 列（A-R）是空白布局假象，实际 Sheet 已填满 33 列（A-AG）；只写前 18 列会漏掉 `A_INT_remove=1`（可拆除）、`A_MAP_size`（占地）、`A_ARR_function`（功能）等关键字段，线上装饰会异常。**配 1118 新行时必须写满 33 列**。

##### TSV vs Sheet 列差异（导出过滤规则）

**规则 1**：`split_cfg_sheet` 在 server_type=0 的表里按 `A_INT_country_use_type` 拆分国服/外服，**该列本身在两份 TSV 里都被删**
**规则 2**：`remove_comment_column` 删除第一个以 `*STR_comment` 结尾且 `*` 不是 `S` 的列（即 `C_STR_comment`、`N_STR_comment` 被删；`S_STR_comment` 保留）

| 表 | Sheet 列 | TSV 列 | 过滤掉的列 |
|---|---|---|---|
| 2148 | 24 | 22 | C_STR_comment（index 1）+ A_INT_country_use_type |
| 1118 | 33 | 33 | S_STR_comment 保留，无 country_use_type |
| 1127 | 16 | 14 | C_STR_comment + A_INT_country_use_type |
| 1111 | 25 | 24 | S_STR_comment 保留，A_INT_country_use_type 删 |
| 1168 | 7 | 7 | 无（全保留）|

##### TSV JSON 字段必须紧凑

TSV 里 `_MAP_` / `_ARR_` 列的 JSON 必须**无空格紧凑格式** `{"typ":"buff","id":12117001,"val":200}`。Python 默认 `json.dumps()` 会加空格，必须指定 `separators=(',', ':')`；否则 git diff 会显示"虚假全改"。

```python
json.dumps(obj, ensure_ascii=False, separators=(',', ':'))
```

##### 装饰物三件套 id 必须连续

**惯例**：一个装饰（如大富翁雕像）的 **本体解锁道具 / 升级材料 / 涂饰道具** 三个 1111 道具 id **必须连续**（`N` / `N+1` / `N+2`），顺序是「本体、升级、涂饰」。

| 装饰 | 解锁 | 升级 | 涂饰 |
|---|---|---|---|
| 2026 春节大富翁 | 11112779 | 11112780 | 11112781 |
| 2026 情人节大富翁 | 11112782 | 11112783 | 11112784 |
| 2026 拓荒节大富翁 | 11112955 | 11112956 | 11112957 |

选号段时：先在 1111 里扫 11112xxx 段的最大连续空位，一次占 3 个号。不要把解锁放到 11111xxx 段再把升级/涂饰塞 11112xxx——**跨段会被策划要求返工**。

##### 1011 i18n TSV 的特殊格式

- 每语种一个 TSV：`fo/i18n/<lang>.tsv`（18 语言）；国服 `cn/i18n/cn.tsv`（1 语言）
- 3 列：`id \t value \t index_int`
- **id 命名 = `<页签名>_<Sheet ID 列>`**（不加 LC_ 前缀，但加页签前缀），如 `ITEM_2026pioneer_windmill_name`
- **按 id 字母序排序**，新增需插入到字母序位置（不能 append 末尾）
- i18n 允许全表推送（其他表只推修改行）

##### 国服 vs 外服传输机制（gsheet_down.py）

1. **目录表 `server_type` 字段**（第 6 列 / index 5）：
   - `0` = 国服+外服都导（按行拆）
   - `1` = 只导外服
   - `2` = 只导国服
2. **1011 是唯一按 server_type=1/2 分两张独立 Google Sheets 文档** 的表：
   - 外服 1011 `11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY`（18 语种）
   - 国服 1011 `1x7E76B9U2CWzOgbuk60F6oEDo_4Lkz1MnRJYSA9m_CM`（只 `cn` 一列）
   - **国服 1011 的 cn 列通过 IMPORTRANGE 从外服 1011 的 cns 列拉数据** → 外服加 cns 翻译 = 国服自动同步，无需手动改国服文档
3. **其他表 server_type=0**：`split_cfg_sheet` 按每行 `A_INT_country_use_type` 拆：
   - `=0` 行同时进 fo/ 和 cn/
   - `=1` 只进 fo/
   - `=2` 只进 cn/
4. **cn/ 实际维护状态**：近一年仅 K5/K2 地图紧急修复；新活动（大富翁等）**默认不推国服**。外服提交是主流程，`cn/` 由国服发版同事周期性同步。
5. **cn/config/ 某些表列数 < fo/**（如 cn/event_decroation_level.tsv 17 列 vs fo/ 22 列）：国服不支持 paint/skill/year_group 机制，字段被历史截除。直接复制 fo 行到 cn TSV 会列错位，**非国服专属需求不要动 cn/**。

##### 新行落表步骤

1. **Sheet 层**：`gws +append` 追加末尾 / `insertDimension + values.update` 插入中间
2. **TSV 层**（5 张 config 表手动构造、不跑 export_sheet.py 全量导）：
   - 从 Sheet 读整行 `A:AZ` 确保完整
   - 按表的过滤规则删除 C_STR_comment / A_INT_country_use_type
   - 用紧凑 JSON 拼 TSV 行
   - append 末尾 / insert 到对应 id 升序位置
3. **i18n TSV**（18 语种全表可推）：按字母序 insert 4 行 × 18 文件
4. **git**：
   - 分支沿用当前（不切）
   - `git pull` 先同步
   - `git add` 指定文件（不用 `-A`）
   - commit 格式：`[配置更新]<表号+连接> <简述>`
   - `git push`
5. **规律校验**：
   - 所有新 ID 严格升序插入到对应段
   - 跨表引用闭环（2148.unlock_item ↔ 1127.unlock_cost ↔ 1111.id；涂饰 group_id 三处一致）
   - citybeauty 值在 1118.status 和 2148.BUFF 完全相同

### 4.21 1142 头像框配置表（avatar_frame）

**定位**：头像框是角色头像外圈装饰（装饰性资产，绝大多数不带属性）。一个头像框 = 1 条 1142 行。

**文档**：`1jBsZOuoMz3uwYHN-Tcotn8QPBgX5LYDpUHXVu2LzpiQ` / 主页签 `avatar_frame`
**规模**：93 条头像框（2026-04 统计）

#### 字段清单（14 列）

| 字段 | 说明 |
|---|---|
| `A_INT_id` | `11421xxx` 头像框主键 |
| `C_STR_comment` | 中文注释（不入 TSV） |
| `A_STR_constant` | 常量名（如 `default_frame`），大部分为空 |
| `C_INT_display_key` | 图标 / 动态资源（1511） |
| `C_INT_display_order` | 列表排序 |
| `A_MAP_lc_name` | 名称 i18n |
| `C_MAP_lc_desc` | 描述 i18n |
| `A_MAP_unlock_requirement` | 解锁条件 JSON，**全表 93 行都是 `{"op":"ge","typ":"building","id":111811,"val":N}`**（要塞等级） |
| `A_ARR_unlock_cost` | 解锁消耗 `[{"typ":"item","id":<1111 道具>,"val":1}]`——val 全是 1 |
| `S_ARR_status_active` | 装备时生效 buff，**93 行里 91 行为空**，仅 2 个头像框（如吃鸡达人）带 buff 加成 |
| `C_MAP_lc_get_from` | 获取途径文案 i18n |
| `C_INT_rarity` | 稀有度序号（每个头像框独立） |
| `C_MAP_access` | 列表页"问号跳转" JSON（见下） |
| `C_INT_dynamic` | 动态等级：`0` 静态图（71）/ `1`（15）/ `2`（7）三档 |

#### `C_MAP_access` 模式（只有两种）

| typ | 含义 | 示例 | 占比 |
|---|---|---|---|
| `others` | 纯文本提示（无跳转） | `{"typ":"others","args":[{"typ":"lc","txt":"LC_MENU_frame_get_through_achievement_before"}]}` | 87/93 |
| `event` | 跳转到 2112 活动 | `{"typ":"event","args":[{"typ":"lc","txt":"LC_MENU_frame_get_desc_limit_event","id":21121395}]}`（id 是 2112 活动 id） | 6/93 |

**`C_MAP_access` 没有 1168 跳转的 typ**，也没有其他形态。

#### 跨表链路

```
2112 活动（drop/package）
  └──→ 1111 解锁道具（A_STR_class="avatar_frame"）
           │ A_MAP_category_param.effect = [{"typ":"avatar_frame","id":<1142 id>,"val":-1},
           │                               {"typ":"item","id":11111031,"val":1000}]  ← 附赠 1000 CDs
           │ （val=-1 表示永久解锁，避免"只激活一段时间"）
           ↓
1142 avatar_frame
  │ A_ARR_unlock_cost = [{item, 1111 id, 1}]  ← 与 1111.effect 头像框 id 闭环
  │ A_MAP_unlock_requirement: 要塞等级门槛（通常 1 或 99）
  ↓
C_MAP_access:
  - others 型 → 只显示文案（玩家自己找）
  - event 型 → id 指向 2112 活动，UI 提供跳转按钮
```

#### 1142 与 1168 的关联（实际情况）

**本次调研结论：1142 不直接关联 1168。**

- `C_MAP_access` 的 typ 只有 `others`（文本）和 `event`（跳 2112 活动），没有 `get_access_group` 或等价形态
- 1111 里所有 103 条 `A_STR_class=avatar_frame` 的解锁道具 `A_INT_get_access_group` **全部为 `0`**
- 1168 表里没有 `C_STR_item_label` 以 `1142` / `11421` 开头的行

**可能的间接路径**（未被本表字段显式编码）：
- 头像框 → 解锁道具 → 活动 `21121xxx`（C_MAP_access.event.id）→ 活动里的某些礼包/掉落道具可能有 1168 跳转
- 但从 1142 自身看不到 1168 身影

**建议**：若策划说 1142 配置"关联 1168"，请让对方指一下具体哪个字段/哪个场景；当前看到的机制是 1111+2112。

#### 新增头像框的步骤

1. **1111 新增解锁道具**（`class=avatar_frame`、`max_own=1`、`use_now=1`、`effect` 指向新 1142 id + 附赠 11111031×1000）
2. **1142 新增行**：
   - ID `11421<下一可用>`
   - `A_MAP_unlock_requirement`：要塞等级条件（无门槛写 1）
   - `A_ARR_unlock_cost`：指回步骤 1 的 1111 id
   - `C_INT_rarity`：从当前最大值往后取
   - `C_MAP_access`：活动专属选 `event` + 活动 id；其他选 `others` + 文案
   - `C_INT_dynamic`：静态 0 / 动态 1 或 2
3. **1511 display_key**：动态头像框需要提供动效资源 key
4. **1011 i18n**：补 name / desc / get_from / 若用 event 还需 `LC_MENU_frame_get_desc_limit_event` 之类 key
5. **2112 活动挂道具**：在活动的 drop/package 里投放 1111 解锁道具

#### 注意事项

- `A_ARR_unlock_cost.val` 永远 1（解锁一次性消耗）；想重复获得头像框没意义（`max_own=1`）
- 解锁后`A_INT_max_own=1` 限制玩家只能拿 1 份，再发第 2 份会被背包拒收
- `val=-1` 在 `effect` 里是"永久"语义，头像框必填 -1；带时效头像框目前未见案例
- `C_INT_rarity` **允许重复**（2026 新头像框 11421098/099/100 都是 1070），不是强制唯一
- 1111 头像框解锁道具 id 段不连续（11111304 / 111110340 / 111111025 / 111111038 等），新增前要扫 `class=avatar_frame` 找真空位，别直接 +1

---

---

## 五、标准操作流程

### 5.1 通用流程

```
Step 1: 定位活动
  → 在 2112 表搜索活动 ID 或名称
  → 解析 I 列 JSON，找到目标组件 typ 和 id

Step 2: 定位子表配置
  → 取组件 id 前4位 → 查"常用表速查"得文档ID + 主页签
  → 在子表中按 id 搜索具体行

Step 3: 读取当前值
  → gws sheets +read 读取目标行/单元格

Step 4: 修改并写入
  → 构造新值（保持 JSON 格式完整）
  → gws sheets spreadsheets values update 写入
  → 用户未指定页签时必须先询问

Step 5: 验证
  → 重新读取确认修改成功
```

### 5.2 修改掉落奖励（drop）

1. 在 1111 表查找新旧道具的 ID
2. 在 2112 表定位活动，解析 drop 组件 ID 列表
3. 在 2124 表找到每个 drop ID 对应的行
4. 读取 G 列 `A_MAP_drop` JSON，在 `args` 数组中替换道具 ID
5. 保持 `num`（数量）、`wgt`（权重）等不变
6. 写入并验证（同一道具可能在多个 drop 配置中出现，需逐一检查）

### 5.3 修改礼包奖励（package）

1. 在 2112 表定位活动，解析 package 组件 ID 列表
2. 在 2135 表查每个 package ID 的 `A_INT_iap` → 得到 2011 ID
3. 在 2013 表中，用 `A_INT_config_id` 匹配 2011 ID → 找到所有价格档位
4. 修改目标字段（售价/奖励/CD 等）
5. 写入并验证

### 5.4 修改任务奖励（task）

1. 在 2112 表定位活动，解析 task 组件 ID 列表
2. 在 2115 表中按 `A_INT_id` 匹配
3. 修改 G 列奖励或 E 列条件
4. 同活动所有 task 的 `A_INT_group` 应保持一致
5. 写入并验证

---

## 六、业务模型 — 已知活动类型

### 6.1 强消耗活动（扭蛋机抽奖）

**玩法**：消耗道具/货币抽奖，从奖池中随机获得奖励。

**配置特征：**

- 4 个 drop 组件：免费/付费 × 阶段1/阶段2
- 通过 `A_ARR_action_time` 区分阶段，`A_STR_action` 区分免费/付费
- 15 个左右阶梯 task，按排行积分递增，最后一个为循环任务
- 多个 package（主礼包组 + 触发礼包组）

### 6.2 Battle Pass 活动（通行证）— 模板 21127638

**玩法**：玩家完成任务获取经验升级 BP，逐级领取奖励。可购买通行证解锁付费轨道。BP 内还嵌套「集结礼包」子系统——全服购买初级通行证的人数达到阈值后，解锁额外阶段奖励。

**标准组件清单（以 21127638 为参考，共 23 个组件）：**


| 组件类型             | 数量  | 配置表  | 作用                        |
| ---------------- | --- | ---- | ------------------------- |
| `battle_pass`    | 1   | 2130 | BP 通行证主配置（升级经验、任务、暴击倍率）   |
| `retake`         | 1   | 2137 | 补签/回购机制                   |
| `jump_link`      | 1   | 2121 | 跳转链接（指向获取途径）              |
| `new_progress`   | 10  | 2121 | 集结礼包阶段奖励（BP 中的子 BP）       |
| `fes_module`     | 1   | 2143 | ⚠️ 本模板中已废弃但必须保留，删除会导致界面错乱 |
| `bp_rank_item`   | 1   | 1111 | ⚠️ 本模板中已废弃但必须保留，删除会导致界面错乱 |
| `cross_progress` | 1   | 2011 | 集结礼包解锁IAP包（跨服进度追踪载体）      |
| `package`        | 6   | 2135 | 商城礼包                      |
| `drop`           | 1   | 2124 | 循环宝箱掉落配置                  |


**配置特征：**

- 1 个 `battle_pass` 组件 → 2130 表（BP 总配置）
- 2130 定义升级经验、暴击倍率、任务列表（daily/achievement/weekly/limit 四类，均指向 2115）
- 2131 绑定 2130，每级一行，定义三轨道奖励：`free_rewards`（免费）、`pay_rewards`（基础付费）、`pay_rewards_2`（豪华付费）
- 购买 BP 的入口通过 2130 的 `A_MAP_pkg` 字段引用 IAP 配置

**集结礼包机制（new_progress + cross_progress）：**

```
cross_progress(2011 ID) ← 集结奖励解锁礼包（玩家购买入口）
       ↓
new_progress × N 个阶段:
  arg2 = 追踪的 IAP(2011 ID，如初级通行证)
  arg1 = 全服/跨服购买人数阈值
  arg3 = 5（跨服维度）
  A_ARR_reward = 免费奖励（达阈值所有人可领）
  A_ARR_reward_expr = 付费奖励
  S_MAP_condition = {"op":"ge","typ":"iap_purchases","id":2013模板ID,"val":1}
```

- 追踪目标：统计购买 `arg2`（初级通行证）的全服/跨服玩家人数
- 免费轨道：达到 `arg1` 阈值后所有玩家可领 `A_ARR_reward`
- 付费轨道：购买了 `cross_progress` 对应的解锁礼包后，可额外领 `A_ARR_reward_expr`
- 阶段数量和阈值梯度每次可调整

#### 6.2.1 节日 BP 活动切换操作流程

将一个已配置的节日 BP 活动（如科技节）切换为另一个节日（如拓荒节）时的标准步骤：

**第一步：新建集结礼包（必须新建，不可复用）**


| 表    | 操作   | 关键字段                                                        |
| ---- | ---- | ----------------------------------------------------------- |
| 2011 | 新建一行 | 复制当前集结礼包行；改 `N_STR_pkg_desc`；`A_MAP_time_info` 绑定 `actv_id` |
| 2013 | 新建一行 | `A_INT_config_id` → 新 2011 ID；改 `N_STR_temp_desc`           |


- **集结礼包名称规则**：2013 的 `A_STR_pkg_title` 应与 2112 活动的 `A_MAP_text.title`（本地化 key）保持一致
- 原因：服务器检测的是历史购买记录，复用旧 ID 会导致上期买过的玩家本期白嫖

**第二步：新建 2130 BP 配置**


| 表    | 操作   | 关键字段                                          |
| ---- | ---- | --------------------------------------------- |
| 2130 | 新建一行 | 找目标节日**上一期**的 2130 行复制；改 `N_STR_comment` 为新年份 |


- `A_MAP_pkg` 保持引用目标节日的通行证 IAP ID（与第三步复用的通行证对应）
- 道具（`quality_up_item`、`level_up_item`）沿用目标节日的道具，可复用
- 奖励/暴击等参数等数值设计表后再调

**第三步：复用通行证礼包（找去年同节日的）**


| 表    | 操作               | 关键字段                                        |
| ---- | ---------------- | ------------------------------------------- |
| 2011 | 修改 2 行（初级+高级通行证） | 名称年份 N→N+1；`A_MAP_time_info` 绑定当前 `actv_id` |


- 寻找去年**同一个节日**的通行证 ID，而非当前节日的 → 名字和道具天然匹配，改动最少
- 必须更新 `A_MAP_time_info`，确保绑定当期活动 ID，否则老玩家购买记录不会刷新

**第四步：修改 2112 活动配置表**


| 字段                  | 操作                  |
| ------------------- | ------------------- |
| `S_STR_comment`     | 改为新节日名称             |
| `A_STR_constant`    | 改为新节日 constant（需确认） |
| `A_INT_show_hud`    | 改为新节日 HUD           |
| 组件 `battle_pass`    | 改为第二步新建的 2130 ID    |
| 组件 `cross_progress` | 改为第一步新建的 2011 ID    |
| Banner 相关           | 按需更新（可手动处理）         |


其余组件（new_progress、package、drop、fes_module、bp_rank_item 等）ID 不变。

**第五步：修改 new_progress × N（2121 表）**


| 字段                   | 操作                    |
| -------------------- | --------------------- |
| `C_STR_comment`      | 改节日名称                 |
| `A_INT_arg2`         | 改为第三步复用的初级通行证 2011 ID |
| `S_MAP_condition.id` | 改为第一步新建的集结礼包 2013 ID  |


**第六步：数值落地（拿到策划设计表后）**

| 对象 | 操作 | 关键字段 |
|---|---|---|
| 2131 等级奖励 | **新建** N 级（和上一期等级数可能不同；如 2025 拓荒节 25 级 → 2026 升到 40 级） | 每级 `A_ARR_free_rewards` / `A_ARR_pay_rewards` / `A_ARR_pay_rewards_2` / `A_INT_exp`；`bp_id` 指向第二步新建的 BP ID |
| 2130 通行证价格 | 同步改 2013 `A_FLT_price` / `A_INT_CDs` / `A_ARR_other_items` 里的 xp val / `A_ARR_price_info` product_id（如 `ape_0699_cd_*`、`ape_1999_cd_*`） | 若价格从 $3.99/$9.99 改到 $6.99/$19.99，CD 要同步（参考科技节 1750/5000）、VIP 经验同 CD |
| 2124 drop 循环宝箱 | **原地改 `A_MAP_drop`**（此 drop ID 多个节日 BP 共用，接受全局换池） | 奖池道具 id 换成本节日的（如拓荒节用 `11117418`/`111110325`） |
| 2137 retake | 找去年同节日的 retake（如拓荒节 `21371111`）复用；否则新建。1:1 比例即 `cost=1, give=1`，"成本价值 X" 指单价×数量的美元值，不是数量 | `A_MAP_cost_asset` 指 BP 经验道具，`A_MAP_give_asset` 指回收资产（如粮食 11111001） |
| 2124 随机礼包 drop | 把 3 个随机礼包奖池（`212452127/128/129` 等）里的 BP 道具 id 替换成本节日的 | 用 **字符串 replace**（原值内的权重/数量不改） |
| 2013 锚点/触发/随机礼包模板 | 9 个 2013 模板的 `A_ARR_other_items` 里 BP 道具 id 替换 | 同上 |
| 2121 new_progress Purchase 奖励 | 按策划改 `A_ARR_reward_expr` 第 3 奖励（典型：L3/L6/L9/L10 = 万能英雄碎片×1，其余档 = 多成长线自选宝箱×2） | FREE 部分通常不变 |
| 2121 jump_link | 新建一条（如 `21219625`），`A_INT_arg1` = 本节日 BP 经验道具 | 旧 jump_link 与其他节日共用，不要原地改 |
| 2112 组件列表中 `retake` 的 id | 若复制自科技节模板，retake id 可能还挂着科技节（如 `21371103`），需要换成本节日的（如 `21371111`） | 不换会出现"回收拓荒节纪念钻头得不到粮食"的跨节日串台 |
| 2168 `A_INT_show_hud` | 查 2168 里本节日那一行的 `A_INT_id`（如拓荒节 `21680032` "2026-5月拓荒节系列活动"） | — |
| 2168 `A_INT_icon_displaykey` | 取 2168 对应行的 `C_INT_display_key`（如拓荒节 `15116147`） | 不是 2168 的 id，是 2168 里那一行 display_key 列的值 |
| 1013 `fes_actv_bp_extra` | 该常量的 `A_ARR_quintuple` 要补 `{"id": <本期活动 ID>}`，不然循环宝箱机制不绑活动 | 多个节日 BP 共享，往数组里 append，不要覆盖 |
| 2143 fes_module / bp_rank_item | **沿用**（每期都不改） | — |
| 2111 activity_calendar | 补一行 `A_INT_activity_id = <本期活动 ID>` 才能后台开启 | — |

**循环宝箱机制（drop + 1013 常量）：**

BP 满级后，每额外积累一定经验就会开启一个宝箱。由 `drop` 组件 + `1013` 常量配置共同控制：

```
1013 常量（如 10137256）:
  A_STR_constant = fes_actv_bp_extra    ← 与 drop 的 A_STR_action 同名绑定
  A_ARR_array = [100, 15]               ← [每次开箱所需经验, 最大开箱次数]
  A_ARR_quintuple = [{"id": 21127638}, {"id": 21127651}, ...]  ← 绑定的活动 ID 列表（每期往里加一个）
      ↓
2124 drop（如 21242156）:
  A_STR_action = fes_actv_bp_extra      ← 与常量同名
  A_MAP_drop = {...}                    ← 宝箱掉落内容（single_random + noget 保底）
```

---

## 七、已知约定与坑点

1. **弃用标记**：B列活动名含"弃用"的不要修改
2. **JSON 字段**：写入时必须保留完整 JSON 格式
3. **行号偏移**：`+read` 时表头在第1行，数据从第2行开始
4. **主页签判定规则**：
  - 同时存在 QA 和 master 页签时，使用 **QA 页签**（master 已弃用不再维护）
  - 页签名与表名相同的通常就是主页签（如 `activity_drop`、`activity_battle_pass`）
  - 以版本号、节日名、功能名命名的页签是临时副本，不是主页签
5. **cross_progress 必填**：BP 活动中 `cross_progress` 组件**必须填写**集结礼包的 2011 ID。若不填，玩家首次进入集结奖励界面时不会显示礼包入口，需第二次拉取活动数据（再次进入活动）才会显示
6. **21127638 模板废弃组件不可删除**：该模板及其轮换副本中，`fes_module` 和 `bp_rank_item` 已废弃，但仍**必须保留**在组件列表中，删除会导致客户端界面错乱
7. **节日 BP 活动 — 集结礼包 ID 必须新建**：每期活动的集结礼包（`cross_progress` 关联的 IAP）必须新建 2011 + 2013 ID，**不可复用**已有的。原因：服务器判断付费集结奖励资格时，检测的是玩家**历史上**是否购买过该礼包，而非活动期间内是否购买。复用会导致上期买过的玩家本期不买也能领奖
8. **节日 BP 活动 — 通行证礼包可复用但需检查**：2 个通行证礼包（初级/高级）一般复用之前已有的 ID（通常是去年的，或名称带"通用"字样的）。复用时需注意：
  - 修改 2011 表的备注名称，避免混淆
  - 检查 2011 表的 `A_MAP_time_info`，确保绑定了当期活动 ID，否则老玩家以前购买过的记录不会刷新
9. **节日 BP 活动 — 道具复用与一致性检查**：通行证解锁道具、BP 经验道具可以复用。但配置完成后需全面校验 2130 配置、礼包配置等所有引用的道具 ID 是否一致
10. **页签确认**：用户未指定页签时必须先询问
11. **gws 输出过滤**：管道给 Python 前需 `grep -v "Using keyring"`
12. **数据量大的表**：读取时尽量指定列范围，避免超时
13. **单元格备注**：配置表的表头或数据单元格可能包含备注说明（Google Sheets Notes），可通过 `gws sheets spreadsheets get --params '{"spreadsheetId":"...","ranges":["Sheet!Cell"],"fields":"sheets.data.rowData.values.note"}'` 读取
14. **图标一致性追踪链**：新增或修改活动道具时，需检查以下图标引用链是否一致：
  - `1111.C_INT_display_key` → `1511 display_key` 表中的图标资源
    - `2112.A_INT_icon_displaykey` → `2168 activity_hud_entries` 表中的 HUD 图标
    - `2112.A_INT_show_hud` → `2168` 表中的活动入口图标
    - 同一活动/道具在不同位置引用的图标应保持一致，避免玩家看到不匹配的图标
15. **背包双清空规则**：如果道具不应出现在背包中，需要同时清空 `1111.C_ARR_display_labels` 和 `1111.A_ARR_use_labels`，只清一个会导致道具仍然在背包中可见或可操作
16. **2111 活动日历必须配置**：在 2112 表中新建活动后，必须在 2111 `activity_calendar` 表中新增对应行，否则后台无法开启该活动。`A_INT_activity_id` 指向 2112 的活动 ID
17. **导出报错定位**：配置表导出时的 JSON 报错（如 `json error on row X col Y`）中的行列号可能包含表头偏移。`row` 通常指 Google Sheet 中的行号（含表头），`col` 对应列索引（从0计数），需结合具体导出工具逻辑判断
18. **`gws +read` 的 values index ≠ sheet 物理行号**：读整列 `!A:A` 再 enumerate 出来的索引，可能和 sheet 真实行号偏移（空行被 API 过滤掉时会）。**写入前**务必用 id 精确校对，例如再用窄 range `!A{N-3}:A{N+3}` 复核；**写入后**立即用 id 回读验证。本项目曾把 21127651 的 5 个字段改动误写到了 21127649（圣诞签到）行上，就是这个偏移坑。
19. **`moveDimension` 会重编行号**：移动新行到指定位置后，source→destination 之间的所有行物理行号都会变（内容跟着走）。move 完再验证时必须用新行号读。
20. **TSV 列号看 header 列数，不要按少量样本猜**：2013 `iap_template_QA` header 有 31 列（中间夹了 `A_STR_pkg_desc` / `S_INT_limit_whitelist` / `A_INT_all_value` 等），容易低估成 10 列。单元格 update 前用 `gws sheets spreadsheets get ... fields=sheets(properties(title))` 或读 A1 整行获取准确列名-字母映射；**整行覆盖写**（一次写 A:AE）比挑列写更安全。
21. **写入 JSON 用紧凑格式**：`json.dumps(x, ensure_ascii=False, separators=(',',':'))`。默认 `{"a": 1}` 带空格和表里历史格式 `{"a":1}` 不一致，会污染 TSV diff。
22. **策划表里道具 id 可能有笔误**：自选宝箱 / 保底特效 等常跨节日沿用同 id 段，策划复制粘贴时经常错（如 111110264 是复活节、111110325 才是拓荒节）。**所有 item id 自己 grep 1111 表核实**，不要依赖策划的注释。
23. **`A_INT_country_use_type` 列隐形**：该列在 sheet 里有，但导出脚本会按官方 `split_cfg_sheet` 逻辑**删除并按值分组**。排查 TSV "全表 diff" 时首先看是不是 header 多了这一列（说明脚本没做 split）。
24. **"只提交自己的改动"做法**：如果 sheet 里积累了别人未导出的增量，导出后 TSV 会同时带我的 + 别人的改动。用 Python 按 `A_INT_id` 过滤：属于自己的 id 行保留新值；别人修改的 id 行回填 HEAD 版本；别人新增的 id 行丢弃。保留新 TSV 行顺序 + 原 header，git diff 最干净。

---

## 八、付费道具单价表

> 数据来源：`1WXygIfKtLtK-TmZmIVZaVuu_LhfE6fSesRpp7KhgSPc`，页签 `付费道具价值`

### 8.1 基础单价（美元/个）

| 道具 | 单价（$） |
| --- | --- |
| CD（光碟） | 0.003992 |
| 1分钟加速（通用） | 0.007561 |
| 1分钟加速（城建） | 0.007561 |
| 1分钟加速（科研） | 0.007561 |
| 1分钟加速（训练） | 0.007561 |
| 1分钟加速（治疗） | 0.007561 |
| 1分钟加速（基因加速） | 0.006048 |
| 粮食 | 0 |
| 钢铁 | 0 |
| 电池 | 0 |
| 高级奖池抽奖券 | 1.00 |
| 通用碎片（橙） | 2.50 |
| 指定碎片（橙） | 1.25 |
| 1英雄升星经验（金/橙） | 0.00998 |
| 1英雄升星经验（紫） | 0.001426 |
| 1英雄升星经验（蓝） | 0.000713 |
| 英雄经验 | 0.000008317 |
| 幸运币 | 0.50 |
| 高级探测抽奖券 | 0.50 |
| 收藏品-橙色升星道具-传说 | 0.50 |
| 1基因片段 | 0.00008317 |
| 军备零件箱 | 0.03 |
| 军备图纸 | 0.83 |
| 光谱芯片 | 0.003992 |
| 紫色装备图纸 | 1.00 |
| 橙色装备图纸 | 2.50 |
| 装备材料-合金零件 | 0.000998 |
| 装备材料-涂料 | 0.000998 |
| 装备材料-精密纤维 | 0.01996 |
| 装备材料-纳米材料 | 0.25 |
| 1体力 | 0.001610 |
| 兵种技能升级材料-能量剂 | 0 |
| 兵种技能升级材料-训练检测仪 | 2.00 |
| 合成挖矿-时光药水 | 0.3590 |
| 合成挖矿-研究药水 | 0.000479 |
| 机甲经验 | 0.000008317 |
| 机甲增强芯片-紫 | 0.50 |
| 机甲手册 | 0.20 |
| 机能核心 | 0.62375 |
| 资源任选 | 0 |
| 多成长线自选宝箱（价值$2） | 2.00 |
| 超凡-多成长线自选宝箱（价值$2） | 2.00 |
| 通用机甲芯片 | 1.6633 |
| 神经增强剂-橙 | 1.00 |
| 战车升级道具 | 0.33 |
| 战车突破图纸 | 1.66 |
| 训练检测仪 | 1.66 |
| 能量剂 | 0.16 |
| 猩战手册 | 3.20 |
| 高分子材料 | 2.00 |
| 重铸矿晶 | 1.00 |
| 高级重铸矿晶 | 3.33 |
| 金刚机甲芯片 | 1.00 |
| 装饰券 | 0.10 |
| 收藏品-红色升星道具-超凡 | 0.80 |
| T6军备养成-高分子材料 | 2.00 |
| 装备突破材料-晶体元件 | 2.00 |
| 弹珠抽奖道具 | 1.00 |
| 打拳体力 | 0.60 |
| 普通大富翁骰子-漫游骰子 | 0.50 |
| 异族大富翁骰子-普通 | 0.50 |
| 异族大富翁骰子-自选 | 0.50 |
| 探宝抽奖道具 | 0.20 |
| 节日道具自选箱 | 1.00 |
| 挖孔道具-核心破译器 | 0.20 |
| 节日BP经验道具 | 0.10 |
| 推币机 | 0.10 |
| 强消耗抽奖券 | 0.50 |

### 8.2 衍生换算规则

游戏内的加速/经验道具以不同规格出现，需要按时间或数量换算：

**加速类（基准：1分钟 = $0.007561）**

| 游戏内道具名 | 分钟数 | 单价（$） |
| --- | --- | --- |
| 5分钟加速 | 5 | 0.0378 |
| 10分钟加速 | 10 | 0.0756 |
| 15分钟加速 | 15 | 0.1134 |
| 30分钟加速（通用/建筑/科研/训练） | 30 | 0.2268 |
| 60分钟加速（通用/建筑/科研/训练） | 60 | 0.4537 |
| 2小时加速 | 120 | 0.9073 |
| 3小时加速 | 180 | 1.3610 |
| 8小时加速 | 480 | 3.6293 |

**英雄升星经验（基准：1点橙色 = $0.00998）**

| 游戏内道具名 | 经验点 | 单价（$） |
| --- | --- | --- |
| 英雄升星-橙色-小-100点经验 | 100 | 0.998 |
| 英雄升星-橙色-中-400点经验 | 400 | 3.992 |
| 英雄升星-紫色-小-100点经验 | 100 | 0.1426 |
| 英雄升星-紫色-中-400点经验 | 400 | 0.5703 |

**VIP经验**：与 CD 等价，$0.003992/点

**零价值道具**：粮食、钢铁、电池、资源任选、能量剂 → $0

**不计价道具**：联盟礼物触发、活动专属UI道具（无游戏内交易价值）

---

## 九、实战补充：联动礼包 / 主城皮肤 / 通用 SOP（liusiyi 视角）

> 前八节是同事 sunminghao 的全量配置知识库（认证账号 sunminghao@nibirutech.com）。
> 本节是 liusiyi (happyfactory.com) 在 P2 节日活动配置实战中（联动礼包 + 主城皮肤为主）累积的踩坑沉淀，作为对前八节的补充。
> 适用范围：行军表情/行军特效/联动/头像框 4 种联动包型 + 主城皮肤套装 + 节日 BP/累充等关联活动。

### 9.1 通用 SOP（任何 P2 配置任务都要遵守）

#### 9.1.1 查值永远以 QA Sheet 为准，不信 gdconfig tsv

任何"现在表里是什么值"的调研、诊断、复用任务，**第一步一定 `gws sheets spreadsheets values get` 读 QA 主页签**。`/Users/marinl/gdconfig` 的 tsv 是某次合并快照，**可能落后多个节日版本**。

**实锤**：2026-04-24 配拓荒节挂机 BP，gdconfig fo 里 2131 bp_id=21301529 的 pay_rewards 显示是科技节道具（11112127 聚能环），但 QA Sheet 真实值已被替换成万圣节 + 登月节道具（11112306/11112582）。按 gdconfig 推会整个走错方向。

`gdconfig tsv` 只在 **push 导表**（`p2-gdconfig-push`）时作为 diff 目标，不是事实源。

#### 9.1.2 新行以参考行为模板 patch（禁止从零 hardcode）

写 2112 / 2135 / 2121 / 2011 / 2013 / 1111 / 1180 / 1168 / 1511 / 2111 等任何新行时：

1. 先读 1~2 条**同类型**真实参考行（QA 主页签）
2. 以参考行为基础，**只覆写必换字段**（ID / constant / comment / 组件 id / 回指 id / filter.id …）
3. 未显式 patch 的字段自动继承参考行

**禁止从零 hardcode**——P2 字段空值约定复杂：

- `A_STR_*` / `S_STR_*` 空值 = 字面量 `""`（不是空 cell）
- `A_MAP_*` 空值 = `{}`
- `A_ARR_*` 空值 = `[]`
- 部分字段空值 = 字面量 `NULL`
- JSON 字段必须紧凑无空格（`json.dumps(obj, separators=(",",":"), ensure_ascii=False)`）

从零写几乎一定违反某条约定。已踩过：`S_STR_banner_obj_url` 误写为空 cell。

#### 9.1.3 QA 写入必按 ID 前驱插入（禁止 values.append）

新行必须**精确**落在"小于 new_id 的最大 ID 所在行 + 1"，**禁止 `values.append` 到表尾**——P2 表 ID 不是全局单调排序：

- 2112：21128001（占位符）位于 21129003（节日行）之后
- 1111：111111025（头像框）在 111110339（特效）之前

```python
def find_insertion_row(values, new_id):
    ids = [(int(r[0]), i+1) for i, r in enumerate(values) if r and r[0].isdigit()]
    preds = [(i, r) for i, r in ids if i < new_id]
    if not preds: raise RuntimeError("new_id 比所有现存 ID 都小")
    return max(preds, key=lambda x: x[0])[1] + 1
```

后续：`batchUpdate({insertDimension: {startIndex: target-1, endIndex: target}})` 开空行 → `values.update(range=f"{tab}!A{target}", ...)` 写入。

#### 9.1.4 资源链路必须全链路闭环

不能只配主链路 `2112 → 组件 → 2011 → 2013`，每个被引用的 id 都必须在对应表里**真实存在**。

- 2013 里所有 `item_id` 必须在 1111（主页签）真实存在
- 美术资源（1365 / 1180 / 1511 / 1142 / 1173 / 1312 / 1388 / 1387 …）**直接新建即可**，不要采用"等美术出新资源再替换"的保守策略——AI 应基于同类已有行做"对照复用 + 逻辑新增"
- **永久版位置铁律**：行军特效套 1365 的 `A_ARR_items` 共 6 个时长版本，**最后一个是永久版**，礼包主外显 `A_ARR_other_items` 用永久版 id（不是首位）
- 配完跑 `scripts/check_refs.py` 深度校验，缺失为 0 才算通过
- **禁止让 1111/资源表指向别节日的资源 id**（破坏"每节日独立资源"约定）

#### 9.1.5 配节日活动必须同步配 2111 调度层

2112 = 配置定义；**2111 = 运行时激活调度**，缺一会 fan-out 出 3 类 bug：

- 主页「前往」按钮找不到 instance（点击无反应）
- 子页签数据拉不到（奖励项显示占位/异常）
- QA 直接开"缺配置行"工单

2111 行 9 列必须齐：

```
A_INT_id / A_INT_activity_id / S_STR_comment / S_MAP_server_info /
S_MAP_start_trigger / S_MAP_time_info / S_MAP_activity_group /
S_INT_data_cross / A_INT_country_use_type
```

**实锤**：拓荒节 2026 头像框礼包 2112/2135/2011/2013/1111/1142 全建，漏 2111 一行 → 同时开 3 个 Jira bug（P2DEV-142134/142135/142136）。

#### 9.1.6 2011 ID 默认从 2011610000 起

历史 `2011500xxx` / `2011400xxx` 段被占用。新建 2011 行（联动礼包 / 行军表情 / 行军特效 / 累充 / 任何 IAP 实例）从 **2011610000** 起，按顺序递增。动手前读 2011 主表，跳过已占号。

#### 9.1.7 TSV 写回保留原文件 trailing newline 状态

gdconfig 的 .tsv 文件**不保证末尾有 `\n`**，无脑补会触发无关行 diff（最后一行被当成被修改：`--- old 没 newline vs +++ new 有 newline`）。

```python
raw = path.read_text(encoding="utf-8")
trailing = raw.endswith("\n")
# ...modify lines...
path.write_text("\n".join(out_lines) + ("\n" if trailing else ""), encoding="utf-8")
```

已在 `fo/config/iap_template.tsv` push hotfix 2013101095-99 时踩过。`p2-gdconfig-push/scripts/patch_tsv.py` 已落地。

#### 9.1.8 写入后必须用 ID 回读验证

`gws +read` 读整列 enumerate 出来的 index 可能与 sheet 物理行号偏移（空行被 API 过滤），写入前用窄 range `!A{N-3}:A{N+3}` 复核 id 是否对齐，**写入后立即用 id 回读验证**。曾把 21127651 的 5 个字段误写到 21127649（圣诞签到）行——就是这个偏移坑。

`moveDimension` 后行号会重编，move 完再验证必须用新行号读。

### 9.2 联动礼包补充（4 种包型）

#### 9.2.1 包型分类

P2 联动礼包体系共 **4 种**，由 `p2-unite-gift-pack` skill 端到端调度：

| 包型 | 资源表 | 主外显 1111 class |
|---|---|---|
| 行军表情礼包 | 1180 map_emoji | `map_emoji` |
| 行军特效礼包 | 1365 marching_effect（含 6 时长版本，永久版在末位） | `marching_effect` |
| 联动礼包 | （无独立资源表，混合道具） | 多 class |
| 头像框礼包 | 1142 avatar_frame | `avatar_frame` |

**Scope 防越界**：这 4 种之外（BP / GACHA / 挖矿 / 累充 / 装饰物 / shop）**不归 unite-gift-pack 管**，要先反问用户类型。

#### 9.2.2 写奖励数组：通用 vs 节日专属（**必须对照确认**）

写 `2013.A_ARR_other_items` / `2121.A_ARR_reward` 时，**不能拿同节日另一种礼包的 id 平移过来**，必须对照**同类型礼包的多节日配置**：

- **通用道具**（科技节 = 情人节 = ... 同一个 id）→ 不换
- **节日专属道具**（每节日独立 id）→ 换成当季新 id

**P2 行军特效礼包 2013 other_items 通用/专属分类（2026 验证）**：

| 位 | 道具 | 类型 | 正确 id |
|---|---|---|---|
| [0] | XP | 通用 | `11161002`（永不换） |
| [1] | 主外显行军特效永久 | **节日专属** | 每节日独立 |
| [2] | 漫游骰子 | 通用 | `11112498`（永不换） |
| [3] | 自选箱 | **节日专属** | 每节日独立 |
| [4] | 多成长线自选宝箱 $2 | 通用 | `11118663`（永不换） |
| [5] | 联盟宝箱 4 | 通用 | `11114318`（永不换） |

**节日 BP 升级道具映射表（2026 全节日已查证）**——这一类道具视觉上像散装通用小物件，**实际是节日专属，必换**：

| 节日 | BP 升级道具 id | 名称 |
|---|---|---|
| 科技节 | `11112127` | 聚能环 |
| 情人节 | `11112408` | 夹心巧克力 |
| 复活节 | `11112091` | 魔术棒 |
| 拓荒节 | `11112150` | 纪念钻头 |
| 端午节 | `11112178` | 船桨 |
| 深海节 | `11112201` | 藏宝图碎片 |
| 万圣节 | `11112306` | 南瓜币 |
| 感恩节 | `11112334` | 感恩食材盒 |
| 圣诞节 | `11112356` | 幸运铃铛 |
| 春节 | `11112398` | 绣球 |
| 登月节 | `11112293` | 纪念胶卷 |
| 周年庆 | `11112226` | 欢乐气筒 |

> 验证规则：拿 id 去 1111 查 comment，含 "{节日}BP" / "{节日}通用" 字样 = 专属。

**真正通用不换的清单（2013 礼包 other_items 里）**：XP `11161002` / 漫游骰子 `11112498` / 多成长线自选宝箱 $2 `11118663` / 联盟礼物 2 `11114316` / 联盟礼物 4 `11114318`。这批之外的任何 item_id 都要进 1111 查 comment 确认。

#### 9.2.3 item_select_box 是外壳，节日道具藏在 select_box 内部

`class=item_select_box` 的 1111 道具是一层外壳，**真正的节日道具配在 `A_MAP_category_param.select_box` 数组里**。

判断"原 id 要换什么"：

1. 看到 `class=item_select_box` 必须深入读 `A_MAP_category_param.select_box`
2. 去**新节日自选宝箱**的 select_box 里找**同 class 对应物**（`battle_pass_exp` 换 `battle_pass_exp`，`event` 换 `event`）
3. 如果原 id 本身已经在新节日 select_box 里 → 跨节日通用，**不用换**

**实锤**：2026-04-24 配拓荒节挂机 BP，L1-4 的 `11112306`（南瓜币-万圣节）需要换成拓荒节版，但**直接搜"拓荒 2026"找不到对应 BP 升级道具**——魔术棒 `11112091` 藏在拓荒节自选宝箱 `111110325` 的 `select_box` 列表里。同数组里的 `11112498`（漫游骰子）也证明是跨节日通用、不用换。

#### 9.2.4 1168 高级行军特效跳转 ≠ 固定模板

1168 `get_access_group` 表里"{节日}-高级行军特效"行的 `C_ARR_access_group[0].args[0]`（跳转 2112 id）**不是固定模板**，由策划按当季节日的**主玩法活动**决定（挖孔 / 钓鱼 / BP / 大富翁 / …）。

**已知映射**：

| 节日 | 高级跳转 2112 id | 主玩法 |
|---|---|---|
| 科技节 / 复活节 | `21127575` | 挖孔 |
| 拓荒节 2026 | `21127700` | 钓鱼 |

**做诊断时**：发现 1168 高级行军特效跳到非挖孔活动 → **不要标红、不要自动改**，可以提示让用户确认。

**相对固定的是低级 1168**：必然跳"同节日的行军特效礼包 2112 id"（低级 = 礼包主卖的永久版）。

#### 9.2.5 联动礼包 skill 调度树

| 入口 / 触发词 | Skill | 职责 |
|---|---|---|
| **端到端**（"配 X 礼包" / "提配置"）| `p2-unite-gift-pack` | 4-Phase 全流程（配置→要图→翻译→落 QA） |
| 只看配置表结构 | `p2-unite-gift-config` | 字段模板 / ID 分配 / patch-from-ref |
| 中文文案 + 英文主译 | `p2-translation-style` | 10 类道具命名+描述风格库 |
| 18 语扩散 | `p2-translation-automatic` | 查重、术语库、生成 18 语 |
| 累充挂钩 | `iap-leichong-sync` | 2011.iap_status 填累充活动 id |

**默认行为（2026-04-17 起）**：`p2-unite-gift-pack` 默认**直接进 QA 主页签**；只有用户加"先写测试页签"才走测试页签路径。Phase 4 永远不自动合并。

#### 9.2.6 测试页签规则（如果走测试流）

1. **位置紧贴 QA**：新 sheet 的 `properties.index = main_idx + 1`，即 QA 主页签右侧。**禁止追加到末尾**——用户要频繁在 QA 和测试之间核对，滑到底翻很费劲
2. **字段一律写正式配置内容**：`A_STR_constant` / `*_STR_comment` / `N_STR_pkg_desc` / `N_STR_temp_desc` 等**所有字符串字段**取值等同上线时的值，不加 `_test` / `(测试)` 标识

> 测试页签 = "正式数据的预览位置"，不是"打草稿的地方"。原则适用于任何 `*_TEST_*` 测试页签。

### 9.3 主城皮肤补充（1312 + 1388 + 1389 + 1111）

> 注：这是和 §4.20 装饰物体系（2148+1118+1127+1111）**不同**的套装机制——主城套装不是"可建造可升级的装饰物"，而是**主城外壳的多组件视觉外显**（无星级、无市容度、无 buff 累计）。

#### 9.3.1 4 表分工

| 表 | 作用 | 粒度 |
|---|---|---|
| 1312 | 主城皮肤主体（低/高级两档） | 一套 = 2 行（低 + 高） |
| 1388 | 装饰件（外显组件，wing/cannon/effect/dragon/...） | 每件外显 1 行（**数量按美需变**） |
| 1389 | 套装清单 | `A_ARR_items` 列出该套包含的所有 1111 解锁 id |
| 1111 | 解锁/时限道具 | 每个组件 × 4 档（永久 + 3 档时限） |

#### 9.3.2 1388 装饰件数量**不固定**（关键铁律）

主城套装的 1388 装饰件数量**按该季美需决定**，不是"wing + cannon + effect" 3 件死模板。

**配套装前必须先问用户美术给了哪几件外显**，不要默认按战地套补齐。

- `C_INT_type` **不是死规则**（不是 1=wing / 2=cannon / 3=effect）
- type 跟着造型命名走（巨龙 = `dragon`，可占 type=1 位；没 cannon 就**不配** type=2）

**已知套装外显数量对照（2025-2026）**：

| 套装 | 装饰件 | 1389.A_ARR_items 长度 | 1111 条数 |
|---|---|---|---|
| 2025 科技节 / 深海节 / 周年庆 / 星球 / 2026 科技节战地套 | 3（wing + cannon + effect） | 5（低主城 + 高主城 + wing + cannon + effect） | 20（5 × 4 档） |
| **2026 拓荒节巨龙套**（特殊） | **2（巨龙 + 特效，无 cannon）** | **4（低 + 高 + 巨龙 + 特效）** | **16（4 × 4 档）** |

> 拓荒节巨龙套 2026-04-21 实锤：用户明确"不会补的，这次是特殊的"。AI 不要主动补 cannon。

#### 9.3.3 主城皮肤与装饰物体系（§4.20）的区分

| 维度 | 主城皮肤套装（1312/1388/1389） | 装饰物（2148/1118/1127） |
|---|---|---|
| 性质 | 外壳视觉换装 | 可建造的"装饰建筑" |
| 升级 | **无星级**（永久 + 时限档位）| 有星级，2148 按星级一行 |
| buff | 通常无 | citybeauty + buff（市容度 + 属性加成） |
| 入口 | 套装清单 1389 | 建造菜单 1127 |
| 1111 class | `city_skin` / `city_skin_ext` 等 | `statue_decorate` / `decorate_paint` |

诊断时不要把这两套体系搞混。

### 9.4 节日活动跨表扩散自检清单（联动礼包 / 主城皮肤场景）

新增任意节日活动后逐项过：

- [ ] **2112** 主配置（`A_ARR_activity_components` 各组件 id 段正确）
- [ ] **2111** activity_calendar 调度行（9 列齐，按 ID 前驱插入）
- [ ] **2135** 桥接（`A_INT_iap` → 新 2011 id）
- [ ] **2011** 礼包条件（`A_MAP_time_info` 绑定 actv_id；新 ID 从 2011610000 段起）
- [ ] **2013** 礼包内容（`A_ARR_other_items` 通用/专属对照 §9.2.2 表）
- [ ] **1111** 解锁/时限道具（class 正确 / `A_MAP_category_param.effect` 闭环）
- [ ] **资源表**（按包型补：1180 表情 / 1365 行军特效 6 时长 / 1142 头像框 / 1173 聊天铭牌 / 1312+1388+1389 主城皮肤 / 1387 主城特效 / ...）
- [ ] **1511** display_key 注册
- [ ] **1011** i18n（IAP / EVENT / ITEM 页签 LC key 补齐 18 语）
- [ ] **1168** get_access_group（高级跳转 = 当季主玩法 2112 id）
- [ ] **1388/1389 主城皮肤数量按美需**，不死板补齐
- [ ] 全链路 `check_refs` 通过（缺失引用为 0）
- [ ] 写入后用 ID 回读验证（防止 enumerate 偏移坑）

---

