# 科技节2026 — 行军特效礼包 + 联动礼包完整参考样本

> 来源：从真实 QA 主页签读取（2026-04-15）。用于后续节日换档的黄金样本。

## 主链路 ID 总览

| 表 | 用途 | 科技节2026 ID | 所在行 |
|---|---|---|---|
| 2112 | 行军特效礼包主活动 | `21127569` | `activity_config_qa!1641` |
| 2112 | 联动礼包主活动 | `21127570` | `activity_config_qa!1642` |
| 2112 | 行军表情礼包主活动 | `21127576` | `activity_config_qa!1648` |
| 2135 | 行军特效 package 壳 | `21359396` | `activity_event_pkg!4677` |
| 2011 | 特效礼包 IAP 壳 | `2011500696` | `iap_config_QA!5021` |
| 2013 | 特效礼包 IAP 模板 | `2013510996` | `iap_template_QA!9267` |
| 2121 | 联动 unite_pkg 组件 | `21217498` | `activity_special_QA!2761` |
| 2121 | 表情礼包 discount 组件 | `21218486` | `activity_special_QA!2994` |
| 2121 | 表情礼包 emoji_show 组件 | `21218487` | `activity_special_QA!2995` |

## 行军特效礼包 — 2112 (21127569)

```
S_STR_comment = 2026科技节-行军特效礼包
A_STR_constant = event_march_effect_2026_tech
S_INT_priority = 49999
A_INT_base_activity_id = 21127505
A_MAP_filter = {"op":"and","args":[
  {"op":"ge","typ":"building","id":111811,"val":6},
  {"op":"eq","typ":"iap_purchases","id":2013510996,"val":0}   // 已购过就隐藏
]}
A_MAP_text = {"group_label":"LC_EVENT_unite_name_3anni_2025","label":"LC_EVENT_march_effect_pkg_2025"}
A_ARR_activity_components = [{"typ":"package","id":21359396}]
A_INT_ui_template = 21191361
S_STR_banner_url = assets/operation/P2dlcimg/activityImg/EventBanner_BG_461.png
S_STR_calendar_banner_url = assets/operation/P2dlcimg/activityImg/EventBanner_Timeline_155.png
A_INT_show_hud = 21680027
A_INT_calendar = 1
C_INT_display_flags = 71
```

## 联动礼包 — 2112 (21127570)

```
S_STR_comment = 联动礼包-2026科技节
A_STR_constant = event_unite_3tech_2026
S_INT_priority = 50000
A_INT_base_activity_id = 21127506
A_MAP_filter = {"op":"ge","typ":"building","id":111811,"val":6}   // 不用加 iap_purchases
A_MAP_text = {
  "group_label":"LC_EVENT_unite_name_3anni_2025",
  "label":"LC_EVENT_unite_event_double_3anni_2025",
  "title":"LC_EVENT_unite_event_double_3anni_2025"
}
A_ARR_activity_components = [{"typ":"unite_pkg","id":21217498}]
A_INT_ui_template = 21191065
S_STR_banner_url = assets/operation/P2dlcimg/activityImg/EventBanner_BG_77.png
A_INT_calendar = 0   // 联动礼包不上日历
C_INT_display_flags = 0
```

## 2135 package — (21359396)

```
N_STR_comment = 2026科技节行军特效礼包
A_INT_iap = 2011500696
A_STR_cd_cost_title = NULL
A_STR_cd_cost_text = NULL
A_INT_order = 996
C_STR_tab = NULL
```

（其他字段都为空/默认。2135 本质就是 2112→2011 的桥）

## 2011 IAP 壳 — (2011500696)

```
N_STR_pkg_desc = 2026科技节-行军特效礼包
A_STR_function = special
A_STR_pkg_type = normal
A_BOL_pirce_display = False
S_MAP_server_info = {"typ":"schema","id":[1,2,3,4,5,6,13,14,15,16,17,18,55]}
A_INT_priority = 3005
A_MAP_time_info = {"normal":[{"actv_id":21127569}]}   // 回指 2112
A_ARR_iap_status = [   // 累充活动联动，每节日都不同
  {"typ":"recharge_actv","id":21127573,"val":1},
  {"typ":"recharge_actv","id":21127577,"val":1},
  {"typ":"recharge_actv","id":21127658,"val":1},
  {"typ":"recharge_actv","id":21127657,"val":1},
  {"typ":"recharge_actv","id":21127344,"val":1},
  {"typ":"recharge_actv","id":21127345,"val":1},
  {"typ":"recharge_actv","id":21127563,"val":1}
]
A_INT_iap_new = 1
A_STR_apply_scene = common
```

