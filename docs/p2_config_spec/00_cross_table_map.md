# P2 配置跨表关联图（00）

> **用途**：6 份规范 MD（10/11/13/19/20/21）的"出向/入向"总索引。诊断 bug、排查断链、理解一个 id 被谁用、改一个字段会影响谁——**先看这里**。
> **数据源**：基于真实 Google Sheets 抽样（2026-04-21）与 6 份 MD 综合绘制。
> **维护原则**：每条边必须标 `字段 / 类型 / 断链后果`；发现新边回写此图。

---

## 设计哲学（先读这段，下面九条主链都是推论）

整个 302 张表是 **三件事的叠加**：

1. **"可获得物"抽象**：无论行军特效、主城皮肤、头像框、英雄招募券、资源包，**全部先登记为一张 1111 item**。游戏侧统一按"道具"发放、持有、消耗。不在 1111 的东西玩家拿不到。
2. **"使用 item 的副作用"路由**：`1111.A_MAP_category_param.effect[].typ` 是路由枚举——它决定**用掉这个道具会激活哪张视觉/功能表**（map_emoji→1180 / marching_effect→1365 / city_skin→1312 / avatar_frame→1142 / nameplate→1173 / …）。typ 写错等于没效果。
3. **"前置条件" 通用 DSL**：全库 requirement / filter / fincond / triggers 共享一套 typ 枚举（building / iap / item / hero / vip / actvstart / schema / server_open_day / research / mecha_level / client_version / ...）。任何地方需要"门槛"都写这套 DSL，不新造语法。

记住这三件事，九条主链都是它们的投影。

---

## 六文件夹定位（诊断时先找文件夹）

| 文件夹 | 角色 | 枢纽表 | 体量 |
|---|---|---|---|
| **10 const** | 全库底座（i18n / 常量 / 开关 / 弹窗 / 渠道 / CDN / 埋点） | 1011 / 1013 / 1014 / 1020 / 1022 / 1023 | 20 表 |
| **11 asset** | 仓库（所有"可拿到的东西"） | **1111 item** ⭐（全库最核心）/ 1114 / 1115 / 1118 / 1119 / 1121 / 1168 | 72 表 |
| **13 map** | 世界（大地图 + 主城视觉件） | 1312 / 1365 / 1180 / 1389 / 1391 / 1317 / 1332 | 77 表 |
| **19 hero** | 英雄（自闭环子系统） | 1920 / 1924 / 1929 / 1935 | 32 表 |
| **20 iap** | 付费（IAP 三层 + VIP/累充/红包/BI） | 2011 / 2013 / 2014 / 2017 | 30 表 |
| **21 event** | 节日/活动（所有限时玩法的编排） | 2111 / 2112 / 2121 / 2135 | 71 表 |

**诊断顺序永远是**：症状 → 找文件夹 → 找该文件夹的 MD（`N_p2_xxx.md`）→ 读底部的 "Jira 自检路径表"。

---

## 三种"隐蔽"引用（bug 最高频来源）

| 记号 | 含义 | 真实例子 | 为什么容易漏 |
|---|---|---|---|
| **[ENUM]** typ 路由 | 一个字段的 typ 枚举决定去哪张表 | `1111.category_param.effect.typ=marching_effect` → 1365；换成 `=map_emoji` → 1180 | 字段名不变，目标表变 |
| **[EMBED]** 嵌入式 id | id 写在 JSON 字符串里，不是独立字段 | `1111.A_ARR_use_labels` 里嵌 `"13650155"`；`2011.A_INT_iap_status` 嵌累充活动 id | grep 才能看到，肉眼扫表漏 |
| **[ARR+混装]** 数组混放不同表 id | 一个 ARR 字段里同时放多张表的 id | `1389.A_ARR_items=[13121063, 13881001]` (1312 皮肤 + 1388 装饰) | 不读业务含义看不出谁指谁 |

---

## 图例

| 记号 | 含义 |
|---|---|
| `A → B` | A 引用 B（A 的某字段存 B.id） |
| `B ← A` | B 被 A 引用（同上反向读法） |
| `[ARR]` | 引用是数组，一个 A 可指多个 B |
| `[MAP]` | 引用在 MAP 的某 key 里 |
| `[EMBED]` | **嵌入式 id**（写在 JSON 字符串里，不是单独字段，易漏） |
| `[ENUM]` | 通过 `typ` 枚举路由到不同 B 表 |
| ⚠️ | 高频 bug 断链点 |

