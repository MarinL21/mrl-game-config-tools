# 10_p2_const 常量配置规范

> **用途**：P2 全库"常量类"配置，包含 i18n、全局常量、格式化、AB 测试、功能开关、弹窗、渠道、版本等。业务代码通过 `A_STR_constant` 或 `A_INT_id` 读取。
>
> **Drive 路径**：`游戏运营策划 > 10_p2_const` 文件夹
> **Jira 自检场景**：弹窗顺序错乱 / 文案显示 key / AB 分桶异常 / 功能开关不生效 / 国服海外分支走错 / 海报图素材 404。

---

## P2 全库通用字段前缀约定（所有表通用）

### 字段名前缀（第 1 段）

| 前缀 | 含义 | 下发客户端 | 说明 |
|---|---|---|---|
| `A_` | Active（策划主配） | ✅ | 主字段，前后端都能读 |
| `S_` | Static（静态策划配） | ❌ 仅服务端 | 仅后端读取，客户端看不到 |
| `C_` | Client（客户端展示） | ✅ 仅客户端 | 仅前端用，后端不读 |
| `N_` | Note（备注） | ❌ | 纯注释字段，构表时剥掉 |

**bug 信号**：如果前端反馈"字段读不到"——先看前缀是不是 `S_`；反之后端取不到看是不是 `C_`。

### 字段名中段（第 2 段）= 数据类型

| 中段 | 类型 | 空值 | 常见 bug |
|---|---|---|---|
| `INT_` | int64 | `0` | 写了字符串会导表失败 |
| `FLT_` | float | `0.0` | 整数 10 和浮点 10.0 运行时都 OK，但 CR 会告警 |
| `STR_` | 字符串 | `""`（**双引号**） | 空字符串必须 `""`，写成空会变 `null` 破坏下游 |
| `ARR_` | 数组 | `[]` | 空数组必须 `[]` 不能留空 |
| `MAP_` | 对象 | `{}` | 空对象必须 `{}` |

### ID 号段规律

- **表号前 4 位** + **千位子号段** + **自增 4 位**
- 例：`10131003` = `1013`(const_config) + `1`(第一子号段) + `003`(第三条)
- 新节日/模块 ID 通常开新千位段，避免和历史 hot_const 冲突。

### 通用尾字段

| 字段 | 含义 | 枚举 | bug 风险 |
|---|---|---|---|
| `A_INT_country_use_type` | 区服开关 | `0=通用 / 1=海外 / 2=国服` | 国服-only 漏配 → 海外下发失败；0 + 2 同时配会双写 |
| `S_MAP_server` | 服务器方案白名单 | `{"typ":"schema","id":[1..17]}` | schema ID 遗漏某个新合服方案 → 该服不下发 |
| `S_MAP_filter` / `S_MAP_condition_player` | 玩家过滤条件 | `{"op":"and/or","args":[...]}` 或 `{"op":"ge/le/eq","typ":"...","id":...,"val":...}` | op 写反 / typ 拼错 → 条件恒真或恒假 |
| `A_MAP_requirement` | 前置条件（通用） | 同上 | 活动未开 → 入口不亮；活动 ID 写错 → 永远不亮 |

### `A_MAP_requirement` / `S_MAP_filter` 的 typ 枚举（高频 bug 区）

| typ | 含义 | 来源 id 指向 |
|---|---|---|
| `actvstart` | 活动已开启 | 2112 活动 id |
| `actvend` | 活动已结束 | 2112 活动 id |
| `event` | 事件活动 | 2121 事件 id |
| `schema` | 服务器方案 | 服务器 schema id |
| `building` | 建筑已建到等级 | 1118 建筑 id |
| `iap` | 购买过某 IAP | 2011 iap id |
| `pay_sign` | 付费签名 | - |
| `tvp` | 酒馆 | 1145/46/47/48 |
| `item` | 持有道具数量 | 1111 item id |
| `hero` | 英雄已招募 | 1920 hero id |
| `union` | 加入联盟 | - |
| `vip` | VIP 等级 | 2017 vip id |
| `client_version` | 客户端版本 ≥ 某值 | 用 `arg2` 传版本号字符串，如 `"0.65.0"` |
| `server_open_day` | 开服天数 ≥ val | - |
| `mecha_level` | 机甲等级 | `id` = 机甲品质，`val` = 等级 |
| `actvstate` | 活动阶段状态 | 2121 事件 id |

