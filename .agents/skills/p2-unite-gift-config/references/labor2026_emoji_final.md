# 拓荒节2026 行军表情礼包 — 最终落表清单

> 状态：已写入 QA / 主页签，终检通过。
> 范围：仅行军表情礼包。行军特效 + 联动见 `labor2026_effect_unite_final.md`。

## 主链路 ID

| 表 | 用途 | 最终 ID | 主页签落点 |
|---|---|---|---|
| 2111 | 活动日历 | `21115768`（原 21117154 已修正位置和 id） | `activity_calendar_QA` row 1931（21116001 节日占位符上方） |
| 2112 | 活动主表 | `21129000` | `activity_config_qa`，`21128001` 占位符上方 |
| 2121 discount | 折扣组件 | `21219622` | `activity_special_QA!A3293:O3293` |
| 2121 emoji_show | 表情展示组件 | `21219623` | `activity_special_QA!A3294:O3294` |
| 2011 | IAP 壳 | `2011610000` | `iap_config_QA!A5111:T5111`（2026-04-20 从 `2011510010` 迁至新号段，避开 bp 冲突）|
| 2013 | IAP 模板 | `2013560123` | `iap_template_QA!A9731:AE9731` |
| 1180 | 地图表情资源 | `11800030` | `qa`，`11800029` 下方 |
| 1111 | 表情道具 | `111110327` | `item!A3233:Y3233` |
| 1168 | get_access_group | `11684882` | `get_access_group（杜绝手搓）!A841:G841` |
| 1511 | display_key | `151105260` | `display_key!A12889:I12889` |

## 引用关系

```
2111.A_INT_activity_id = 21129000
2112.A_INT_id = 21129000
2112.A_ARR_activity_components = [{"typ":"discount","id":21219622},{"typ":"emoji_show","id":21219623}]

2121(21219622).A_ARR_status = [{"typ":"iap","id":2011610000}]
2011(2011610000).A_MAP_time_info = {"normal":[{"actv_id":21129000}]}
2013(2013560123).A_INT_config_id = 2011610000

2121(21219623).A_INT_arg1 = 11800030
1111(111110327).A_MAP_category_param = {"effect":[{"typ":"map_emoji","id":11800030,"val":-1}]}
1180(11800030).C_INT_access_group = 11684882
1180(11800030).C_INT_display_key_emoji = 151105260
1111(111110327).C_INT_display_key = 151105260
1168(11684882).C_ARR_access_group = [{"id":11531001,"args":["21129000"]}]
```

## 2013 关键字段

- `A_INT_id = 2013560123`
- `N_STR_temp_desc = 2026拓荒节-行军表情4.99`
- `A_FLT_price = 4.99`
- `A_MAP_limit = {"limit_cnt":1,"limit_type":"period"}`
- `A_INT_CDs = 1250`
- `A_INT_all_value = 6175`
- `A_STR_pop_banner_url = assets/operation/P2dlcimg/llustration/EventBanner_BG_90.png`
- `A_STR_banner_url = assets/operation/P2dlcimg/activityImg/EventBanner_BG_100.png`
- `A_ARR_other_items`:

```json
[
  {"asset":{"typ":"xp","id":11161002,"val":1250},"setting":{"serial_number":0,"ishighlight":false}},
  {"asset":{"typ":"item","id":111110327,"val":1},"setting":{"serial_number":999,"ishighlight":true}},
  {"asset":{"typ":"item","id":111110325,"val":5},"setting":{"serial_number":200,"ishighlight":true}},
  {"asset":{"typ":"item","id":11112150,"val":40},"setting":{"serial_number":100,"ishighlight":true}},
  {"asset":{"typ":"item","id":11118663,"val":2},"setting":{"serial_number":10,"ishighlight":false}},
  {"asset":{"typ":"item","id":11114316,"val":1},"setting":{"serial_number":1,"ishighlight":false}}
]
```

## 2112 关键字段

- `S_STR_comment = 拓荒节2026-行军表情礼包`
- `A_STR_constant = event_labor_emoji_2026`
- `A_INT_base_activity_id = 21127183`
- `A_MAP_filter = {"op":"ge","typ":"building","id":111811,"val":6}`
- `A_MAP_text = {"group_label":"LC_EVENT_unite_name_3anni_2025","label":"LC_IAP_map_emoji_actv_title"}`
- `A_INT_ui_template = 21191260`
- `S_STR_banner_url = assets/operation/P2dlcimg/activityImg/EventBanner_BG_329.png`
- `A_INT_show_hud = 21680031`
- `S_STR_calendar_banner_url = assets/operation/P2dlcimg/activityImg/EventBanner_Timeline_160.png`
- `C_INT_display_flags = 71`

## 1180 / 1111 / 1168 / 1511 关键字段

### 1180 (11800030)
- `A_STR_constant = map_emoji_labor2026`
- `N_STR_comment = 动态表情-拓荒节2026`
- `A_INT_emoji_type = 2`, `A_INT_last_time = 5000`, `C_INT_priority = 1029`
- `A_INT_year_group = 2026`

### 1111 (111110327)
- `S_STR_comment = 行军表情-动态-拓荒节2026`
- `A_STR_class = map_emoji`, `A_INT_quest_class = 20`
- `A_FLT_value = 1000`, `A_INT_max_own = 99`
- `A_MAP_lc_name = {"typ":"lc","txt":"LC_ITEM_map_emoji_labor2026"}`
- `C_MAP_lc_desc = {"typ":"lc","txt":"LC_ITEM_map_emoji_labor2026_desc"}`
- `A_INT_source = 11740000`

### 1168 (11684882)
- `S_STR_comment = 动态表情-拓荒节2026`
- `C_STR_item_label = non_item`

### 1511 (151105260)
- `S_STR_comment = 动态表情：拓荒节2026`

## 遗留

- `2011.A_ARR_iap_status = []`（累充活动待确认后用 `iap-leichong-sync` 填）