---

## 主链 1：节日活动端到端（21 → 10 + 11 + 13 + 20 全串）

```
┌─ 1022 function_switch (10) ──[前置开关]──┐
│                                           │
1011 i18n (10) ←──[LC key, 全表]            │
1023 popwindow (10) ←──[2112.popwindow_id]  │
                                            ▼
2111 activity_calendar (21)  ──[A_INT_activity_id]──► 2112 activity_config (21) ⭐ 主表
     └ 触发时机 / server_info                              │
                                                          │ A_ARR_activity_components[typ]
           ┌──────────────────────────────────┬───────────┼──────────────┬──────────────┐
           │                                  │           │              │              │
      typ=task                           typ=exchange  typ=rank     typ=rank_reward  typ=pkg
           │                                  │           │              │              │
           ▼                                  ▼           ▼              ▼              ▼
      2115 task (21)                     2116 exch   2122 rank_rule  2118 rank_rwd   2135 package (21) ⭐
      fincond→1014 counter (10)         ────────    score→1014        reward→1111      │
                                                                                       │ A_INT_iap_status
      typ=chest/mysterious_trace/                                                      ▼
          unite_pkg/emoji_show/discount  ──────────► 2121 activity_special (21)   2011 iap_config (20)
                                                    （兜底表，非 task/rank/pkg 全进这）  │ A_INT_iap_status
      typ=drop  ──► 2124 activity_drop                                                 ▼
      typ=retake ──► 2137 activity_asset_retake                                   2013 iap_template (20) ⭐
      typ=bp    ──► 2130 activity_battlepass                                           │ A_ARR_get_items
      typ=puzzle/shoot_hunt ──► 2146/2139                                              │ A_ARR_other_items
                                                                                       ▼
                                                                                  1111 item (11) ⭐
                                                                                       │ effect.typ [ENUM]
                                       ┌───────────┬───────────┬──────────┬────────────┼───────────┐
                                       ▼           ▼           ▼          ▼            ▼           ▼
                                  1114 rss (11)  1180 emoji  1365 march  1312 city  1142 avatar  1173 chat
                                                 (11)         (13)        (13)       frame (11)  skin (11)
                                                                │
                                            ┌───────────────────┼────────────┐
                                            ▼                   ▼            ▼
                                       1391 suit (13)    1512 effect_list  1511 display_key
                                       ← 1390 deco       (13)              (全局,10/11/13 都用)
```

**⚠️ 高频断链点**：
1. **2135.A_INT_iap_status → 2011 不存在**：礼包按钮灰 / 买完不发货
2. **2013.A_ARR_get_items 的 item id → 1111 不存在**：买了收不到
3. **1111.effect[].id → 1365/1180/1312 不存在**：收到了但背包/行军无外观
4. **1365.C_INT_effect_key → 1512 不存在**：行军出黑框
5. **2112.components[].id → 2115/2135 不存在**：模块整块失败
6. **2111 时间 → 2112 `A_INT_start_trigger` 不对齐**：活动不开或提前关

---

## 主链 2：IAP 三层 + 跨表联动

```
2011 iap_config (20) ⭐ 商品实例（每个 SKU）
     │ A_INT_iap_status / A_INT_template [EMBED]
     ▼
2013 iap_template (20) ⭐ 礼包模板（可复用）
     │ A_ARR_get_items      → 1111 item (奖励)
     │ A_ARR_other_items    → 1111 item (折扣/双倍提示)
     │ A_STR_product_id     → App Store / Google Play 配置
     ▼ 被 2135.A_INT_iap_status 挂载回活动

其它引用 2013 的上游：
  · 2017 VIP.special_offer / special_monthly   → 2013 [ARR]  VIP 专属礼包
  · 2034 mecha_achievement.A_INT_iap           → 2013        机甲成就礼包（注意：这里字段名叫 iap）
  · 2035 iap_pop_first.A_INT_iap_id            → 2013        破冰弹窗  （这里字段名叫 iap_id，**历史命名不一致**）
  · 2036 time_card_reward                      → 2013        时间卡
  · 2016 cumulative                            → 2013        累充每档礼包
  · 2019 red_packet                            → 2013        红包
  · 2030 bi_offer                              → 2013        BI 智能推荐
```