**常见 bug**：typ 写成 `actvend` 但想做"活动开启中"（应该 `actvstart`）→ 条件恒假；id 写成 2121 的事件 id 但 typ 写 `actvstart`（应该 `event`）→ 恒不满足。`client_version` 用的是 `arg2` 不是 `val`，容易写错字段名。

---

## 表清单

| 表号 | 表名 | 用途 | 主 Tab |
|---|---|---|---|
| 1011 | p2_i18n | 18 语本地化总表（按模块分 Tab） | 按模块 (ITEM/ASSET/ARENA 等 39 个模块 + AI暂存) |
| 1012 | p2_val_format | 文本格式化规则（LC/plain/var） | val_display |
| 1013 | p2_const_config | 全局常量主表 | const_config |
| 1014 | p2_statistical_data | 埋点统计数据定义 | statistical_data |
| 1015 | p2_first_name | NPC 英文名-名 | 工作表1 |
| 1016 | p2_last_name | NPC 英文名-姓 | 工作表1 |
| 1017 | p2_logo_text | LOGO/按钮等非 i18n 主表的多语言文案 | MENU |
| 1018 | p2_ab_test | AB 测试配置 | ab_test |
| 1019 | p2_statistical_data_relation | 埋点 counter 的关联关系 | statistical_data_relation |
| 1020 | p2_dlc_priority | DLC/CDN 资源地址与优先级 | 工作表1 |
| 1021 | p2_china_holiday | 国服节假日日期表（防沉迷用） | 工作表1 |
| 1022 | p2_function_switch | 功能总开关 | qa |
| 1023 | p2_popwindow | 主城弹窗优先级配置 | popwindow |
| 1024 | p2_merge_server_counter | 合服 counter 重置映射 | 工作表1 |
| 1025 | p2_hot_const_config | 热更常量（不需停服生效） | 主页签 |
| 1026 | p2_domestic_channel | 国服渠道分类 | 工作表1 |
| 1027 | p2_channel_detail | 渠道详情（含 bundle_id） | 工作表1 |
| 1028 | p2_google_smart_event | Google 智能事件上报（广告价格-权重） | 工作表1 |
| 1029 | p2_update_tips_version | 功能版本更新提示 | update_tips_version |
| 1030 | p2_iaa_center | 广告聚合中心条目配置 | 主页签 |

---

## 1011_p2_i18n — 18 语本地化总表

**用途**：全游戏所有 `LC_XXX` 文本的 18 语翻译。被 1017 之外的所有表通过 `LC_` 前缀的字符串引用。

**结构特殊性**：**不是一张表，而是 39+ 个模块 Tab**（IAP / ARENA / ART / BUFF / BUILDING / ASSET / ERRCODE / CHINA / HORDE / HERO / FTE / EVENT / ITEM / MENU / KVK / LEADERBOARD / NEWS / MAP / MAIL / NPC / PLAYER / PUSH / QUEST / RESEARCH / RSS / SITUATION / SATELLITE / SOCIAL / SOLDIER / STORY / TIP / TRIGGER / UNION / METRO / minigame 等）。每个模块一个独立 Tab，列结构一致。

**列结构（所有模块 Tab 通用）**：

| 列 | 含义 | 枚举/格式 | bug 模式 |
|---|---|---|---|
| `ID_int` | 数字 id | 10 位，前 7 位 `1011XXX` = 所在模块分段 | id 冲突时导表会覆盖 |
| `ID` | LC key（代码/配置实际引用的） | `{prefix}_{snake_case}` 例 `add_CD_desc` | 拼写错、大小写错 → 前端显示原 key 不翻译 |
| `cn` | 简中（中国台湾外简体） | - | 以 cn 为主来源翻译其他语言 |
| `en` | 英文 | - | 英文缺失会 fallback 到 ID 原串 |
| `fr / de / po / zh / id / th / sp / ru / tr / vi / it / pl / ar / jp / kr` | 16 种语言 | - | 漏翻 → 显示为 cn 或 LC_key |
| `cns` | 简中（国服专用，含敏感词调整） | - | 海外不读 cns；国服漏配 cns 回落 cn |

**AI翻译暂存 Tab 特殊字段**：
| 列 | 含义 |
|---|---|
| `✅提交` | FALSE=草稿 / TRUE=已审核待提交 |
| `目标页签` | 填 `ITEM`/`ASSET` 等模块名，审核后写入正式 Tab |

