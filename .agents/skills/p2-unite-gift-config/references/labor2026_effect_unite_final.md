# 拓荒节2026 行军特效礼包 + 联动礼包 — 已落 QA 最终清单

> 状态：2026-04-16 全部迁移到 QA 主页签，终检通过。

## 主链路 ID

| 表 | 用途 | ID | QA 落点 |
|---|---|---|---|
| 2112 | 行军特效礼包 | `21129001` | `activity_config_qa` row 1778 |
| 2112 | 联动礼包 | `21129002` | `activity_config_qa` row 1779 |
| 2135 | 特效 package | `21359990` | `activity_event_pkg` 末尾 |
| 2011 | 特效 IAP 壳 | `2011610001` | `iap_config_QA` row 5112（2026-04-20 从 `2011510011` 迁至新号段，避开 bp 冲突）|
| 2013 | 特效 IAP 模板 | `2013560124` | `iap_template_QA` 末尾 |
| 2121 | 联动 unite_pkg | `21219624` | `activity_special_QA` 末尾 |
| 2111 | 表情日历 | `21115768` | `activity_calendar_QA` row 1931 (21116001 上方) |
| 2111 | 特效日历 | `21115769` | `activity_calendar_QA` row 1932 |
| 2111 | 联动日历 | `21115770` | `activity_calendar_QA` row 1933 |

## 资源链路 ID（低级+高级两套）

### 低级（礼包投低级，主外显=永久版 111110333）

| 表 | ID | 说明 |
|---|---|---|
| 1512 | `15121052` | 低级 effect_key, `C_STR_file=TroopsTrail/5Yuexingjun/Prefab/Fx_TroopsTrail_2026wuyuejie_01` |
| 1511 | `151105261` | 低级 display_key |
| 1365 | `13650159` | 低级套, items=[328..333] |
| 1111 | `111110328`~`333` | 6 时长版(1天/3天/7天/14天/30天/**永久**) |

### 高级（前瞻建设）

| 表 | ID | 说明 |
|---|---|---|
| 1512 | `15121053` | 高级 effect_key, `C_STR_file=TroopsTrail/5Yuexingjun/Prefab/Fx_TroopsTrail_2026wuyuejie_02` |
| 1511 | `151105262` | 高级 display_key |
| 1365 | `13650160` | 高级套, items=[334..339] |
| 1111 | `111110334`~`339` | 6 时长版(永久=339) |

### 获取途径跳转（1168）

| 1168 id | comment | item_label(1365套) | 跳转活动 |
|---|---|---|---|
| `11684883` | 26拓荒节-低级行军特效 | `13650159` | `21129001` 特效礼包 |
| `11684884` | 26拓荒节-高级行军特效 | `13650160` | `21127575` 挖孔小游戏 |

## 2013 other_items（终检确认）

```json
[
  {"asset":{"typ":"xp","id":11161002,"val":5000},"setting":{"serial_number":0,"ishighlight":false}},
  {"asset":{"typ":"item","id":111110333,"val":1},"setting":{"serial_number":999,"ishighlight":true}},
  {"asset":{"typ":"item","id":11112498,"val":20},"setting":{"serial_number":200,"ishighlight":true}},
  {"asset":{"typ":"item","id":111110325,"val":10},"setting":{"serial_number":100,"ishighlight":true}},
  {"asset":{"typ":"item","id":11118663,"val":10},"setting":{"serial_number":10,"ishighlight":false}},
  {"asset":{"typ":"item","id":11114318,"val":1},"setting":{"serial_number":1,"ishighlight":false}}
]
```

通用道具（不换）：11161002(XP) / 11112498(漫游骰子) / 11118663(成长线) / 11114318(联盟宝箱)
节日专属（已换）：111110333(拓荒节低级永久特效) / 111110325(拓荒节自选箱)

## 2121 联动 reward（终检确认）

```json
[
  {"asset":{"typ":"item","id":11112498,"val":20},"setting":{"serial_number":5,"ishighlight":false}},
  {"asset":{"typ":"item","id":111110325,"val":10},"setting":{"serial_number":5,"ishighlight":false}},
  {"asset":{"typ":"item","id":11118663,"val":5},"setting":{"serial_number":5,"ishighlight":false}}
]
```

## 2112 关键字段

### 行军特效 21129001
- `A_STR_constant = event_march_effect_2026_labor`
- `A_MAP_filter = {"op":"and","args":[..building>=6..,{"op":"eq","typ":"iap_purchases","id":2013560124,"val":0}]}`
- `A_ARR_activity_components = [{"typ":"package","id":21359990}]`
- `A_INT_show_hud = 21680031`
- `C_INT_display_flags = 71`

### 联动 21129002
- `A_STR_constant = event_unite_3labor_2026`
- `A_ARR_activity_components = [{"typ":"unite_pkg","id":21219624}]`
- `A_INT_calendar = 0` (联动不上日历)

## 引用关系一览

```
主链路:
  2112(21129001) → 2135(21359990) → 2011(2011610001) → 2013(2013560124)
  2112(21129002) → 2121(21219624)
  2121.expr.args → [2013560123(表情礼包), 2013560124(特效礼包)]

资源链路(低级):
  2013.other_items → 1111(111110333 永久)
    → 1365(13650159).A_ARR_items=[328..333]
    → 1365.effect_key → 1512(15121052)
    → 1365/1111.display_key → 1511(151105261)
  1111.A_ARR_use_labels → ["bag","13650159"]
  1168(11684883).item_label=13650159, args→21129001

资源链路(高级):
  1111(339) → 1365(13650160) → 1512(15121053) → 1511(151105262)
  1168(11684884).item_label=13650160, args→21127575
```

## 待美术提供

| 项 | 当前 |
|---|---|
| ~~1512 C_STR_file~~ | ✅ 已填入真实路径（见下） |
| Banner 资源 | 沿用科技节 |
| `A_ARR_iap_status` | 空 (等累充确认) |