**⚠️ 断链点**：
- 2034 `A_INT_iap` vs 2035 `A_INT_iap_id` 名字不一致，跨表查询要双查
- 2013.product_id 在 AppStore 后台没录 → 真实玩家付费 pending 但不到账（跨系统断链）

---

## 主链 3：主城皮肤体系（13 核心 + 11）

```
1312 city_skin (13) ⭐ 主城皮肤实体
   │ A_ARR_items         → 1111 item [ARR]   解锁道具（付费拥有的是 1111 item）
   │ A_INT_suit_id       → 1389 套装（若为套装件）
   │ status_active       穿戴 buff
   │ skin_level          基地等级梯度
   ▲
   │ 1111.item.effect.typ = "city_skin" 激活
   │
1389 city_suit (13) 套装集合
   │ A_ARR_items   [13121063,13121064,13881001,13881002,13881003]  （**皮肤件 1312 + 装饰件 1388 混装**）
   │ A_INT_suit    = 13121065  （集齐后激活的**底座皮肤 id**，指向 1312）
   │ status_active 集齐穿戴 buff
   ▲
   │ 1388 city_suit_decoration.A_INT_suit_id → 1389  （装饰件反挂回套装）
   │
1387 city_effect (13) 主城特效
   │ C_INT_effect_key   → 1512
   │ A_INT_suit_id      → 1389（部分节日套装带特效）
```

**⚠️ 断链点**：
- 1389.A_ARR_items 漏配某装饰件 → 玩家收齐了但"差一件"，羁绊不触发
- 1389.A_INT_suit 指向的 1312 不存在 → 集齐瞬间变默认皮肤
- 1312.skin_level 漏基地等级 → 高级主城变默认
- 1111.item 的 effect.typ 写成 `skin` 而非 `city_skin` → 付费 item 到手但穿不上

---

## 主链 4：行军特效体系（13 核心 + 11 + 全局）

```
1365 march_effect (13) ⭐ 行军特效实体（单件）
   │ C_INT_display_key         → 1511 display_key (全局)
   │ C_INT_effect_key          → 1512 effect_list  普通特效
   │ C_INT_effect_special_key  → 1512              特殊特效（集齐后）
   │ C_INT_effect_exhibit_key  → 1512              展示用
   │ A_ARR_status_active       穿戴 buff 12xxx
   │ A_ARR_items               → 1111 item [ARR] 解锁道具
   │ A_INT_suit_id             → 1391 套装
   ▲
   │ 1111.item.effect.typ = "marching_effect" 激活
   │
1391 march_effect_suit (13) 行军特效套装
   │ A_ARR_items   [1365件 id + 1390装饰件 id 混装]
   │ A_INT_suit    基础 1365 id
   ▲
   │ 1390 march_effect_decoration.A_INT_suit_id → 1391  （装饰件反挂回套装）

1111.A_ARR_use_labels [EMBED]：
   └ 字符串形式嵌入 1365 套 id（换节日时必须跟改，**易漏**）
```

**⚠️ 断链点**：
- 1365.effect_key → 1512 不存在 → 行军出黑框
- 1391.A_ARR_items 缺 1365 或 1390 的某个 id → 集齐不羁绊
- 1111.A_ARR_use_labels 嵌入的 1365 id 不换节日 → 跨节日混淆

---

## 主链 5：行军表情体系（11 + 13 + 21）

```
1180 map_emoji (13/11) ⭐ 行军表情实体（12 列，含 year_group）
   │ A_INT_year_group    节日年度分组
   │ display_key         → 1511
   ▲
   │ 1111.item.effect.typ = "map_emoji" 激活
   │
1393/1394 emoji_collect (13) 表情集卡
   │ A_ARR_items  → 1111 item [ARR]  该年所有 emoji item
   │ A_INT_max_number  集卡阈值
```

**⚠️ 断链点**：
- 1393/4 的 A_ARR_items 长度与 A_INT_max_number 错位 → 奖励达成错位
- A_ARR_items 的 year_group 不一致 → 收集数错算