**跨表引用**：
- **被引用**：几乎全库所有含 `LC_` 前缀字符串的字段，主要在 1017 logo_text、1023 popwindow、1111 item（item_name/desc）、1030 iaa_center（name/claim_text）、2112 活动、2135 礼包、1920 hero 等。
- **特殊**：国服走 `cns` 列（见 `1011_p2_i18n -国服（自动更新）` 副表）。

**常见 bug**：
- **LC key 不存在**：新配的 `LC_EVENT_xxx` 没录入 1011 → 游戏显示原 key 而不是译文。自检：grep 配置里的 LC_xx，去 1011 对应模块 Tab 搜 ID 列。
- **语言漏翻**：某些小语种为空 → 该语种回落到 ID 本身（不是 cn）。
- **国服 cns 漏配**：国服包显示的是带敏感词的 cn → 要么补 cns，要么在 1013 标注"无需 cns"。
- **AI翻译暂存未提交**：把 `✅提交=TRUE` 漏勾 → 正式模块 Tab 没数据。

---

## 1012_p2_val_format — 文本格式化规则

**用途**：定义一段待替换文本该用什么格式化策略（查 LC / 纯文本 / 变量）。

**字段**：
| 字段 | 含义 | 枚举/格式 | bug |
|---|---|---|---|
| `S_INT_id` | 格式规则 ID | 10121XXX | - |
| `S_STR_typ` | 格式化类型 | `lc`（走 1011 翻译） / `plain`（原文输出） / `var`（代码变量替换） | 写成 `localized` 等非枚举值会 fallback |
| `S_STR_comment` | 策划备注 | 自由文本 | - |

**常见 bug**：配置中 `typ=plain` 但文本填了 LC_key → key 不被翻译直接显示。

---

## 1013_p2_const_config — 全局常量主表

**用途**：P2 全局战斗/联盟/城建/资源系数等硬编码常量的集中管理。代码通过 `A_STR_constant` 字符串读。

**字段**：
| 字段 | 含义 | 枚举/格式 | 关联 | bug 模式 |
|---|---|---|---|---|
| `A_INT_id` | 主键 | 10131xxx | - | - |
| `S_STR_comment` | 策划备注 | 自由文本 | - | - |
| `A_STR_constant` | 代码 key | snake_case 字符串 | 代码 `ConfigManager.GetConst("xxx")` | 拼错 → 代码 fallback 默认值；`nil_1/nil_2` 表示已废弃占位 |
| `A_FLT_val` | 数值（单值常量） | 浮点 | - | 毫秒/秒/小时单位混淆 |
| `A_ARR_array` | 数组常量 | `[a,b,c]` | - | 与 `A_FLT_val` 互斥，非空数组时 val 忽略 |
| `A_ARR_quintuple` | 五元组常量（物品/货币数组） | `[{"typ":"vm/item","id":xxx,"val":xxx}]` | 1111 item / 1115 vm | `typ=vm` 用的是 1115 货币 id；`typ=item` 用 1111 |
| `A_MAP_requirement` | 生效条件 | 见顶部 requirement 枚举 | - | 条件恒假 → 该常量不生效，按代码默认值走 |
| `A_INT_use_type` | 使用范围 | `0=通用 / 1=特殊场景` | - | 新加的特殊场景要特判 |
| `A_INT_country_use_type` | 区服 | 0/1/2 | - | 国服独立调参时必须配 2，否则被 0 覆盖 |

**典型常量示例（用于查表定位）**：
- `battle_coef_1` / `battle_coef_2`：伤害公式系数
- `v_troop_range_radius_extra`：部队射程（毫米）
- `v_march_trigger_battle_radius_extra`：触发战斗半径（毫米）
- `map_fixed_refresh_cd`：NPC 刷新间隔（毫秒）
- `create_union_cost_coin`：创联盟金币消耗
- `union_init_max_member_num`：联盟初始人数上限
- `repair_city_wall_cd`：城墙修理 CD（毫秒）
- `combustion_dec_city_defense_cd`：城墙燃烧掉城防速率（毫秒/点）
- `fire_fighting_costs`：灭火费用（五元组）

**常见 bug**：
- **单位搞混**：CD 字段用毫秒，但策划按秒填（300 vs 300000）→ 行为快 1000 倍。
- **val 和 array 双写**：代码可能只读一个，另一个被忽略。
- **国服独立改值**：只改了 `country_use_type=0` 的行 → 国服也被改，应该新增 `country_use_type=2` 的行。

---

## 1014_p2_statistical_data — 埋点统计 counter 定义

