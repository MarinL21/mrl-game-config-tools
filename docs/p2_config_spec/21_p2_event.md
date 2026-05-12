# 21_p2_event 节日活动配置规范（全 72 张）

> **用途**：P2 所有节日活动/限时活动/BP/大富翁/挖孔/钓鱼/盲盒等——**运营策划最高频配置的文件夹**。被 1023 弹窗、2011 iap、1180 表情、1365 行军特效等全库引用。
>
> **Jira 自检场景**：活动没开 / 开服时间错 / 任务不计数 / 礼包买完不发货 / BP 经验卡住 / 排行榜算分错 / 兑换发错奖 / 大富翁格子跳错 / 挖孔关卡卡死 / 节日弹窗不出 / 礼包/任务跨节日平移 id 错误。

> **前置**：字段前缀约定见 [`10_p2_const.md`](./10_p2_const.md)；礼包 item 定义见 [`11_p2_asset.md#1111`](./11_p2_asset.md)；IAP 模板见 [`20_p2_iap.md#2013`](./20_p2_iap.md)。

---

## 节日活动配置拓扑（**必知**）

一个节日活动典型由 **12 张表协同**（参考 `p2-unite-gift-config` skill）：

```
2111 日历（何时开服启动，持续多久）
  ↓ activity_id
2112 activity_config（主表，挂 components）
  ├─ components.typ=task → 2115 activity_task
  ├─ components.typ=exchange → 2116 activity_item_exchange
  ├─ components.typ=chest / mysterious_trace / unite_pkg / emoji_show / discount / … → 2121 activity_special（兜底）
  ├─ components.typ=rank → 2122 activity_rank_rule
  ├─ components.typ=rank_reward → 2118 activity_rank_rewards
  ├─ components.typ=pkg → 2135 activity_package
  ├─ components.typ=drop → 2124 activity_drop
  ├─ components.typ=retake → 2137 activity_asset_retake
  ├─ components.typ=bp → 2130 activity_battlepass
  └─ components.typ=puzzle / shoot_hunt / … → 2146/2139（节日特有玩法）

**不通过 components.typ 挂载的独立玩法表**（由 2112.activity_id 或独立 id 索引）：
  · 2117 活动道具回收（按 A_INT_group 聚合）
  · 2148 节日装饰 / 2151 大富翁 / 2159 节日弹窗 / 2174 挖孔 / 2176 钓鱼

2112.rank_group → 2114
2121.reward_expr → 2121 自引用（阶段奖）
2122.score_rule → 1014 counter
2115.fincond → 1014 counter

礼包：
2135 activity_package ─┬─ iap → 2013 (20_iap)
                        ├─ get_items → 1111 (11_asset)
                        └─ banner → 1020 (10_const)

表情礼包：
2135.get_items → 1111 item → item 的 effect 激活 1180 map_emoji

行军特效礼包：
2135.get_items → 1111 item → effect → 1365 march_effect
```

**配新节日实例**（见 user memory `skill执行必须Step0自主学习`）：必须先从真实表读 ≥2 个节日对照，再确认 id 号段。

---

## 表清单（按子系统分组）

