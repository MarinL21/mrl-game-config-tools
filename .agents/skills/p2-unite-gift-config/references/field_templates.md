# 每张表字段模板（换档时必换标记为 🔴）

## 2112 activity_config_qa（25 列）

| 字段 | 特效礼包 | 联动礼包 | 表情礼包 |
|---|---|---|---|
| `A_INT_id` 🔴 | 每节日新增 ID | 同左 | 同左 |
| `S_STR_comment` 🔴 | `{年}{节日}-行军特效礼包` | `联动礼包-{年}{节日}` | `{节日}{年}-行军表情礼包` |
| `A_STR_constant` 🔴 | `event_march_effect_{yyyy}_{festival_key}` | `event_unite_3{festival_key}_{yyyy}` | `event_{festival_key}_emoji_{yyyy}` |
| `S_INT_priority` | 49999 | 50000 | 49997 |
| `A_INT_base_activity_id` 🔴 | 每节日专属 | 每节日专属 | 每节日专属 |
| `A_MAP_filter` 🔴 | `{"op":"and","args":[{"op":"ge","typ":"building","id":111811,"val":6},{"op":"eq","typ":"iap_purchases","id":<本活动2013_id>,"val":0}]}` | `{"op":"ge","typ":"building","id":111811,"val":6}` | `{"op":"ge","typ":"building","id":111811,"val":6}` |
| `A_MAP_text` 🔴 | `{"group_label":"LC_EVENT_unite_name_3anni_2025","label":"LC_EVENT_march_effect_pkg_2025"}` | `{"group_label":"...","label":"LC_EVENT_unite_event_double_3anni_2025","title":"..."}` | `{"group_label":"...","label":"LC_IAP_map_emoji_actv_title"}` |
| `A_ARR_activity_components` 🔴 | `[{"typ":"package","id":<2135_id>}]` | `[{"typ":"unite_pkg","id":<2121_id>}]` | `[{"typ":"discount","id":<2121_id>},{"typ":"emoji_show","id":<2121_id>}]` |
| `A_INT_ui_template` | 21191361 | 21191065 | 21191260 |
| `S_INT_rank_group` | 1 | 1 | 1 |
| `S_STR_banner_url` 🔴 | `EventBanner_BG_<节日码>.png` | `EventBanner_BG_<节日码>.png` | `EventBanner_BG_<节日码>.png` |
| `A_INT_show_hud` 🔴 | 节日通用 show_hud（如拓荒节 21680031 / 科技节 21680027） | 同左 | 同左 |
| `A_INT_calendar` | 1 | **0** | 1 |
| `S_STR_calendar_banner_url` 🔴 | Timeline banner | `""` | Timeline banner |
| `C_INT_display_flags` | 71 | 0 | 71 |

## 2135 activity_event_pkg（13 列）— 仅特效礼包用

| 字段 | 值 |
|---|---|
| `A_INT_id` 🔴 | 每节日新增 |
| `N_STR_comment` 🔴 | `{年}{节日}行军特效礼包` |
| `A_INT_iap` 🔴 | 指向本活动的 2011 ID |
| `A_STR_cd_cost_title` | `NULL` |
| `A_STR_cd_cost_text` | `NULL` |
| `A_INT_order` | 996 |
| `C_STR_tab` | `NULL` |

## 2011 iap_config_QA（20 列）

| 字段 | 特效礼包 | 表情礼包 |
|---|---|---|
| `A_INT_id` 🔴 | 每节日新增 | 同 |
| `N_STR_pkg_desc` 🔴 | `{年}{节日}-行军特效礼包` | `{年}{节日}-行军表情礼包` |
| `A_STR_function` | `special` | `special` |
| `A_STR_pkg_type` | `normal` | `normal` |
| `A_BOL_pirce_display` | `False` | `False` |
| `S_MAP_server_info` | `{"typ":"schema","id":[1,2,3,4,5,6,13,14,15,16,17,18,55]}` | 同 |
| `A_INT_priority` | 3005 | 3005 |
| `A_MAP_time_info` 🔴 | `{"normal":[{"actv_id":<本活动2112_id>}]}` | 同 |
| `A_ARR_iap_status` 🔴 | 累充活动数组（可先空，等确认） | 同 |
| `A_INT_iap_new` | 1 | 1 |
| `A_STR_apply_scene` | `common` | `common` |