---

## 主链 6：头像框 / 铭牌 / 旗帜（11 独立视觉件）

```
1142 avatar_frame (11)  ← 1111.effect.typ="avatar_frame"
1143 flag (11)          ← 1111.effect.typ="flag"
1173 chat_skin/nameplate(11) ← 1111.effect.typ="nameplate"
1144 poster (11)        ← 1111.effect.typ="poster"

A_ARR_unlock_cost [EMBED]：嵌入 1111 item id（付费解锁道具）
```

---

## 主链 7：道具入口中枢（11 内部）

```
1111 item ⭐
   │ A_INT_source / A_INT_get_access_group  → 1168
   ▼
1168 get_access_group  （**杜绝手搓**，ID 插件专查表之一）
   │ C_ARR_access_group  [{"id":1153xxxx,"args":[...]}]
   ▼
1153 access_item (11)  具体入口条目（"去活动页" / "去商城" 等）
   │ args 可以是 1111/1114/2112/2011 任意 id（按 1153 条目语义）
```

**⚠️ 断链点**：
- 新道具漏登记 1168 → 背包点"问号"无跳转
- 1168 的 access_group.args 传错 id 类型 → 跳转目标错

---

## 主链 8：英雄体系（19 内部自闭环 + 11/20 入口）

```
1920 hero (19) ⭐ 英雄主表
   │ A_ARR_skill   → 1924 技能 [ARR]
   │ A_ARR_talent  → 1923 天赋树 [ARR]
   │ A_ARR_skin    → 1950 皮肤 [ARR]
   ▼
1924 skill → 1925-1928 技能效果/词条（6 表联动，**最脆弱**）

招募：
1929 gacha_pool.drop.group  → 1930 gacha_reward.group  [一对多]
     └ 1931 保底规则

装备：
1935 equip → 1936 level_group → 1937 word_buff → 1938 entry
1111 item.effect.typ="hero_exp" / "hero_fragment" → 1920  (被 11 入口引用)
```

---

## 主链 9：前置条件表达式（全表通用，10 定义）

**所有 requirement / filter / fincond / triggers / showcond 的 typ 枚举**（见 [`10_p2_const.md#requirement`](./10_p2_const.md)）：

| typ | 指向表 | 典型用法 |
|---|---|---|
| `actvstart` / `actvend` / `actvstarttime` | 2112 | 活动开启/结束/已开始 |
| `actvtask` / `iap_actvtask` | 2115 | 活动任务完成 / 礼包关联任务完成 |
| `event` | 2121 | 事件活动 |
| `schema` | 服务器 schema | 服白名单 `"id":schema编号` |
| `building` | 1118 | 建筑等级 `"id":111811,"val":6` = 要塞≥6 级 |
| `iap` | 2011 | 购买记录 |
| `iap_purchases` | 2011/2013 | 已购买礼包 `"id":礼包id,"val":1`（BP 集结礼包付费奖励常用） |
| `item` | 1111 | 持有道具数 |
| `hero` | 1920 | 招募状态 |
| `hero_extra_talent_unlock` | - | 英雄额外天赋解锁 |
| `vip` | 2017 | VIP 等级 |
| `tvp` | 1145-1148 | 酒馆 |
| `function_unlock` | - | 功能解锁 |
| `research` | 1119 | 科研等级 `"id":科研id,"val":等级` |
| `tank_unlock` | - | 载具解锁 |
| `abtest` | - | AB 测试分组 `"id":测试id,"val":1` |
| `total_pay` | - | 累计付费 |
| `client_version` | - | 版本号（用 `arg2` 传值，**不是 val**） |
| `server_open_day` | - | 开服天数 |
| `mecha_level` | - | 机甲等级（id=品质, val=等级） |
| `in_ubattle_war` | - | 在跨服战中 |
| `building_start` / `situation_start` / `metro_small_level_event` | - | 触发用（非过滤用） |
| `bi_kvk_heal_speed` / `bi_kvk_train_speed` | - | KVK 治疗/训练加速（BI 触发） |

**复合条件**（and/or 嵌套）：
```json
{"op":"and","args":[
  {"op":"ge","typ":"building","id":111811,"val":5},
  {"op":"ge","typ":"actvtask","id":211562067,"val":1}
]}
```
运算符 `op`：`ge`(≥) / `le`(≤) / `eq`(=) / `ne`(≠) / `lt`(<) / `and` / `or`。

