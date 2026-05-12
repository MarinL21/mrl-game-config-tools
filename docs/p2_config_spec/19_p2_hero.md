# 19_p2_hero 英雄/技能/天赋/装备/皮肤 配置规范

> **用途**：P2 英雄体系——英雄数据、星级、技能、天赋、天赋树、装备、词条、皮肤、招募 gacha、雕像技能、召唤兽、共享技能。被 `typ:"hero"` / `typ:"herotalent"` / `typ:"hero_data"` / `typ:"equipment"` 等广泛引用。
>
> **Jira 自检场景**：英雄技能不触发 / 天赋加点失效 / 技能伤害计算错 / 招募池 up 卡不出 / 装备词条 buff 错 / 皮肤穿不上 / 雕像技能不生效 / 合服英雄属性错 / 装备升级材料消耗异常。

> **前置**：字段前缀约定见 [`10_p2_const.md`](./10_p2_const.md)。

---

## 表清单（按子系统分组）

### 英雄主体
| 表号 | 用途 |
|---|---|
| [1920](#1920) | **英雄主表**（46 列） |
| [1921](#1921) | 英雄星级等级（每星每级的属性/技能解锁） |
| [1925](#1925) | 英雄升星配置 |

### 天赋
| 表号 | 用途 |
|---|---|
| [1922](#1922) | 天赋点 |
| [1923](#1923) | 天赋树（领袖/征服等） |
| [1933](#1933) | 双天赋重置 |
| [1947](#1947) | 天赋推荐（空） |

### 技能
| 表号 | 用途 |
|---|---|
| [1924](#1924) | 英雄技能主表 |
| [1926](#1926) | 技能触发条件 |
| [1927](#1927) | 技能效果（空） |
| [1928](#1928) | 英雄 FX（空） |
| [1932](#1932) | 技能渲染（抓取失败） |
| [1944](#1944) | 雕像技能 |
| [1945](#1945) | 特殊描述（震慑/沉默等） |
| [1946](#1946) | 召唤兽 |
| [1951](#1951) | 共享技能（空） |
| [1952](#1952) | 技能元素（电/大电等） |

### 招募 Gacha
| 表号 | 用途 |
|---|---|
| [1929](#1929) | 招募池 |
| [1930](#1930) | 招募奖励 |
| [1931](#1931) | 特殊保底 |

### 装备（战装实验）
| 表号 | 用途 |
|---|---|
| [1934](#1934) | 装备蓝图（空） |
| [1935](#1935) | 装备主表 |
| [1936](#1936) | 装备等级 |
| [1937](#1937) | 词条 buff |
| [1938](#1938) | 词条库 |
| [1939](#1939) | 词条技能 |
| [1940](#1940) | 词条技能效果 |
| [1941](#1941) | 词条技能触发条件 |
| [1942](#1942) | 词条技能渲染 |

### UI / 筛选
| 表号 | 用途 |
|---|---|
| [1943](#1943) | 组队评分等级 |
| [1948](#1948) | 英雄筛选器 |
| [1949](#1949) | 装备筛选器 |

### 皮肤
| 表号 | 用途 |
|---|---|
| [1950](#1950) | 英雄皮肤 |

---

<a id="1920"></a>
## 1920_p2_hero_data — 英雄主表（46 列，核心）

**字段**：
| 字段 | 含义 | 枚举/格式 | 关联 | bug |
|---|---|---|---|---|
| `A_INT_id` | 英雄 id | 19201xxx | - | - |
| `A_STR_constant` | code key | 可空 | - | - |
| `A_INT_if_staff` | 是否 staff（顾问类）| 0/1 | - | - |
| `C_INT_staff_display_key` | staff 图标 | - | - | - |
| `A_ARR_hero_staff_skill` | staff 技能 | - | - | - |
| `A_STR_type` | 英雄类型 | `player`（玩家）等 | - | - |
| `A_INT_quality` | 品质 | 1/2/3/4/5 | - | 2=蓝 3=紫 4=橙 5=红 |
| `C_INT_display_key` | 头像 | - | - | - |
| `C_INT_display_order` | 排序 | - | - | - |
| `C_INT_enable` | 启用 | 0=隐藏 / 1=上线 | - | 新英雄 enable=0 线上不可见 |
| `C_MAP_showcond` | 显示条件 | - | - | - |
| `A_INT_max_level` | 最大等级 | 通常 40/60 | - | - |
| `A_INT_level_group` | 等级组 | 指向 1921 | 1921 | 改等级曲线改 level_group |
| `A_INT_star_group` | 升星组 | 指向 1925 | 1925 | - |
| `A_INT_hero_skin_id` | 默认皮肤 | 指向 1950 | 1950 | - |
| `A_MAP_lc_name` / `C_MAP_lc_desc` / `C_MAP_lc_story` | 名字/描述/故事 LC | - | 1011 HERO | - |
| `A_MAP_unit` | 英雄单位道具 | `{"typ":"item","id":11116201,"val":10}` | 1111 | 招募需要的灵魂石 item id |
| `A_ARR_hero_active_skill` | 主动技能 id 列表 | | 1924 | 技能 id 失效 → 释放崩溃 |
| `A_ARR_hero_passive_skill` | 被动技能 id 列表 | 3 个 | 1924 | - |
| `A_ARR_hero_talent_skill` | 天赋技能 id 列表 | 3 个 | 1924 | - |
| `A_ARR_hero_talent_tree` | 天赋树 id 列表 | 3 个 | 1923 | - |
| `A_ARR_get_access` | 获取途径 | `[{"id":11531002}]` | 1153 | - |
| `A_ARR_talent_skill_unlock_need` | 天赋技能解锁所需点数 | `[50,50,50]` | - | - |
| `C_INT_act_cd` | 行动 CD | - | - | - |
| `A_ARR_hero_attack_skill` | 普攻技能 id | | 1924 | - |
| `A_INT_buff_power_c` | 战力基础系数 | - | - | 合服英雄战力偏差常来源于此 |
| `C_INT_map_unit_render` | 地图渲染 | → 1360 | 1360 | - |
| `C_ARR_hero_sound` | 音效 | 数组 `[{"typ":"click_march","txt":"Play_xxx"}]` | Wwise | 音效事件名写错 → 静音 |
| `A_INT_double_talent_showtype` | 双天赋展示 | 0/其它 | - | - |
| `A_STR_banner_url` / `A_STR_hero_url` | 招募海报/立绘 URL | - | 1020 | 路径变要 bump 1020 version |
| `C_MAP_hero_ability` | 能力标签 | `{"typ":3,"arg1":15,...}` | - | - |
| `C_ARR_hero_team_score` | 组队评分权重 | 4 浮点数 | - | - |
| `N_INT_team_recommend` / `S_ARR_talent_recommend` | 推荐配置 | - | - | - |
| `C_STR_hero_guide` | 英雄引导 key | - | - | - |
| `A_INT_country_use_type` | 区服 | 0/1/2 | - | - |
| `A_INT_troop` | 所属兵种 | → 1122 | 1122 | - |
| `C_MAP_hero_team_trooprating` | 组队对兵种适配 | `{"11221001":1,"11221002":1,"11221003":1,"11221004":1.6}` | 1122 | - |
| `C_INT_hero_scorefix` | 评分修正 | - | - | - |
| `C_INT_on_demand` | 按需加载 | 0/1 | - | - |
| `A_ARR_share_skills` | 共享技能 | → 1951 | 1951 | - |
| `C_INT_effect_displaykey` | 英雄特效 | - | - | - |

**常见 bug**：
- **enable=0 上线**：新英雄配好但 enable 字段忘改 1 → 玩家看不到（招募池也抽不出）。
- **skill id 指向废弃/未配技能**：`hero_active_skill/passive_skill/talent_skill` 里任意 id 指向 1924 不存在的 id → 运行时崩。
- **hero_skin_id 未配**：显示裸模。
- **get_access 漏配**：新英雄 1153 get_access 没加对应路径 → 玩家不知道在哪招募。

---

<a id="1921"></a>
## 1921_p2_hero_star_level — 英雄星级等级

**字段**：
- `A_INT_level_group`：等级组（被 1920.level_group 引用）
- `A_INT_lvl` / `A_INT_star`：等级/星级
- `A_INT_exp`：升级所需经验
- `A_INT_point`：获得的天赋点
- `A_ARR_rage`：怒气成长 `[{"typ":"attack","val":70},{"typ":"hitted","val":30}]`
- `A_ARR_status`：属性 + power 数组
- `A_ARR_hero_skill`：达到该等级解锁的技能 id 列表

**bug**：每级 `A_ARR_hero_skill` 不是所有级别都需要；只在解锁时填。漏填 → 技能永远不解锁。

---

<a id="1922"></a>
## 1922_p2_hero_talent — 天赋点

**字段**：
- `A_INT_talent_id`：天赋模板 id
- `A_INT_talent_tree`：所属天赋树 → 1923
- `A_INT_lvl` / `A_INT_lvl_max`：天赋等级
- `A_INT_cost_point`：消耗点数
- `A_MAP_requirement`：前置天赋 `{"op":"ge","typ":"talent_id","id":xxx,"val":xxx}`
- `A_ARR_status`：天赋 buff
- `S_ARR_skill`：天赋激活的技能 id
- `A_MAP_path`：UI 坐标 `{"col":1,"row":1}`
- `C_ARR_talent_data`：前端展示数值（百分比）
- `A_INT_recommend_index`：推荐顺位

**bug**：前置天赋 id 失效 → 永远加不上；UI path 冲突 → 天赋树显示错乱。

---

<a id="1923"></a>
## 1923_p2_hero_talent_tree — 天赋树

- `A_INT_talent_skill`：天赋树激活的技能 → 1924
- `A_INT_talent_skill_unlock_need`：解锁所需点数（50）
- `A_INT_talent_tree_coef`：系数

---

<a id="1924"></a>
## 1924_p2_hero_skill — 技能主表（28 列，核心）

**字段**：
| 字段 | 含义 | 枚举 | 关联 | bug |
|---|---|---|---|---|
| `A_INT_id` | 主键 | 19240xxx（含 lv） | - | - |
| `A_INT_group` | 技能组（不含 lv） | - | - | - |
| `A_ARR_upgrade_need` | 升级材料 | `[{"typ":"item","id":11116201,"val":10}]` | 1111 | - |
| `A_STR_class` | 技能类型 | `hero_active`/`hero_passive`/`hero_talent`/`hero_attack` | - | class 错 → 技能找错触发时机 |
| `A_INT_lv` / `A_INT_max_lv` | 等级 | - | - | - |
| `A_INT_cd` | CD（秒） | - | - | - |
| `A_INT_cd_type` | CD 类型 | 1/2/3 | - | - |
| `A_STR_target_troops` | 目标部队 | `round_enemy_troop`/`self_troop`/`all` 等 | - | 枚举写错 → 找不到目标 |
| `A_INT_troops_radius` | 生效半径（mm） | 6500 等 | - | - |
| `A_INT_troops_count` | 生效部队数 | - | - | - |
| `S_INT_troops_select` | 目标选择策略 | - | - | - |
| `A_STR_soldier_select` | 选择哪种兵 | `all`/其它 | - | - |
| `S_ARR_target_soldier` | 目标兵种 | → 1121 | 1121 | - |
| `A_INT_soldier_count` | 目标兵数量 | - | - | - |
| `A_ARR_status` | buff | `[{"typ":"power","id":12141005,"val":1400}]` | 12xxx | - |
| `C_INT_skill_render` | 技能渲染 | → 1932 | 1932 | - |
| `C_ARR_skill_data` | 展示数据 | `[75,0.02]` | - | 数值和 status 不匹配 → 前端显示和实际效果不符 |
| `A_ARR_condition` | 触发条件 | → 1926 | 1926 | - |
| `A_ARR_skill_effect` | 技能效果 id | → 1927 | 1927 | - |
| `A_INT_log_display_level` | 日志等级 | - | - | - |
| `S_INT_active_skill_rage_select` | 怒气释放选择 | - | - | - |
| `S_INT_save_skill` | 保存技能 | - | - | - |

**bug**：
- **class 和实际效果不符**：配 `hero_passive` 但 cd/target 都填了 → 代码按被动处理，主动释放无效。
- **status 的 buff id 失效**：战斗时报错但不崩（buff 没应用）。
- **skill_data 显示值和 status 值不同步**：策划描述"攻击+20%"但实际是 +200%。

---

<a id="1925"></a>
## 1925_p2_hero_star — 升星表

- `A_INT_level_group`：等级组（匹配 1920.star_group）
- `A_INT_star_lvl` / `A_INT_max_star`：星级
- `A_INT_exp`：升星所需经验
- `A_ARR_star_cost_lucky`：升星消耗材料 id 列表（→ 1111）`[11116104,11116105,11116106]`
- `A_INT_point`：获得的额外天赋点
- `A_ARR_status`：升星属性
- `A_ARR_hero_skill`：升星解锁的技能

---

<a id="1926"></a>
## 1926_p2_skill_condition — 技能触发条件

- `A_STR_condition_type`：`normal_atk`（普攻触发）/ `skill_atk`（技能后）/ 其它
- `A_FLT_cast_prob`：触发概率（0.25 = 25%）
- `A_ARR_condition_args`：条件参数

**bug**：概率 >1 时代码可能崩；条件 type 拼错 → 技能永远不触发。

---

<a id="1927"></a>
## 1927_p2_skill_effect — 技能效果（**空表主 Tab**）

抓取到的主 Tab 为空 — 但此表有 9 个可见 Tab，真实数据在别的 Tab。请直接开表查。

<a id="1928"></a>
## 1928_p2_hero_fx — 英雄 FX（主 Tab 空）

类似，建议直接开表查。

<a id="1932"></a>
## 1932_p2_skill_render — 技能渲染（抓取失败）

抓取失败。预测字段：id + display_key + 动画 key + 音效 key。

---

<a id="1929"></a>
## 1929_p2_hero_gacha_pool — 招募池

**字段**：
- `A_ARR_drop`：按 group 抽 `[{"group":2,"wgt":1990},{"group":3,"wgt":3870},...]` → 1930
- `A_INT_use_item`：消耗道具 → 1111（通常是招募卡）
- `A_STR_title`：池名 LC
- `A_STR_hero_url` / `A_STR_banner_url`：立绘 URL（需 1020 注册）
- `A_INT_type`：池类型 1=普通/2=稀有
- `A_INT_drop_special`：特殊保底 → 1931
- `A_ARR_lifetime`：生效时间区间 `[0,99999]` = 永久；`[0,170]` = 限时
- `S_MAP_requirement`：前置条件

---

<a id="1930"></a>
## 1930_p2_hero_gacha_reward — 招募奖励

**字段**：
- `A_INT_group`：分组（匹配 1929.drop.group）
- `A_MAP_asset`：奖励内容（`{"typ":"item","id":xxx,"val":xxx}`）
- `A_INT_probability`：组内权重
- `A_STR_group_desc`：分组描述 LC
- `A_STR_group_color_desc` / `A_INT_group_color`：颜色

**bug**：group 和 1929 的 drop.group 错配 → 抽不出来；probability 总和 0 → 该组抽空。

---

<a id="1931"></a>
## 1931_p2_hero_gacha_special — 招募特殊保底

- `A_INT_drop_special`：保底 id（匹配 1929.drop_special）
- `A_STR_typ`：保底类型（`cycle` 循环保底等）
- `A_ARR_arg`：保底参数 `[0,100]` = 每抽 100 次触发
- `A_STR_desc`：描述

---

<a id="1933"></a>
## 1933_p2_hero_double_talent — 双天赋重置

- `A_INT_level_group` / `A_INT_max_exchange_times` / `A_INT_exchange_times`：重置次数配置
- `A_INT_need_hero_unit`：需要的英雄灵魂石
- `A_INT_point`：消耗点数
- `A_ARR_need_extra_item`：额外消耗

<a id="1947"></a>
## 1947_p2_hero_talent_recommend — 推荐天赋（空）

主 Tab 空。

---

<a id="1934"></a><a id="1935"></a><a id="1936"></a>
## 1934-1936 装备三件套

### 1934 blueprint — 蓝图（主 Tab 空）

### 1935 hero_equipment — 装备主表
- `A_INT_level_group`：等级组 → 1936
- `A_INT_quality`：品质
- `A_STR_pic_url`：图标 URL
- `C_INT_display_quality`：前端品质色
- `A_INT_equipment_slot`：装备槽位
- `A_INT_addition_effect`：附加效果（词条 buff）→ 1937
- `S_STR_version`：起始版本
- `A_INT_quality_requirement`：升级到该品质所需等级
- `A_INT_optional_skills`：可选技能 → 1939
- `A_INT_suit_id`：套装 → 2157 活动装备套装
- `C_INT_type_id`：类型

### 1936 hero_equipment_lvl — 装备等级
- `A_INT_level_group`：等级组（匹配 1935.level_group）
- `A_INT_lvl` / `A_INT_max_lvl`：等级
- `A_ARR_upgrade_cost`：升级材料 `[{"typ":"material","id":19345xxx,"val":x}]`
- `A_ARR_status`：属性
- `A_ARR_transform_asset`：转化资产
- `A_INT_skill_lvl`：对应技能等级
- `S_ARR_bossrush_status`：boss rush 模式属性
- `A_ARR_convert_xp` / `A_ARR_downgrade_asset` / `C_INT_downgrade_ratio`：降级回收
- `A_ARR_breakthrough` / `A_INT_breakthrough_skill_lv`：突破

---

<a id="1937"></a><a id="1938"></a><a id="1939"></a><a id="1940"></a><a id="1941"></a><a id="1942"></a>
## 1937-1942 词条体系

### 1937 equipment_entry_buff — 词条 buff 池
- `A_ARR_entry_effect1/2/3/4`：4 级词条效果
- `A_ARR_entry_skill`：词条技能 → 1939
- `A_ARR_optional_skills`：可选技能
- `A_ARR_entry_attribute1~4`：词条属性 4 等级
- `A_ARR_breakthrough_effect/attribute`：突破属性
- `A_ARR_recommend_attribute1/2`：推荐属性

### 1938 equipment_entry_library — 词条库
- `A_INT_buff_type` / `A_INT_buff`：词条类型和 buff 指向 → 1939
- `A_INT_status_min` / `A_INT_status_max` / `A_INT_status_diff`：属性范围
- `A_ARR_power_coef`：战力系数

### 1939 equipment_entry_skill — 词条技能（32 列）
字段类似 1924 hero_skill。关键：
- `A_STR_class`：`equipment_active`
- `A_STR_type`：`active`
- `S_INT_skill_use_limit`：使用上限（-1=无限）
- `S_INT_battle_use`：战斗内次数
- `S_INT_daily_use_limit`：日次数上限

### 1940 skill_effect — 技能效果
- `A_STR_effect_type`：`control`（控制）/`damage` 等
- `A_ARR_effect_args`：参数 `[100,510,3]`（例：100% 概率，510 半径，3 秒）
- `A_INT_clean_type`：清除类型
- `A_INT_effect_time`：效果时长
- `A_ARR_gfx`：特效 `[{"typ":"gfx","id":15120321,"val":1}]`

### 1941 skill_condition — 触发条件
同 1926 结构。

### 1942 skill_render — 渲染
- `C_INT_skill_act`：动作 key
- `C_INT_damage_show_delay`：伤害延迟
- `C_INT_break`：可否打断
- `C_STR_skill_sound`：音效事件

---

<a id="1943"></a>
## 1943_p2_hero_team_score_grade — 组队评分等级

- `C_INT_score`：评分阈值（120=S+, 110=S）
- `C_STR_color`：颜色
- `C_INT_display_key`：UI key

---

<a id="1944"></a>
## 1944_p2_hero_statue_skill — 英雄雕像技能

字段同 1924 hero_skill，`A_STR_class` = `hero_statue`。通过 1370 hero_statue 引用。

---

<a id="1945"></a>
## 1945_p2_hero_special_description — 特殊描述

定义 `震慑`/`沉默`/`眩晕` 等效果的名字与描述，被 1924/1939 skill 的 tooltip 引用。

---

<a id="1946"></a>
## 1946_p2_skill_summon — 召唤兽

- `S_INT_attack_troop` → 1317（NPC 部队）
- `S_INT_troop_num`：召唤数量
- `S_INT_rule`：召唤规则（1/2/3...）
- `S_INT_ai`：AI 类型
- `S_ARR_guard`：守护目标
- `S_ARR_formation`：阵型
- `S_INT_guard_radius` / `S_INT_patrol_radius`：守护/巡逻半径
- `S_ARR_effect`：额外效果

---

<a id="1948"></a><a id="1949"></a>
## 1948-1949 筛选器

- `C_INT_group`：分组（1=排序 / 2=筛选）
- `C_INT_arg`：参数值
- `C_MAP_lc_name`：LC

---

<a id="1950"></a>
## 1950_p2_hero_skin — 英雄皮肤

**字段**：
- `A_INT_hero_id` → 1920
- `A_INT_class`：皮肤类别 1/其它
- `C_INT_display_skin_colour_key`：皮肤颜色 key
- `A_ARR_status_active`：穿戴 buff
- `A_ARR_skin_owned_buff`：拥有时 buff
- `A_ARR_items`：解锁道具 → 1111
- `A_MAP_showcond`：展示条件
- `A_INT_activity_select`：所属活动 → 2121/2112
- `C_INT_area` / `C_INT_camera_angle` / `C_MAP_hero_actv_place`：展示位置参数
- `A_STR_gacha_banner_url` / `A_STR_gacha_reward_url` / `A_STR_gacha_select_url`：招募各界面图
- `C_ARR_tag_show`：标签显示

**bug**：皮肤礼包 item 和 1950.items 对应错 → 付费买不上；activity_select 填错 → 皮肤提前或延后显示。

---

<a id="1951"></a>
## 1951_p2_hero_share_skills — 共享技能（主 Tab 空）

被 1920.share_skills 引用的结构，实际数据可能在其它 Tab。

---

<a id="1952"></a>
## 1952_p2_hero_skill_elements — 技能元素

- `A_INT_duration`：元素存在时长
- `A_INT_priority`：元素优先级
- `A_INT_priority_attenuation`：衰减
- `A_ARR_merge_ingredients`：合成素材 `[19521001,19521001]`（两个小电合成大电）

用于"元素反应"类技能。

---

## 跨表引用拓扑

```
1920 hero_data ─┬─ level_group → 1921 / star_group → 1925
                 ├─ hero_skin_id → 1950
                 ├─ talent_tree[0..2] → 1923
                 ├─ active_skill/passive_skill/talent_skill/attack_skill → 1924
                 ├─ unit → 1111
                 ├─ get_access → 1153
                 ├─ troop → 1122
                 ├─ map_unit_render → 1360
                 └─ share_skills → 1951

1921 ← 由 1920.level_group 指向
1925 ← 由 1920.star_group 指向
1923 talent_tree.talent_skill → 1924

1924 hero_skill ─┬─ class 决定行为类型
                  ├─ status → 12xxx buff
                  ├─ condition → 1926
                  ├─ skill_effect → 1927
                  ├─ skill_render → 1932
                  └─ upgrade_need → 1111

1929 gacha_pool.drop.group ↔ 1930 gacha_reward.group
1929 drop_special → 1931

1935 equipment.addition_effect → 1937
1935 level_group ↔ 1936 hero_equipment_lvl
1935 optional_skills → 1939
1937 entry_skill → 1939
1939 equipment_entry_skill:
  ├─ condition → 1941
  ├─ skill_effect → 1940
  └─ skill_render → 1942

1950 skin.hero_id → 1920
1950 skin.activity_select → 2121/2112

1946 summon.attack_troop → 1317
```

---

## Jira 工单常见自检路径

| 现象 | 先查的表 | 定位方法 |
|---|---|---|
| 英雄线上不可见 | 1920 | `C_INT_enable` / `A_INT_country_use_type` |
| 英雄技能不触发 | 1924 + 1926 | class 枚举 / condition cast_prob |
| 英雄天赋加点无效 | 1922 | `A_MAP_requirement` 前置天赋是否失效 |
| 英雄招募池 up 卡不出 | 1929 + 1930 | drop.group 和 reward.group 对应 |
| 招募保底不触发 | 1929 + 1931 | drop_special 关联 |
| 装备属性不对 | 1936 | `A_ARR_status` 的 buff_id + arg1 |
| 装备升级材料错 | 1936 | `A_ARR_upgrade_cost` 的 material id |
| 词条 buff 不生效 | 1937 / 1938 / 1939 | 词条三表联动：buff_type/buff → skill |
| 装备技能打不出来 | 1939 + 1940 + 1941 | class=`equipment_active`；condition 概率 |
| 雕像技能不触发 | 1944 + 1370 | 1370.hero_statue_skill 是否含该 id |
| 皮肤穿不上 | 1950 | `A_ARR_items` 的道具 id 和礼包对应 |
| 皮肤穿上属性错 | 1950 | `A_ARR_status_active` 和 `skin_owned_buff` |
| 新英雄展示页错位 | 1920 | `C_INT_display_order` 和 `A_INT_quality` |
| 合服后英雄战力偏差 | 1920 + 1921 + 1925 | `A_INT_buff_power_c` 和星级累积 buff |
| 元素反应不触发 | 1952 | `A_ARR_merge_ingredients` 配方 |
| 召唤兽 AI 异常 | 1946 | `S_INT_ai` + `S_ARR_guard/formation` |

---

**维护建议**：词条技能 1937-1942 六表联动是英雄装备系统最脆弱的一环，改其中任一都要校验下游。招募 gacha 池 1929→1930→1931 拓扑在节日换档时经常因 group 错配导致 up 卡不出。