**用途**：定义游戏中所有埋点统计（玩家行为计数），代码通过 constant 读 counter 类型和上报规则。被 2112 活动任务、2115 任务、2118 排行奖励广泛引用。

**字段**：
| 字段 | 含义 | 枚举 | bug |
|---|---|---|---|
| `A_INT_id` | 主键 | 10141xxx | - |
| `S_STR_comment` | 策划备注 | - | - |
| `N_STR_arg_comment` | 参数字段说明（表+字段定位） | 例 `building表A_INT_building_id` | N_ 开头不下发 |
| `A_STR_constant` | counter 代码 key | snake_case，例 `pevent_building_level_cnt` | 活动配任务时 id 和 constant 要对上 |
| `S_STR_counter` | counter 累计模式 | `reset`（重置，如"当前等级"） / `accum`（累加，如"升级次数"） / `max`（取最大） | accum 写成 reset → 任务 progress 异常归零 |
| `S_INT_source` | 上报源 | 1=客户端 / 2=服务器（根据实际 counter 定义） | 写反会导致服务器不认可客户端上报 |
| `A_INT_sc` | Special Counter 标记 | 0/1 | 1 表示这个 counter 用于特殊结算 |
| `S_INT_record_type` | 数据类型 | 1/2 | 影响存储方式 |

**常见 bug**：
- **counter 模式错**："关卡通过次数"应该是 `accum`，但写成 `reset` → 合服/跨日后计数归零。
- **id 被活动引用但改了 constant**：下游 2115 任务 task 还引用旧 constant → 任务进度卡 0。
- **记忆提示**：挖孔 6 期曾发生 `digkeys_start_level` vs `status=1` 口径错配（见 project_dighole_6q_event_workaround memory）。

---

## 1015_p2_first_name / 1016_p2_last_name — NPC 英文名库

**用途**：随机 NPC 生成时抽取名字。海外使用，国服不走。

**字段**（两表同结构）：
| 字段 | 含义 |
|---|---|
| `A_INT_ID` | 主键（10150xxx / 10160xxx） |
| `A_STR_Name` | 英文名/姓 |

**bug**：
- 新加 name 但 ID 与旧 ID 冲突 → 老存档的 NPC 名字显示混乱。
- 国服不需要此表但若代码误读 → 国服 NPC 也显示英文名。

---

## 1017_p2_logo_text — 非 LC 模板的多语言文案

**用途**：游戏中一部分按钮、LOGO、关键 UI 文本**不走 1011 的 LC 机制**，直接用此表（按 key 匹配）。通常 14~15 种语言（**不含 cns**）。

**字段**：
| 字段 | 含义 | bug |
|---|---|---|
| `ID` | 文案 key（代码硬编码） | 不能任意改名，改名后代码失效 |
| `cn/en/fr/de/po/zh/id/th/sp/ru/tr/jp/kr/ar` | 14 语 | 缺语言 → 该语言显示原 key |

**常见 bug**：改 1017 文案时"只改了 cn" → 其他语言还是旧文案但下游无报错。

---

## 1018_p2_ab_test — AB 测试配置

**用途**：A/B/C 分组测试。策划通过 switch 控制开关、proportion 控制分桶比例。

**字段**：
| 字段 | 含义 | 枚举/格式 | bug |
|---|---|---|---|
| `A_INT_id` | 主键 | 10181xxx | - |
| `S_STR_comment` | 方案描述（A/B/C 各代表什么） | 必写 | 不写 → 后续改配置不知道哪个版本是啥 |
| `A_STR_constant` | 代码 key | 可空 | - |
| `A_INT_switch` | 测试开关 | `0=关 / 1=开` | 开启后才分桶 |
| `A_ARR_proportion` | 分组比例 | `[A权重, B权重, ...]` 例 `[1,0]`=全部 A，`[0,1]`=全部 B，`[0,1,0]` ABC 三桶全在 B | **总和 0** 时崩溃；**长度** 必须等于要测试的桶数 |
| `S_MAP_server` | 生效服务器 | `{"typ":"schema","id":[...]}` | 漏填 schema id → 那些服不分桶 |
| `S_MAP_filter` | 玩家筛选 | 条件 map | 例 `{"op":"ge","typ":"building","id":111811,"val":0}` = 主城≥0 |
| `S_STR_type_filter` | filter 类型 | `country` / `0`（无筛选） | - |
| `A_INT_country_use_type` | 区服 | 0/1/2 | - |