### 日历 & 主表
| 表号 | 用途 |
|---|---|
| [2111](#2111) | 活动日历（启动时机） |
| [2112](#2112) | **活动主表**（components 挂载） |
| [2113](#2113) | ~~activity_schema 废弃~~ |

### 组件表（components.typ 对应）
| 表号 | 用途 | 对应 typ |
|---|---|---|
| [2114](#2114) | 排名分组 | - |
| [2115](#2115) | **任务** | `task` |
| [2116](#2116) | 道具兑换 | `exchange` |
| [2117](#2117) | 道具回收 | **独立**（不挂 components） |
| [2118](#2118) | 排名奖励 | `rank_reward` |
| [2119](#2119) | UI 模板 | - |
| [2120](#2120) | UI 模块 | - |
| [2121](#2121) | **特殊组件**（宝箱/神秘踪迹/阶段奖等） | `chest`/`mysterious_trace`/... |
| [2122](#2122) | **排名规则** | `rank` |
| ~~2123~~ | ~~activity_popwindow 已废弃~~ | - |
| [2124](#2124) | 活动掉落 | `drop` |
| [2125](#2125) | 折扣 | - |
| [2126](#2126) | 部落捐赠升级 | - |
| [2127](#2127) | 社区链接 | - |
| [2128](#2128) | GvE 集结 | - |
| [2129](#2129) | 护送 buff | - |

### BP（Battle Pass）
| 表号 | 用途 |
|---|---|
| [2130](#2130) | BP 主表 |
| [2131](#2131) | BP 等级奖励 |
| [2143](#2143) | 节日 BP 模块 |

### 联盟总动员
| 表号 | 用途 |
|---|---|
| [2132](#2132) | 联盟竞赛礼包 |
| [2133](#2133) | 联盟竞赛任务 |

### 生成实体/礼包
| 表号 | 用途 |
|---|---|
| [2134](#2134) | 活动生成实体（解锁野怪带） |
| [2135](#2135) | **活动礼包**（节日包核心） |
| [2136](#2136) | 周期循环（兑换） |
| [2137](#2137) | 活动资产回收 |
| [2138](#2138) | 活动 proto 模块 |

### 特殊玩法
| 表号 | 用途 |
|---|---|
| [2139](#2139) | 飞机射击 |
| [2140](#2140) | 伤害奖励 |
| [2141](#2141) | Without gacha 池 |
| [2142](#2142) | Without gacha 奖励 |
| [2144](#2144) | 英雄成就（活动版） |
| [2145](#2145) | 活动 tips |
| [2146](#2146) | 拼图活动 |
| [2147](#2147) | 集卡 gacha 补充 |

### 节日装饰
| 表号 | 用途 |
|---|---|
| [2148](#2148) | 节日装饰等级 |
| [2171](#2171) | 装饰涂装技能 |
| [2172](#2172) | 美化值等级 |
| [2173](#2173) | 美化商店 |
| [2149](#2149) | Gachabox 升级（空） |

### 大富翁 & Boss
| 表号 | 用途 |
|---|---|
| [2150](#2150) | Hoggboss 类型（空） |
| [2151](#2151) | 大富翁地图 |
| [2152](#2152) | 大富翁奖励 |
| [2153](#2153) | 大富翁骰子 |
| [2178](#2178) | 大富翁怪物 |
| [2179](#2179) | 大富翁魔法骰子 |
| [2180](#2180) | 大富翁怪物 buff |
| [2181](#2181) | 大富翁怪物技能 |

### 装备/兵种成就
| 表号 | 用途 |
|---|---|
| [2154](#2154) | Without gacha 保底 |
| [2155](#2155) | 兵种武装成就 |
| [2156](#2156) | 楼层 gacha |
| [2157](#2157) | 装备套装（战装实验） |
| [2158](#2158) | 装备套装成就 |
| [2161](#2161) | 兵种技能成就 |

### 节日弹窗/HUD/调查
| 表号 | 用途 |
|---|---|
| [2159](#2159) | 节日弹窗 |
| [2163](#2163) | 满意度调研 |
| [2165](#2165) | 周年报告 |
| [2168](#2168) | 节日 HUD 入口 |
| [2169](#2169) | HUD 样式 |

### 竞技场 & 竞猜
| 表号 | 用途 |
|---|---|
| [2160](#2160) | 挖矿活动分级 |
| [2162](#2162) | 精英竞技场阶段 |
| [2170](#2170) | 精英竞技场竞猜 |

### 限时抢购 & 盲盒
| 表号 | 用途 |
|---|---|
| [2164](#2164) | 盲盒期 |
| [2166](#2166) | 限时抢购 raffle |
| [2167](#2167) | 限时抢购 virtual（价格系数） |

### 挖孔 & 钓鱼 & 推币
| 表号 | 用途 |
|---|---|
| [2174](#2174) | **挖孔关卡（老版）** |
| [2175](#2175) | 挖孔方块类型 |
| [2183](#2183) | 挖孔关卡新版（v7） |
| [2176](#2176) | 钓鱼引导组 |
| [2177](#2177) | 钓鱼引导 |
| [2182](#2182) | 推币机 |

---

<a id="2111"></a>
## 2111_p2_activity_calendar — 活动日历

**用途**：控制活动**什么时候开、持续多久、何时关闭**。运营改档期必动这张表。

**字段**：
| 字段 | 含义 | 枚举/格式 | bug |
|---|---|---|---|
| `A_INT_id` | 日历主键 | 21111xxx | - |
| `A_INT_activity_id` | 关联的 2112 主表 id | → 2112 | activity_id 失效 → 活动永远不开 |
| `S_STR_comment` | 策划备注 | - | - |
| `S_MAP_server_info` | 生效服 | `{"typ":"schema","id":[0]}`=所有服；`{"typ":"serverid","id":[xxx,xxx]}`=特定服 | schema=[0] 表示通用，不能漏 |
| `S_MAP_start_trigger` | 启动触发 | `{"typ":"reg"}`=注册后/`{"typ":"afcutc","val":"0h"}`=按 UTC 时间 | typ 错 → 活动不启动或错时启动 |
| `S_MAP_time_info` | 时间配置 | `{"fcastdur":"0h", "actvdur":"288h", "closedur":"0h"}` — 预告/活动/关闭时长 | 单位是小时字符串；actvdur 为 0 → 秒结束 |
| `S_MAP_activity_group` | 活动组（节日串联） | `{}` | - |
| `S_INT_data_cross` | 跨数据 | 0/1/2 | 2=数据跨服清算 |
| `A_INT_country_use_type` | 区服 | 0/1/2 | - |

**常见 bug**（用户高频）：
- **actvdur 单位错**：写成分钟数（60）而不是小时数（`"60h"`）→ 活动 60 秒结束。
- **schema 漏新合服 id**：新合服服看不到活动。
- **start_trigger typ 写错**：`reg`（注册后）vs `afcutc`（UTC 时间）不同逻辑。
- **国服 vs 海外时区**：UTC 时间换算错，提前/延后 8 小时开。

---

<a id="2112"></a>
## 2112_p2_activity_config — 活动主表（**核心**）

**用途**：节日/活动的**主配置**。挂载具体 components（task/pkg/rank 等）。

**字段**：
| 字段 | 含义 | 枚举/格式 | 关联 | bug |
|---|---|---|---|---|
| `A_INT_id` | 活动主键 | 21121xxx | - | - |
| `S_STR_comment` | 策划备注 | - | - | - |
| `A_STR_constant` | code key | - | - | - |
| `A_INT_index` | 索引 | - | - | - |
| `S_INT_priority` | 优先级 | - | - | - |
| `A_INT_base_activity_id` | 基础活动 id（继承） | 通常 = A_INT_id | - | - |
| `A_MAP_filter` | 玩家筛选 | `{"op":"ge","typ":"building","id":111811,"val":3}` | - | - |
| `A_MAP_text` | 文案 | `{"group_label":"LC_xxx","label":"LC_xxx"}` | 1011 EVENT | - |
| `A_ARR_activity_components` | **components 列表** | `[{"typ":"task","id":2115xxx},{"typ":"exchange","id":2116xxx}]` | 2115/2116/2118/2121/2122/2124/2135 等 | **typ/id 错配 = 组件不加载** |
| `A_MAP_description` | 活动描述 | `{"rule":"LC_xxx","note":"LC_xxx"}` | 1011 | - |
| `A_INT_ui_template` | UI 模板 | → 2119 | 2119 | 新模板漏配 → UI 错版 |
| `S_INT_rank_group` | 排名组 | → 2114 | 2114 | - |
| `S_STR_banner_obj_url` / `S_STR_banner_url` | banner URL | - | 1020 | URL 拼错或 version 没 bump → 图不更新 |
| `S_STR_banner_version` | banner 版本 | `1`/`2` | - | bump 此字段触发客户端重下 |
| `A_INT_default_displaykey` / `A_INT_icon_displaykey` | 默认/图标 key | - | - | - |
| `A_INT_show_hud` | 是否上 HUD | 0/1 | - | - |
| `A_INT_calendar` | 是否进日历 | 0/1 | - | - |
| `A_ARR_calendar_reward` | 日历奖励 | - | - | - |
| `S_STR_calendar_banner_url` | 日历 banner | - | 1020 | - |
| `A_INT_dependent` | 依赖活动 id | - | - | 依赖链形成环 → 都不启动 |
| `S_STR_mini_banner_url` | 小 banner | - | 1020 | - |
| `C_INT_display_flags` | 显示标志 | - | - | - |
| `A_INT_country_use_type` | 区服 | 0/1/2 | - | - |

**`A_ARR_activity_components` 的 typ 枚举**（**高频 bug 点**）：
| typ | 关联表 |
|---|---|
| `task` | 2115 |
| `exchange` | 2116 |
| `chest` / `mysterious_trace` / 其它特殊 | 2121 |
| `rank` | 2122 |
| `drop` | 2124 |
| `pkg` | 2135 |
| `bp` | 2130 |
| `rank_reward` | 2118 |
| 节日特有（如 `puzzle`, `shoot_hunt`） | 2146/2139 |

**常见 bug**：
- **components 中 id 失效**：引用的 2115/2135 等子表行不存在 → 组件加载失败。
- **ui_template 和 components 不匹配**：模板要求 3 个模块但 components 只配了 2 个。
- **base_activity_id 不一致**：通常要等于 A_INT_id，否则继承关系乱。

---

<a id="2114"></a>
## 2114_p2_activity_rank_group — 排名分组

简单映射：`A_INT_id` → `A_INT_rank_group`。

---

<a id="2115"></a>
## 2115_p2_activity_task — 活动任务

**字段**：
| 字段 | 含义 | 枚举 | 关联 | bug |
|---|---|---|---|---|
| `A_INT_group` | 任务组 | - | - | 通常对应一个活动 |
| `A_INT_id` | 任务 id | 211510xxx | - | - |
| `N_STR_comment` | 备注 | - | - | - |
| `A_MAP_showcond` | 显示条件 | `{"op":"and","args":[{"op":"ge","typ":"actvstarttime",...}]}` | - | 恒假 → 任务隐藏 |
| `A_MAP_fincond` | 完成条件 | `{"cat":10148026,"val":1,"op":"ge"}` — cat 指向 1014 counter | 1014 | **cat 对应 counter 失效是最常见 bug** |
| `A_INT_pretrace` | 前置任务 | - | 自表 | - |
| `A_ARR_reward` | 奖励 | `[{"asset":{"typ":"item","id":xxx,"val":x},"setting":...}]` | 1111 | item id 失效 → 任务完成不发奖 |
| `A_STR_task_desc` / `A_MAP_task_label_1/2` | 文案 | LC_EVENT_xxx | 1011 EVENT | - |
| `A_INT_display_order` | 显示顺序 | - | - | - |
| `A_INT_daily_reset` | 每日重置 | 0/1 | - | - |
| `A_INT_can_ad_reward` | 是否可广告双倍 | 0/1 | - | - |

**bug**（用户 memory 多次提到）：
- **fincond.cat 和 1014 counter constant 不对齐**：任务进度卡 0。比如挖孔 6 期用 `digkeys_start_level` 替代 `status=1`。
- **新活动任务跨节日平移**：通用任务 id 可以复用，但活动专属 id 必须换。

---

<a id="2116"></a>
## 2116_p2_activity_item_exchange — 道具兑换

**字段**：
- `A_INT_group` / `A_INT_id`：分组和 id
- `A_ARR_item_give` / `A_ARR_item_get`：付出/获得（→ 1111）
- `A_INT_limit_num`：兑换次数上限
- `A_INT_if_remind`：是否提醒
- `A_MAP_requirement`：兑换前置
- `S_MAP_show_requirement`：展示条件
- `S_ARR_bargain_count` / `S_MAP_bargain_limit`：砍价次数
- `C_INT_discount`：折扣
- `C_MAP_type_title`：分类标题

---

<a id="2117"></a>
## 2117_p2_activity_item_recycle — 道具回收

**挂载方式**：**不通过 2112.components.typ**，由节日玩法代码按 `A_INT_group` 索引一组回收规则（多数老节日标 "弃用"，仍作为历史配置存在）。

**字段**：
- `A_INT_group`：分组 id（入口，节日代码按 group 读取整组）
- `A_INT_id`：回收规则主键
- `N_STR_comment`：策划备注
- `A_INT_item_id` → 1111（被回收的道具）
- `A_ARR_reward`：回收奖励 `[{"typ":"item","id":xxx,"val":xxx}]`
- `A_INT_item_max`：回收数量上限（0=无限）

---

<a id="2118"></a>
## 2118_p2_activity_rank_rewards — 排名奖励

- `A_INT_group`：组（对应 2122.`A_INT_rank_components`）
- `A_INT_rank_start` / `A_INT_rank_end`：排名区间
- `A_ARR_reward`：奖励（通用奖励格式）

**标准 12 档分布**（每组通常 12 行）：1-1 / 2-2 / 3-3 / 4-4 / 5-5 / 6-6 / 7-7 / 8-10 / 11-15 / 16-25 / 26-50 / 51-100。前 7 名单档给奖，8 名后按区间递减。

---

<a id="2119"></a>
## 2119_p2_activity_ui_template — UI 模板

- `A_ARR_modules`：该模板用到的模块 id 列表（→ 2120）
- `A_INT_UITemplate`：UI 模板内部 id

**bug**：2112.ui_template 指向的 2119 行的 modules 在 2120 不全 → UI 渲染报错。

---

<a id="2120"></a>
## 2120_p2_activity_ui_module — UI 模块

- `S_STR_module`：模块类名（`PublicModule`/`RewardBoxModule` 等）
- `C_STR_constant`：代码 constant
- `C_INT_model` / `C_BOL_model_only` / `C_BOL_view_only`：MVC 分层
- `S_ARR_actvc_type`：关联活动 type
- `S_INT_proto_module` → 2138

---

<a id="2121"></a>
## 2121_p2_activity_special — 特殊组件（**高频**）

**用途**：2112.components 中 `typ:"chest"`、`mysterious_trace` 等非通用组件。

**字段**：
| 字段 | 含义 | 枚举/格式 | bug |
|---|---|---|---|
| `A_INT_id` | 主键 | 21211xxx | - |
| `A_STR_type` | 组件类型 | `chest`/`mysterious_trace`/... | 代码按 type 分支，改 type 要代码配合 |
| `A_ARR_reward` | 奖励 | - | - |
| `A_MAP_expr` | 表达式 | - | - |
| `A_INT_arg1/2/3` | 参数 1/2/3 | - | 含义随 type 变 |
| `A_ARR_reward_expr` | 条件奖励 | - | - |
| `A_STR_desc` | 描述 | `NULL`/LC | - |
| `A_ARR_array` | 通用数组 | - | - |
| `A_ARR_status` | buff | - | - |
| `S_MAP_condition` | 条件 | - | - |
| `S_ARR_score_rule` | 积分规则 | - | 用于 mysterious_trace 等按进度的组件 |

**常见 bug**：arg1/2/3 的含义依赖 type，改 type 忘改 args → 行为异常。

---

<a id="2122"></a>
## 2122_p2_activity_rank_rule — 排名规则

**字段**：
| 字段 | 含义 | 格式 |
|---|---|---|
| `A_INT_group` / `A_INT_id` | 分组/id | - |
| `A_ARR_score_rule` | 积分规则 | `[{"cat":10145019,"val":1000,"score":1}]` — cat → 1014 counter，val=每次，score=折算分 |
| `A_MAP_start_time` | 开始类型 | `{"typ":"overall"}` |
| `A_INT_rank_unit` | 排名单位 | 1=个人 / 2=联盟 / 3=部落 / 4=服务器 / 5=服务器组 |
| `A_INT_rank_scope` | 排名范围 | 同 rank_unit 5 档；**必须 > rank_unit**；跨服个人排行跑马灯需填 5 |
| `A_INT_rank_components` | **关联 2118.A_INT_group（排名奖励）** | - |
| `A_STR_rank_title` | 标题 LC | - |
| `A_INT_icon_display_key` | 图标 | - |
| `A_INT_min_score` | 最低入榜分 | - |
| `A_INT_retain_rank` | 保留名次 | - |
| `A_MAP_score_req` | 入榜条件 | - |
| `A_INT_score_change_tips` | 排名变化提示 | - |

**bug**：score_rule.cat 指向 1014 counter 失效 → 积分永远 0；rank_unit 写错 → 个人榜变联盟榜；`A_INT_rank_scope ≤ rank_unit` → 跨服跑马灯不弹。

**分组惯例**（以强消耗活动 schema6 group=243 为例）：21222098~21222103 是 6 个**积分子规则**行（斗士/收藏品/军备/机甲/战装/加速）；21222104 是**主排名行**，`score_rule` 引用上方 6 个子 id 汇总积分，`rank_components=272` 指向 2118 组。2121 的 `actv_show_rank` 组件 `A_INT_arg1` 也指向 21222104。

---

<a id="2124"></a>
## 2124_p2_activity_drop — 活动掉落

**字段**：
| 字段 | 含义 | 枚举 | bug |
|---|---|---|---|
| `A_STR_action` | 掉落触发动作 | `pve_all`（打野）/ `tracks_donate`（神秘踪迹贡献）等 | - |
| `A_ARR_action_ids` | 动作 id 过滤 | `[]` = 所有 | - |
| `S_MAP_counter_ids` | counter 映射 | - | - |
| `A_MAP_drop` | 掉落内容 | `{"typ":"single_random","num":1,"args":[...]}` | - |
| `A_ARR_action_time` | 触发时间窗 | `[1,999999]` | - |
| `S_INT_mail_id` | 发邮件 id | - | - |
| `A_ARR_display_drop` | 展示用掉落（和 drop 可不同） | - | - |
| `S_INT_day_refresh` | 每日刷新 | 0/1 | - |
| `S_STR_type` | 类型 | `bag`/`mail`/... | - |
| `C_MAP_desc` | 描述 | - | - |
| `S_INT_base` | 基础数量 | 1 | - |
| `S_ARR_refresh` | 刷新规则 | `[]` | - |
| `A_MAP_filter` | 玩家筛选 | - | - |
| `S_MAP_asset_limit` | 资产限制 | - | - |
| `S_STR_action_desc` | 动作描述 | - | - |

---

<a id="2125"></a>
## 2125_p2_activity_discount — 折扣

`A_ARR_item_free` / `A_ARR_item_discount` / `A_FLT_discount_rate` — 展示型折扣。

---

<a id="2126"></a>
## 2126_p2_activity_donate_lvl_up — 部落捐赠升级

- `S_ARR_donation`：捐赠物
- `S_ARR_crit`：暴击权重 `[{"num":1,"weight":40},{"num":2,"weight":30},...]`
- `S_ARR_reward`：各档奖励
- `A_ARR_max_num`：各档上限
- `A_ARR_get_access`：获取途径 id 列表
- `S_INT_scope`：范围

---

<a id="2127"></a>
## 2127_p2_activity_community_link — 社区链接

Facebook/Discord 等外部链接。`C_ARR_loc` 是生效语言列表。

---

<a id="2128"></a>
## 2128_p2_activity_gve_call — GvE 集结

- `A_INT_diffcuty` / `A_STR_diffcuty_desc`：难度
- `A_INT_level` / `A_INT_npc_id`：关卡级 + NPC id → 1317
- `A_ARR_reward` / `A_ARR_final_reward`：过程/最终奖励
- `A_INT_mail_id` / `A_INT_final_mail_id`：奖励邮件

---

<a id="2129"></a>
## 2129_p2_activity_escort_buff — 护送 buff

- `A_INT_buff_id` → 12xxx
- `A_INT_buff_value`：buff 值
- `A_ARR_buff_time`：生效时段 `[{"starttime":7,"endtime":8}]`（小时粒度）

**bug**：活动时段填错小时 → buff 不生效或永久生效。

---

<a id="2130"></a><a id="2131"></a><a id="2143"></a>
## 2130-2131 Battle Pass

### 2130 battle_pass 主表
- `A_INT_exp`：每级经验
- `A_INT_start_level`：起始等级
- `A_ARR_daily_taskids` / `A_ARR_achivement_taskids` / `A_ARR_weekly_taskids` / `A_ARR_limit_taskids` → 2115
- `A_MAP_pkg`：付费激活判断 `{"op":"or","args":[{"typ":"iap","id":201390001,"display":...}]}` → 2013
- `A_ARR_max_levelup_rewards`：满级奖励
- `C_ARR_banner_reward` / `C_INT_banner_title_text_fill`：banner 展示
- `S_ARR_quality_up_item`：提档道具
- `A_ARR_level_up_item`：升级道具
- `S_ARR_crit`：暴击权重
- `A_INT_max_levelup_can_use`：单次最大
- `A_ARR_reward_buff` / `C_INT_level_start_id` / `A_INT_type`：其它

### 2131 battle_pass_level
- `A_INT_bp_id` → 2130
- `A_INT_level`：等级
- `A_ARR_free_rewards` / `A_ARR_pay_rewards` / `A_ARR_pay_rewards_2`：免费/付费/付费2 奖励
- `A_INT_exp`：该级经验
- `A_INT_show_type` / `C_INT_next`：UI 显示

### 2143 节日 BP 模块
- `C_MAP_anim_name` / `C_MAP_audio_name` / `C_MAP_localiztion`：动画/音效/LC 配置
- `C_INT_use_effect_wait_time` / `C_INT_guide` / `C_INT_use_anim_effect_wait_time`：时间参数

### 节日 BP 换档 SOP（template 21127638 及其轮换副本）

**标准组件清单**（23 个，每期复制旧活动再改）：

| typ | 数量 | 目标表 | 换档是否改 |
|---|---|---|---|
| `battle_pass` | 1 | 2130 | **新建**（改 comment 为新年份） |
| `new_progress` | 10 | 2121 | 改 `A_INT_arg2`(通行证 2011) + `S_MAP_condition.id`(集结礼包 2013) |
| `cross_progress` | 1 | 2011 | **新建**（id 必须新，服务器查历史购买记录） |
| `package` | 6 | 2135 | 通行证复用去年同节日，更新 `A_MAP_time_info.actv_id` |
| `drop` | 1 | 2124 | **原地改 `A_MAP_drop`**（此 drop id 多节日 BP 共用） |
| `retake` | 1 | 2137 | 去年同节日复用，否则新建 |
| `jump_link` | 1 | 2121 | **新建**（`A_INT_arg1` = 本节日 BP 经验道具） |
| `fes_module` + `bp_rank_item` | 2 | 2143 / 1111 | **已废弃但必须保留**，删除会界面错乱 |

**6 步换档**：

| 步骤 | 表 | 动作 |
|---|---|---|
| 1 集结礼包 | 2011 + 2013 | **新建** 2 行。复制老行改 `N_STR_pkg_desc`；2011.`A_MAP_time_info` 绑新 `actv_id`；2013.`A_INT_config_id` 指向新 2011；2013.`A_STR_pkg_title` 与 2112.`A_MAP_text.title` 对齐 LC |
| 2 BP 主配置 | 2130 | **新建** 1 行，从目标节日上一期复制；`A_MAP_pkg` 保持引用通行证 IAP；道具沿用 |
| 3 通行证礼包 | 2011 × 2（初级 + 高级） | 修改去年**同节日**的 2 行：名称 N→N+1；`A_MAP_time_info` 绑当期 `actv_id` |
| 4 2112 活动主行 | 2112 | 改 `S_STR_comment` / `A_STR_constant` / `A_INT_show_hud`；组件 `battle_pass` 改新 2130；组件 `cross_progress` 改新 2011 |
| 5 阶段奖励 | 2121 × N | 每个 `new_progress` 改 `A_INT_arg2` = 第 3 步初级通行证 2011 id，`S_MAP_condition.id` = 第 1 步集结礼包 2013 id |
| 6 数值落地 | 2131 / 2130 / 2124 / 2137 / 2013 / 2168 / 1013 / 2111 | 见下表，拿到策划设计表后再动 |

**第 6 步细项**：

| 目标 | 关键动作 |
|---|---|
| 2131 等级奖励 | **新建** N 级（每期等级数可能不同，如 25→40）；`A_INT_bp_id` 指新 2130；三轨道奖励 `free_rewards`/`pay_rewards`/`pay_rewards_2` 按策划 |
| 2130 + 2013 通行证定价 | `A_FLT_price` / `A_INT_CDs` / `A_ARR_other_items` VIP 经验 / `A_ARR_price_info` 的 product_id（`ape_{CODE}_cd_*`）全部同步改 |
| 2124 循环宝箱 | **原地改** `A_MAP_drop`，把奖池 item id 换成本节日的 |
| 2124 随机礼包 drop | 3 个随机礼包奖池里 BP 道具 id **字符串 replace**（权重/数量不改） |
| 2013 锚点/触发/随机礼包模板 | 9 个 2013 模板的 `A_ARR_other_items` BP 道具 id 替换 |
| 2121 new_progress 付费奖励 | `A_ARR_reward_expr` 按策划改（典型：L3/L6/L9/L10 = 万能英雄碎片×1，其余 = 多成长线自选宝箱×2）；免费轨道通常不变 |
| 2112.组件 retake id | 若从科技节模板复制，retake id 可能还挂着科技节（如 21371103），要换成本节日的（如拓荒节 21371111）。不换 = 回收拓荒节纪念钻头得不到粮食（跨节日串台） |
| 2168 HUD | `A_INT_show_hud` 查 2168 本节日那行的 `A_INT_id`；`A_INT_icon_displaykey` 取那行的 `C_INT_display_key`（不是 2168 的 id） |
| 1013 `fes_actv_bp_extra` | `A_ARR_quintuple` **append** `{"id": <本期活动 id>}`，不覆盖。不加 = 循环宝箱不绑活动 |
| 2111 activity_calendar | 补 `A_INT_activity_id = <本期活动 id>`，不补后台开不了活动 |

**循环宝箱机制**（drop + 1013 常量协同）：

```
1013 常量（如 10137256）:
  A_STR_constant = fes_actv_bp_extra          ← 和 2124 drop 的 A_STR_action 同名绑定
  A_ARR_array = [100, 15]                      ← [每次开箱所需经验, 最大次数]
  A_ARR_quintuple = [{"id": 21127638}, {"id": 21127651}, ...]  ← 每期 append
      ↓
2124 drop（如 21242156）:
  A_STR_action = fes_actv_bp_extra
  A_MAP_drop = {single_random + noget 保底}
```

**集结礼包（new_progress + cross_progress）关键参数**：

```
cross_progress(2011 id) ← 集结奖励解锁礼包（玩家付费入口）
     ↓
new_progress × 10 阶段（在 2121）:
  arg1 = 人数阈值（典型梯度 1/10/50/100/200/300/400/600/800/1000，可调）
  arg2 = 初级通行证的 2011 id（追踪购买人数）
  arg3 = 5 （跨服计算维度：1=个人/2=联盟/4=服务器/5=跨服）
  A_ARR_reward = 免费奖励（达阈值所有人可领）
  A_ARR_reward_expr = 付费奖励
  S_MAP_condition = {"op":"ge","typ":"iap_purchases","id":<集结礼包 2013 id>,"val":1}
```

**坑点清单**：

1. **集结礼包必须新建**：服务器检测"历史上是否购买过该礼包 id"而非"活动期内"，复用旧 id = 上期买过的玩家本期白嫖付费奖励
2. **通行证可复用但必须更新 time_info**：否则老玩家以前购买记录不刷新（本期以为自己买过）
3. **21127638 模板的 fes_module / bp_rank_item 不能删**：已废弃，但删除会导致客户端界面错乱
4. **cross_progress 必填**：不填 → 首次进入集结奖励界面不显示礼包入口，要二次拉取活动数据才显示
5. **retake id 跨节日串台**：复制科技节模板没换 retake id → 回收本节日纪念道具得到的是科技节资产
6. **道具一致性校验**：通行证解锁道具、BP 经验道具可复用，但配置完后要全面 grep 2130 / 2013 / 2124 / 2121 引用的所有道具 id 是否一致

---

<a id="2132"></a><a id="2133"></a>
## 2132-2133 联盟总动员

### 2132 alliance_competition_package
超大字段表（30 列）— 联盟等级、升降级点数、任务数、刷新次数、奖励。

关键字段：
- `A_INT_league_level`：等级（1=青铜/2=白银/3=黄金/...）
- `A_STR_league_title` / `A_INT_league_display_key`：等级 UI
- `A_INT_drop_personal` / `A_INT_drop_alliance` / `A_INT_drop_personal_first` / `A_INT_drop_daily`：掉落 id
- `A_INT_personal_rank_rule` / `A_INT_union_rank_rule` → 2122
- `A_ARR_progress`：进度奖励列表（→ 2121 或 2135）
- `A_INT_personal_task` / `A_INT_alliance_task` / `A_INT_daily_task` → 2133
- `A_INT_league_up_point` / `A_INT_league_down_point`：升降分
- `A_INT_league_group_max` / `A_INT_league_group_min`：组人数范围

### 2133 alliance_competition_task
- `A_INT_task_quality`：任务稀有度
- `A_INT_task_id` → 2115
- `A_INT_task_time`：任务持续（毫秒）
- `A_INT_probability`：出现概率
- `A_INT_reward_points` / `A_INT_reward_bonus`：积分/加成奖励

---

<a id="2134"></a>
## 2134_p2_activity_create_entity — 活动生成实体

用于节日解锁特殊野怪/带。`A_ARR_refresh_band` → 1314。

---

<a id="2135"></a>
## 2135_p2_activity_package — 活动礼包（**节日核心**）

**用户高频配置的表**（见 `p2-unite-gift-pack` skill）。

**字段**：
| 字段 | 含义 | 枚举 | 关联 | bug |
|---|---|---|---|---|
| `A_INT_id` | 主键 | 21350xxx | - | - |
| `N_STR_comment` | 策划备注（礼包中文名） | - | - | - |
| `A_INT_iap` | 关联的 IAP | → 2013（iap template） | 2013 | `0` = 非付费礼包（用 vm 买）；非 0 = 付费礼包必须对应 2013 |
| `A_MAP_cost` | 消耗 | `{"typ":"vm","id":11151001,"val":700}` 或 `{}` | 1115/1111 | cost={} 表示由 iap 支付 |
| `A_ARR_get_items` | 获得道具 | `[{"asset":{"typ":"item","id":xxx,"val":x},"setting":...}]` | 1111 | 道具 id 失效 → 买了没东西 |
| `A_INT_cost_limit` | 购买次数 | -1=无限/0=禁售/正数=限购 | - | - |
| `A_STR_banner_url` | 海报 URL | `""` 表示无 | 1020 | 必须在 1020 注册 |
| `A_STR_cd_cost_title` / `A_STR_cd_cost_text` | 标题/文本 LC | `""`/`NULL`/LC_xxx | 1011 EVENT | - |
| `A_MAP_filters` | 玩家筛选 | `{}` | - | - |
| `A_INT_order` | 排序 | - | - | - |
| `C_INT_all_value` | 战力折算 | - | - | - |
| `C_STR_tab` | 页签 | `NULL`/其它 | - | - |

**常见 bug**（用户高频踩坑）：
- **iap id 失效**：付费礼包在 20_iap.2013 的 id 不存在 → 充值后不到账（见 user memory `资源链路必须全链路闭环`）。
- **get_items 跨节日平移**：直接复制上一节日的 id → 通用道具 OK，但节日专属道具 id 没换（见 user memory `通用道具vs节日专属道具`）。
- **banner_url 漏 bump 1020 version**：换图不生效。
- **cost_limit=0**：礼包禁售但没提示。

---

<a id="2136"></a>
## 2136_p2_activity_cycle_period — 周期循环

- `A_INT_activity_config_id` → 2112
- `A_INT_cycle`：循环次数（0/1/2/...）
- `A_ARR_exchange`：该周期兑换 `[{"give":11117077,"get":11116221}]`

---

<a id="2137"></a>
## 2137_p2_activity_asset_retake — 活动资产回收

- `A_MAP_give_asset`：给予
- `A_MAP_cost_asset`：消耗

节日 BP 结束清理残留的专属 item。

---

<a id="2138"></a>
## 2138_p2_activity_proto_module — 活动 proto

proto 级模块（`DaysQuestListModule`/`DailyResetModule` 等）。被 2120 引用。

---

<a id="2139"></a>
## 2139_p2_activity_shoot_hunt — 飞机射击

字段超多（38 列），包含 stage 配置、剧本、道具消耗、HP、弱点等。节日限定玩法。

---

<a id="2140"></a>
## 2140_p2_activity_history_damage_reward — 历史伤害奖励

- `A_INT_group` / `A_INT_damage` / `A_ARR_reward`：档位奖励。

---

<a id="2141"></a><a id="2142"></a>
## 2141-2142 Without Gacha

### 2141 without_gacha_pool
- `S_ARR_drop`：按 group 抽 `[{"group":1,"wgt":50},{"group":2,"wgt":4950}]` → 2142
- `S_ARR_use_item`：消耗
- `S_ARR_improve`：进阶奖励
- `S_INT_group_up_quality`：提档品质
- `A_INT_interval` / `A_INT_activity`：间隔/活动

### 2142 without_gacha_reward
- `A_INT_group` 对应 2141.drop.group
- `A_MAP_asset`：奖励
- `A_INT_probability` / `A_INT_max` / `A_INT_reward_index` / `A_INT_probability_show` / `A_INT_special_reward`

---

<a id="2144"></a>
## 2144_p2_activity_hero_achievement — 活动英雄成就

- `A_INT_quality`：英雄品质
- `A_MAP_fincond`：完成条件 `{"op":"ge","typ":"hero_star","val":4}`
- `S_ARR_reward`：奖励
- `A_INT_iap`：付费礼包关联 → 2013

---

<a id="2145"></a>
## 2145_p2_activity_tips — 活动引导

- `A_STR_constant`：code key
- `A_ARR_building`：关联建筑 → 1118
- `A_ARR_activity`：关联活动 `[{"actv_id":21121022}]`
- `A_ARR_building_function` → 1130
- `C_MAP_description`：提示文案

---

<a id="2146"></a>
## 2146_p2_activity_puzzle — 拼图活动

- `A_INT_GROUP`：拼图组
- `A_INT_DISPLAY_KEY`：碎片图
- `A_INT_TASK`：触发任务 → 2115
- `A_INT_SHOW_ITEM`：显示 item → 1111
- `A_INT_TIME`：顺序

---

<a id="2147"></a>
## 2147_p2_activity_collection_gacha_add — 集卡 gacha 补充

活动期间加入集卡 gacha 池的额外奖励。关联 1157/1158。

---

<a id="2148"></a>
## 2148_p2_event_decroation_level — 节日装饰等级

- `A_INT_group_id`：装饰组
- `A_INT_building`：对应建筑 → 1118
- `A_INT_unlock_item`：解锁道具 → 1111
- `A_INT_paint`：涂装类型
- `A_INT_star` / `A_INT_star_max`：星级
- `A_MAP_lc_name` / `C_MAP_lc_desc` / `C_MAP_lc_desc_get`：文案
- `A_ARR_BUFF`：buff
- `C_ARR_paint_item` / `A_ARR_paint_buff`：涂装相关
- `A_ARR_upgrade_cost`：升星消耗
- `S_ARR_retake`：结束回收
- `A_INT_decroation_paint_skill` → 2171
- `C_STR_upitem_get_access`：获取途径
- `A_INT_year_group`：年份分组

**bug**：year_group 漏配 → 跨年装饰混配；decroation_paint_skill id 失效 → 涂装无 buff。

### 装饰物 4 表联动 SOP（+涂饰 1 表 = 5 表）

**核心认知**：节日装饰本质是"可升级星级的建筑"。1 个装饰的完整配置必须同时出现在 4 张表（2148 + 1118 + 1127 + 1111），带涂饰的加 2171，缺 1 张 = 无法建造/无法升级/升级后无视觉。字段定义详见 [11_p2_asset.md 1118/1127/1111](./11_p2_asset.md) + [本文 2148/2171](#2148)。

**跨表 ID 链路**：

```
1111 item (解锁道具, class=statue_decorate)
  │ A_MAP_category_param.effect = [{"typ":"holiday_statue","id":2148 一星 id}, ...]
  ↓
2148 event_decroation_level (group_id=214801，每星级 1 行)
  │ A_INT_building    = 1118107        ← 1118 家族 id（7 位）
  │ A_INT_unlock_item = 1111解锁道具 id
  │ A_ARR_upgrade_cost = [{typ:item,id:1111升级材料 id,val:5}]
  ↓
1118 building (A_INT_building_id=1118107，每星级 1 行，id=家族×100+星)
  ↑
1127 building_build (建造菜单入口)
  │ A_ARR_building_ids = [1118 家族 id]
  │ A_ARR_unlock_cost  = [{typ:item, id:1111解锁道具, val:1}]
```

> **ID 编号**：1118 家族 id 是 7 位（`1118xxx`），每星级 id = 家族×100+星序（`111810701/02/03`）。2148 group_id 是 6 位（`214801`），和 1118 家族 id 是平行编号，不是拼接关系。

**配置一个新装饰的 10 步**：

1. **规划 id**：确定 1118 家族 id（7 位）、2148 group_id（6 位）、1127 入口 id、1111 解锁道具 + 升级材料 id
2. **1111 新增解锁道具**：`A_STR_class=statue_decorate`、`A_INT_quest_class=23`、`effect` 指向 2148 **一星 id**、`S_INT_use_now=1`（获得即用）、`A_INT_max_own=最大星级`（防重复）、`A_ARR_use_labels=["bag"]`
3. **1111 新增升级材料**：`A_STR_class=event`、`C_ARR_display_labels=["bag_other"]`、`S_INT_use_now=0`、`A_INT_max_own=999999999`。多难度可拆多条
4. **2148 按星级展开**：每星 1 行，`A_INT_group_id` 同值；`A_INT_building` 指 1118 家族 id；`A_INT_unlock_item` 回指步骤 2；`upgrade_cost` 指步骤 3；最高星填 `S_ARR_retake`；`A_ARR_BUFF` 写该星级全部 buff（citybeauty + 属性 buff）
5. **1118 按星级展开**：每星 1 行，`A_INT_building_id` 同值；`A_INT_type=2`（装饰类）；美术 display_key、lc_name、size、function、remove/remove_rebate 按家族配。**⚠️ 1118 新行必须写满 33 列**（不要只写看得见的 18 列，会漏 remove/size/function 导致上线异常）
6. **1127 新增建造入口**：`A_ARR_building_ids=[1118 家族 id]`、`C_ARR_display_labels=["decoration"]`、`A_ARR_unlock_cost` = 步骤 2 解锁道具、`C_INT_subtab=4`（装饰分类）
7. **1011 i18n**：补 `A_MAP_lc_name / C_MAP_lc_desc / C_MAP_lc_desc_get / C_ARR_unlock_desc` 等 key
8. **1511 display_key**：所有 `C_INT_display_key / C_INT_model_display_key` 要在 1511 注册
9. **1168 get_access_group**：升级材料配入口（对应 2148.`C_STR_upitem_get_access`），玩家才能点问号跳转
10. **活动联动**：解锁道具 + 升级材料挂到 2124 drop 或 2013 礼包

**buff 归属铁律**（基于 46 组活动装饰 222 行样本）：

- **2148.`A_ARR_BUFF` 是唯一权威**：citybeauty（id=`12230001`）+ 属性 buff（`typ=buff`，id 段 `12117xxx`）都写这里
- **1118.`A_ARR_status` 只放 citybeauty** 1 条：全表 775 行 type=2 装饰无一例外。往 1118 加 `typ=buff` 会导致双重生效
- **citybeauty 冗余同步**：1118 和 2148 两张表的 citybeauty 值必须**完全相同**，改一个要同步改

**星级数值标准档**（可直接套）：

| star_max | 1 星 | 2 星 | 3 星 | 4 星 | 5 星 | 6 星+ |
|---|---|---|---|---|---|---|
| 3 | 200 | 2000 | 4000 | — | — | — |
| 5 | 200 | 1000 | 2000 | 4000 | 8000 | — |
| 10（线性） | 200 | 2000 | 4000 | 5000 | 6000 | +1000/星 → 11000 |
| 10（倍增） | 500 | 2000 | 4000 | 6000 | 8000 | +2000/星 → 18000 |

- **老 3 星装饰多恒定型**（buff val 全程 200 不变，靠"加 buff id + 加 citybeauty"拉升）
- **10 星装饰多阶梯型**（val 逐星 +100，如 12117002: 200→300→...→1000）
- **1 星 buff 的版本演进**：老 ≤2024 的 1 星只给 citybeauty 不给 buff；新 2025+（大富翁系列、2026 春节/情人节/复活节）1 星就送 1 条 buff（解锁即收益）
- **热门 buff id**：12117002/12117009/12117005/12117015(春节/复活节系)/12117004/12117006/12117013(感恩节/周年)/12117010/12117011/12117017(周年/圣诞)

**涂饰 + 技能机制**（47 组里 24 组支持，10 星装饰 100% 支持）：

```
2148.A_INT_paint = 1                         ← 标记"支持涂饰"
2148.C_ARR_paint_item = [1111 涂饰道具 id]
2148.A_ARR_paint_buff = [{typ:buff,id:bufid,val:逐星递增}]
2148.A_INT_decroation_paint_skill = 2171 技能 id（0=该星不解锁技能）
    │
    ├─→ 1111 涂饰道具（class=decorate_paint）
    │     A_MAP_category_param.effect = [
    │       {"typ":"decorate_paint","id":2148.group_id,"val":86400000},
    │       {"typ":"item","id":自身,"val":1}
    │     ]
    │     A_ARR_use_labels = ["bag", "<group_id>"]  ← 第二项必须是 2148 group_id
    │     S_INT_use_now = 0（手动使用）
    │
    └─→ 2171 event_decroation_skill
          A_INT_group（技能组）下 N 级（id = group×10 + 等级）
          A_ARR_status = [{typ:buff, id:bufid, val:持续时长ms, arg1:数值千分位}]
```

**涂饰机制规律**（24 组 144 行样本）：

1. 1 个涂饰道具 → 激活该 group 涂饰 24 小时（86400000ms），到期退回非涂饰态，要续用
2. 同家族一般只绑 1 种涂饰道具（22/24）
3. `paint_buff` 100% 是单条 buff，**从 1 星起就给**（不同于主 BUFF 老版 1 星只给 citybeauty）
4. 技能主流**从第 3 星解锁**：10 星装饰配 8 级技能组（star 3-10 → lv 1-8），6 星配 4 级（star 3-6 → lv 1-4）——严格对应关系
5. 技能 status 时长分档：`7200000ms`（2 小时战斗类）/ `28800000ms`（8 小时集结类）/ `3600000ms`（1 小时）
6. `arg1` = 千分位数值：500=5%、1000=10%、2000=20%；技能升级就是拉 arg1，buff id 和 val 不变

**大富翁 5 星标准模板**（2025+ 节日高频，活动 id=21127362 "漫游奇遇"）：

对标样本：214834 周年庆 / 214839 圣诞 / 214841 春节 / 214842 情人节 / 214848 复活节 / 214849 拓荒节。

| 字段 | 1 星 | 2 星 | 3 星 | 4 星 | 5 星 |
|---|---|---|---|---|---|
| citybeauty | 200 | 1000 | 2000 | 4000 | 8000 |
| 主 BUFF buff 条数 | 1 | 2 | 2 | 2 | 2 |
| 主 BUFF val | 200 | 200 | 400 | 600 | 800 |
| paint_buff val | 200 | 400 | 600 | 800 | 1000 |
| upgrade_cost 材料数 | — | 6 | 12 | 15 | 20 |
| skill（4 级组/2 星起） | 0 | lv1 | lv2 | lv3 | lv4 |
| S_ARR_retake | — | — | — | — | `[{item,11111021,1}]` = 200 CDs |

**节省翻译策略**：`2148.C_MAP_lc_desc` + `1127.C_ARR_unlock_desc` **复用已有 EVENT key** `LC_EVENT_3anni_decoration_get_desc_1`（= "通过活动'漫游奇遇'获得"，多节日大富翁共享）；装饰本体 lc_name 新建 ITEM 段；涂饰道具新建 `LC_ITEM_<主题>_paint_decoration_paint_name/desc`。不新建 BUILDING 段 key。

**大富翁 1168 标准 6 行配法**：每装饰 5 + 1 = 6 条 1168 连续 id。5 行：每星 1 条，`C_STR_item_label` = 2148 **行 id**（如 214849**01~05**），`access_group=[{"id":11531001,"args":["<活动 id>"]}]`；1 行：涂饰道具，`C_STR_item_label` = 2148 **group_id**（如 214849）。**2148.`C_STR_upitem_get_access` 按星升序映射前 5 条；涂饰道具的 1168 id 写到 1111 涂饰道具的 `A_INT_get_access_group`**（不是 2148）。

**装饰三件套 id 必须连续**（大富翁惯例）：解锁道具 / 升级材料 / 涂饰道具的 1111 id 必须 `N / N+1 / N+2`。选号段时先 grep 1111 找 `11112xxx` 段最大连续空位，一次占 3 个号。跨段（解锁放 11111、升级塞 11112）会被策划要求返工。

**坑点清单**：

1. **星级数量不对齐**：2148 和 1118 必须一一对应；1118 少一行 = 最高星无模型；2148 少一行 = 点升级无反应
2. **解锁道具 effect 必须指向一星**：`holiday_statue.id` = 2148 的 star=1 那行；指向其他星 = 一次性升到目标星
3. **2148.unlock_item 和 1127.unlock_cost 不一致**：建造菜单解锁道具 ≠ 活动逻辑期望道具
4. **buff 归属错放**：属性 buff 只写 2148；`typ=buff` 绝不往 1118 放
5. **缺 get_access_group**：问号按钮无反应，玩家不知道去哪拿材料
6. **轮换活动 `A_INT_year_group` 漏配**：跨年复用时会错乱老号玩家数据
7. **涂饰道具 use_labels 第二项必须是 group_id**：漏填 → 道具不绑装饰 → 点使用无反应
8. **技能组等级数 = `star_max - (首次解锁星 - 1)`**：10 星装饰配 6 级技能组 = 8-10 星技能无效
9. **paint_buff 和 A_ARR_BUFF 不要混配**：一条 buff 同时放两字段会叠加

**ID 分配节奏**（截至 2026-04）：

| 表 | 最新已用 | 下一空位 |
|---|---|---|
| 2148 group_id | 214849 | 214850 |
| 1118 building_id | 1118220 | 1118221（之后是 kvk6 大号段 1118924+，装饰可安全 +1） |
| 1127 A_INT_id | 11275234 | 11275235 |
| 1111 `11111xxx` 段 | 11111361 | 11111362 |
| 1111 `11112xxx` 段 | 11112954 | 11112955 |
| 1168 A_INT_id | 11684890 | 11684891 |
| 2171 group | 2171018 | 按需新建或复用热门组 |

---

<a id="2149"></a>
## 2149_p2_activity_upgrade_gachabox — 升级宝箱（空）

<a id="2150"></a>
## 2150_p2_activity_hoggboss_type — Hoggboss 类型（空）

---

<a id="2151"></a><a id="2152"></a><a id="2153"></a>
## 2151-2153 大富翁 Gacha

### 2151 monopoly_gacha_map — 大富翁地图
- `A_INT_lv`：地图等级
- `A_INT_cycle_num`：循环次数（-1=无限）
- `A_ARR_use_item`：消耗
- `A_STR_type`：`cycle`
- `A_INT_steps_start` / `A_INT_steps_count`：格子起始+数量
- `A_ARR_dice` → 2153
- `A_STR_banner_url` → 1020
- `A_ARR_health` / `A_INT_dizz_value` / `A_ARR_dizz`：生命与眩晕

### 2152 monopoly_gacha_reward — 格子奖励
- `A_INT_map_id` → 2151
- `A_STR_type`：格子类型 `start`/`event`/...
- `A_MAP_rewards`：奖励
- `A_MAP_expr`：触发条件
- `A_INT_weight`：权重
- `A_INT_display_key1` / `A_ARR_display_key2`：图标

### 2153 monopoly_gacha_dice — 骰子
- `A_INT_hero_id` → 1920（骰子使用的英雄）
- `A_ARR_dice_num`：骰面
- `S_ARR_dice_num_weight`：骰面权重

---

<a id="2154"></a>
## 2154_p2_activity_without_gacha_floor — Without gacha 保底

- `S_ARR_drop`：按层掉落 `[{"group":101,"wgt":1412,"floor":1},...]`
- `A_INT_activity` → 2112
- `A_INT_floor` / `S_INT_gacha_minimum`：层级和最低抽数

---

<a id="2155"></a>
## 2155_p2_activity_soldierarm_achievement — 兵种武装成就

- `A_INT_soldier_category` → 1122
- `A_MAP_filters`：达成条件 `{"op":"ge","typ":"soldier_arms","ids":[11661008,...]}` → 1166
- `A_ARR_reward` / `A_INT_iap`：奖励和礼包

---

<a id="2156"></a>
## 2156_p2_activity_floor_gacha — 楼层 gacha

- `A_INT_component_id`：组件
- `A_INT_floor`：层
- `S_ARR_freerandfloors` / `A_ARR_randfloors`：免费/付费可抽层
- `S_INT_upgrade_times`：升层次数
- `S_ARR_randcost` / `S_ARR_randpool`：成本与池

---

<a id="2157"></a><a id="2158"></a>
## 2157-2158 装备套装

### 2157 equipment_suit
- `A_STR_suit_name`：LC
- `A_ARR_equipment_id` → 1935
- `A_INT_quality` / `A_INT_type` / `A_INT_priority`：品质/类型/优先级

### 2158 equipment_achievement
- `A_INT_suit_id` → 2157
- `A_MAP_filters`：达成条件 `{"op":"ge","typ":"equipment_assemble","ids":[...]}`
- `A_ARR_reward` / `A_INT_iap`：奖励

---

<a id="2159"></a>
## 2159_p2_activity_festival_popwindow — 节日弹窗

- `A_INT_event_id` → 2112
- `A_INT_priority`：弹窗优先级
- `A_STR_title`：LC
- `A_INT_reward_type`：奖励类型
- `S_ARR_reward`：预览奖励
- `A_STR_reward_url` / `A_STR_banner_url` → 1020

**注**：这是**节日内**的弹窗（独立于 1023 全局弹窗）。1023.components.typ=event 会指向 2121 event id，而此表是 2112 活动 id。

---

<a id="2160"></a>
## 2160_p2_activity_metro_grade — 挖矿活动分级

- `A_MAP_lc_name`：等级名（普通/精英/传奇）
- `A_INT_grade_up_rank` / `A_INT_grade_down_rank`：升降名次
- `A_INT_rank_rule` → 2122
- `A_INT_actv_grade` / `A_INT_actv_type`：等级/类型

---

<a id="2161"></a>
## 2161_p2_activity_soldierskill_achievement — 兵种技能成就

同 2155 结构，针对兵种技能。`A_INT_skill_id` → 34_p2_soldier_skill。

---

<a id="2162"></a>
## 2162_p2_elite_arena_competition_stage — 精英竞技场阶段

- `A_INT_constant`：阶段序号
- `A_ARR_stagemap`：阶段地图 → 1373
- `A_INT_battlenum`：战斗数
- `A_INT_stage_time` / `A_ARR_battle_time`：阶段/战斗时长（毫秒）

---

<a id="2163"></a>
## 2163_p2_activity_survey — 满意度调研

- `A_INT_switch`：开关
- `A_INT_group`：组
- `C_STR_title` / `C_STR_desc`：LC
- `A_ARR_tags`：选项标签
- `A_ARR_reward`：完成奖励
- `S_MAP_filter`：目标玩家
- `S_MAP_activity_info`：关联活动
- `A_ARR_limit`：时间/次数限制 `[60,3]`

---

<a id="2164"></a>
## 2164_p2_collction_blindbox_period — 盲盒期

- `A_INT_current_period`：当前期号
- `A_INT_package_id` → 2135
- `A_INT_use_item` → 1111

---

<a id="2165"></a>
## 2165_p2_activity_anni_report — 周年报告

玩家周年回顾页各维度分数配置（建号天数/等级/战力 等）。`S_INT_left`/`S_INT_right` 定义范围。

---

<a id="2166"></a>
## 2166_p2_activity_flash_sale_raffle — 限时抢购抽奖池

- `A_MAP_category_param`：抽奖配置 `{"drop":{"typ":"single_random","num":1,"args":[...]}}`

---

<a id="2167"></a>
## 2167_p2_activity_flash_sale_virtual — 限时抢购价格系数

- `A_ARR_array_time`：时间分段（小时比例）
- `A_ARR_array_coefficient`：各段价格系数 `[3,0.7,1.35]` — 初期 3 倍/中期 0.7/后期 1.35

---

<a id="2168"></a><a id="2169"></a>
## 2168-2169 HUD 入口

### 2168 activity_hud_entries
- `C_INT_style` → 2169
- `C_MAP_bg_music`：背景音乐 Wwise 事件（`{"play":"Play_tech_festival_2025_music","stop":"Stop_xxx"}`）
- `C_BOL_show_countdown`：倒计时
- `C_STR_bi_click_event`：UI 点击事件类（`UIHudHolidaySciHUD`）

### 2169 hud_entry_style
- `A_STR_constant`：样式 key（`Holiday`/`ItemCollect`）

---

<a id="2170"></a>
## 2170_p2_elite_arena_competition_guessing — 精英竞技场竞猜

- `A_INT_class`：竞猜类型
- `A_MAP_time`：时间窗 `{"start":{"stage":2,"time_index":9999},"end":{"stage":...}}`
- `A_ARR_reward_win` / `A_ARR_reward_lose`：赢/输奖励
- `C_MAP_lc_name/desc/c1/c2`：LC

---

<a id="2171"></a>
## 2171_p2_event_decroation_skill — 装饰技能

字段类似 1924 hero_skill，`A_STR_class` = `decroation_paint_skill`。被 2148 引用。

---

<a id="2172"></a>
## 2172_p2_event_citybeauty_level — 美化值等级

- `A_INT_beauty`：所需美化值
- `A_INT_star` / `A_INT_level`：星级/等级
- `A_ARR_buff`：等级 buff
- `A_ARR_upgrade_reward`：升级奖励

---

<a id="2173"></a>
## 2173_p2_event_citybeauty_shop — 美化值商店

- `A_MAP_item` → 1111
- `A_MAP_price`：用美化值买
- `A_MAP_limit`：限购

---

<a id="2174"></a><a id="2175"></a><a id="2183"></a>
## 2174-2183 挖孔关卡

### 2174 event_hole_digging（老版）
- `A_INT_activity_id` → 2112
- `A_INT_level`：关卡
- `A_ARR_rules`：每关规则 `[{"id":21750006,"num":1}]` → 2175
- `A_INT_COST_Num` / `A_BOOL_is_guaranteed`：消耗/保底
- `A_INT_grid`：网格尺寸
- `A_INT_task_id` / `A_INT_free_task_id` → 2115

### 2175 event_hole_type
- `A_ARR_variants`：方块变体 `[{"Row":0,"Col":0},{"Row":0,"Col":1},...]`
- `A_INT_show`：显示
- `A_ARR_get_reward`：奖励
- `C_INT_unity_key` / `C_INT_collection_group`：UI 配置

### 2183 event_hole_digging_new（v7 新版）
新版字段：
- `A_INT_level_type`：关卡类型
- `A_INT_board_rows` / `A_INT_board_cols`：棋盘尺寸
- `A_ARR_treasure_pool`：宝藏池 `[{"treasure_id":21750001,"num":1,"allow_rotate":false,...}]`
- `A_ARR_tool_trigger`：工具触发
- `A_MAP_reward_window`：奖励窗口
- `A_ARR_blocked_cells`：屏蔽格子
- `A_INT_tip_num`：提示数

**bug**（user memory）：挖孔 6 期埋点 bug 用 `digkeys_start_level` 替代 `status=1` 作为完成口径；7 期修复后恢复 skill 原 SQL。

---

<a id="2176"></a><a id="2177"></a>
## 2176-2177 钓鱼引导

### 2176 fishing_game_guide_group
- `A_MAP_lc_name`：组名（`2026年春节钓鱼` 等）
- `A_ARR_illustrate_reward`：图鉴奖励
- `A_ARR_card_list`：卡列表

### 2177 fishing_game_guide
- `A_INT_quality`：品质
- `A_INT_point`：积分
- `A_INT_item` → 1111（对应鱼 item）
- `A_ARR_get_reward`：获取奖励
- `A_INT_group_id` → 2176

---

<a id="2178"></a><a id="2179"></a><a id="2180"></a><a id="2181"></a>
## 2178-2181 大富翁怪物

### 2178 monopoly_monster
怪物基础数据：`A_INT_monster_type` / `A_INT_monster_level` / `A_INT_health` / `A_ARR_monster_buff` → 2180 / `A_INT_monster_skill_cd` / `A_MAP_drop_skill/normal/beat` / `A_ARR_monster_reward`。

### 2179 monopoly_magic_dice
- `A_INT_dice_result`：骰子点数
- `A_STR_desc`：LC
- `A_INT_weight`：权重
- `A_MAP_event`：触发事件

### 2180 monopoly_monster_buff
怪物 buff 定义。

### 2181 monopoly_monster_skill
怪物技能定义。

---

<a id="2182"></a>
## 2182_p2_coinpusher — 推币机

超大字段表（35 列）— 推币玩法参数。类似 2139 shoot_hunt 结构。

---

## 跨表引用拓扑（精简）

```
2111 日历 ─── activity_id → 2112

2112 activity_config ─┬─ components → 2115/2116/2117/2118/2121/2122/2124/2135/2130 等
                       ├─ ui_template → 2119 → modules → 2120
                       ├─ rank_group → 2114
                       └─ banner URL → 1020

2115 activity_task ── fincond.cat → 1014 counter

2122 rank_rule ── score_rule.cat → 1014 counter

2124 drop ── action_ids 关联各模块

2135 activity_package ─┬─ iap → 2013
                        ├─ get_items → 1111
                        └─ banner → 1020

2130 BP ─┬─ taskids → 2115
          ├─ pkg.args[iap] → 2013
          └─ level → 2131

2132 alliance_comp_pkg ── task → 2133 → task_id → 2115

2148 decroation_level ─┬─ building → 1118
                        ├─ paint_skill → 2171
                        └─ year_group 必须对齐

2151 monopoly_map ─┬─ dice → 2153 → hero → 1920
                    └─ reward → 2152 (by map_id)

2178 monster ─┬─ buff → 2180
               ├─ skill → 2181
               └─ reward → 1111

2159 festival_popwindow ── event_id → 2112

2168 HUD ── style → 2169；music Wwise 事件
```

---

## Jira 工单常见自检路径

| 现象 | 先查的表 | 定位方法 |
|---|---|---|
| 活动不启动 | 2111 + 2112 | time_info/server_info/start_trigger 是否正确 |
| 活动启动时间错（8 小时偏差） | 2111 | UTC vs 服务器时区换算 |
| 活动组件不加载 | 2112 | `A_ARR_activity_components` typ/id 对齐 |
| 任务进度卡 0 | 2115 + 1014 | `A_MAP_fincond.cat` 对应 counter 是否存在/正确 |
| 任务奖励没发 | 2115 | `A_ARR_reward` 的 item id 是否有效 |
| 排行榜分数永远 0 | 2122 + 1014 | `A_ARR_score_rule.cat` 对齐 |
| 排行榜范围错（个人 vs 联盟） | 2122 | `A_INT_rank_unit` |
| 礼包买完没发货 | 2135 + 1111 | `A_ARR_get_items` item 是否有效；iap 关联 2013 |
| 节日弹窗不弹 | 2159 / 1023 | event_id 对齐；1023 typ=event 对齐 2121 而非 2112 |
| BP 经验卡住 | 2130 + 2115 | `taskids` 的任务是否生效；`A_INT_exp` 数值 |
| BP 付费激活无效 | 2130 + 2013 | `A_MAP_pkg.args.iap` 对应的 2013 是否有效 |
| 大富翁格子奖励错 | 2151 + 2152 | `A_INT_map_id` 关联和 `A_STR_type` |
| 大富翁骰子不出稀有 | 2153 | `S_ARR_dice_num_weight` |
| Monopoly 怪物血量错 | 2178 | `A_INT_health` |
| 挖孔关卡卡死 | 2174/2183 + 2115 | `A_INT_task_id` 是否生效；埋点口径（digkeys_start_level） |
| 节日装饰升不了星 | 2148 | `A_ARR_upgrade_cost` item id 有效性 |
| 节日 BP 道具结束后残留 | 2137 | `A_MAP_give_asset` + `A_MAP_cost_asset` |
| 限时抢购价格异常 | 2167 | `A_ARR_array_coefficient` 分段 |
| 装备套装成就不触发 | 2157 + 2158 | suit_id 关联；filters.ids 和 1935 实际 equipment id |
| 英雄成就礼包不弹 | 2144 | `A_MAP_fincond` typ（hero_star/hero_level） |
| 活动 HUD 音效不放 | 2168 | `C_MAP_bg_music` Wwise 事件名拼写 |
| 新节日 id 号段冲突 | 全部 | 必须按号段规范（见 user memory 2011_id_range） |

---

**维护建议**：
1. 节日新实例配置严格走 `p2-unite-gift-pack` skill 的 SOP，不要绕过 Step0（从真实表读 ≥2 节日对照）。
2. 跨节日平移 id 时必须区分通用 vs 专属（见 user memory `通用道具vs节日专属道具`）。
3. 新合服必须在 2111.server_info 和 2014 iap_coeffs 的 schema list 同步扩展。
4. 任务/排行的 counter id（`A_MAP_fincond.cat` / `score_rule.cat`）是节日活动最脆弱的引用链，每个新活动务必 grep 1014 校验。
