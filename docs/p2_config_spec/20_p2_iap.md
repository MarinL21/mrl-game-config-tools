# 20_p2_iap 内购/VIP/成长基金/成就礼包/红包 配置规范

> **用途**：P2 所有**内购付费**相关——从 IAP 套装定义、模板内容、价格档位、VIP 体系、累充、酒馆会员、成就礼包、破冰礼包、红包、BI 推荐到退款配置。被 `typ:"iap"` / `typ:"iap_purchases"` / `typ:"vip"` 全库引用。
>
> **Jira 自检场景**：礼包买完没发 / VIP 经验不涨 / 累充不解锁 / 成就礼包不触发 / 国服/海外价格档位错 / 破冰礼包不弹 / 时卡奖励错 / 红包分发异常 / BI 推荐不精准 / 退款率配置错。

> **前置**：字段前缀约定见 [`10_p2_const.md`](./10_p2_const.md)。`typ:"iap"` 的 id 指向本文件夹的 2011（套装入口）或 2013（模板细节）。

---

## 表清单

### IAP 主体（2011-2016）
| 表号 | 用途 |
|---|---|
| [2011](#2011) | **IAP 主表**（套装入口，不含内容） |
| [2013](#2013) | **IAP 模板**（具体内容） |
| [2014](#2014) | IAP 系数（按 schema 分服调价） |
| [2016](#2016) | 累充礼包 |

### VIP 体系
| 表号 | 用途 |
|---|---|
| [2017](#2017) | VIP 等级 |
| [2018](#2018) | VIP 签到 |
| [2019](#2019) | VIP buff |

### 成长基金
| 表号 | 用途 |
|---|---|
| [2020](#2020) | 主城成长基金 |
| [2031](#2031) | 地铁/挖矿成长基金 |

### 订单 / 管理
| 表号 | 用途 |
|---|---|
| [2021](#2021) | IAP 页签顺序 |
| [2022](#2022) | 每日特惠（空） |
| [2023](#2023) | 每日领取（分期奖励） |

### 自定义宝箱 / 阶段奖励
| 表号 | 用途 |
|---|---|
| [2024](#2024) | 自定义宝箱内容 |
| [2025](#2025) | 新人阶段奖励 |

### 酒馆会员
| 表号 | 用途 |
|---|---|
| [2026](#2026) | 酒馆会员等级 |
| [2027](#2027) | 酒馆会员特权 |

### 成就礼包（按品类）
| 表号 | 用途 |
|---|---|
| [2032](#2032) | 科技成就 |
| [2033](#2033) | 科技成就任务 |
| [2034](#2034) | 机甲成就 |
| [2039](#2039) | 战车成就 |
| [2041](#2041) | 机甲驾驶员成就 |

### 红包 / 时卡 / 破冰 / BI / 广告
| 表号 | 用途 |
|---|---|
| [2028](#2028) | 退款概率 |
| [2029](#2029) | 红包（节日分发） |
| [2030](#2030) | BI IAP 推荐 |
| [2035](#2035) | 破冰礼包弹窗 |
| [2036](#2036) | 时间卡奖励 |
| [2040](#2040) | IAP 广告推送 |
| [2042](#2042) | 每日礼包 |

### 酒馆积分（内购兑换）
| 表号 | 用途 |
|---|---|
| [2037](#2037) | 酒馆积分兑换 IAP |
| [2038](#2038) | 酒馆 IAP 积分 |

---

## IAP 核心拓扑（**必知**）

```
2011 iap_config   <─── 玩家买一个套装 = 买这里一条
  ↓ config_id
2013 iap_template <─── 具体套装内容、价格、美术
  ↓ coeffs_id
2014 iap_coeffs   <─── schema 级的价格系数
  ↓ group/daily_iap_id 等被
2025/2023/...     <─── 派生礼包引用
```

**配新礼包**：一般要动 **2011**（入口/函数/优先级）+ **2013**（内容/价格）+ **1111**（礼包拆出的 item）+ **1023 弹窗**（如果要弹）。

**iap id 的两种含义**：
- `2013xxxxxxxx`（10 位）= 2013 template id（具体档位）— 大部分 requirement 里 `typ:"iap"` 用的是这个
- `2011xxxxxxx`（9 位）= 2011 config id（套装入口）— 破冰弹窗等走这个

---

<a id="2011"></a>
## 2011_p2_iap_config — IAP 主表（套装入口）

**字段**：
| 字段 | 含义 | 枚举/格式 | 关联 | bug |
|---|---|---|---|---|
| `A_INT_id` | 主键 | 201110001 起；节日新段从 **2011610000** 起（见 user memory） | - | 重用 id → 老玩家存档有残留 |
| `N_STR_pkg_desc` | 策划注释（中文名） | - | - | N_ 不下发 |
| `A_STR_function` | 代码 function | `basic_CDs`/`accum_recharge`/`bi_pkg_push`/`daily_package` 等 | - | function 决定入口逻辑，写错会走错代码分支 |
| `A_STR_pkg_type` | 包类型 | 同 function 或别 | - | - |
| `A_STR_paywall_tab` | 所属 paywall 页签 | 匹配 2021 的 `A_STR_tab_name` | 2021 | 写错 → 在付费墙找不到 |
| `A_BOL_pirce_display` | 是否显示价格 | `True`/`False` | - | - |
| `S_MAP_server_info` | 生效服务器 | `{"typ":"schema","id":[...]}` | - | 新合服漏加 schema id → 该服看不到 |
| `A_INT_priority` | 优先级 | 数字大=先排 | - | - |
| `A_MAP_time_info` | 时间窗（5 模式） | 顶层 key 决定模式，见下表 | 2112(actv_id) | 时间窗错 → 提前/延后上架；节日 BP 通行证复用必须更新 actv_id |
| `S_MAP_filters` | 玩家筛选 | - | - | - |
| `A_MAP_triggers` | 触发条件 | - | - | - |
| `A_ARR_iap_status` | 套装状态 buff | `[]`/status 数组 | 12xxx | - |
| `A_INT_iap_new` | 新标签 | 0/1 | - | - |
| `S_MAP_group_limit` | 组限制 | `{}` 默认 | - | - |
| `A_STR_apply_scene` | 应用场景 | `common`/`festival` 等 | - | - |
| `A_INT_close_sell_out` | 卖完关闭 | 0/1 | - | 1=某玩家买过就隐藏 |
| `A_STR_sub_scene` / `A_STR_sub_tab` | 子场景/子页签 | - | - | - |
| `A_INT_country_use_type` | 区服 | 0/1/2 | - | - |
| `A_INT_double_coupon` | 双倍券 | 0/1 | - | - |

**常见 bug**：
- **schema 列表漏新合服 id**：玩家在新合服服看不到礼包；改 2011 时忘了扩展 schema list。
- **function 写错**：把 `basic_CDs` 写成 `basic_cds`（大小写）→ 代码走默认分支，UI 显示但点击无效。
- **priority 冲突**：多个礼包同优先级 → 顺序按 id 随机。
- **id 号段**（见 user memory）：节日新实例默认从 `2011610000` 起，不能占用 5/4 段。

**A_MAP_time_info 5 种模式**（顶层 key 决定语义）：

| 模式 | 示例 | 含义 |
|---|---|---|
| `normal` | `{"normal":[{"actv_id":21127364}]}` | **活动礼包最常用**：绑定 2112 活动 id，活动期间生效 |
| `normal`（base） | `{"normal":[{"actv_base_id":21121559}]}` | 绑定基础活动 id |
| `normal`（永久） | `{"normal":[{"start_time":0,"duration":3153600000}]}` | start_time=0 + duration≈100 年 = 永久 |
| `normal`（延迟） | `{"normal":[{"actv_id":21121141,"day":4,"duration":259200}]}` | 活动开始第 4 天起生效，持续 3 天 |
| `scene` | `{"scene":{"duration":43200,"refresh_time":43200,"buy_refresh":1}}` | 触发场景型，按刷新时间重置 |
| `cycle` | `{"cycle":[{"range":"day","hour":0,"duration":86400}]}` | 周期型，按天/小时循环 |
| `time` | `{"time":[{"start_time":"2025-10-30 00:00:00","duration":345600}]}` | 绝对时间型 |
| `time_card` | `{"time_card":{"duration":604800}}` | 周卡/月卡型 |

**常用 duration（秒）**：3600=1h / 43200=12h / 86400=1d / 172800=2d / 259200=3d / 604800=7d / 2592000=30d / 3153600000≈100 年（永久）。

**`A_STR_function` vs `A_STR_pkg_type`**：function 给**客户端**用（控制前端入口逻辑），pkg_type 给**服务器**用（和 2013.`A_STR_temp_type` 必须一致）。默认 `function=normal_pkg` + `pkg_type=normal`。随机礼包专用：`function=random_pkg` + `pkg_type=random`，并且 `A_ARR_iap_status` 额外包含 `{"typ":"drop","id":2124xxxx}` 指向 drop 奖池。

**`S_MAP_server_info` 生命周期 schema id 对照**：1=第1-13天 / 2=14-43 / 3=24-86 / 4=87-170 / 5=171-299 / 6=300+ / 13-18=KVK1-6 / 55=巅峰领土战。默认全 schema 覆盖 `[1,2,3,4,5,6,13,14,15,16,17,18,55]`。

---

<a id="2013"></a>
## 2013_p2_iap_template — IAP 模板（具体内容）

**字段**：
| 字段 | 含义 | 枚举 | 关联 | bug |
|---|---|---|---|---|
| `A_INT_id` | 主键 | 2013xxxxxxxx（10 位） | - | - |
| `A_STR_temp_type` | 模板类型 | `basic_CDs`/其它 | - | 和 2011 function 通常一致 |
| `A_INT_config_id` | 对应 2011 套装 id | → 2011 | 2011 | 失效 → 套装显示空 |
| `A_INT_coeffs_id` | 系数表 id | → 2014 | 2014 | 系数失效 → 价格错 |
| `N_STR_temp_desc` | 策划备注 | - | - | - |
| `A_STR_pkg_title` / `A_STR_pkg_desc` | 标题/描述 LC | LC_IAP_xxx | 1011 IAP | - |
| `A_FLT_price` | 基础价（美元） | 0.99/4.99/9.99/... | - | - |
| `A_ARR_price_info` | 各渠道产品 id | `[{"pay_type":"gplay","product_id":"ape_0099_cd_an"},{"pay_type":"appstore","product_id":"..."}]` | - | **product_id 拼错 → 整个渠道充值失败**（最高频 bug） |
| `A_MAP_limit` | 购买限制 | `{"limit_cnt":0,"limit_type":"period"}` | - | limit_cnt=0 = 无限；若限购需填正数 |
| `S_INT_limit_whitelist` | 限购白名单 | - | - | - |
| `A_INT_CDs` | 含多少 CD（游戏币） | - | 1115 | - |
| `A_INT_all_value` | 总价值（战力折算） | - | - | 新礼包漏配 → 战力收益分析报错 |
| `A_ARR_CD_items` | CD 类道具 | - | 1111 | - |
| `A_ARR_speedup_items` | 加速类道具 | - | 1111 | - |
| `A_ARR_resource_items` | 资源类道具 | - | 1111/1114 | - |
| `A_ARR_pvp_items` | PvP 类道具 | - | 1111 | - |
| `A_ARR_other_items` | 其它道具（主要） | `[{"asset":{"typ":"item","id":11114303,"val":1},"setting":...}]` | 1111 | 道具 id 失效 → 买了没东西 |
| `A_ARR_card_items` | 卡类 | - | - | - |
| `A_ARR_tag_txt` | 标签文本 | `[{"typ":"lc","txt":"LC_IAP_CD_first_buy","tag":1,"val":...}]` | 1011 | - |
| `A_INT_hud` | HUD 显示 | 0/1 | - | - |
| `A_STR_style_url` / `A_STR_pop_banner_url` / `A_STR_banner_url` | 样式/弹窗/横幅 URL | - | 1020 | URL 拼错 404 |
| `A_MAP_param_color` | 参数色 | - | - | - |
| `A_INT_tag` | 标签类型 | 1（首充）/其它 | - | - |
| `A_STR_subscript` / `A_STR_sub_desc` | 角标/副描述 | - | - | - |
| `A_MAP_special_style` | 特殊样式 | - | - | - |
| `A_INT_country_use_type` | 区服 | 0/1/2 | - | - |
| `A_ARR_increment_items` | 增量道具 | - | - | - |

**常见 bug**：
- **product_id 和各渠道实际不匹配**：Google Play / App Store / 华为 / 小米 各渠道后台 product id 必须和 `A_ARR_price_info` 一一对应。typo 最高频。
- **other_items 里 item id 失效**：买了不发货。
- **首充 tag 漏配**：首充 buff 不触发，玩家二次充值误触发。
- **banner_url/style_url 没 bump 1020 version**：换图但客户端还是老图。

---

<a id="2014"></a>
## 2014_p2_iap_coeffs — IAP 系数

**字段**：
- `A_INT_id`：主键
- `A_ARR_coeffs`：按 schema 的系数数组 `[{"schema":1,"ratio":[1,1,1,1,1],"time_card_ratio":[1]}, ...]`
  - `schema`：服务器方案号
  - `ratio`：各类别系数（可能是 CD/speedup/rss/pvp/other 五类）
  - `time_card_ratio`：时卡专用系数

**bug**：合服后 schema 扩了但 coeffs 未补对应条目 → 新 schema 走默认系数（通常 1），导致定价异常。

---

<a id="2016"></a>
## 2016_p2_iap_recharge — 累充礼包

**字段**：
- `A_STR_function`：`accum_recharge`
- `A_INT_claim_CDs`：累充 CD 阈值
- `A_STR_banner_url`：海报
- `A_ARR_rewards`：奖励 `[{"asset":{"typ":"item","id":xxx,"val":x},"setting":...}]`
- `A_INT_all_value`：总价值
- `A_MAP_time_info`：时间窗 `{"server_open":[{"start_time":0,"duration":3715200}]}`
- `A_INT_hud`：HUD

**bug**：claim_CDs 档位不按梯度递增 → 累计奖励错跳档。

---

<a id="2017"></a>
## 2017_p2_vip — VIP 等级

**字段**：
- `A_INT_level`：VIP 等级（0-∞）
- `A_INT_xp`：升到该级所需经验
- `C_INT_is_highlight`：高亮显示
- `A_ARR_daily_free_reward`：每日免费奖励（→ 1111）
- `A_ARR_special_offer`：专属 IAP 礼包 id 列表（→ 2013）
- `C_ARR_special_monthly`：月卡特权列表（→ 2013）
- `A_MAP_purchase_limit`：购买限制 `{"typ":"level"}`
- `C_INT_level_icon`：等级图标
- `A_ARR_buff`：VIP buff 列表（→ 2019）
- `C_INT_vip_text` / `C_INT_vip_num`：UI key
- `A_ARR_extra_reward`：额外奖励

**bug**：special_offer 的 2013 id 失效 → VIP 专属礼包不显示；buff 的 2019 id 失效 → VIP 等级升了但特权无效。

---

<a id="2018"></a>
## 2018_p2_vip_sign — VIP 签到

- `A_INT_day`：第几天
- `A_INT_vip_xp`：获得 VIP 经验

---

<a id="2019"></a>
## 2019_p2_vip_buff — VIP buff

**字段**：
- `A_INT_buff_id`：实际 buff id → 12xxx
- `C_STR_type`：类型 `int`/`float`
- `A_INT_value`：值
- `C_MAP_buff_name` / `C_MAP_buff_desc`：LC
- `C_INT_buff_icon`：图标
- `C_INT_prev_buff`：前置 buff

**bug**：被 2017.buff 引用，id 链断 → VIP 升级没效果。

---

<a id="2020"></a>
## 2020_p2_growth_investment — 成长基金

**字段**：
- `A_INT_building_level`：基地等级阈值
- `A_INT_type`：基金类型
- `A_ARR_reward_free` / `A_ARR_reward_pay`：免费/付费奖励
- `C_INT_display_url_free` / `S_STR_style_url_purchase`：UI URL
- `A_INT_reward_CDs`：现金 CD
- `C_INT_display_base_level`：展示等级
- `C_INT_pay_value`：付费标价
- `S_MAP_unlock_requirement`：解锁条件
- `C_INT_display_icon_free` / `C_INT_display_icon_pay`：图标
- `C_INT_phase_monkey`：阶段标记

**bug**：基金未购买但玩家升了建筑级 → `reward_free` 发到但 `reward_pay` 漏发没记录（需配合购买状态）。

---

<a id="2021"></a>
## 2021_p2_iap_order — IAP 页签顺序

**字段**：
- `A_STR_tab_name`：页签名（匹配 2011.paywall_tab）
- `A_INT_order`：排序
- `A_MAP_tab_triggers`：显示条件
- `S_ARR_tab_contents`：该页签内容列表
- `S_STR_control_id`：UI 控制 id（`UIIAPMain.Tab.xxx`）
- `S_STR_free_control_id`：免费版本控制 id

**bug**：2011.paywall_tab 写的名字在 2021 中找不到 → 礼包找不到归属页签，消失。

---

<a id="2022"></a>
## 2022_p2_iap_daily_specials — 每日特惠（主 Tab 空）

<a id="2023"></a>
## 2023_p2_iap_daily_receive — 每日分期领取

**字段**：
- `A_INT_iap_template_id`：关联 2013 模板
- `A_ARR_reward`：`[{"daily":2,"Goods":[{"asset":{"typ":"item","id":xxx,...},"setting":...}]},...]` — 按天拆分发放

**bug**：daily 数字错 → 发放节奏混乱；Goods 为空 → 某天无奖励。

---

<a id="2024"></a>
## 2024_p2_iap_custom_chest — 自定义宝箱

**字段**：
- `A_INT_template_id`：**关联 2013 模板 id**（= 2013 的 `A_INT_id`）
- `A_MAP_path`：宝箱位置 `{"col":1,"row":1}`（决定 UI 布局）
- `A_MAP_CD_items` / `A_MAP_speedup_items` / `A_MAP_resource_items` / `A_MAP_pvp_items` / `A_MAP_other_items`：各类可选项
- `A_INT_max`：每日最多选几个（通常 1）

**关联结构**：1 个 2013 → N 个 2024（每个 2024 = 一个可选奖励坑位）。template_id 失效 → 整个宝箱不显示。

### 2024 + item_subscription 两种模式

**2024 与 1111 解锁道具各自独立绑定 2013，不互相依赖**：

- `2024.A_INT_template_id → 2013`（定义自选坑位内容）
- `1111.A_MAP_category_param.effect.id → 2013`（当 `class=item_subscription` 时，定义解锁哪套自选奖励）
- 两者可指向同一个 2013，也可指向不同 2013

**自选周卡完整链路**（两种模式殊途同归）：

```
2112 活动
  └─ package(2135) → 2011(fes_weekly_card) → 2013（直售层）
       │
       ├─ 路径 A: 直接购买
       │    2013 本身被 2024 直接绑定
       │    玩家购买 → 获得自选奖励资格
       │
       └─ 路径 B: 全选包解锁道具
            2013 奖励中含解锁道具（1111, class=item_subscription）
            └─ effect.id → 某个 2013（可以和路径 A 同一个）
                 └─ 被 2024 通过 template_id 绑定
```

**解锁道具机制**（`class=item_subscription`）：

| 字段 | 说明 | 示例 |
|---|---|---|
| `A_STR_class` | 固定 `item_subscription` | - |
| `A_MAP_category_param.effect` | `[{"typ":"item_subscription","id":2013xxxx}]` | `2013400161` |

玩家使用该道具后解锁对应 2013 关联的自选奖励（2024 表），周卡期间每日可领。

**操作要点**：

- 轮换活动要分离解锁道具时，只需新建 1111 道具并让 `effect.id` 指向已有的 2013，**无需新建 2024 坑位**
- 2024 坑位只在自选奖励内容变化时才需要改
- 全选包的 2011.`S_MAP_filters` 会检查其他档位的 2013 id 是否未购买（互斥逻辑）

---

<a id="2025"></a>
## 2025_p2_iap_stage_reward_config — 阶段奖励

**字段**：
- `A_INT_group` / `A_INT_base_group`：分组
- `S_MAP_time_info`：时间窗 `{"regutc":{"regutc_day":0,"duration":604800}}` — 注册后 N 天内
- `A_MAP_condition`：达成条件 `{"typ":"item","id":xxx,"val":N}`
- `A_ARR_rewards`：奖励
- `S_ARR_daily_iap_id` / `S_ARR_weekly_iap_id`：每日/每周 IAP 模板 id

**bug**：regutc_day 偏移错 → 新手阶段提前结束；daily_iap_id 失效 → 新手阶段每日礼包不显示。

---

<a id="2026"></a><a id="2027"></a>
## 2026-2027 酒馆会员

### 2026 tavern_membership
- `A_INT_level`：会员等级
- `A_INT_point_require`：积分门槛
- `A_INT_point_item`：积分对应 item id（→ 1111）
- `A_ARR_iap_id`：该等级对应的 IAP（→ 2013）
- `A_ARR_privilege`：特权列表 `[{"id":20270003}]` → 2027
- `C_INT_card_display_key` / `C_INT_card_number`：卡面 UI

### 2027 membership_privilege
- `C_INT_privilege_group`：特权分组
- `A_STR_constant`：code key（`tavern_privilege_ap` 等）
- `C_STR_privilege_display_key` / `C_STR_privilege_name` / `C_STR_privilege_desc`：UI
- `S_ARR_shield_server`：屏蔽服列表
- `C_INT_unlock_level`：解锁会员等级

**bug**：2026 privilege 里的 id 在 2027 不存在 → 特权失效。

---

<a id="2028"></a>
## 2028_p2_iap_refund — 退款概率

**字段**：
- `S_ARR_range`：累计付费区间 `[0,99.99]`
- `A_FLT_refund_seven`：7 日内退款率
- `A_FLT_prob`：当前概率
- `A_FLT_history_prob`：历史概率

用于风控，调整高风险玩家的退款概率预警。

---

<a id="2029"></a>
## 2029_p2_red_pack — 红包

**字段**：
- `A_STR_constant`：code key
- `A_ARR_lc_content`：祝福语 LC
- `A_MAP_rewards`：红包金额 `{"typ":"vm","id":11151001,"val":75}`
- `A_INT_num`：分发人数
- `A_ARR_channel`：可分发渠道 `[1,2,3]`
- `A_FLT_val`：有效时长（毫秒）`86400000` = 1 天
- `A_INT_rule`：规则
- `C_ARR_event_pack`：关联节日活动 id → 2121（春节等）
- `A_INT_limit`：限制
- `A_INT_quality_display` / `A_INT_bg_display`：品质和底图

**bug**：event_pack 节日 id 失效 → 红包在节日外触发；channel 列表不含玩家当前渠道 → 红包分享菜单不显示。

---

<a id="2030"></a>
## 2030_p2_bi_iap_push — BI IAP 推荐

**字段**：
- `S_STR_typ`：BI 类型 `bi_hero_exp` / `bi_hero_purple_star` 等
- `S_MAP_filters`：玩家条件
- `S_INT_pay_total`：累计付费阈值

bug：typ 拼错或 filter 恒假 → BI 推荐不生效。

---

<a id="2031"></a>
## 2031_p2_metro_growth_investment — 地铁成长基金

同 2020 结构，针对挖矿/地铁小游戏。

- `A_INT_minecraft_level`：挖矿等级阈值
- `C_INT_show_type`：展示类型

---

<a id="2032"></a><a id="2033"></a>
## 2032-2033 科技成就

### 2032 tech_achievement
- `A_INT_level`：成就等级
- `A_INT_xp`：升级所需 xp
- `A_ARR_reward`：等级奖励
- `A_INT_package_unlcok`：关联解锁礼包 → 2013

### 2033 tech_achievement_task
- `A_INT_category`：任务分类（20 = 民用科技等）
- `A_MAP_showcond` / `A_MAP_fincond`：显示/完成条件（counter → 1014）
- `A_INT_pretrace`：前置
- `A_ARR_awards`：奖励
- `A_INT_display_tab`：页签（11321003 = 1132 科技分类）
- `S_INT_show_type`：展示类型

**bug**：fincond 的 counter id（`10142128`）和 1014 实际不符 → 任务进度卡 0（见 user memory 中的 counter 口径 bug）。

---

<a id="2034"></a>
## 2034_p2_mecha_achievement — 机甲成就

- `A_INT_quality`：机甲品质
- `A_MAP_fincond`：完成条件 `{"op":"ge","typ":"mecha_level","id":3,"val":60}`
- `A_INT_iap`：对应 IAP 模板 id → 2013（**命名注意**：本表用 `A_INT_iap`，2035 同位字段叫 `A_INT_iap_id`，历史遗留不一致，查表时两个都要认）
- `A_INT_mecha_id`：机甲 id → 40_p2_mecha_system

---

<a id="2035"></a>
## 2035_p2_iap_pop_first — 破冰礼包弹窗

**字段**：
- `A_INT_iap_id`：对应 IAP 模板 id → 2013
- `A_STR_front_banner1`：弹窗图路径（需 1020 注册）
- `A_INT_display_key`：UI key
- `A_INT_parameter`：参数
- `A_INT_effect`：效果 displaykey
- `A_INT_discount_icon`：折扣图标

**bug**：iap_id 失效 → 弹窗显示但点击跳错/跳空白。

---

<a id="2036"></a>
## 2036_p2_time_card_reward — 时间卡奖励

**字段**：
- `S_MAP_server_info`：生效服
- `A_INT_val`：卡激活数（0=免费；1=激活1张）
- `S_ARR_reward`：奖励
- `A_INT_priority`：优先级

按 schema × val 分层发奖。新合服漏配 → 时卡奖励缺失。

---

<a id="2037"></a>
## 2037_p2_tavern_exchange_iap — 酒馆积分兑换 IAP

- `S_INT_iap_id` / `S_FLT_price`：关联 IAP 和价格
- `S_MAP_item_id`：兑换的 item
- `A_ARR_need_point`：所需积分 `[{"typ":"xp","id":11161009,"val":100}]` → 1116
- `A_INT_buy_limit`：购买上限
- `A_INT_refresh_time`：刷新间隔（毫秒）
- `A_INT_iap_type`：0/3 — 0=纯积分兑换，3=积分+现金

<a id="2038"></a>
## 2038_p2_tavern_iap_point — 酒馆 IAP 积分

- `S_FLT_price`：IAP 价格
- `A_INT_iap_id` → 2013
- `A_ARR_get_point`：获得积分数量
- `C_ARR_access_group`：获取途径（→ 1153）

---

<a id="2039"></a>
## 2039_p2_tank_achievement — 战车成就

类似 2034，针对战车系统。`A_INT_tank_slot_id` 指向战车槽位。

<a id="2040"></a>
## 2040_p2_iap_ads_push — IAP 广告推送

- `S_INT_id`：IAP 模板 id
- `S_FLT_point`：推送权重

用于 Google Ads 智能事件权重（配合 1028）。

<a id="2041"></a>
## 2041_p2_mecha_driver_achievement — 机甲驾驶员成就

- `A_INT_need_power`：战力阈值
- `A_ARR_free_reward`：免费奖励
- `A_INT_link_iap` → 2013
- `C_INT_power`：战力显示

<a id="2042"></a>
## 2042_p2_daily_package — 每日礼包

- `A_ARR_reward`：每日免费礼包内容
- `S_MAP_filters`：玩家筛选 `{"op":"or","args":[{"op":"eq","typ":"iap_purchases","id":...}]}` — 通常用于新手或首充判定

---

## 跨表引用拓扑

```
2011 config ─┬─ 被 requirement "typ=iap" 全库引用
              ├─ 决定 IAP 入口函数
              └─ config_id 被 2013.config_id 反查

2013 template ─┬─ config_id → 2011
                ├─ coeffs_id → 2014
                ├─ other_items/resource_items 里 item → 1111/1114/1115
                ├─ banner/style/pop_banner URL → 1020
                └─ 被 2017.special_offer / 2023.iap_template_id / 2024.template_id / 2025.daily_iap_id / 2029 / 2034 / 2035 / 2037 / 2038 广泛引用

2014 coeffs ── 按 schema 分服系数；新合服必须扩 schema

2017 vip ─┬─ special_offer → 2013
          ├─ buff → 2019
          └─ 被 requirement "typ=vip" 引用

2026 tavern_membership ─┬─ iap_id → 2013
                         ├─ privilege → 2027
                         └─ point_item → 1111

2033 tech_achievement_task ── fincond.cat → 1014

2035 pop_first ── iap_id → 2013；front_banner1 → 1020

2029 red_pack ── event_pack → 2121

1023 popwindow.components.typ=iap, id=[2011xxx] → 2011
1023 popwindow.components.typ=iap_recharge → 2016 概念

2030 bi_iap_push ── 被代码按 S_STR_typ 索引，不直接绑 id
```

---

## Jira 工单常见自检路径

| 现象 | 先查的表 | 定位方法 |
|---|---|---|
| 礼包买完不发货 | 2013 | `A_ARR_other_items` 的 item id 是否有效 |
| 充值无响应 | 2013 | `A_ARR_price_info.product_id` 拼写 |
| 礼包不显示（某服） | 2011 + 2014 | schema 列表是否含当前服 |
| 礼包不显示（某国） | 2011 + 2013 | `A_INT_country_use_type` |
| 礼包在付费墙找不到 | 2011 + 2021 | paywall_tab 在 2021 有没有注册 |
| 首充没奖励 | 2013 | `A_INT_tag`=1 + first_buy tag_txt |
| 累充不触发 | 2016 | `A_INT_claim_CDs` 阈值和 `A_MAP_time_info` |
| VIP 升级无特权 | 2017 + 2019 | buff id 是否有效；prev_buff 链 |
| VIP 月卡不发货 | 2017 + 2013 | `C_ARR_special_monthly` → 2013 模板 |
| 成长基金付费界面错 | 2020 | `A_INT_building_level` 阈值 |
| 科技成就任务卡 0 | 2033 + 1014 | fincond.cat 对应 1014 counter 是否存在 |
| 机甲成就礼包不触发 | 2034 | `A_MAP_fincond` 的 `typ`/`id` |
| 破冰弹窗空白 | 2035 + 2013 | iap_id 是否有效 |
| 时卡奖励漏发 | 2036 | schema + val 组合是否覆盖 |
| 酒馆会员积分兑换失效 | 2037 | `S_MAP_item_id` 和 `A_ARR_need_point` |
| 新手阶段礼包不弹 | 2025 | regutc_day 偏移 / daily_iap_id 有效性 |
| 红包分享渠道缺失 | 2029 | `A_ARR_channel` 和 event_pack 时间窗 |
| BI 推荐太激进/太保守 | 2030 | `S_STR_typ` 和 `S_MAP_filters` |
| 自定义宝箱坑位空 | 2024 | `A_MAP_path` 和 `A_INT_max` |
| 退款率异常 | 2028 | `S_ARR_range` 和 `A_FLT_refund_seven` |

---

**维护建议**：IAP 配置是**后端+多渠道**耦合最严重的一块——改 2013 的 `A_ARR_price_info` 必须同步到各渠道后台的 product 清单。2011/2013/2014 三表联动改动要一次过 CR，单表改漏是顶级付费事故源。