## 2013 IAP 模板 — (2013510996)

```
A_STR_temp_type = normal
A_INT_config_id = 2011500696
A_INT_coeffs_id = 2014001
N_STR_temp_desc = 2026科技节-行军特效19.99
A_STR_pkg_title = LC_EVENT_march_effect_pkg_2025
A_STR_pkg_desc = LC_EVENT_march_effect_pkg_2025
A_FLT_price = 19.99
A_ARR_price_info = [{pay_type:gplay, product_id:ape_1999_cd_an}, ...14种渠道]
A_MAP_limit = {"limit_cnt":1,"limit_type":"period"}
S_INT_limit_whitelist = 1
A_INT_CDs = 5000
A_INT_all_value = 26500
A_ARR_other_items = [
  {"asset":{"typ":"xp","id":11161002,"val":5000},                "setting":{"serial_number":0,  "ishighlight":false}},  // XP
  {"asset":{"typ":"item","id":111110212,"val":1},                "setting":{"serial_number":999,"ishighlight":true }},   // 主外显：行军特效永久版
  {"asset":{"typ":"item","id":11112498, "val":20},               "setting":{"serial_number":200,"ishighlight":true }},   // 科技节活动道具
  {"asset":{"typ":"item","id":111110105,"val":10},               "setting":{"serial_number":100,"ishighlight":true }},   // 科技节自选箱
  {"asset":{"typ":"item","id":11118663, "val":10},               "setting":{"serial_number":10, "ishighlight":false}},   // 成长线
  {"asset":{"typ":"item","id":11114318, "val":1},                "setting":{"serial_number":1,  "ishighlight":false}}    // 联盟宝箱
]
A_ARR_tag_txt = [{"typ":"roi","tag":2}]
```

## 2121 联动 unite_pkg — (21217498)

```
C_STR_comment = 联动礼包-3周年行军特效表情
A_STR_type = unite_pkg
A_ARR_reward = [
  {"asset":{"typ":"item","id":11112498, "val":20},"setting":{"serial_number":5,"ishighlight":false}},   // 活动道具
  {"asset":{"typ":"item","id":111110264,"val":10},"setting":{"serial_number":5,"ishighlight":false}},   // 自选箱
  {"asset":{"typ":"item","id":11118663, "val":5 },"setting":{"serial_number":5,"ishighlight":false}}    // 成长线
  // 注意：科技节联动礼包 reward 只有 3 项，没有主外显头像框，不同节日可不同
]
A_MAP_expr = {
  "val": 7400,
  "args": [
    {
      "op":  "LC_EVENT_battlepass_2_specialtask_lock",
      "id":  2013501999,                                                              // 指向：要被购买过的表情礼包 2013 ID
      "typ": "LC_EVENT_unite_spring_emoji_pkg_desc",
      "arg2":"assets/operation/P2dlcimg/activityImg/EventBanner_Obj_97.png"
    },
    {
      "op":  "LC_EVENT_battlepass_2_specialtask_lock",
      "id":  2013510995,                                                              // 指向：要被购买过的特效礼包 2013 ID
      "typ": "LC_EVENT_unite_spring_march_pkg_desc",
      "arg2":"assets/operation/P2dlcimg/activityImg/EventBanner_Obj_98.png"
    }
  ]
}
A_INT_arg2 = 1
A_STR_desc = NULL
```

**注意**：科技节联动礼包的 `A_MAP_expr.args[].id` 分别是 `2013501999` 和 `2013510995`，与同节日主链路的 `2013502000`（表情礼包）、`2013510996`（特效礼包）差了 1。这可能是该节日的设计微调，其他节日换档时需要**根据真实表格里当季两个礼包的 2013 ID 确认**，不要盲目 -1。

## 2121 表情礼包 discount — (21218486)

```
C_STR_type = discount
A_ARR_status = [{"typ":"iap","id":2011400529}]   // 回指：表情礼包的 2011 IAP 壳 ID
```

## 2121 表情礼包 emoji_show — (21218487)

```
C_STR_type = emoji_show
A_MAP_expr = {"arg2":"assets/operation/P2dlcimg/activityImg/EventBanner_Emoji_Iap_4.png"}
A_INT_arg1 = 11800028                             // 指向：1180 map_emoji ID
```