## 2013 iap_template_QA（31 列）

| 字段 | 特效礼包 | 表情礼包 |
|---|---|---|
| `A_INT_id` 🔴 | 每节日新增 | 同 |
| `A_STR_temp_type` | `normal` | `normal` |
| `A_INT_config_id` 🔴 | 本活动 2011 ID | 同 |
| `A_INT_coeffs_id` | 2014001 | 2014001 |
| `N_STR_temp_desc` 🔴 | `{年}{节日}-行军特效19.99` | `{年}{节日}-行军表情4.99` |
| `A_STR_pkg_title` | `LC_EVENT_march_effect_pkg_2025` | （用节日自己的 LC） |
| `A_FLT_price` | 19.99 | 4.99 |
| `A_ARR_price_info` | `ape_1999_cd_*` 系列 14 渠道 | `ape_499_cd_*` 系列 |
| `A_MAP_limit` | `{"limit_cnt":1,"limit_type":"period"}` | 同 |
| `S_INT_limit_whitelist` | 1 | 1 |
| `A_INT_CDs` | 5000 | 1250 |
| `A_INT_all_value` | 26500 | 6175 |
| `A_ARR_other_items` 🔴 | 见下方"奖励数组模板" | 同 |
| `A_ARR_tag_txt` | `[{"typ":"roi","tag":2}]` | `[{"typ":"roi","tag":2}]` |
| `A_STR_pop_banner_url` 🔴 | `EventBanner_BG_<码>.png` | 同 |
| `A_STR_banner_url` 🔴 | `EventBanner_BG_<码>.png` | 同 |

### 奖励数组模板（serial_number 排序规则）

```json
[
  {"asset":{"typ":"xp","id":11161002,"val":<CDs值>},           "setting":{"serial_number":0,  "ishighlight":false}},
  {"asset":{"typ":"item","id":<主外显>,"val":1},                "setting":{"serial_number":999,"ishighlight":true }},
  {"asset":{"typ":"item","id":<节日活动道具>,"val":<数量>},     "setting":{"serial_number":200,"ishighlight":true }},
  {"asset":{"typ":"item","id":<节日自选箱>,"val":<数量>},       "setting":{"serial_number":100,"ishighlight":true }},
  {"asset":{"typ":"item","id":<成长线>,"val":<数量>},           "setting":{"serial_number":10, "ishighlight":false}},
  {"asset":{"typ":"item","id":<联盟宝箱>,"val":1},              "setting":{"serial_number":1,  "ishighlight":false}}
]
```

数量差异：
- **特效礼包**：活动道具 20 / 自选箱 10 / 成长 10 / XP 5000
- **表情礼包**：活动道具 40 / 自选箱 5 / 成长 2 / XP 1250

## 2121 activity_special_QA（15 列）

### discount 类（表情礼包用）

```
A_STR_type = discount
A_ARR_status = [{"typ":"iap","id":<本活动2011_id>}]
```

### emoji_show 类（表情礼包用）

```
A_STR_type = emoji_show
A_INT_arg1 = <1180_map_emoji_id>
A_MAP_expr = {"arg2":"<表情展示 banner url>"}
```

### unite_pkg 类（联动礼包用）

```
A_STR_type = unite_pkg
A_ARR_reward = [...联动奖励数组...]   // 主外显头像框 val=1 serial=5，其他补价值道具 serial 都用 5
A_MAP_expr = {
  "val": 7400,
  "args": [
    {"op":"<LC条件>", "id":<表情礼包2013id>, "typ":"<LC描述>", "arg2":"<banner路径>"},
    {"op":"<LC条件>", "id":<特效礼包2013id>, "typ":"<LC描述>", "arg2":"<banner路径>"}
  ]
}
A_INT_arg2 = 1
A_STR_desc = NULL
```

## 表情资源链（1180 / 1111 / 1168 / 1511） — 仅表情礼包

参考 `labor2026_final.md` 第 5 节（字段结构与值都在那里）。