**⚠️ 最高频 bug**：typ 用错（`actvend` 想做"开启中"）、id 用错系（2112 vs 2121 常混）、client_version 用 val 不用 arg2、BP 集结礼包付费奖励的 `iap_purchases.id` 填 2011 而非 2013。

---

## 独立玩法表（非 components.typ 挂载，自闭环）

| 表 | 用途 | 入口 | 关键引用 |
|---|---|---|---|
| 2117 item_recycle | 活动道具回收 | A_INT_group | item_id→1111, reward→1111 |
| 2148 festival_decoration | 节日装饰 | activity_id→2112 | → 1312/1365/1387 |
| 2151 monopoly | 大富翁 | activity_id→2112 | 格子奖→1111 |
| 2159 festival_popwindow | 节日弹窗 | activity_id→2112 | banner→1020, jump→2112 |
| 2174 dighole | 挖孔 | activity_id→2112 | 关卡→自表，奖→1111 |
| 2176 fishing | 钓鱼 | activity_id→2112 | 同上 |
| 2034 mecha_achievement | 机甲成就礼包 | fincond=mecha_level | iap→2013 |

这些表**不走** 2112.components.typ 路由，但会通过 `A_INT_activity_id` 或 `A_MAP_requirement.typ=actvstart` 绑定到 2112。

---

## 废弃/历史表（查到不要用）

| 表 | 状态 | 替代 |
|---|---|---|
| 2113 activity_schema | 废弃 | 并入 2112 |
| 2123 activity_popwindow | **真实表名含"弃用"** | 节日弹窗改走 2159 |
| 2117（部分 group） | comment 标"弃用" | 视情况仍在用 |

---

## 跨文件夹边汇总（一个 id 被哪些表引用）

> 用于改一个 id 前反查"会打断谁"。

| id 所在表 | 被下列表引用（A_ARR/MAP 类） | 断链后果 |
|---|---|---|
| 1011 i18n LC key | 几乎所有表的 lc_name/lc_desc/name/desc | 文案显示原 key |
| 1111 item | 2013/2135/2115/2116/2124/2137/2174 等 40+ 表 | 发奖不到账 |
| 1114 rss | 1111.effect / 2013.get_items | 资源加不上 |
| 1168 access_group | 1111.source / 1111.get_access_group | 问号无跳转 |
| 1312 city_skin | 1389.items / 1389.suit / 1111.effect | 皮肤不显示 |
| 1365 march_effect | 1391.items / 1391.suit / 1111.effect / 1111.use_labels[EMBED] | 特效黑框 |
| 1180 map_emoji | 1111.effect / 1393.items / 1394.items | 表情不触发 |
| 1511 display_key | 所有视觉表（1365/1312/1387/1142 等） | UI 图标丢 |
| 1512 effect_list | 1365.effect_key / 1387.effect_key | 美术特效路径断 |
| 2011 iap_config | 2135.iap_status / requirement.typ=iap | 礼包按钮灰 |
| 2013 iap_template | 2011 / 2017.special_offer / 2034 / 2035 / 2036 / 2016 / 2019 / 2030 | 付费模板断 |
| 2112 activity_config | 2111 / 2135 / requirement.typ=actvstart / 2148/2151/2159/2174/2176 | 活动整块不亮 |
| 2115 task | 2112.components(typ=task) | 任务不计数 |
| 2121 activity_special | 2112.components(典型兜底) | 节日玩法模块失败 |
| 2135 activity_package | 2112.components(typ=pkg) | 付费墙找不到礼包 |

---

## 图的维护

- **新增一条边**：回写对应主链段落 + 底部"跨文件夹边汇总"表。
- **废弃一条边**：移入"废弃/历史表"，保留历史但标明。
- **真实表与本图冲突**：**以真实表为准**，gws 验证后回写本图（记录日期）。
- **本图被 skill `p2-config-diagnosis` 软链引用**（如需）。

---

_基于 2026-04-21 真实 Google Sheets 抽样复核生成。下次重大改表（新增节日模块/废弃表）时重跑一遍抽样验证。_