**常见 bug**：
- **proportion 长度错**：描述里说 ABC 三方案但 proportion 只写了 2 项 → 第三桶永远进不去。
- **switch=0 但策划以为开了**：实际没分桶，全量走默认逻辑。
- **schema id 列表遗漏**：新合服后未加 → 该合服服玩家全量跳过 AB 分桶。

---

## 1019_p2_statistical_data_relation — 埋点关联关系

**用途**：一条行为可能同时触发 player/union/horde/server 级的多个 counter。此表定义这些 counter 的联动。

**字段**：
| 字段 | 含义 |
|---|---|
| `A_INT_id` | 主键 |
| `S_STR_comment` | 策划备注（同时解释这条行为的 counter 覆盖面） |
| `A_STR_constant` | counter group key |
| `A_INT_player` | 指向 1014 个人 counter id |
| `A_INT_union` | 指向 1014 联盟 counter id（0=无联盟级） |
| `A_INT_horde` | 指向 1014 部落 counter id（0=无） |
| `A_INT_server` | 指向 1014 服务器 counter id（0=无） |

**常见 bug**：
- 只改了 1014 player counter 的定义，但 1019 这里的 union/horde 还引用旧 id → 联盟/部落排行榜数据错乱。
- 新加活动 counter 忘了在 1019 登记 → 联盟级排行榜不计数。

---

## 1020_p2_dlc_priority — DLC / CDN 资源地址表

**用途**：运营资源（活动海报、banner、插画等）的 CDN URL 与优先级。**改图必动这张表**。

**字段**：
| 字段 | 含义 | 枚举/格式 | bug |
|---|---|---|---|
| `A_INT_id` | 主键 | 10201xxx | - |
| `A_STR_urls` | 资源路径（相对 CDN 根） | 例 `assets/operation/P2dlcimg/llustration` | **漏后缀**、**漏前缀** 都会 404 |
| `A_INT_priority` | 加载优先级（数字大越优先） | 999/998/… | 多资源冲突时按此排 |
| `A_STR_version` | 版本号 | `1`/`2` | 改图时 bump version 触发客户端重新下载 |
| `N_STR_comment` | 策划备注（说明这张图放哪） | 例 `所有大屏礼包的海报` | - |

**常见 bug**：
- **没 bump version**：换了图但 version 没改 → 客户端缓存老图不刷。
- **路径大小写/拼写错**：CDN 404，活动入口/弹窗显示空白。
- **漏配**：新加了海报但忘了 1020 注册 → 客户端读不到资源。

---

## 1021_p2_china_holiday — 国服节假日表

**用途**：国服防沉迷——节假日允许未成年登录时长不同。此表是节假日日期枚举。

**字段**：
| 字段 | 含义 |
|---|---|
| `A_INT_id` | 主键（10211xxx） |
| `A_INT_year` | 年 |
| `A_INT_month` | 月 |
| `A_INT_day` | 日 |

**bug**：跨年新节假日没及时加（如每年除夕）→ 未成年那天玩不够时长。**每年 12 月做年度更新**。

---

## 1022_p2_function_switch — 功能总开关

**用途**：一类功能的全局关停开关。代码通过 function 字符串查。**全库最容易出 bug 的表之一**（关错开关整块功能下线）。

**字段**：
| 字段 | 含义 | 枚举 | bug |
|---|---|---|---|
| `A_INT_id` | 主键 | 10221xxx；**相同 id 可多行**（按 country_use_type 拆） | - |
| `S_STR_function` | 功能代码 key | snake_case，如 `praise_5star` / `bi_pkg_push` / `actv_calendar` | 拼错 → 代码读默认值，功能"幽灵上线" |
| `S_INT_switch` | 开关值 | `0=关 / 1=开` | 国服 praise_5star 关但海外开（隐私合规） |
| `A_INT_country_use_type` | 区服 | 0=通用 / 1=海外 / 2=国服 | 同 id 通常拆两行（1 和 2），别填 0 |

**常见 bug**：
- **同 id 多行覆盖**：country_use_type=0 + 2 同时存在 → 覆盖顺序不确定。
- **海外关了但国服没关**（或反之）：因为两行独立配置，改一行忘另一行。
- **function 字符串 typo**：`function_switch` 这条（id=10221006）就是 typo——应该叫"总开关"但名字 `function_switch` 和表名一样，代码读不到。

**已知功能 key 样本**：
- `praise_5star` - 五星好评弹窗
- `grading_system` - 评分体系
- `bi_pkg_push` - BI 礼包推送
- `actv_calendar` - 活动日历
- `visit_system` - 拜访系统

