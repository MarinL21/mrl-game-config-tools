# 13_p2_map 大地图/NPC/竞技场/行军特效/装饰 配置规范

> **用途**：P2 世界大地图上的**所有对象**——主城、NPC 野怪/采集点、联盟资源矿、部落建筑、过关、探索遗迹、竞技场、迷雾解锁、行军特效/装饰/套装、铭牌皮肤等。
>
> **Jira 自检场景**：野怪等级不对 / 联盟矿定位错 / 行军特效不生效 / 主城皮肤穿不了 / 地图过关不开 / 探索奖励错 / 竞技场机器人战力异常 / 迷雾解锁不触发 / 节日主城套装错配。

> **前置**：字段前缀约定见 [`10_p2_const.md`](./10_p2_const.md)。

---

## 表清单（按子系统分组）

### 地图结构 & 区域
| 表号 | 用途 |
|---|---|
| [1310](#1310) | map 类型分发主表（类似 1110 asset） |
| [1332](#1332) | 固定点位（氏族总部、基地等绝对坐标对象） |
| [1340](#1340) | 联盟中心排行（空） |
| [1335](#1335) | 地图标记（玩家标记类型） |
| [map_p2_region](#map_region) | 地图区域划分（外圈/内圈，颜色→area_id） |
| [map_p2_zone_index_color](#map_color) | 颜色16进制 → area_id 映射 |

### 主城皮肤 / 特效 / 套装
| 表号 | 用途 |
|---|---|
| [1312](#1312) | 主城皮肤 |
| [1387](#1387) | 主城特效 |
| [1388](#1388) | 主城套装装饰件 |
| [1389](#1389) | 主城套装集合 |
| [1392](#1392) | 主城范围特效 |
| [1360](#1360) | 地图单位渲染参数（model_radius/atk_radius） |
| [1379](#1379) | 地图单位音效 |

### 行军特效（核心）
| 表号 | 用途 |
|---|---|
| [1365](#1365) | **行军特效主表** |
| [1390](#1390) | 行军特效装饰件 |
| [1391](#1391) | 行军特效套装 |

### 地图表情奖励（联动）
| 表号 | 用途 |
|---|---|
| [1393](#1393) | 表情收集奖励（按年） |
| [1394](#1394) | 表情收集引导（按年） |

### NPC 野怪 & 采集点
| 表号 | 用途 |
|---|---|
| [1313](#1313) | NPC 刷新区域 |
| [1314](#1314) | NPC 刷新带（等级分布） |
| [1315](#1315) | NPC 移动规则 |
| [1316](#1316) | NPC 采集点（采集参数） |
| [1317](#1317) | NPC 部队（野怪战斗参数） |
| [1318](#1318) | NPC 城寨 |
| [1319](#1319) | 搜索配置（搜索某类 NPC） |
| [1321](#1321) | 行军类型 |
| [1322](#1322) | NPC 移动路径点 |
| [1323](#1323) | 特殊部队 |
| [1324](#1324) | 特殊城市分类 |
| [1326](#1326) | NPC 大类（buff_category，空） |
| [1333](#1333) | NPC 部队分类（普通/精英/boss） |
| [1334](#1334) | NPC 采集点分类 |
| [1363](#1363) | NPC 克制分类 |
| [1364](#1364) | 雷达机器人（PVE 战斗） |

### 联盟 & 部落（Horde）& 领地
| 表号 | 用途 |
|---|---|
| [1337](#1337) | 领地建筑（火箭基地/中继点等） |
| [1338](#1338) | 联盟资源矿 |
| [1339](#1339) | 联盟哨塔消耗 |
| [1345](#1345) | 部落火车厢 |
| [1353](#1353) | 氏族修铁路连接 |
| [1372](#1372) | 建筑单位（中立建筑占位/打断机关） |
| [1378](#1378) | 奇迹附加 buff（联盟捐赠） |

### 过关 / 探索 / 迷雾解锁
| 表号 | 用途 |
|---|---|
| [1346](#1346) | 区域过关 |
| [1347](#1347) | 探索遗迹 |
| [1348](#1348) | 探索分类 |
| [1349](#1349) | 探索奖励（空） |
| [1367](#1367) | 迷雾解锁档位奖励 |
| [1368](#1368) | 迷雾解锁排名奖励 |
| [1369](#1369) | 迷雾解锁主线任务 |
| [1370](#1370) | 英雄雕像 |
| [1371](#1371) | 外建筑（据点） |
| [1377](#1377) | 图鉴奖励 |
| [1330](#1330) | 废墟玩法 |
| [1336](#1336) | 火车路径点 |

### 竞技场
| 表号 | 用途 |
|---|---|
| [1357](#1357) | 全能竞技场积分奖励 |
| [1358](#1358) | 全能竞技场机器人 |
| [1359](#1359) | 精英竞技场机器人 |
| [1361](#1361) | 英雄竞技场积分 |
| [1362](#1362) | 英雄竞技场机器人 |
| [1373](#1373) | 精英竞技场地图 |
| [1374](#1374) | 精英竞技场建筑 |
| [1375](#1375) | 精英竞技场 AI |
| [1376](#1376) | 精英竞技场奖励 |

### 运输 / 补给
| 表号 | 用途 |
|---|---|
| [1355](#1355) | 运输补给车 |
| [1356](#1356) | 运输异变刷新 |

### 部队阵型 & 地图筛选 UI
| 表号 | 用途 |
|---|---|
| [1331](#1331) | 部队阵型 |
| [1342](#1342) | 地图单位筛选器 |
| [1343](#1343) | 地图单位图例 |
| [1344](#1344) | 玩家建筑（空） |
| [1341](#1341) | 战利品分配 |

### 地下世界 (Underworld)
| 表号 | 用途 |
|---|---|
| [1381](#1381) | 地下采集点 |
| [1382](#1382) | 地下 NPC 刷新带 |
| [1383](#1383) | 地下 NPC 刷新区 |
| [1384](#1384) | 地下搜索 |
| [1385](#1385) | 地下地图筛选 |
| [1386](#1386) | 地下地图图例 |

### 其它
| 表号 | 用途 |
|---|---|
| [1329](#1329) | 追击距离时间 |
| [1366](#1366) | 聊天头衔 |

---

<a id="1310"></a>
## 1310_p2_map — 地图对象分发主表

注册每个 `A_STR_typ` 指向哪张表（类似 1110）。例如 `1316`=npc_gather、`1311`=city、`1317`=npc_troop。

新增地图对象类型必须先在这里注册，否则全库引用找不到。

---

<a id="1312"></a>
## 1312_p2_city_skin — 主城皮肤（核心）

**字段**：
| 字段 | 含义 | bug |
|---|---|---|
| `A_STR_constant` | code key（`default` 等） | - |
| `C_INT_class` | 皮肤大类 | - |
| `A_INT_skin_quality` | 品质 0-5 | - |
| `A_INT_dyeing_skin` | 染色皮肤 id | 有染色则指向另一行；无则 0 |
| `C_ARR_skin_level` | 每个基地等级的美术 `[{"level":1,"skin":15111047},{"level":4,"skin":15111048},...]` | 漏配某等级 → 该级显示默认皮肤 |
| `A_INT_collision_radius` / `A_INT_exclusion_radius` | 碰撞/排他半径 | 改大 → 与邻建筑重叠 |
| `A_ARR_status_active` | 穿戴 buff | - |
| `A_ARR_innate_effect` | 被动效果 | - |
| `A_ARR_items` | 解锁道具 | 1111 | item 没挂对 → 付费了穿不上 |
| `A_INT_can_transformation` | 可变形 0/1 | - |
| `A_ARR_transformation_cost` | 变形消耗 | - |
| `A_ARR_bond_effect` | 套装羁绊效果 | - |
| `A_INT_suit_id` | 套装 id | 1389 | - |
| `A_INT_activity_id` | 活动 id | 2121 | 限时皮肤关联节日 event |

**常见 bug**：节日主城皮肤 `skin_level` 漏配某基地级别 → 高级主城变回默认；`A_INT_suit_id` 和 1389.A_ARR_items 不对应 → 集齐套装不触发羁绊。

---

<a id="1313"></a><a id="1314"></a><a id="1315"></a><a id="1316"></a><a id="1317"></a>
## 1313-1317 NPC 刷新体系

**拓扑**：
```
1313 zone (大区域矩形)  ──> 1314 band (某等级的刷新带)  ──> 1333 class (哪类 NPC)
                                │
                                ▼
                          1317 npc_troop 实际野怪参数
                                │
                                ▼
                          1315 npc_moving 移动规则
```

### 1313_p2_map_npc_refresh_zone
- `A_MAP_rectangle_zone`：`{"x1":0,"x2":120000,"y1":0,"y2":120000}`
- `A_INT_band_id`：指向 1314
- `A_INT_lvl`：区域等级

### 1314_p2_map_npc_refresh_band
- `S_ARR_refresh`：`[{"minlv":1,"maxlv":1,"id":13340001,"wt":70}]` → 1334 采集类/1333 部队类
- `S_STR_band_type`：`"MapUnitNpcGatherable"` / `"MapUnitUgNpcGatherAble"` 等
- `S_INT_count`：每 zone 刷多少
- `S_STR_spawn_rule`：`"NormalRefresh"`

### 1317_p2_npc_troop（野怪战斗核心，35 列）
关键字段：
- `A_INT_class_id`：指向 1333
- `A_INT_rank`：等级
- `A_ARR_troop_composition`：野怪部队组成 `[{"typ":"soldier","id":11217502,"val":500}]`
- `A_ARR_hero_composition`：野怪英雄 `[{"typ":"hero_data","id":19200301,"lv":1}]`
- `S_MAP_drop_first_blood` / `S_MAP_drop_attack` / `S_MAP_drop_rally`：一血/攻击/集结掉落
- `A_ARR_status`：野怪 buff
- `S_INT_attacknum`：攻击次数
- `S_MAP_robot_rally_requirement` / `S_INT_robot_rally_group` / `S_ARR_robot_troop_composition`：机器人集结参数
- `A_INT_protect_time`：保护时间

**bug**：
- 野怪 level 和 troop_composition 不匹配 → 战力异常。
- drop_rally 和 drop_attack 写反 → 集结奖励发错。
- hero_composition 里英雄 id 指向废弃英雄（1920）→ 野怪直接崩。

### 1318_p2_npc_city — 野蛮人城寨
结构类似 1317，额外有 `A_MAP_requirement` 控制开启条件。

### 1319_p2_search — 搜索配置
- `C_INT_type`：搜索类型
- `A_ARR_npc_id`：可被搜出的 NPC id 数组（→ 1317）
- `S_INT_search_radius`：搜索半径（mm）
- `S_INT_create` / `S_INT_create_max_number` / `S_INT_create_cooldown`：创建规则

---

<a id="1321"></a>
## 1321_p2_march_type — 行军类型

定义行军目的枚举（采集/攻击/集结/运输/侦察等）。代码按 id 分支处理。

---

<a id="1322"></a>
## 1322_p2_map_npc_moving_point — NPC 路径点
用于巡逻 NPC 的移动点位。

<a id="1323"></a>
## 1323_p2_special_troop — 特殊部队
特殊玩法（运输车、火箭车等）的部队参数。

<a id="1324"></a>
## 1324_p2_special_city_category — 特殊城市分类
分类特殊地图对象（火箭基地、哨所、遗迹类）。

<a id="1326"></a>
## 1326_p2_npc_class — NPC 分类（空表）
主 tab `buff_category` 无数据。预留分类表。

<a id="1327"></a>
## 1327_p2_special_building — 特殊建筑

<a id="1328"></a>
## 1328_p2_troop_show_info — 部队展示信息
显示参数（模型大小等）。

<a id="1329"></a>
## 1329_p2_chasing_distance_time — 追击距离时间
行军线刷新参数 `A_INT_add_val_ge` + `A_INT_refresh_frame`。

<a id="1330"></a>
## 1330_p2_ruin_play — 废墟玩法
- `A_STR_special_city_class`：`ruin`
- `S_MAP_drop_attack` / `S_MAP_drop_scout`：攻击/侦察掉落
- `S_INT_monster_pro` / `S_INT_monster_class`：怪物概率/分类

<a id="1331"></a>
## 1331_p2_troop_formation — 部队阵型
阵型参数（unit 数量范围、LOD 等级）。

<a id="1332"></a>
## 1332_p2_map_fixed_point — 固定点位（核心）

**用途**：地图上绝对坐标的固定对象（氏族总部、火箭基地、中继点、特殊城市等）。

**关键字段**：
- `A_STR_object_type`：`ruin`/`city`/`train_point` 等
- `A_MAP_position`：`{"x":795000,"z":3625000}`（大地图绝对坐标）
- `A_INT_npc_id` → 1317；`A_INT_sp_id` → 1324；`A_INT_terr_id` → 1337
- `A_ARR_horde_own`：归属部落列表（0=无主）
- `S_ARR_attach_buff` / `A_ARR_attach_donate_buff`：附加 buff 和捐赠 buff
- `A_INT_defence_npc_id`：守卫 NPC

**bug**：新地图版本调整坐标但 1171 建筑重置表没同步 → 合服/迁服玩家主城落在新 1332 位置但自家建筑还在旧点。

<a id="1333"></a>
## 1333_p2_npc_troop_class — NPC 部队分类

- `A_STR_constant`：`normal_monster`/`elite_monster`/`boss` 等
- `A_INT_troopid_start`：该类起始 npc_troop id
- `C_INT_troop_type`：部队 type
- `S_INT_battle_damage_wound`：战伤比例（1000 = 100%）
- `A_ARR_counter_class`：克制的克制类 → 1363
- `A_INT_reconver_fight_end`：战斗结束后是否恢复
- `S_INT_return_asset_ratio`：资源返还比例

<a id="1334"></a>
## 1334_p2_npc_gather_class — 采集点分类

`A_INT_start_index`：采集点 id 段起始（13161000/13161010 等）。1316 数据就按此分类。

<a id="1335"></a>
## 1335_p2_map_mark — 地图标记
玩家可用的标记类型（重要/朋友/进攻等）。

<a id="1336"></a>
## 1336_p2_train_point — 火车路径点
部落火车的行驶节点 `A_MAP_coord` 和 `A_INT_next_id`（链表）。

<a id="1337"></a>
## 1337_p2_territory_building — 领地建筑

关键字段：
- `A_INT_sp_id` → 1324
- `A_INT_border`：建造时间
- `A_INT_hp`：耐久
- `A_ARR_cost_putout_coin` / `A_ARR_cost_putout_cd`：熄火消耗
- `A_INT_cond_occupy`：占领条件
- `A_INT_honor_coin_reward`：荣誉币奖励
- `S_INT_open_last`：开启持续时间

<a id="1338"></a>
## 1338_p2_union_rss_spot — 联盟资源矿

- `A_INT_speed`：NPC 采集速度
- `A_INT_rss_id` → 1114
- `A_INT_sp_id` → 1324
- `A_INT_lvl`：矿等级
- `S_INT_player_speed`：玩家采集速度
- `S_INT_npc_id` → 1317（保护 NPC）

<a id="1339"></a>
## 1339_p2_union_tower_cost — 联盟哨塔消耗

- `A_INT_union_building_id` → 1337/13440001 等
- `A_INT_order`：建造顺序
- `A_ARR_cost`：`[{"typ":"vm","id":11151003,"val":30000}]`
- `A_INT_member_requirement`：最低成员数
- `A_INT_power_requirement`：最低战力

<a id="1340"></a>
## 1340_p2_union_center_rank — 联盟中心排名（空表）

<a id="1341"></a>
## 1341_p2_loot_be_assigned — 战利品分配

- `A_INT_building_type` → 1337
- `A_ARR_content`：战利品道具
- `A_INT_num`：数量

<a id="1342"></a>
## 1342_p2_map_unit_filter — 地图筛选器

- `C_INT_controlled`：是否受控
- `C_ARR_filter_info_low` / `C_ARR_filter_info_high` / `C_ARR_filter_info_all`：低/高缩放级别过滤信息
  - 格式：`[{"unit":"MapUnitRallyTroop","relation":"union"}]`

<a id="1343"></a>
## 1343_p2_map_unit_legend — 地图图例

- `C_ARR_filter`：关联 filter id 数组
- `C_ARR_filter_detail`：`[{"filter_id":1,"type":"low"}]`

<a id="1344"></a>
## 1344_p2_map_player_building — 玩家地图建筑（空，kvk6 测试）

<a id="1345"></a>
## 1345_p2_horde_train — 部落火车
车厢参数（火车头/车厢/货厢），字段类似建筑（bubble/function/size）。

<a id="1346"></a>
## 1346_p2_pass — 区域过关

- `A_INT_lv`：关卡等级
- `A_ARR_connect_area`：`[7,11]`（连接的两个 area_id）
- `A_INT_area_id`：关卡 id
- `C_STR_prefab`：美术 prefab 路径
- `A_MAP_pos`：位置
- `C_INT_pass_towards`：朝向
- `C_INT_world_trend_unlock`：天下大势解锁 id → 2311
- `A_INT_map_id_connect`：连接的 fixed_point id → 1332

**bug**：天下大势阶段 id 和 1346 没对齐 → 玩家打通阶段但过关没开。

<a id="1347"></a><a id="1348"></a><a id="1349"></a>
## 1347-1349 探索遗迹

### 1347 explore_relic
- `A_INT_categories` → 1348
- `A_MAP_pos`：绝对坐标
- `A_INT_cost_time`：探索时长

### 1348 explore_categories
- `A_STR_constant`：`rocket_relic_lv1` 等
- `A_INT_class` / `A_INT_mail_id`：分类/探索报告邮件
- `A_MAP_requirement`：开启条件
- `C_INT_display_key` / `C_INT_display_key_bubble`：UI key

### 1349 explore_relic_reward
**空表**，无字段。

<a id="1353"></a>
## 1353_p2_fix_rail — 氏族修铁路

- `A_INT_relate_to_building_id` → 1332（氏族总部）
- `A_MAP_coord`：`{"position":{"x":xxx,"z":xxx},"fixlink":{"x":xxx,"z":xxx}}`

<a id="1355"></a><a id="1356"></a>
## 1355-1356 运输补给

### 1355 transport_supplies（补给车，18 列）
- `A_INT_special_troop` → 1323
- `A_INT_base_lv`：仓库等级
- `A_INT_truck_quality`：车质量
- `A_ARR_transport_reward1`-`reward6`：六个等级奖励
- `A_ARR_guard_reward` / `S_ARR_plunder_reward`：护送/掠夺奖励
- `A_ARR_npc_troop_num`：NPC 刷新参数 `[{"typ":13179011,"val":300,"speed":50,"area":1}]`
- `A_INT_truck_quality_weights`：质量权重
- `A_MAP_server_info`：生效服 schema

### 1356 transport_mutant_refresh
变异车刷新规则。

<a id="1357"></a><a id="1358"></a><a id="1359"></a>
## 1357-1364 竞技场系列

### 1357 all_round_arena_score / 1361 hero_arena_score（积分）
- `A_INT_differ`：积分差值
- `A_INT_win_point` / `A_INT_fail_point`：胜负积分
- `S_MAP_drop_win` / `S_MAP_drop_fail`：胜负掉落

### 1358/1359/1362 各竞技场机器人
- `A_MAP_lc_name`：机器人名（LC）
- `A_INT_score` / `A_INT_power`：积分/战力
- `A_ARR_npc_troop` → 1317
- `A_INT_avatar` → 1133

### 1363 npc_counter_class
克制分类 id（普通野怪/巨猿 等）。

### 1364 radar_robot — 雷达机器人
雷达扫描出的 NPC 战斗参数（troop_composition + hero_composition + status + resource_min/max）。

<a id="1360"></a>
## 1360_p2_map_unit_render — 地图单位渲染

`C_INT_model_radius` / `C_INT_atk_radius`：模型/攻击半径（mm）。被 1121 soldier 的 model_radius 引用。

---

<a id="1365"></a>
## 1365_p2_march_effect — 行军特效主表（**高频配置**）

**字段**（核心）：
| 字段 | 含义 | 关联 | bug |
|---|---|---|---|
| `A_INT_id` | 主键 | 13650xxx | - |
| `A_STR_constant` | code key | - | 可空 |
| `C_INT_class` | 特效大类 | 0=默认/1=普通/… | - |
| `C_INT_skin_quality` | 品质 | 0-5 | - |
| `C_INT_display_key` | 图标 | - | - |
| `C_INT_effect_key` / `C_INT_effect_special_key` / `C_INT_effect_exhibit_key` | 普通/特殊/展示用特效 key | 1512（直接 equals，无前缀） | effect_key 写错 / 1512 没登记 → 行军时看不到特效 |
| `A_MAP_lc_name` / `C_MAP_lc_desc` | LC | 1011 | - |
| `A_ARR_status_active` | 穿戴 buff | 12xxx | - |
| `A_ARR_innate_effect` | 被动效果 | 12xxx | - |
| `A_ARR_items` | 解锁道具 id 列表（多件=升级解锁） | 1111 | `[11117128,11117129,...]` — 用户高频配置的字段 |
| `A_INT_npc_troop_id` | 关联 NPC troop id（展示用） | 1317 | - |
| `C_INT_show_afterimage` | 是否显示残影 | 0/1 | - |
| `C_INT_show_type` | 展示方式 | 1/其它 | - |
| `A_INT_suit_id` | 所属套装 | 1391 | 0=非套装件 |
| `A_INT_country_use_type` | 区服 | 0/1/2 | - |

**常见 bug**（见用户 memory）：
- 行军特效礼包 item 和 1365.items 数量不对应 → 升级级别错。
- 节日 effect_key 换档时忘了 bump → 玩家看到老特效。
- `suit_id` 错配 → 套装羁绊不触发。

---

<a id="1366"></a>
## 1366_p2_chat_title — 聊天头衔

- `C_INT_type`：头衔类型
- `A_MAP_lc_name`：头衔名
- `S_MAP_unlock_requirement`：解锁（overlord/cross_overlord 等）

<a id="1367"></a><a id="1368"></a><a id="1369"></a>
## 1367-1369 迷雾解锁

### 1367 mist_unlock_reward — 档位奖励
- `A_INT_area_ratio`：解锁面积比例
- `A_ARR_awards`：奖励
- `C_INT_important`：重要标记

### 1368 mist_unlock_rank_reward — 排名奖励
- `A_INT_group` / `A_INT_rank_start` / `A_INT_rank_end`：分组+排名区间

### 1369 mist_unlock_main_quest — 主线任务
- `A_MAP_fincond`：完成条件（counter 定义，→ 1014）
- `A_MAP_map_unlock_mist_reward`：解锁奖励 `{"typ":"wreckage_unlock"}` / `{"typ":"mist_unlock","id":...}`

<a id="1370"></a>
## 1370_p2_hero_statue — 英雄雕像

- `A_INT_group_id`：分组
- `A_INT_building_id` → 1118
- `A_INT_star` / `A_INT_star_max`：星级
- `A_ARR_hero_statue_skill` → 1944
- `A_INT_hero` → 1920
- `S_MAP_unlock_requirement`：解锁（通常 `{"typ":"herotalent","id":xxx,"val":100}`）

<a id="1371"></a>
## 1371_p2_outbuilding — 外建筑

- `A_INT_requirement`：战力阈值
- `S_ARR_status`：buff

<a id="1372"></a>
## 1372_p2_building_unit — 建筑单位
中立建筑占位、组队 boss 打断机关等（`A_STR_constant` = `interrupt_building` 等）。

<a id="1373"></a><a id="1374"></a><a id="1375"></a><a id="1376"></a>
## 1373-1376 精英竞技场

### 1373 elite_arena_map
- `S_ARR_buffs`：地图 buff（带 `effect_time`）
- `A_INT_max_battle_time`：最大战斗时间（秒）
- `A_ARR_building` → 1374
- `S_MAP_ai` → 1375
- `A_ARR_owner_pos` / `A_ARR_target_pos`：出生点位
- `A_INT_map_reward` → 1376

### 1374 elite_arena_building
中立建筑（血量、位置、buff）。

### 1375 elite_arena_ai
AI 行为逻辑（`S_ARR_aim` = 目标列表）。

### 1376 elite_arena_reward
`S_MAP_drop_win` / `S_MAP_drop_fail`。

<a id="1377"></a>
## 1377_p2_illustrate_reward — 图鉴奖励
- `A_INT_type`：图鉴类型
- `A_INT_get_num`：收集数量阈值
- `A_ARR_awards`：奖励

<a id="1378"></a>
## 1378_p2_wonder_attach_buff — 奇迹附加 buff（联盟捐赠）
- `A_INT_group`：分组
- `A_MAP_buff`：具体 buff
- `A_MAP_donate_base`：捐赠基础消耗
- `A_INT_max_xp`：最大经验
- `A_MAP_donate_reward`：捐赠奖励（CD）

<a id="1379"></a>
## 1379_p2_map_unit_sound — 地图单位音效
`C_STR_sound_walk` / `C_STR_sound_click`：Wwise 事件名。

---

<a id="1381"></a><a id="1382"></a><a id="1383"></a><a id="1384"></a><a id="1385"></a><a id="1386"></a>
## 1381-1386 地下世界（uw_）

字段结构对应地表 1316/1314/1313/1319/1342/1343 的地下版。关键差异：
- `S_STR_band_type` = `MapUnitUgNpcGatherAble`（uw 前缀）
- 1381 `A_INT_mining_group`：共享采集池

<a id="1387"></a>
## 1387_p2_city_effect — 主城特效
- `A_STR_constant`：`empty`（无特效兼容）
- `C_INT_effect_key`：特效 key
- `A_ARR_status_active`：穿戴 buff（常见 `{"typ":"citybeauty_score",...}`）

<a id="1388"></a>
## 1388_p2_city_suit_decoration — 套装装饰件
- `C_INT_type`：类型（1=翅膀 / 2=炮弹 等）
- `C_STR_code_effect`：代码特效名（`ScienceSkin2025ALv2` 等）
- `A_INT_suit_id` → 1389

<a id="1389"></a>
## 1389_p2_city_suit — 套装集合

**结构**（以真实行 `13891001 2025科技节主城套装` 为准）：

| 字段 | 含义 | 样本 |
|---|---|---|
| `A_INT_id` | 套装 id | `13891001` |
| `C_STR_comment` | 策划备注 | `2025科技节主城套装` |
| `C_INT_display_key` | 展示 key | → 1511 |
| `A_INT_skin_quality` | 套装品质 | 5 |
| `A_MAP_lc_name` | 套装名 LC | `{"typ":"lc","txt":"LC_EVENT_tech_2025_city_suit_name"}` |
| `A_ARR_status_active` | 穿戴效果 | `[{"typ":"buff","id":12117006,"val":1000}]` |
| `A_ARR_items` | **组件 id 数组**（含 1312 皮肤件 id + 1388 装饰件 id） | `[13121063,13121064,13881001,13881002,13881003]` |
| `A_INT_suit` | **基础皮肤 id**（集齐 items 后激活的 1312 底子） | `13121065` |
| `A_INT_preview` | 预览展示 | 1 |
| `C_ARR_position` / `C_ARR_scale` / `C_ARR_lightwidth` | 视觉参数 | - |

**关键理解**：`A_ARR_items` 是集齐条件（皮肤件 + 装饰件混装），`A_INT_suit` 是集齐后激活的**底座皮肤 id**（1312）。两个字段都要配对，缺一套装不触发。

<a id="1390"></a>
## 1390_p2_march_effect_decoration — 行军特效装饰件
同 1388 结构，但针对行军特效。`A_INT_suit_id` → 1391。

<a id="1391"></a>
## 1391_p2_march_effect_suit — 行军特效套装
- `A_ARR_items`：套装组件 id（含 1365 行军特效件 + 1390 装饰件）
- 例：`[13650139,13900001,13900002,13900003]` = 行军特效主体 + 3 个装饰
- `A_INT_suit`：套装标识

**bug**：A_ARR_items 里 13650xxx（1365 id）和 13900xxx（1390 id）任一失效 → 套装不集齐不触发羁绊。

<a id="1392"></a>
## 1392_p2_city_effect_extent — 主城范围特效
高阶版主城特效，额外的范围参数：
- `A_ARR_extent_active`：范围激活 buff
- `A_INT_size` / `A_INT_inner_size`：外径/内径
- `A_INT_bond_effect_extennt`：羁绊扩展

<a id="1393"></a>
## 1393_p2_emoji_reward — 表情收集奖励

**字段**：
- `A_INT_decorate_type`：装饰类型（14 = 表情）
- `A_INT_year_group_id`：年份（2024/2025/2026）
- `A_MAP_fincond`：完成条件 `{"cat":101428002,"arg":{"ids":[2024]},"val":2,"op":"ge"}` — 2024 年表情收集≥2
- `A_ARR_buff`：达成奖励 buff

**bug**：year_group_id 写错 → 跨年收集计数错乱（混入别年）。

<a id="1394"></a>
## 1394_p2_emoji_guide — 表情收集引导

- `A_ARR_items`：该年份所有 emoji 对应的 1111 item id 列表
- `A_ARR_emoji_reward` → 1393
- `A_INT_max_number`：年度表情总数
- `A_INT_year_group`：年份

**bug**：
- `A_INT_max_number` 小于 `A_ARR_items` 长度 → 奖励达成错位。
- `A_ARR_items` 里 item id 不对应 1111 中 `year_group` = 同年的表情 → 收集数错算。

---

<a id="map_region"></a>
## map_p2_region — 地图区域划分（非 id 命名表）

特殊命名——**非数字 id 命名**。维护大地图颜色带 → area_id 的映射。

<a id="map_color"></a>
## map_p2_zone_index_color — 颜色索引
16 进制颜色 → area_id。

---

## 跨表引用拓扑

```
1310 ─── 所有地图对象 typ 分发

1313 zone → 1314 band → 1317 npc_troop / 1316 npc_gather
                          │                │
                          ▼                ▼
                    1333 class         1334 class

1332 fixed_point ─┬─ object_type=ruin → 1330/1337
                   ├─ npc_id → 1317
                   ├─ sp_id → 1324
                   └─ terr_id → 1337

1337 territory_building ← 1338 rss_spot ← 1339 tower_cost
                                │
                                ▼
                          1341 loot_be_assigned

1346 pass.map_id_connect → 1332
1346 pass.world_trend_unlock → 2311 situation

1365 march_effect ─┬─ items → 1111
                    ├─ suit_id → 1391 suit
                    └─ status_active/innate_effect → 12xxx buff

1391 suit.items ── 组合 1365 + 1390

1312 city_skin ─┬─ skin_level[i].skin = 美术 displaykey
                 ├─ suit_id → 1389
                 └─ activity_id → 2121

1393 emoji_reward ── year_group_id 必须对齐 1394
1394 emoji_guide ── items 必须对齐 1111 中 year_group 相同的表情

1373 elite_arena_map ─┬─ building → 1374
                       ├─ ai → 1375
                       └─ map_reward → 1376

1370 hero_statue ── hero → 1920；building_id → 1118（阅兵场类）

1367/68/69 迷雾 ── fincond 指向 1014 counter
```

---

## Jira 工单常见自检路径

| 现象 | 先查的表 | 定位方法 |
|---|---|---|
| 野怪等级不对 | 1317 + 1314 | 1317.rank vs 1314.refresh 的 minlv/maxlv |
| 野怪部队战力错 | 1317 | troop_composition 里 soldier val |
| 联盟矿采集速度慢 | 1338 | `A_INT_speed` + `S_INT_player_speed` |
| 联盟哨塔消耗错 | 1339 | `A_ARR_cost` 里 vm id + val |
| 行军特效不显示 | 1365 | `C_INT_effect_key` 是否有效 美术资源 |
| 行军特效套装不集齐 | 1391 + 1365 + 1390 | items 数组 id 链 |
| 主城皮肤某级显示异常 | 1312 | `C_ARR_skin_level` 是否覆盖该等级 |
| 主城套装羁绊不触发 | 1389 | `A_ARR_items` 是否含所有组件 id |
| 节日主城特效不生效 | 1387 / 1388 | `A_INT_suit_id` 对齐 1389 |
| 表情奖励不计数 | 1393 + 1394 + 1111 | year_group 必须三表一致 |
| 过关不开 | 1346 | `C_INT_world_trend_unlock` 对齐 2311 situation 阶段 |
| 探索遗迹无奖励 | 1348 + 1347 + 邮件 | categories 的 mail_id 和 lc_explore_desc |
| 竞技场机器人战力异常 | 1358/1359/1362/1364 | `A_INT_power` 和 npc_troop 是否匹配 |
| 精英竞技场地图 buff 错 | 1373 | `S_ARR_buffs` 的 `effect_time` 和 buff id |
| 合服后大地图建筑位置错 | 1332 / 1171 | fixed_point 坐标和 1171 建筑重置表是否同步 |
| 部落火车错节 | 1345 + 1336 | train_point.next_id 链表 |
| 地下采集不刷 | 1381 + 1382 + 1383 | uw 版本的三件套是否齐 |
| 迷雾任务不计 | 1369 + 1014 | `A_MAP_fincond.cat` 对齐 1014 counter |
| 领地建筑熄火后 buff 还在 | 1337 + 1378 | `A_ARR_attach_donate_buff` 生命周期 |

---

**维护建议**：地图 NPC 刷新涉及 1313/1314/1317/1333/1334 多表联动，改一张表必须校验上下游。行军特效和主城套装的 items 数组断链是高频 bug 点。
