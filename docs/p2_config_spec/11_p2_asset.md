# 11_p2_asset 资产/建筑/兵种/科技/酒馆/集卡 配置规范

> **用途**：P2 全库"资产类"核心配置——包含道具、资源、货币、建筑、科技、兵种、头像、酒馆、集卡、商店、地图表情等**玩家可拥有的一切对象**。所有 `typ:"item"` / `typ:"building"` / `typ:"research"` / `typ:"soldier"` / `typ:"rss"` / `typ:"vm"` 引用都指向这里。
>
> **Jira 自检场景**：道具图标错乱 / 建筑升级卡住 / 科技前置失效 / 兵种训练失败 / 商店商品价格错 / 头像框解锁不正确 / 酒馆/集卡抽奖概率异常 / 资源上限溢出。

> **前置知识**：字段前缀 `A_/S_/C_/N_` + 类型中段 `INT_/FLT_/STR_/ARR_/MAP_` 等通用约定见 [`10_p2_const.md`](./10_p2_const.md) 顶部。本文只列**各表特有字段**。

---

## 表清单（按子系统分组）

### 资产主表（asset-typ 分发入口）
| 表号 | 用途 |
|---|---|
| [1110](#1110_p2_asset) | **asset 主表**——登记所有 `typ:"xxx"` 对应的子表 ID 段 |

### 核心货币与资源（5 种 typ）
| 表号 | 用途 | typ 关键字 |
|---|---|---|
| [1111](#1111_p2_item) | **道具主表**（食物/加速卡/盾/碎片/CD 等） | `item` |
| [1114](#1114_p2_rss) | 资源（食物/钢铁/铀/电池等） | `rss` |
| [1115](#1115_p2_vm) | 虚拟货币（CD/荣誉币/钻石等） | `vm` |
| [1116](#1116_p2_xp) | 经验类资源（玩家xp/vip xp） | `xp` |
| [1117](#1117_p2_recover) | 可恢复资源（体力/行动力） | `recover` |

### 商店 & 兑换
| 表号 | 用途 |
|---|---|
| [1113](#1113_p2_item_store) | 道具购买商店 |
| [1151](#1151_p2_secret_shop_item) | 神秘商店商品池 |
| [1154](#1154_p2_vip_shop) | VIP 商店 |
| [1165](#1165_p2_stores) | 商店主表（神秘/普通/VIP 商店登记） |
| [1161](#1161_p2_asset_retake) | 资产回收规则 |
| [1162](#1162_p2_asset_retake_shop) | 资产回收商店 |
| [1183](#1183_item_bag_classification) | 背包分类 |
| [1197](#1197_p2_wonder_reward_retake) | 跨版本资产回归（玩家粒度） |
| [1179](#1179_p2_capsule_rss_convert_cost) | 胶囊资源兑换 |

### 建筑体系
| 表号 | 用途 |
|---|---|
| [1118](#1118_p2_building) | **建筑主表**（所有建筑等级数据） |
| [1125](#1125_p2_building_slot) | 城市建筑坑位 |
| [1126](#1126_p2_city_building_skin) | 建筑皮肤 |
| [1127](#1127_p2_building_build) | 建筑建造条件（建造流程） |
| [1128](#1128_p2_instant_price_asset) | 资源立刻购买定价曲线 |
| [1129](#1129_p2_instant_price_time) | 时间立刻购买定价曲线 |
| [1130](#1130_p2_building_function) | 建筑功能菜单 |
| [1131](#1131_p2_building_bubble) | 建筑气泡 |
| [1140](#1140_p2_city_map_grid) | 主城地块网格 |
| [1169](#1169_p2_city_area) | 主城区域解锁 |
| [1170](#1170_p2_paradeground) | 阅兵场建筑 |
| [1171](#1171_p2_building_reset_v36) | 建筑布局重置模板 |
| [1172](#1172_p2_paradeground_soldiershow) | 阅兵场兵种展示 |

### 科技/研究
| 表号 | 用途 |
|---|---|
| [1119](#1119_p2_research) | **科技主表** |
| [1132](#1132_p2_research_category) | 科技分类 |
| [1178](#1178_p2_battery_research_skill) | 电池研究技能树 |
| [1196](#1196_research_fast_up) | 合服科技追赶 |
| [1199](#1199_p2_research_change) | 科技改动回补 |
| [1198](#1198_p2_tavern_change) | 酒馆改动回补 |

### 兵种
| 表号 | 用途 |
|---|---|
| [1121](#1121_p2_soldier) | **兵种主表**（等级+属性+升级） |
| [1122](#1122_p2_soldier_category) | 兵种分类（步兵/骑兵/远程） |
| [1124](#1124_p2_speedup) | 加速类型定义 |
| [1166](#1166_p2_soldier_arms) | 兵种武装（装备） |
| [1167](#1167_p2_arms_group) | 武装组合 |
| [1137](#1137_p2_hero_stationed) | 英雄驻防点（哪些建筑可驻防） |
| [1138](#1138_p2_hero_stationed_buff) | 驻防 buff |
| [1139](#1139_p2_hero_stationed_exercise) | 驻防演习 |

### 外观/个性化
| 表号 | 用途 |
|---|---|
| [1133](#1133_p2_player_avatar) | 玩家头像 |
| [1142](#1142_p2_avatar_frame) | 头像框 |
| [1143](#1143_p2_city_wall_flag) | 城墙旗帜 |
| [1144](#1144_p2_nation_flag) | 国旗（国籍） |
| [1159](#1159_p2_player_badge) | 玩家徽章 |
| [1173](#1173_p2_chat_skin) | 聊天铭牌皮肤 |
| [1184](#1184_p2_theme_decoratiton) | 主题装饰 |
| [1160](#1160_p2_banana_decorations) | 香蕉装饰 |
| [1180](#1180_p2_map_emoji) | **地图表情**（行军表情） |

### 酒馆
| 表号 | 用途 |
|---|---|
| [1145](#1145_p2_tavern_login_reward) | 酒馆登录奖励 |
| [1146](#1146_p2_tavern_bar_gift) | 酒馆吧台礼物（gacha 池） |
| [1147](#1147_p2_tavern_story_gift) | 酒馆剧情礼物 |
| [1148](#1148_p2_tavern_trader_list) | 酒馆商人交易 |
| [1150](#1150_p2_tavern_top_pool) | 酒馆池权重 |
| [1152](#1152_p2_banana_hologram) | 香蕉投影仪 |
| [1153](#1153_p2_get_access) | 获取途径入口 |
| [1168](#1168_p2_get_access_group) | 获取途径分组 |

### 集卡
| 表号 | 用途 |
|---|---|
| [1155](#1155_p2_collection) | **集卡主表** |
| [1156](#1156_p2_collection_group) | 集卡分组 |
| [1157](#1157_p2_collection_gacha_package) | 集卡 gacha 礼包 |
| [1158](#1158_p2_collection_gacha_reward) | 集卡 gacha 奖励 |
| [1164](#1164_p2_collection_power_buff) | 集卡战力 buff |
| [1176](#1176_p2_collection_platform) | 集卡展台 |
| [1181](#1181_p2_collection_filter) | 集卡筛选器 |
| [1182](#1182_p2_collection_break_achievement) | 集卡突破成就（空表） |

### 其它
| 表号 | 用途 |
|---|---|
| [1120](#1120_p2_drop) | 通用掉落规则 |
| [1135](#1135_p2_player_level) | 玩家等级 |
| [1163](#1163_p2_inner_coin) | 内购货币（方舟币） |
| [1174](#1174_p2_daily_growth) | 每日成长分道具权重 |
| [1175](#1175_p2_safe_box) | 保险箱（金库） |
| [1177](#1177_p2_citybeauty_reward) | 城市美化奖励 |

---

<a id="1110_p2_asset"></a>
## 1110_p2_asset — 资产类型分发主表

**用途**：登记每个 `typ:"xxx"` 指向哪张子表。代码拿到 `{"typ":"item","id":11111001}` 时先查 1110 找到 typ=item 对应 1111。

**字段**：
| 字段 | 含义 | 枚举/格式 | bug |
|---|---|---|---|
| `A_INT_id` | 子表号 | `1111`/`1114`/`1115`/`1116`/`1117` 等 | - |
| `A_STR_typ` | 资产类型 key | `item`/`rss`/`vm`/`xp`/`recover`/`building`/`soldier`/`research`/`collection`/`hero`/`buff`/`power` 等 | typ 名换了但 1110 没同步 → 全库引用失效 |
| `A_STR_comment` | 注释 | - | - |
| `A_MAP_lc_name` | 类型 LC | - | - |

**常见 bug**：新增 typ 类型（如新版本加了 `theme_deco`）但未登记此表 → 所有引用 `{"typ":"theme_deco",...}` 的配置全都指向空。

---

<a id="1111_p2_item"></a>
## 1111_p2_item — 道具主表（全库最核心之一）

**用途**：所有"道具"的定义（普通道具、加速卡、资源道具、装备碎片、礼包道具、活动道具等）。被几乎全库表通过 `{"typ":"item","id":1111xxxx}` 引用。

**字段**：
| 字段 | 含义 | 枚举/格式 | 关联 | bug 模式 |
|---|---|---|---|---|
| `A_INT_id` | 主键 | 1111xxxxx | - | 新增 ID 必须去活动礼包类表（2135/2013）同步引用 |
| `S_STR_comment` | 道具中文名（策划辨识用） | - | - | - |
| `A_STR_constant` | 代码 constant | 可空；非空时代码按 constant 读 | - | - |
| `A_STR_class` | 道具大类 | `item_rss`/`item_speedup`/`item_chest`/`item_shield`/`item_collection_frag`/`item_gift_gacha`/`""` 等 | - | class 错 → 在背包错分类页签显示 |
| `A_INT_quest_class` | 任务分类 | int | 2115 | 活动任务 typ=use_item 时按此分类匹配 |
| `C_INT_display_order` | 排序（小的先） | - | - | - |
| `C_INT_display_key` | 客户端 displaykey（图标资源 id） | - | - | 改图必动 displaykey |
| `C_INT_display_quality` | 品质色（客户端） | 0/1/2/3/4/5/6 = 白/绿/蓝/紫/橙/红/金 | - | 品质不一致视觉异常 |
| `C_MAP_lc_upper_show` | 顶部角标 LC | - | 1011 | - |
| `A_MAP_lc_name` | 道具名 LC | `{"typ":"lc","txt":"LC_ITEM_xxx_name"}` 或 args 带参 | 1011 ITEM | LC key 漏录 1011 → 显示原 key |
| `C_MAP_lc_desc` | 描述 LC | - | 1011 | - |
| `C_MAP_lc_usetip` | 使用提示 LC | - | 1011 | - |
| `A_FLT_value` | 等效价值（用于战力折算） | - | - | 新道具漏配 value → 战力不计入 |
| `A_INT_max_own` | 持有上限 | - | - | 999999 = 实际无上限 |
| `A_INT_max_get` | 单次获取上限 | - | - | - |
| `A_INT_max_use` | 单次使用上限 | - | - | - |
| `C_ARR_display_labels` | 客户端显示 label | `["bag_asset","rss_food"]` 等 | - | 背包筛选按这个 |
| `A_ARR_use_labels` | 使用分类 label | - | - | - |
| `A_MAP_category_param` | 使用效果配置（effect.typ 完整枚举见下） | `{"effect":[{"typ":"rss","id":11141001,"val":10000}]}` 获得资源 | 见下表 | effect 里 id 无效 → 用了但没东西 |
| `A_INT_fixed_use` | 使用数量固定值 | -1=玩家选数量 / >0=固定次数 | - | - |
| `S_INT_use_now` | 立即使用 | 0/1 | - | - |
| `C_ARR_drop_display` | 掉落展示 | - | - | - |
| `A_INT_source` | 来源 get_access_group | 指向 1168 | 1168 | 新道具要补 1168 → 否则点击问号无跳转 |
| `A_INT_get_access_group` | 获取途径分组 | 同上 | 1168 | - |
| `A_INT_country_use_type` | 区服 | 0/1/2 | - | - |

**`A_MAP_category_param.effect[].typ` 完整枚举**（路由到的视觉/资源表 — **节日礼包 item 必查**）：

| typ | 用途 | id 指向 | val 含义 |
|---|---|---|---|
| `rss` | 获得资源 | 1114 资源 id | 数量 |
| `item` | 获得道具 | 1111 item id | 数量 |
| `buff` | 叠加 buff | 1116/buff 表 | 时长/强度 |
| `marching_effect` | 行军特效（拥有） | 1365 march_effect id | `-1`=永久 / 正数=秒数（86400=1天,604800=7天,2592000=30天） |
| `city_skin` | 主城皮肤（拥有） | 1312 city_skin id | 同上 |
| `city_effect` | 主城特效（拥有） | 1387 city_effect id | 同上 |
| `map_emoji` | 行军表情（拥有） | 1180 map_emoji id | 同上 |
| `avatar_frame` | 头像框 | 1142 avatar_frame id | 同上 |
| `nameplate` | 铭牌聊天框 | 1173 chat_skin id | 同上 |
| `voucher` | 代金券 | 2011 IAP id | - |
| `vip_xp` | VIP 经验 | - | 数量 |
| `hero_exp` / `hero_fragment` | 英雄经验/碎片 | 1920 hero id | 数量 |

**常见 bug**：
- **使用 effect 的 id 失效**：`category_param.effect[0].id` 指向的 1114 资源 id 被删 → 使用报错。
- **新道具漏配 get_access_group**：在活动里给了玩家但玩家不知道哪来的，UI 跳转空白。
- **display_quality 和实际资源不符**：橙色道具但 quality=3（紫）→ 视觉异常。
- **跨节日 item_id 平移**：通用道具（如加速卡）不换 id；节日专属道具必须换（见 feedback_common_vs_festival_items memory）。
- **effect.typ 写错**：例 marching_effect 写成 map_effect → 客户端读不到，玩家背包看不到外观。

---

<a id="1113_p2_item_store"></a>
## 1113_p2_item_store — 道具商店

**字段**：
| 字段 | 含义 | 枚举 | bug |
|---|---|---|---|
| `A_INT_id` | 主键 | 11131xxx | - |
| `A_STR_constant` | 代码 key | 可空 | - |
| `A_MAP_item_id` | 商品（指向 1111） | `{"typ":"item","id":1111xxxx,"val":1}` | item id 失效 → 无法购买 |
| `A_MAP_cost_asset` | 价格（可能带条件折扣） | `{"args":[{"typ":"vm","id":11151001,"args":[{"typ":"common","val":N}]}]}` | vm id 错 → 扣错货币 |
| `A_MAP_requirement` | 购买前置条件 | - | - |
| `A_MAP_display_requirement` | 展示条件 | - | - |
| `S_INT_daily_max` | 每日购买上限 | -1=无限 | 0 = 禁售 |

---

<a id="1114_p2_rss"></a>
## 1114_p2_rss — 资源主表

**字段**：
| 字段 | 含义 | 枚举 | 关联 |
|---|---|---|---|
| `A_INT_id` | 主键 | 11141xxx（食物=11141001/钢铁=11141003/铀等） | - |
| `A_INT64_max_own` | 持有上限（**注意 INT64**） | 默认 999999999999 | - |
| `A_INT64_max_get` / `max_use` | 单次获取/使用上限 | - | - |
| `C_INT_access_group_id` | 获取途径 | 指向 1168 | 1168 |
| `A_INT_source` | source 途径 | 指向 1174 daily_growth | 1174 |

**常见 bug**：新资源（如节日专属资源）加到 1114 但 max_own 用了 INT 而非 INT64 → 溢出归零。

---

<a id="1115_p2_vm"></a>
## 1115_p2_vm — 虚拟货币主表

**字段**：同 1114，关键字段 `A_STR_constant` 决定代码 key。
- `11151001` = CDs（Core Diamond，主钻）
- `11151002` = 荣誉币
- `11151003+` = 各活动货币、kvk币、联盟币等

**bug**：节日活动货币经常错绑 vm id → 活动结束后该货币被重置或残留异常。

---

<a id="1116_p2_xp"></a>
## 1116_p2_xp / <a id="1117_p2_recover"></a>1117_p2_recover — 经验与恢复类资源

- **1116**：玩家经验、VIP 点数等累积类
- **1117**：体力、行动力等按时间恢复的资源。`A_INT_restore_time` = 每点恢复毫秒；`A_INT_max_natural_recover` = 自然恢复上限。

**bug**：`restore_time` 单位搞错（填秒数）→ 恢复速度快 1000 倍或慢 1000 倍。

---

<a id="1118_p2_building"></a>
## 1118_p2_building — 建筑主表（核心，33 列）

**用途**：所有建筑每一级的完整数据。一个建筑多行（每级一行）。

**关键字段**：
| 字段 | 含义 | 枚举/格式 | 关联 | bug |
|---|---|---|---|---|
| `A_INT_id` | 主键（含等级） | 111811xx（基地各级） | - | - |
| `A_INT_building_id` | 建筑模板 id（不含等级） | 6 位 | - | 同建筑所有等级的 building_id 相同；写错 → 跨级引用断 |
| `A_INT_type` | 建筑类型 | 1=主城建筑 / 其它值待确认 | - | - |
| `A_INT_lvl` | 当前等级 | 0/1/2/.../max_lvl | - | 0级 = 未建/破损态 |
| `A_INT_max_lvl` | 最大等级 | 30/35/40等 | - | 超过会卡 |
| `A_INT64_cost_time` | 升级时长（毫秒） | **INT64** | - | 填成秒 → 建筑秒完 |
| `A_ARR_cost_asset` | 升级消耗 | `[{"typ":"rss","id":11141001,"val":10000},...]` | 1114/1115 | id 失效 → 升级报错 |
| `A_ARR_add_asset` | 升级时额外给予 | 通常 `[]` | - | - |
| `A_MAP_requirement` | 升级前置 | `{"op":"and","args":[...]}` | - | 逻辑写反 → 永远不能升 |
| `A_ARR_status` | 建筑 buff（升级后生效） | `[{"typ":"buff","id":12112033,"arg1":0},{"typ":"power","id":xxx,"val":xxx}]` | 12xxx buff 表 | arg1/val 单位错 → buff 失效或溢出 |
| `A_ARR_function` | 建筑菜单功能 | `[1130func_id 列表]` | 1130 | function id 无效 → 菜单缺按钮 |
| `C_ARR_bubble` | 建筑气泡 | `[11311xxx]` | 1131 | - |
| `C_INT_fire` | 能否着火 | 0/1 | - | - |
| `A_INT_remove` | 可拆除 | 0/1 | - | - |
| `A_ARR_remove_rebate` | 拆除返还 | `[]` | - | - |
| `A_MAP_size` | 占地 | `{"x":10,"z":10}` | - | x/z 冲突别的建筑 → 地块错乱 |
| `C_MAP_next_unlock` | 下一级解锁描述 | LC map | 1011 | - |

**常见 bug**：
- **时长 INT64 溢出**：填成 int → 大于 21 亿毫秒（约 25 天）就溢出负数，建筑秒建。
- **function id 遗漏**：新加按钮但 1118.function 没同步 → 玩家建筑菜单缺按钮。
- **size 碰撞**：新建筑 size 改了但 1125 坑位没调 → 和相邻建筑重叠。

---

<a id="1119_p2_research"></a>
## 1119_p2_research — 科技主表

**字段**：
| 字段 | 含义 | 关联 | bug |
|---|---|---|---|
| `A_INT_id` | 主键（含等级） | - | - |
| `A_INT_research_id` | 科技模板 id | - | - |
| `A_INT_category` | 科技分类 | 1132 | 分类 id 写错 → 研究院分页错位 |
| `A_INT_lvl` / `A_INT_lvl_max` | 等级 | - | - |
| `A_INT64_cost_time` / `A_ARR_cost_asset` | 研究时长/消耗 | 1114/1115 | - |
| `A_MAP_requirement` | 前置条件 | 通常 `{"op":"ge","typ":"building","id":11181X,"val":N}` | - | - |
| `A_ARR_status` | buff 数组 | 12xxx | - |
| `A_MAP_path` | UI 坐标 `{"col":1,"row":1}` | - | 两科技同坐标 → 研究树视觉叠加 |
| `A_ARR_PreTech` | 前置科技 | `[{"id":111901}]` | 自表 | 前置 id 失效 → 永远无法研究 |
| `A_INT_ui_shape` | UI 形状 | - | - |
| `S_ARR_battle_skill` | 战斗技能（部分科技） | - | - |

**常见 bug**：
- **PreTech 循环引用**：A 前置 B，B 前置 A → 两个都研究不了。
- **requirement 建筑 id 错**：写成别建筑 → 永远不满足。

---

<a id="1120_p2_drop"></a>
## 1120_p2_drop — 掉落规则

**字段**：
| 字段 | 含义 | 格式 |
|---|---|---|
| `S_MAP_drop` | 掉落配置 | `{"typ":"single_all/single_group/...","num":N,"args":[{"typ":"item/rss/vm","id":xxx,"val":xxx,"wgt":xxx}]}` |

**typ 枚举**：
- `single_all`：从 args 里挑 num 个（每个都出）
- `single_group`：按权重抽一个
- `group_all`：按权重抽多个

**bug**：`wgt` 总和 0 → 掉落空；`num` 大于 args 长度 → 部分保底失败。

---

<a id="1121_p2_soldier"></a>
## 1121_p2_soldier — 兵种主表（35 列）

**关键字段**：
| 字段 | 含义 | 关联 | bug |
|---|---|---|---|
| `A_INT_id` | 主键（含等级） | - | - |
| `A_INT_category` | 兵种分类 | 1122 | - |
| `A_INT_hospital_priority` | 医院救治优先级 | - | 影响战损恢复顺序 |
| `A_INT_lvl` / `A_INT_lvl_max` | 等级 | - | - |
| `A_INT_train_cost_time` / `A_ARR_train_cost_asset` | 训练时长/消耗 | 1114/1115 | - |
| `A_INT_heal_cost_time` / `A_ARR_heal_cost_asset` | 救治时长/消耗 | - | - |
| `A_INT_upgrade_cost_time` / `A_ARR_upgrade_cost_asset` / `A_INT_upgrade_id` / `A_MAP_upgrade_requirement` | 升级字段组 | 升级到 upgrade_id 对应兵种 | 升级 id 错 → 升级成别的兵种 |
| `A_ARR_maintain_cost_asset` | 维护消耗 | - | - |
| `A_ARR_status` / `A_ARR_soldier_stat` | buff 和属性 | - | soldier_stat 写 `[{"typ":"atk","val":58},{"typ":"def","val":130}]` |
| `A_ARR_skill` | 兵种技能 | - | - |
| `C_MAP_skill_act` / `C_ARR_Attack_act` | 技能/攻击表现 | - | - |
| `C_INT_model_radius` / `C_INT_atk_radius` | 模型/攻击半径（mm） | - | - |
| `A_INT_arms_level` | 武装等级 | 1166/1167 | - |
| `A_INT_wonder_ratio` | 奇迹倍率 | - | - |

---

<a id="1122_p2_soldier_category"></a>
## 1122_p2_soldier_category — 兵种分类

**关键字段**：
- `A_INT_id` → `11221001`（打击手）、`11221002`（飙车族）、`11221003`（神枪手）、`11221004`（旗手）
- `A_STR_class`：`infantry` / `cavalry` / `ranged` 等代码 key
- `A_INT_city_defense`：城防加成
- `A_ARR_atk_coef` / `A_ARR_def_coef`：克制关系数组 `[{"id":11221003,"arg1":1.5},{"id":11221004,"arg1":0.5}]` = 对该类克制 1.5 倍 / 被克制 0.5 倍
- `A_ARR_arms`：武装 id 数组 → 1166

**bug**：克制系数配错 → 兵种平衡翻车。

---

<a id="1124_p2_speedup"></a>
## 1124_p2_speedup — 加速类型

| id | constant | 用途 |
|---|---|---|
| 11241001 | `general` | 通用加速 |
| 11241002 | `building` | 建筑加速 |
| 11241xxx | `research/soldier/...` | 各场景加速 |

道具（1111）的加速类 item 通过指向 1124 的 constant 决定能加速什么。

---

<a id="1125_p2_building_slot"></a>
## 1125_p2_building_slot — 建筑坑位

**字段**：
- `A_INT_preset`：坑位预设建筑 id（指向 1118）
- `A_MAP_position`：`{"x":40,"z":1}`
- `A_ARR_fog_unlock`：迷雾解锁条件
- `A_INT_pkg` / `A_INT_safe_box`：关联内购/金库
- `A_MAP_requirement`：解锁条件

---

<a id="1126_p2_city_building_skin"></a>
## 1126_p2_city_building_skin — 建筑皮肤

| 字段 | 含义 |
|---|---|
| `A_INT_building_id` | 指向 1118.building_id |
| `S_MAP_requirement` | 穿着条件（如 kvk_count=2） |
| `S_INT_duration` | 持续时长（-1=永久） |
| `S_INT_item_id` | 解锁需要的 item（1111） |
| `C_INT_is_default` | 是否默认 |

---

<a id="1127_p2_building_build"></a>
## 1127_p2_building_build — 建造条件

- `A_ARR_building_ids`：`[111817]` 可以造哪些建筑
- `A_INT_count` / `A_INT_count_max`：可造数量
- `A_MAP_requirement`：建造前置
- `A_ARR_unlock_cost`：解锁消耗

---

<a id="1128_p2_instant_price_asset"></a>
## 1128_p2_instant_price_asset / <a id="1129_p2_instant_price_time"></a>1129_p2_instant_price_time

**用途**：分段线性定价曲线（资源立刻补全/时间立刻购买）。

**格式**：`A_MAP_line` = `{"x1":5000000,"y1":7500,"x2":10000000,"y2":15000}` — 在 [x1,x2] 内按直线插值价。

**bug**：分段不覆盖全区间 → 某价位读不到，代码用默认值。

---

<a id="1130_p2_building_function"></a>
## 1130_p2_building_function — 建筑菜单按钮

| id | constant | 用途 |
|---|---|---|
| 11301001 | `info` | 建筑详情 |
| 11301002 | `upgrade` | 升级 |
| 11301037/70/71 | 其它 | 各种功能按钮 |

---

<a id="1131_p2_building_bubble"></a>
## 1131_p2_building_bubble — 建筑气泡

**字段**：
- `C_INT_type`：气泡类型
- `C_INT_show_priority`：显示优先级
- `C_INT_response_type`：点击响应（3=跳转）
- `A_MAP_requirement`：显示条件
- `C_STR_bg_color`：颜色

---

<a id="1132_p2_research_category"></a>
## 1132_p2_research_category — 科技分类

- `11321001`=军事、`11321002`=资源、`11321003`=城建等
- `C_STR_path`：banner 图路径（需在 1020 注册）

---

<a id="1133_p2_player_avatar"></a>
## 1133_p2_player_avatar — 玩家头像（需手动查）

**注**：抓取失败，建议直接打开表查字段。常规字段推测：id / display_key / requirement / item 解锁。

---

<a id="1135_p2_player_level"></a>
## 1135_p2_player_level — 玩家等级

- `A_INT_player_level`：等级
- `A_INT_player_exp`：所需经验
- `A_INT_stamina` / `A_INT_vitality`：体力/活力上限
- `A_ARR_add_asset`：升级奖励
- `A_ARR_status`：战力 power 配置

---

<a id="1137_p2_hero_stationed"></a>
## 1137_p2_hero_stationed — 英雄驻防点

- `A_INT_build_id`：哪个建筑可驻防
- `A_ARR_hero_unlock`：解锁英雄等级 `[20,25]`（需 hero 至少 20 级解锁）
- `A_INT_buff_group`：关联 1138 的 group_id
- `A_ARR_hero_talent_limit`：限定天赋 id（→ 1922）

---

<a id="1138_p2_hero_stationed_buff"></a>
## 1138_p2_hero_stationed_buff — 驻防 buff

- `A_INT_group_id`：分组（匹配 1137.buff_group）
- `A_INT_power_lv`：战力等级
- `A_ARR_buff`：buff 列表
- `A_ARR_epic_status`：史诗级 buff

---

<a id="1139_p2_hero_stationed_exercise"></a>
## 1139_p2_hero_stationed_exercise — 驻防演习

- `A_INT_exp_cost`：消耗经验
- `A_INT_discount` / `A_INT_discount_cd`：折扣与 CD
- `A_INT_buff_rate` / `A_INT_buff_last_time`：buff 倍率/持续时间
- `A_ARR_buff_list`：可触发 buff

---

<a id="1140_p2_city_map_grid"></a>
## 1140_p2_city_map_grid — 主城地块网格

- `A_INT_width` / `A_INT_height`：76x76 等
- `A_ARR_city_map_grid`：每格类型 0/1/2 的大数组
- `A_MAP_requirement`：激活条件（通常按基地等级/挖孔解锁）

---

<a id="1142_p2_avatar_frame"></a>
## 1142_p2_avatar_frame — 头像框

| 字段 | 含义 | 关联 | bug |
|---|---|---|---|
| `A_MAP_lc_name` | 头像框名 LC | 1011 ASSET | - |
| `A_MAP_unlock_requirement` | 解锁条件 | - | 全表 93 行 100% 是 `{"op":"ge","typ":"building","id":111811,"val":N}`（要塞等级） |
| `A_ARR_unlock_cost` | 解锁消耗 | 1111 | 头像框 item id 写错 → 领了用不了；val 永远 1 |
| `S_ARR_status_active` | 穿着时激活 buff | - | 93 行中 91 行为空，仅 2 个带 buff |
| `C_MAP_access` | 列表页"问号跳转" | 见下表 | 只有 2 种 typ |
| `C_INT_rarity` | 稀有度 | 9999=默认 | 允许重复（2026 新增 11421098/099/100 都是 1070） |
| `C_INT_dynamic` | 是否动态 | 0=静态(71)/1(15)/2(7) | 动态框用 spine |

**`C_MAP_access` 只有两种 typ**（本表不直接关联 1168）：

| typ | 含义 | 示例 | 占比 |
|---|---|---|---|
| `others` | 纯文本提示，无跳转 | `{"typ":"others","args":[{"typ":"lc","txt":"LC_MENU_frame_get_through_achievement_before"}]}` | 87/93 |
| `event` | 跳转到 2112 活动 | `{"typ":"event","args":[{"typ":"lc","txt":"LC_MENU_frame_get_desc_limit_event","id":21121395}]}` | 6/93 |

> **1142 不直接关 1168**：没有 `get_access_group` typ；1111 里 103 条 `class=avatar_frame` 的解锁道具 `A_INT_get_access_group` 全是 0；1168 表无 `C_STR_item_label` 以 1142/11421 开头的行。若策划说"关联 1168"，要求对方指具体字段。

**新增头像框 5 步**：

1. **1111 新增解锁道具**：`class=avatar_frame`、`A_INT_max_own=1`、`S_INT_use_now=1`、`effect=[{"typ":"avatar_frame","id":新 1142 id,"val":-1}, {"typ":"item","id":11111031,"val":1000}]`（val=-1 = 永久解锁；附赠 1000 CDs 是惯例）
2. **1142 新增行**：`A_INT_id=11421<下一可用>`（id 段不连续，要 grep `class=avatar_frame` 找真空位，不要直接 +1）
3. **1511 display_key**：动态头像框要提供动效资源 key
4. **1011 i18n**：补 name / desc / get_from；用 event 还要 `LC_MENU_frame_get_desc_limit_event` 之类 key
5. **2112 活动挂道具**：在 drop/package 投放 1111 解锁道具

**bug**：头像框礼包 item 解锁但 1142 unlock_cost 没写对应 item id → 头像框按钮灰；`A_INT_max_own=1` 会拒收第 2 份；val 写正整数会变成"激活一段时间"而非永久。

---

<a id="1143_p2_city_wall_flag"></a>
## 1143_p2_city_wall_flag / <a id="1144_p2_nation_flag"></a>1144_p2_nation_flag

- **1143**：城墙旗帜（玩家自选）
- **1144**：国家/地区旗帜（基于玩家国籍显示）

字段均含 display_key、lc_name、lc_desc、unlock_requirement、unlock_cost。

---

<a id="1145_p2_tavern_login_reward"></a>
## 1145-1148, 1150 酒馆系列

- **1145 tavern_login_reward**：周期登录奖励（`S_INT_cycle_order` 第几天 / `A_ARR_item_id` 奖励）
- **1146 tavern_bar_gift**：吧台礼物 gacha 池（`A_INT_pool_id` / `S_INT_weight`）
- **1147 tavern_story_gift**：剧情奖励（`A_INT_story_order` / `C_ARR_story_content`）
- **1148 tavern_trader_list**：商人交易（`A_ARR_item_pay` 付出 / `A_ARR_item_get` 获得 / `A_INT_weight`）
- **1150 tavern_top_pool**：池权重（`A_INT_pool_id` / `A_INT_weight`）

**bug**：gacha 池 weight 总和为 0 → 永远抽不到；pool_id 错配 → 领取走错池。

---

<a id="1151_p2_secret_shop_item"></a>
## 1151_p2_secret_shop_item — 神秘商店商品池

**字段**：
- `S_MAP_filter`：玩家过滤（建筑等级、vip 等）
- `A_INT_item_id`：指向 1111
- `S_INT_category`：档位分类
- `A_INT_chance`：进入概率
- `S_ARR_number_range` / `S_ARR_discount_type` / `S_ARR_discount_gems_chance` / `S_ARR_discount_rss`：数量+折扣权重
- `S_INT_gem_cost` / `S_INT_rss_cost`：钻石/资源价

**bug**：filter 不生效 → 新玩家看到高级商品；discount weight 配错 → 折扣分布异常。

---

<a id="1152_p2_banana_hologram"></a>
## 1152_p2_banana_hologram — 香蕉投影仪

- `A_INT_lvl`：等级
- `C_ARR_size`：占地 `[4,4]`
- `C_ARR_slot`：插槽位置
- `C_ARR_pass`：可通行格子
- `A_INT_battery_capacity` / `consumption`：电池容量/消耗

---

<a id="1153_p2_get_access"></a>
## 1153_p2_get_access — 获取途径单条

- `C_INT_jump`：是否可跳转
- `C_INT_iap_plate` / `C_INT_iap_display_type`：内购面板关联
- `C_INT_iaa_display_key`：IAA 跳转 key
- `C_MAP_show_requirement` / `C_MAP_lc_tip_desc`：展示条件与描述

**典型 id**：
- `11531001` 活动通用（带参数跳转）
- `11531002` 万能碎片兑换
- 常在 1111.get_access_group 里作为 args 的 id 引用

---

<a id="1154_p2_vip_shop"></a>
## 1154_p2_vip_shop — VIP 商店

- `A_INT_vip`：解锁 vip 等级
- `A_MAP_item` / `A_MAP_price` / `A_INT_discount` / `A_INT_limit`
- `A_INT_issvip`：是否 svip

---

<a id="1155_p2_collection"></a>
## 1155_p2_collection — 集卡主表

**字段**：
- `A_INT_class_id`：大类 id（1155000 = 兼容类；1155100/1155200 等 = 具体集卡分组）
- `A_INT_starlv` / `A_INT_star`：星级
- `A_INT_quality`：品质
- `A_INT_group_id`：指向 1156
- `A_ARR_cost_asset` / `A_MAP_transform_asset`：成本与转化
- `A_ARR_innate_effect`：天赋效果（持有即生效）
- `A_ARR_exhibition_effect`：展示效果（需上展台）
- `A_ARR_get_access`：获取途径
- `A_INT_coef` / `A_FLT_value`：战力系数/等效价值

---

<a id="1156_p2_collection_group"></a>
## 1156_p2_collection_group — 集卡分组

- `A_INT_group_id`：组 id（匹配 1155.group_id）
- `A_ARR_group`：组员集卡 id 数组
- `A_INT_sum_slv`：集齐等级
- `A_ARR_group_effect`：集齐效果

---

<a id="1157_p2_collection_gacha_package"></a>
## 1157_p2_collection_gacha_package / <a id="1158_p2_collection_gacha_reward"></a>1158_p2_collection_gacha_reward

**1157 字段**：
- `A_ARR_drop`：`[{"group":7,"wgt":200},...]` 按 group 抽
- `A_MAP_use_item`：消耗道具
- `A_MAP_use_cd`：CD 购买价
- `A_INT_cd_limit` / `A_INT_free` / `A_INT_daily_limit`：限制
- `A_STR_title`：LC key（英雄/集卡系列名）
- `A_STR_collection_url`：海报（1020 注册）
- `A_ARR_drop_guide`：引导池
- `A_ARR_show_collection`：UP 卡 id

**1158 字段**：group + 奖励 + probability（保底/概率）。

**bug**：drop.group 和 1158.group 不匹配 → 抽不出东西；show_collection 里 id 失效 → UI 显示空。

---

<a id="1159_p2_player_badge"></a>
## 1159_p2_player_badge — 玩家徽章

字段：`A_INT_type` / `A_INT_class` / `A_INT_quality` + unlock_requirement + unlock_cost。

---

<a id="1160_p2_banana_decorations"></a>
## 1160_p2_banana_decorations — 香蕉装饰

- `C_ARR_level_display`：`[{"level":1,"skin":15113621}]`
- `A_MAP_time_info`：限时装饰 `{"actv_id":21121114}` → 关联 2121 event

---

<a id="1161_p2_asset_retake"></a>
## 1161_p2_asset_retake / <a id="1162_p2_asset_retake_shop"></a>1162_p2_asset_retake_shop — 资产回收

**1161**：
- `A_MAP_give_asset` / `A_MAP_cost_asset`：回收规则（交 → 换）
- `S_INT_start_handle` / `S_INT_end_handle`：开始/结束处理（1=立即，2=延迟）
- `A_MAP_lc_reason`：原因文案

**1162**：回收商店（用回收得的货币换奖励）。

---

<a id="1163_p2_inner_coin"></a>
## 1163_p2_inner_coin — 方舟币（内购货币）

同 1114 结构。注意：玩家持有上限 INT64。

---

<a id="1164_p2_collection_power_buff"></a>
## 1164_p2_collection_power_buff — 集卡战力 buff

- `A_INT_need_power`：达到战力阈值
- `A_ARR_power_buff`：解锁的 buff
- `A_ARR_free_reward`：免费领取
- `A_INT_link_iap`：关联 iap（指向 2013）

---

<a id="1165_p2_stores"></a>
## 1165_p2_stores — 商店主表

注册各个商店（secret_shop/common_shop/...）的入口。`C_ARR_show_vm` 控制显示哪些货币切换。

---

<a id="1166_p2_soldier_arms"></a>
## 1166_p2_soldier_arms / <a id="1167_p2_arms_group"></a>1167_p2_arms_group — 兵种武装

**1166**：兵种的装备单件（对应部位 arms_slot 的每一级）
**1167**：武装组合（多件装备组成套装）

**字段**（1166）：
- `A_INT_soldier_category`：→ 1122
- `A_INT_arms_slot`：装备槽位
- `A_INT_order_in_slot` / `A_INT_quality` / `A_INT_lv` / `A_INT_max_lv`
- `A_ARR_cost_asset`：升级消耗
- `A_ARR_status`：buff
- `A_INT_arms_id`：武装逻辑 id
- `A_FLT_value`：等效价值（战力）

---

<a id="1168_p2_get_access_group"></a>
## 1168_p2_get_access_group — 获取途径分组（**杜绝手搓**）

**字段**：
- `A_INT_id`：主键（11681xxx）
- `A_STR_constant` / `C_STR_item_label`：标签
- `C_ARR_access_group`：`[{"id":11531047,"args":["11141001"]}]` — 引用 1153 的条目，args 传参（**不只是 item_id**：按 1153 条目语义可以是 1111 item id / 1114 资源 id / 2112 活动 id / 2011 IAP id 等）
- `C_MAP_lc_name` / `C_MAP_label_name`：文案

**bug**：新道具必须补 1168 → 否则背包点"问号"无跳转。节日礼包 item 经常漏登记。

---

<a id="1169_p2_city_area"></a>
## 1169_p2_city_area — 主城区域

- `A_ARR_position`：`[{"x":26,"z":0},{"x":50,"z":24}]` 区域矩形
- `A_MAP_requirement_chapter_quest`：章节任务前置
- `A_INT_requirement_fence` / `A_ARR_distory_fence`：栅栏解锁
- `A_ARR_fog_unlock`：雾区解锁位置
- `A_ARR_unlock_elements`：解锁后出现的元素

---

<a id="1170_p2_paradeground"></a>
## 1170_p2_paradeground / <a id="1172_p2_paradeground_soldiershow"></a>1172_p2_paradeground_soldiershow — 阅兵场

1170 字段结构同 1118 建筑，外加 `C_ARR_show_num` = `[数量,间距,宽度]`。
1172 = 阅兵场上展示的兵种模型参数（`C_INT_model_size` / `C_INT_type_num` / `C_INT_soldier_speed`）。

---

<a id="1171_p2_building_reset_v36"></a>
## 1171_p2_building_reset_v36 — 建筑布局重置模板

版本迭代时给老玩家的默认布局（`A_INT_building_id` + `A_ARR_position`）。每次主城大版本更新要手配。

---

<a id="1173_p2_chat_skin"></a>
## 1173_p2_chat_skin — 聊天铭牌皮肤

- `C_INT_display_key_chat`：**聊天框主体资源**（气泡背景）→ 1511
- `C_INT_display_key_show`：**道具图标资源**（背包里的图标）→ 1511
- `C_INT_display_order`：显示排序，数字越大越靠前（新增时在当前最小 -1）
- `A_MAP_lc_name` / `C_MAP_lc_desc`：铭牌名/描述，格式 `{"typ":"lc","txt":"LC_ITEM_xxx"}`
- `A_ARR_status_active`：激活条件，通常 `[]`
- `A_ARR_items`：**关联的 1111 道具 id 列表**，如 `[111111037]`
- `C_STR_color_quote_name` / `C_STR_color_quote_txt` / `C_STR_color_split_line` / `C_STR_color_dialogue_name` / `C_STR_color_dialogue_txt`：5 个 HEX 颜色
- `C_STR_user_labels`：用户标签，通常填 1173 id 本身
- `A_BOL_preview`：是否可预览，通常 `True`

**新增铭牌 4 表联动 SOP**：

```
Step 1: 1511 display_key — 新增 2 条
  ├─ 道具图标（仅道具图标）      → 1173.display_key_show + 1111.display_key
  └─ 聊天框主体（聊天框,铭牌资源） → 1173.display_key_chat
  美术稍后按 id 补资源，字段先填 "0"，C_MAP_text_image 填 "{}"

Step 2: 1111 item — 新增 1 条
  A_STR_class = "chat_skin"
  A_INT_quest_class = 30
  C_INT_display_key = Step 1 的道具图标 id
  C_INT_display_quality = 沿用近期铭牌的品质 id（如 15112564）
  A_MAP_lc_name / C_MAP_lc_desc → 1011 ITEM 段
  C_MAP_lc_usetip = {"typ":"lc","txt":"LC_ITEM_season_extra_reward_usedtip"} (通用)
  A_FLT_value = 2500
  A_INT_max_own=9999999, A_INT_max_get=1, A_INT_max_use=1

Step 3: 1173 chat_skin — 新增 1 条
  display_key_chat / display_key_show 指向 Step 1
  A_ARR_items = [Step 2 的 1111 id]
  C_INT_display_order = 上一条 -1
  5 个颜色字段（见下）
  C_STR_user_labels = 本条 1173 id

Step 4: 1011 i18n (ITEM 页签) — 新增 2 条
  name key: LC_ITEM_<节日缩写><年份>_nameplate_name (如 LC_ITEM_labor26_nameplate_name)
  desc key: LC_ITEM_<节日缩写><年份>_nameplate_desc
```

**5 色配色要点**：

- `quote_name` / `dialogue_name`：用铭牌**主色（较亮）**，名字醒目
- `quote_txt` / `dialogue_txt`：用**深色/暗色**，文字在铭牌背景上清晰可读
- `split_line`：取铭牌边框或装饰元素的颜色
- 同时保证在浅色/深色聊天背景下都有对比度

**bug**：`A_ARR_items` 指向的 1111 解锁道具缺 `A_STR_class=chat_skin` → 使用道具无效果；颜色值漏填 `#` → 客户端渲染默认白色；display_key_chat 和 display_key_show 填反 → 背包图标变聊天气泡。

---

<a id="1174_p2_daily_growth"></a>
## 1174_p2_daily_growth — 每日成长分

- `A_FLT_coef`：每件资产加分系数（0=不计分）
- `A_INT_ratio`：倍率
- `C_INT_show_type`：显示方式

被 1111 item.source 引用——定义某种道具算不算成长分。

---

<a id="1175_p2_safe_box"></a>
## 1175_p2_safe_box — 保险箱

- `A_ARR_lock`：锁定规则 `[{"val":12000,"arg1":30,"arg3":70}]`
- `A_ARR_awards` / `A_ARR_awards_destory`：正常奖励 / 销毁奖励

---

<a id="1176_p2_collection_platform"></a>
## 1176_p2_collection_platform — 集卡展台

- `A_INT_index_id`：展台索引
- `A_INT_lvl` / `A_INT_lvl_max`
- `A_ARR_upgrade_cost` / `A_ARR_reward` / `A_ARR_upgrade_reward`
- `A_INT_income_num_max`：最大产出数
- `A_INT_bubble`：气泡 id
- `A_INT_link_iap`：绑定 iap

---

<a id="1177_p2_citybeauty_reward"></a>
## 1177_p2_citybeauty_reward — 城市美化奖励

- `A_INT_threshold`：美化值阈值
- `S_ARR_awards`：达到阈值给的奖励

---

<a id="1178_p2_battery_research_skill"></a>
## 1178_p2_battery_research_skill — 电池研究技能树

字段类似 1119，但加了：
- `A_INT_xp` / `A_INT_max_xp`：技能经验
- `A_ARR_donate_cost` / `A_ARR_member_award`：联盟捐赠消耗与奖励
- `A_ARR_use_cost` / `A_INT_cd`：释放消耗与 CD

---

<a id="1179_p2_capsule_rss_convert_cost"></a>
## 1179_p2_capsule_rss_convert_cost — 胶囊资源兑换

- `A_INT_convert_times`：第几次兑换（0=首次免费）
- `A_ARR_convert_cost`：消耗
- `A_ARR_rss_get`：获得

---

<a id="1180_p2_map_emoji"></a>
## 1180_p2_map_emoji — 地图表情（行军表情）

**核心表**（用户高频配置的表，联动礼包核心）。

**字段**：
| 字段 | 含义 | 关联 | bug |
|---|---|---|---|
| `A_INT_id` | 主键（11800xxx） | - | - |
| `A_STR_constant` | 代码 key（`map_emoji_laugh` 等） | - | 拼错代码找不到 |
| `S_MAP_unlock_requirement` | 解锁条件 | - | - |
| `A_MAP_lc_name` | LC 名 | 1011 ITEM（LC_ITEM_map_emoji_xxx） | - |
| `C_MAP_lc_desc` | 描述 | - | - |
| `A_INT_emoji_type` | 表情类型（1=静态/其他=动态） | - | - |
| `A_INT_last_time` | 持续时长（毫秒） | 5000 等 | - |
| `C_INT_priority` | 显示优先级 | 1000+ | - |
| `C_INT_access_group` | 获取途径 | → 1168 | - |
| `A_INT_year_group` | 年份分组（换档用） | - | 节日表情按 year_group 隔离 |
| `C_INT_display_key_emoji` | 客户端 key | - | - |

**bug**：`year_group` 漏配 → 往年表情混在当年组。跨节日平移 emoji_id（同一 id 改用途）→ 老玩家背包残留旧表情。

---

<a id="1181_p2_collection_filter"></a>
## 1181_p2_collection_filter — 集卡筛选器

- `C_INT_group`：分组（1=品质类）
- `C_MAP_arg`：`{"typ":"quality","ids":[1]}`
- `C_STR_color` / `C_STR_bg_color`：颜色

---

<a id="1182_p2_collection_break_achievement"></a>
## 1182_p2_collection_break_achievement — （空表/未启用）

主 Tab `qa` 无字段。新功能占位。

---

<a id="1183_item_bag_classification"></a>
## 1183_item_bag_classification — 背包分类页

- `A_INT_page`：页码
- `A_ARR_quintuple`：归入此页的 item 列表
- `A_ARR_rss`：归入的资源
- `A_INT_unlock`：解锁条件

---

<a id="1184_p2_theme_decoratiton"></a>
## 1184_p2_theme_decoratiton — 主题装饰

字段同 1142 avatar_frame，多了 `A_STR_category`（个人主题/战争主题等）。

---

<a id="1196_research_fast_up"></a>
## 1196_research_fast_up — 合服科技追赶

- `A_INT_server_min_day` / `A_INT_server_max_day`：合服后开服天数区间
- `A_INT_category`：科技分类 → 1132
- `A_INT_min_power` / `A_INT_max_power`：玩家战力区间
- `A_ARR_cost_asset`：追赶消耗

---

<a id="1197_p2_wonder_reward_retake"></a>
## 1197_p2_wonder_reward_retake — 跨版本奇迹奖励回归

玩家粒度的资产找回表。`S_INT_player_id` 为玩家 id。仅在重大版本扣除后补发。

---

<a id="1198_p2_tavern_change"></a>
## 1198_p2_tavern_change / <a id="1199_p2_research_change"></a>1199_p2_research_change

版本改动的补偿表。1198 = 酒馆改动补偿（按 building_id+lvl），1199 = 科技改动补偿（按 research_id+lvl）。

---

## 跨表引用拓扑（11_asset 主出入向）

```
1110 asset ─── 所有 typ 注册中心
                 │
                 ▼
1111 item  ─┬─ 被 2135 礼包 / 1113 商店 / 2011 iap / 奖励数组 引用
            ├─ effect/source 指向 1114/1115/1174/1168
            └─ get_access_group 指向 1168 → 1153

1114 rss / 1115 vm / 1116 xp / 1117 recover
            ──被 1111/1113/1118/1119/1121/几乎所有消耗奖励字段引用

1118 building ─┬─ function → 1130 / bubble → 1131 / size 影响 1125 1140
                ├─ lvl 影响 requirement "typ=building"（全库最多）
                └─ 被 1126 皮肤 / 1127 建造 / 1171 重置引用

1119 research ─┬─ category → 1132
                ├─ PreTech 自引用
                └─ 被 requirement "typ=research" 全库引用

1121 soldier ── category → 1122；arms_level → 1166；upgrade_id 自引用

1155-1158/1164/1176/1181/1182 集卡系
1157.drop.group ↔ 1158.group 必须对应

1168 get_access_group ── 道具入口中枢，被 1111/1114 广泛引用

1180 map_emoji ── 被 2135 节日礼包 / 2112 活动引用
```

---

## Jira 工单常见自检路径

| 现象 | 先查的表 | 定位方法 |
|---|---|---|
| 道具显示原 LC key | 1111 + 1011 | 找 1111 对应行的 lc_name，去 1011 ITEM Tab 搜 key |
| 道具图标错 | 1111 | 检查 `C_INT_display_key` |
| 使用道具无效果 | 1111 | `A_MAP_category_param.effect` 里 id 是否有效 |
| 新道具背包找不到来源 | 1168 + 1153 | 1168 是否已登记 → 1153 条目是否存在 |
| 建筑升级消耗错 | 1118 | `A_ARR_cost_asset` 的 rss/vm id + val |
| 建筑无法升级（按钮灰） | 1118 | `A_MAP_requirement` 条件恒假？lvl 是否达到 max_lvl？ |
| 建筑功能按钮缺失 | 1118 + 1130 | 1118.function 里是否包含 1130 对应 id |
| 科技无法研究 | 1119 | `A_ARR_PreTech` 前置是否失效 / `A_MAP_requirement` 建筑等级 |
| 兵种克制异常 | 1122 | `A_ARR_atk_coef` / `A_ARR_def_coef` |
| 兵种训练数据错 | 1121 | `train_cost_time` 单位（毫秒） / `train_cost_asset` id |
| 商店商品扣错货币 | 1113 / 1151 / 1154 | `A_MAP_cost_asset` 或 `S_INT_gem_cost/rss_cost` |
| 神秘商店新玩家看到高级货 | 1151 | `S_MAP_filter` 是否含 building 等级 |
| 头像框礼包解锁失败 | 1142 | `A_ARR_unlock_cost` item id 对应 1111 是否存在 |
| 行军表情礼包道具用不了 | 1180 + 1111 | 1180 emoji_id 和 1111 里礼包 item 的 effect 关联 |
| 集卡 gacha 抽不出 | 1157 + 1158 | 1157.drop.group 和 1158.group 是否对应 |
| 合服后资源归零 | 1114 | `A_INT64_max_own` 是否 INT64 而非 INT |
| 新渠道新道具显示不出来 | 1111 + 1168 | country_use_type 配置 |
| 节日结束道具残留 | 1180 / 1111 | `year_group` 隔离 / `max_own=0` 清空 |

---

**维护建议**：跨表引用断裂（id 失效、group 不对应）是本文件夹 80% bug 的根因。写新配置时**先把 id 跨表搜一遍**（可用 [id-lookup-plugin](../../.claude/skills/id-lookup-plugin)）。