---

## 1023_p2_popwindow — 主城弹窗管理表

**用途**：**P2 主城所有弹窗的唯一入口**。控制哪些弹窗出现、优先级、条件、素材。**弹窗顺序错乱 90% 在这张表**。

**字段**：
| 字段 | 含义 | 枚举/格式 | bug 模式 |
|---|---|---|---|
| `A_INT_id` | 弹窗 ID | 10231xxx | - |
| `A_STR_comment` | 弹窗描述 | 必写 | - |
| `A_MAP_components` | 绑定组件 | `{"typ":"event/iap_scene/iap/bi_vip0_push/iap_recharge/iap_newbieshop/situation/pay_sign","id":[...]}` | typ 写错 → 弹窗永远不触发 |
| `S_MAP_condition_player` | 玩家条件 | 条件 map | 例 `{"op":"ge","typ":"building","id":111811,"val":3}` |
| `A_STR_goto` | 点击跳转 | `""` 或跳转 URL/页面代码 | 写成纯字符串要用双引号包；`""` 表示无跳转 |
| `S_MAP_pop_range` | 弹出范围限制 | `{}` 或时间/次数限制 | - |
| `A_INT_priority` | 优先级（**大的先弹**） | 常见 9999/9998/9997/.../5000/.../2000 | **多弹窗 priority 同值** → 顺序不确定 |
| `A_STR_title` | 标题 LC_key | `LC_XX_xxx` 或 `""` | 拼错 → 显示 key 文本 |
| `A_ARR_reward` | 奖励预览数组 | `[{"typ":"item","id":xxx,"val":xxx}]` | 显示 only，实际奖励由组件给 |
| `A_MAP_title_color` | 标题颜色 | `{"color1":"#ffcc4c","color2":"#ffa200","outline1":"#bb1400","outline2":"#b21501"}` | color 漏配 → 默认白色 |
| `A_STR_banner_url` | 海报路径 | `assets/operation/P2dlcimg/...` | 必须在 1020 注册 |
| `A_INT_button_color` | 按钮色 | 0/1/2/3 | - |
| `A_INT_pop_style` | 弹窗样式 | `0/2/3/101`… | 101=situation 专用；0=默认 |
| `A_ARR_get_reward` | 获取奖励配置 | `[{"typ":"item","id":xxx,"val":xxx}]` 或 `[]` | 有些弹窗自己不给奖 |
| `A_STR_subtitle` | 副标题 LC_key | `""` 为空 | - |
| `A_STR_desc` | 描述 LC_key | `""` 为空 | - |
| `A_INT_displaykey` | 展示 key（客户端标识） | int | - |
| `A_INT_country_use_type` | 区服 | 0/1/2 | - |

**components typ 枚举（高频）**：
| typ | 触发条件 | id 指向 |
|---|---|---|
| `event` | 事件活动进行中 | 2121 事件 id |
| `iap_scene` | 情景礼包 | - |
| `iap` | 某 iap 未购买+在时间窗内 | 2011 iap id + val=时间窗毫秒 |
| `bi_vip0_push` | BI 推 VIP0 破冰 | - |
| `iap_recharge` | 连续充值触发 | - |
| `iap_newbieshop` | 新玩家商店每日 | - |
| `situation` | 天下大势阶段 | 2112/2311 situation id 数组 |
| `pay_sign` | KVK 破冰付费签到 | - |

**常见 bug**：
- **priority 相同**：多个弹窗撞 2000 → 顺序看运气。
- **banner_url 没 bump 1020 version**：活动换图后弹窗还是老图。
- **typ=event 但填的是 2112 活动 id**（应该是 2121 事件 id）→ 弹窗永远不出。
- **situation pop_style 忘写 101**：显示为普通弹窗样式。
- **LC key 漏录 1011**：title/subtitle/desc 拼写错 → 显示原 key。

---

## 1024_p2_merge_server_counter — 合服 counter 映射

**用途**：合服时，原服各个 counter 的"起始新 id"映射——用来在合服后保持 counter 累积不丢。

**字段**：
| 字段 | 含义 |
|---|---|
| `A_INT_id` | 主键（10240xxx） |
| `S_INT_counter` | 对应 1014 的 counter id |

**bug**：新加埋点 counter 后忘登记 1024 → 合服时该 counter 丢历史。

---

## 1025_p2_hot_const_config — 热更常量

**用途**：**1013 的热更变体**——不停服即可更新的常量。字段结构和 1013 完全一致，但走独立下发通道。

**字段**：与 1013 相同（见 1013 段）。

**常见 bug**：
- 改了 1013 没生效：可能该常量已被迁移到 1025，应改 1025。
- 1013 和 1025 同时配同一 constant → 冲突。
- 新加常量想热更但配到 1013 → 要停服才生效。

---

## 1026_p2_domestic_channel — 国服渠道分类

**用途**：国服 bundle 标识归类（官方服 vs 渠道服）。

**字段**：
| 字段 | 含义 | 枚举 |
|---|---|---|
| `A_INT_id` | 主键 | 10260xxx |
| `S_STR_qudao` | 渠道 key | `official_server` / `huawei_server`（代码只认这两类） |
| `S_STR_comment` | 策划备注 | - |

---

## 1027_p2_channel_detail — 渠道详情

**用途**：每个国服渠道的 bundle_id 与分类对应。代码通过 bundle_id 反查走哪类支付/审核流程。

**字段**：
| 字段 | 含义 | 枚举/格式 | bug |
|---|---|---|---|
| `A_INT_id` | 主键 | 10270xxx | - |
| `S_STR_bundle_id` | 应用 bundle id | 例 `com.tap4fun.ape.cn.huawei` | 必须和 iOS/Android 实际打包 bundle 对应，拼错直接识别失败 |
| `S_STR_server_channel` | 关联的渠道分类 | 引用 1026 的 `S_STR_qudao` | 写错名字 → 未知渠道走通用逻辑 |
| `N_STR_comment` | 渠道中文名 | 例 `华为渠道` | - |

**常见 bug**：新增渠道（如拼多多、vivo 等）忘同步 1026 + 1027 → 新渠道付费走默认逻辑。

---

## 1028_p2_google_smart_event — Google 智能事件上报

**用途**：Google Ads / Firebase 智能事件的价格档位-权重映射。用于广告 ROAS 上报分桶。

**字段**：
| 字段 | 含义 |
|---|---|
| `A_INT_id` | 主键（10280xxx） |
| `C_FLT_price` | 美元价格（0.99/1.99/2.99…） |
| `C_INT_weight` | 权重 |

**bug**：新增档位但没加到 1028 → 该档位充值不上报广告事件。

---

## 1029_p2_update_tips_version — 功能更新提示

**用途**：功能版本升级后给玩家弹"什么变了"的提示。代码按 constant 或 comment 读。

**字段**：
| 字段 | 含义 | bug |
|---|---|---|
| `A_INT_id` | 主键（10290xxx） | - |
| `S_STR_comment` | 功能中文名（酒馆/任务系统等） | - |
| `A_STR_constant` | 代码 key | 可空；非空时按 constant 匹配 |
| `A_STR_min_version` | 起始版本号 | 例 `0.52.0` | 改版本号没同步 → 老版本玩家看到新提示 |

---

## 1030_p2_iaa_center — 广告聚合中心

**用途**：游戏内"广告中心"页面条目配置（免费体力/免费加速/多倍资源等）。主要服务 IAA 场景。

**字段**：
| 字段 | 含义 | 枚举/格式 | 关联 | bug 模式 |
|---|---|---|---|---|
| `A_INT_id` | 主键 | 10300xxx | - | - |
| `S_STR_comment` | 功能中文名 | - | - | - |
| `A_STR_constant` | 代码 key | 例 `mutiple_rss_get` / `free_ap` / `hero_advanced_gacha` | - | 改名代码失效 |
| `C_STR_name` | 显示名 LC key | `LC_EVENT_iaa_center_xxx` | 1011 EVENT | LC 漏录 |
| `C_STR_claim_text` | 领取按钮 LC key | `LC_EVENT_xxx_button` / `LC_EVENT_login_bp_normal_get` | 1011 EVENT | - |
| `C_MAP_goto` | 点击跳转 | `{"cat":10141012}` 指向 1014 埋点 counter，或 `{}` 无跳转 | 1014 | cat id 写错 → 跳空页 |
| `C_INT_display_key` | 展示 key | `15119829` 等客户端标识 | - | - |
| `C_INT_display_order` | 排序（数字越大越靠前） | 99/98/… | - | 相同值顺序不定 |
| `A_ARR_ads_reward` | 看广告奖励 | `[{"typ":"item","id":xxx,"val":xxx}]` 或 `[]` | 1111 item | 空数组表示无实物奖（只加 buff） |
| `A_FLT_ratio` | 资源倍率（多倍资源时用） | `2` / `4` | - | - |
| `A_MAP_requirement` | 显示条件 | `{"op":"and","args":[{"op":"ge","typ":"actvstart","id":21122134,"val":1},...]}` | 2112 | 活动未开 → 入口不显示 |
| `A_INT_display_type` | 展示类型 | 0/... | - | - |
| `S_MAP_triggers` | 额外触发条件 | `{}` 为空 | - | - |
| `A_INT_duration` | 持续时间（秒） | - | - | - |
| `S_MAP_limit` | 次数限制 | `{"limit_cnt":3,"limit_type":"daily","refresh_duration":86400}`；`-1`=无限 | - | limit_cnt=0 → 玩家永远领不到 |
| `A_INT_get_cd` | 领取 CD（秒） | - | - | 0=无 CD |

**常见 bug**：
- **requirement 的 actvstart id 写错**：新活动 ID 没同步 → 广告中心入口不亮。
- **ads_reward 的 item id 失效**：1111 里物品被删或换 id → 领不到奖。
- **limit_cnt 配 0**：整条目禁用但未说明。
- **国服/海外分流靠 requirement 的 `typ:client_version` / `server_open_day`**：1030 无 `country_use_type` 字段，分流完全靠 requirement 表达式（参见真实 1030 第 1 行 requirement 样本）；写漏会导致国服展示 IAA 入口。

---

## 跨表引用拓扑（10_p2_const 出向/入向）

```
1011 i18n ─┬─ 被 1017 1023 1030 2112 2135 1111 1920 等几乎所有表引用（LC_ key）
           └─ 国服走 cns 列（独立副表 1011-国服）

1013 const_config ─┬─ quintuple 引用 1111 item / 1115 vm
                    ├─ requirement 引用 2112 actvstart / 1118 building / 2011 iap 等
                    └─ 1025 hot_const 是热更副本

1014 stat_data ─┬─ 被 1019 关联 / 1024 合服映射
                └─ 被 2112 2115 2118 活动任务/排行大量引用 constant

1018 ab_test  ── filter 引用 1118 building id

1022 function_switch ── 代码层 feature flag，所有模块都可能引用

1023 popwindow ─┬─ components typ=event 引用 2121 event id
                 ├─ components typ=iap 引用 2011 iap id
                 ├─ banner_url 必须在 1020 dlc_priority 注册
                 └─ title/subtitle/desc LC 在 1011

1026 channel ── 被 1027 引用

1030 iaa_center ─┬─ C_MAP_goto cat 指向 1014
                  ├─ A_ARR_ads_reward 指向 1111 item
                  ├─ requirement 指向 2112 actvstart
                  └─ name/claim_text 指向 1011 EVENT 模块
```

---

## Jira 工单常见自检路径

| 现象 | 先查的表 | 定位方法 |
|---|---|---|
| 某文案显示 `LC_XXX` 原 key | 1011 | 去对应模块 Tab 按 ID 列搜，看是否缺行/漏翻 |
| 主城弹窗不出/顺序错 | 1023 | 检查 `A_MAP_components` typ 和 id、`A_INT_priority`、`S_MAP_condition_player` |
| 活动海报 404 / 换图没生效 | 1020 | 检查 `A_STR_urls` 拼写 / `A_STR_version` 是否 bump |
| AB 分桶不生效 | 1018 | 检查 `A_INT_switch=1`、`A_ARR_proportion` 长度对、`S_MAP_server` 含当前 schema |
| 活动任务 counter 不累积 | 1014 + 1019 | 1014 counter 类型 reset/accum 对；1019 是否有联盟/部落级联动 |
| 某功能在海外关了但国服开了（或反之） | 1022 | 检查同 id 是否有 country_use_type=1 和 2 两行 |
| 某常量改了没生效 | 1013 / 1025 | 可能该常量已迁到 1025（热更）；或 country_use_type 漏配国服 |
| 新渠道支付不走渠道流程 | 1026 + 1027 | bundle_id 拼写 / server_channel 引用 |
| 广告中心某条目不显示 | 1030 | requirement 里 actvstart id / limit_cnt 是否 ≥1 |
| 国服未成年节假日时长错 | 1021 | 当年日期是否完整（尤其除夕/春节） |

---

**维护建议**：每次 S 级 bug 定位到 10_const 时，把新的踩坑点补到本文件对应表的"常见 bug"段。
