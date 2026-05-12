---
name: p2-unite-gift-pack
description: >-
  P2 联动礼包体系（行军表情 / 行军特效 / 联动 / 头像框 共 4 种包型）的全流程 skill。
  一条指令完成配置 → 要图 → 翻译 → 落 QA 的端到端。默认直接进 QA 主页签。
  触发：配置{节日}X礼包、提配置{节日}X、联动礼包、行军表情礼包、行军特效礼包、头像框礼包。
  Scope 只限这 4 种包型，BP / GACHA / 挖矿 / 累充 / 装饰 等活动不在本 skill 范围。
---

# P2 联动礼包全流程 Skill

## Scope 边界（只处理这 4 种）

| 包型 | 2112 组件 | 2013 temp_type | 涉及表 |
|---|---|---|---|
| 行军表情礼包 | `discount` + `emoji_show` | normal | 2112/2121×2/2011/2013/1111/1180/1168/1511/2111 |
| 行军特效礼包 | `package` | normal | 2112/2135/2011/2013/1111×12/1365×2/1511×2/1512×2/1168×2/2111 |
| 联动礼包（条件奖励） | `unite_pkg` | — | 2112/2121/2111 |
| 头像框礼包 | `package` | normal | 2112/2135/2011/2013/1111/1142/1511 |

**NOT IN SCOPE**（碰到这些先问用户是否切到别的 skill）：BP / 通行证 / GACHA / 抽奖 / 挖矿小游戏 / 对对碰 / 合成 / 累充 / 装饰升级 / 限时抢购 / bp 升级道具的制作 / shop 配置 / 节日日历（2111 整体规划）。

## 与其他 skill 的关系

本 skill 是**调度器**。具体能力分派：

| Skill | 职责 | 本 skill 什么时候调它 |
|---|---|---|
| `p2-unite-gift-config` | 配置表结构、ID 分配、patch-from-ref、资源链路、BP 道具 id 映射、通用 vs 专属对照 | Phase 1 全程 |
| `p2-translation-style` | 美术图 → 中文名 + 中文描述 + LC key 命名 + 英文主译 + 风格校准 | Phase 3a |
| `p2-translation-automatic` | 18 语言扩散 + 提交 1011 主表 AI翻译暂存 | Phase 3b |
| `iap-leichong-sync`（待补） | 回填 2011.iap_status 累充挂钩 | 用户说累充排好了之后 |

**本 skill 自己不做**：翻译文案风格判定（归 style skill）、18 语生成（归 automatic skill）、BP / GACHA 表配置（不在 scope）。

---

## 触发词

**命中条件**：用户句式同时包含 (a) 节日名 + (b) 下列 4 类包型之一。

- "配置 {节日} {类型}礼包"
- "提配置 {节日} {类型}"
- "帮我把 {节日}{类型}礼包做到 QA"
- "做一个 {节日}{类型}礼包"
- "把 {节日} 的 4 类联动礼包一起配"

**可选后缀**（改变默认行为）：
- `先写测试页签` → Phase 1 写 `*_TEST_{节日pinyin}{年}` 测试页签，停在 Phase 4 等用户说 "合到 QA"
- `不要翻译` → 跳过 Phase 3
- `只要 Phase N` → 只做指定阶段

**误触发防御**：如果用户只说 "配 {节日} 礼包" 不指明类型，**必须**先反问："你指的是表情 / 特效 / 联动 / 头像框哪一种？还是其他类型礼包（那个归别的 skill）？" 不能默默挑一种开工。

---

## 完整流程（4 Phase）

```
用户触发
  ↓
┌──────────── Phase 1: 配置（默认直接写 QA） ─────┐
│  调 p2-unite-gift-config                        │
│  1) Step 0 自主学习（读 ≥2 节日同类型真实行）   │
│     输出对照表给用户确认                         │
│  2) ID 分配 / patch-from-ref                    │
│  3) 写入 QA 主页签（默认）                       │
│     · **所有表**：按 §ID 顺序规则找数值前驱       │
│       → insertDimension 在前驱行+1                │
│     · **禁止** values.append 到表格底部           │
│     【如用户加"先写测试页签"】                  │
│     · 写 *_TEST_{节日pinyin}{年}                 │
│     · 紧贴 QA 主页签右侧（index=main+1）         │
│     · 测试页签里 2 条数据直接从 A1 开始写即可     │
│  4) 资源链路闭环（scripts/check_refs.py）        │
└──────────────────────────────────────────────────┘
  ↓
┌──────────── Phase 2: 收集美术 ──────────────────┐
│  主动向用户要 N 张截图：                          │
│  · 表情礼包 → 1 张表情图                          │
│  · 特效礼包 → 1 张行军特效图（高级档）           │
│  · 头像框礼包 → 1 张头像框图（动态款）           │
│  · 联动礼包 → 复用前两张（不需要新图）           │
│  同时问（可缺省走默认）：                          │
│  · 1512 `C_STR_file` Prefab 路径（特效用）       │
│  · 1142 `C_INT_dynamic` 动/静/海报（头像框用）   │
│  · banner 是否换节日专属（默认沿用同节日其他包）  │
└──────────────────────────────────────────────────┘
  ↓
┌──────────── Phase 3: 翻译 ─────────────────────┐
│  3a) 调 p2-translation-style                     │
│       入：美术图 + 节日英文代号 + 包型           │
│       出：LC key 列表 + 中文名 + 中文描述        │
│                                                  │
│  3b) 调 p2-translation-automatic                 │
│       入：3a 输出                                 │
│       出：18 语翻译写入 1011 主表                │
│           `AI翻译暂存` 页签                       │
│       告诉用户行号，让用户去勾选提交              │
└──────────────────────────────────────────────────┘
  ↓
┌──────────── Phase 4: QA 合并 ──────────────────┐
│  仅当 Phase 1 用了"先写测试页签"才需要。        │
│  默认已直接进 QA，本 Phase 跳过。                 │
│                                                  │
│  触发：用户说 "合到 QA" / "贴到 QA"              │
│  执行：                                          │
│  · 所有表按 §ID 顺序规则找数值前驱 → 插入        │
│  · 回读关键字段 diff，报给用户                   │
└──────────────────────────────────────────────────┘
  ↓
输出总结表
```

---

## 交接协议（跨 skill 不能变）

### Phase 1 → Phase 2

Phase 1 结束必须输出：

- 每张表新 ID + 落点（QA 行号 或 测试页签名）
- LC key 清单（每个 item ≥ 2 个：`_name` / `_desc`；特效分档 ×2；头像框多款 ×N）
- 美术待填字段：
  - 1512 `C_STR_file`（特效 Prefab）
  - 1142 `C_INT_dynamic`（头像框动/静/海报）
  - 2112/2013 banner URL
  - 1142 `C_INT_rarity`（默认 1070 用头像框礼包档）

### Phase 2 → Phase 3a

给 `p2-translation-style` 的入参结构：

```json
{
  "festival_code": "sea",
  "festival_year": "2026",
  "items": [
    {
      "lc_key_prefix": "sea_avatar_name_2026",
      "item_type": "avatar_frame",
      "image_path": "/path/to/image.png",
      "context": "头像框礼包主外显动态款"
    }
  ]
}
```

**节日英文代号**（命中即用，未命中问用户）：

| 节日 | code | 节日 | code |
|---|---|---|---|
| 科技节 | `sc` 或 `tech` | 情人节 | `vd` |
| 复活节 / 拓荒节 | `easter` 或 `labor` | 深海节 | `sea` |
| 春节 | `spring` | 万圣节 | `hallo` |
| 感恩节 | `tg` | 圣诞节 | `xmas` |
| 黑五 | `blafri` | 登月节 | `moon` |
| 音乐节 | `music` | 周年庆 | `3rd`（3 周年）等 |

### Phase 3a → Phase 3b

`p2-translation-style` 输出必须直接喂 `p2-translation-automatic`：

```json
[
  {"target_tab": "ITEM", "id": "sea_avatar_name_2026", "cn": "深海冰皇"},
  {"target_tab": "ITEM", "id": "sea_avatar_desc_2026", "cn": "来自深渊王座，凛冬不灭的至尊。"}
]
```

`p2-translation-automatic` 自补 18 语言，写入 1011 主表 `AI翻译暂存`。

### Phase 3 → Phase 4

Phase 3 完成后：
- 默认（Phase 1 已直 QA）：**无 Phase 4**，本 skill 结束
- 测试页签模式：等用户说"合到 QA"后执行 Phase 4

---

## 默认行为 & 打断点

| 节点 | 默认 | 打断 |
|---|---|---|
| Phase 1 Step 0 | 读 ≥2 节日对照 | "我清楚结构，跳 Step 0" |
| Phase 1 写入位置 | **QA 主页签** | "先写测试页签" |
| Phase 2 要图 | 按包型要对应张数 | "图晚点给，先把配置做完" |
| Phase 3a | 自动调 style skill | "我给你 cn，你直接调 automatic" |
| Phase 3b | 自动提交 1011 暂存 | "不要翻译" |
| Phase 4 合并 | 默认不触发（除非走了测试页签） | 用户说"合到 QA"才动 |

**铁律**：
1. Phase 4 永远不自动执行，即使走了测试页签模式也要等用户明示"合到 QA"
2. Step 0 永远不可跳过（除非用户明示"跳 Step 0"）
3. 写 QA 前必须把 ID 分配、落点、美术占位、LC key 清单先给用户看一遍

---

## 命名 / ID 参考（正本）

### LC key 模板（1011 主表无 LC_ITEM_ 前缀）

| 包型 | name key | desc key |
|---|---|---|
| 行军表情 | `map_emoji_{code}{年}` | `map_emoji_{code}{年}_desc` |
| 行军特效·低级 | `{code}_marcheffect_low_{年}` | `{code}_marcheffect_low_{年}_desc` |
| 行军特效·高级 | `{code}_marcheffect_high_{年}` | `{code}_marcheffect_high_{年}_desc` |
| 头像框·动态 | `{code}_avatar_name_{年}` | `{code}_avatar_desc_{年}` |
| 头像框·静态 | `{code}_stationary_avatar_name_{年}` | `{code}_stationary_avatar_desc_{年}` |

> 注：写入 1111 时在前面加 `LC_ITEM_` 前缀；写 1011 主表不加。

### 1111 item comment 模板

| 包型 | comment |
|---|---|
| 行军表情 | `行军表情-动态-{节日中}{年}` |
| 行军特效 | `{年}{节日中}行军特效-{低/高级}-{时长}` |
| 头像框·动态 | `{年}{节日中}动态头像框` |
| 头像框·静态 | `{年}{节日中}静态头像框` |

### 测试页签命名（仅 opt-in 模式）

`{原页签前缀}_TEST_{节日pinyin}{年}` ，紧贴 QA 主页签右侧（index=main+1）。内容**按正式配置写**，不加 `_test` / `(测试)` 标记。

---

## ID 顺序规则（所有表通用铁律）

**规则**：新行的落点 = 该表当前"小于 new_id 的最大 ID"所在行的下一行。**禁止 values.append 到表格底部**（即使前驱正好在底部也要走 insertDimension 流程，防止未来数据结构变化）。

### 算法

```python
# 1. 读目标表 A 列全部 ID
ids_with_rows = [(int(id_str), row_num) for row_num, id_str in enumerate(col_A, 1)
                 if id_str.isdigit()]

# 2. 找小于 new_id 的最大 ID 所在行
candidates = [(i, r) for i, r in ids_with_rows if i < new_id]
if not candidates:
    # 极罕见：new_id 是最小值，询问用户
    ask_user()
else:
    predecessor_id, predecessor_row = max(candidates, key=lambda x: x[0])
    target_row = predecessor_row + 1

# 3. insertDimension 在 target_row
batchUpdate([{
    "insertDimension": {
        "range": {"sheetId": ..., "dimension": "ROWS",
                  "startIndex": target_row - 1, "endIndex": target_row},
        "inheritFromBefore": True
    }
}])

# 4. values.update 写入
values.update(range=f"{tab}!A{target_row}", body={"values": [row_values]})
```

### 为什么不能 append 到底

1. **占位符保护**：2112 `21128001` 节日占位符、2111 `21116001` 节日占位符在表中间，append 会破坏它们的位置逻辑
2. **同 ID 段连续性**：`21129000-21129004` 节日包 4 条应该连排；若表末尾有 `21128xxx` 其他活动，append 会把 `21129004` 塞到 `21128xxx` 后面，打乱 ID 段
3. **手动查找可靠性**：用户肉眼顺查 / 跨表查 ID 插件依赖 ID 局部单调
4. **同节日活动聚合**：同节日表情/特效/联动/头像框 4 条要聚在一起

### 和旧"2112/2111 placeholder 上方"规则的关系

旧规则 "2112 新行写到 21128001 节日占位符上方" 是本规则的**同义表述**：
- `21129004` 的数值前驱是 `21129003`
- 按本规则 insert 在 `21129003 所在行 + 1`
- 该位置正好是 `21128001` 占位符所在行 → 占位符被 insert 推下去
- 两种表述等价

### 本次深海节 2026 头像框落点复核

| 表 | new_id | 前驱 | 前驱行 | 落点 | 校验 |
|---|---|---|---|---|---|
| 2112 | 21129004 | 21129003 | 1776 | 1777 | ✓ |
| 2135 | 21359992 | 21359991 | 4833 | 4834 | ✓ |
| 2011 | 2011610003 | 2011610002 | 5113 | 5114 | ✓ | *（2026-04-20 从 `2011510013` 迁至 `2011610003` 新号段，避开 bp 冲突；详见 `p2-unite-gift-config` §5.4 2011 规则）*
| 2013 | 2013560126 | 2013560125 | 9732 | 9733 | ✓ |
| 1111 | 111110340 | 111110339 | 3245 | 3246 | ✓ |
| 1142 | 11421099 | 11421098 | 93 | 94 | ✓ |
| 1511 | 151105265 | 151105264 | 12893 | 12894 | ✓ |

7 条本次恰好符合（前驱都在表尾）。但**本次的"巧合"不能作为未来简化的借口**。

### 校验脚本（每次 Phase 1 写入前必跑）

```python
def find_insertion_row(sid, tab, new_id):
    d = gws_get(sid, f"{tab}!A:A")
    ids = [(int(r[0]), i+1) for i, r in enumerate(d.get("values",[])) if r and r[0].isdigit()]
    preds = [(i, r) for i, r in ids if i < new_id]
    assert preds, f"new_id {new_id} 比所有现存 ID 都小，需用户确认"
    pred_id, pred_row = max(preds, key=lambda x: x[0])
    return pred_row + 1, pred_id
```

---

## 头像框礼包专项 — 9 处必查清单

> 2026-05-06/07 沉淀。Jira 凭证：P2DEV-142432/142465/142466/142483/142484/142485/142486/142488 全部走真表诊断 + 修复后归纳。
> 头像框礼包是 2026 才形成的新形态（早期没有），复用表情礼包/联动礼包模板时**任意一处漏改 = 一个客户端 bug**。
>
> ⚠️ **本节只对头像框礼包生效**。行军表情礼包正确用 `LC_IAP_map_emoji_actv_title`（→「表情上新」），行军特效礼包另有自己的 title key，**不要把这里的"必改成"反向套到表情/特效/联动包**。

| # | 表 / 字段 | 错误模式（沿用模板的默认值） | 必改成 | bug 凭证 |
|---|---|---|---|---|
| 1 | **2112.21129XXX**.A_MAP_text.group_label | 沿用周年庆/老节日 key（如 `LC_EVENT_unite_name_3anni_2025`） | 新建 `LC_EVENT_unite_name_<节日>_<年>_avatar` | 142465 |
| 2 | **2013.2013560XXX**.A_STR_pkg_title | 沿用表情包 `LC_IAP_map_emoji_actv_title`（克隆 emoji pack 模板的副作用，邮件标题/正文均渲染"表情上新"）| **推荐**直接复用 `LC_EVENT_avatar_frame_new`（i18n 已存在=「头像框上新」，与 2112.A_MAP_text.label 一致，无需新建/翻译）；如需 IAP_xxx_actv_title 命名规范则新建 `LC_IAP_avatar_frame_actv_title` 走 18 语扩散 | 142485（拓荒节2026 + 深海节2026 同 bug，2013560125/126 双修） |
| 3 | **2013.2013560XXX**.A_ARR_other_items | **漏 item 11114316**（帮派礼物，同节日所有表情礼包 `2013101135` 等都有）| 末尾追加 `{"asset":{"typ":"item","id":11114316,"val":1},"setting":{"serial_number":1, "ishighlight": false}}` | 142486 / 142483 |
| 4 | **1142.11421XXX**.C_MAP_lc_get_from (K列) + C_MAP_access (M列) | 引用黑五等老节日 `LC_MENU_frame_get_through_2025blafri_after/before` | K=`..._after` / M=`..._before`，**两列必须同时改**，详见下文 §写入避坑 | 142488 / 142599 |
| 5 | **1011 MENU** | `frame_get_through_<节日>_<年>_<after/before>` 18 语缺失 | 走 `p2-translation-automatic`，参考 `frame_get_through_2026sci_*` 镜像；**中文必须对齐模板**：before=`通过[X]获得`（不带"将"）/ after=`于{0}通过[X]获得`（**必须含 `{0}`** 否则获得日期不显示） | 142488 / 142599 |
| 6 | **1168** 头像框礼包跳转行 | 全表无对应行 → 客户端"前往"按钮无反应（typ=others 不可跳） | 新增 row：label=`non_item`，access_group=`[{"id":11531001,"args":["<2112_actv_id>"]}]`，lc_name=`{"typ":"lc","txt":"LC_ITEM_item_cap"}`，label_name=`{}` | 142484 |
| 7 | **1168** 主城套装跳转（如同期附带）| 套装 4-5 件全部无 1168 行 → "前往"全无反应 | 每件单独建行：label=1312/1388 ID，access 跳本季主玩法+累充 actv_id（参考战地套 11684832-836 模板） | 142435 |
| 8 | **1011 ITEM** | 头像框 name/desc 18 语未扩散 → 客户端显示 LC 键值 | 走 `p2-translation-automatic`，可镜像同节同类 desc | 142432 / 142466 |
| 9 | **1142.unlock_cost.item.id** ↔ **2013.other_items serial=999** | 礼包给的"专属解锁道具" id 与 1142 unlock_cost 不一致 → 玩家买完 不解锁头像框 | 必须**完全相同**：1142.A_ARR_unlock_cost[0].id == 2013.other_items[serial=999].asset.id == 1111 头像框关联道具 ID | — |

### 配置自检顺序

```
Step 0  读 2112.21129XXX 全行，确认 group_label/label LC_Key 是新节日的
Step 1  读 2013.2013560XXX（**头像框礼包语境**），确认：
        ├─ pkg_title 必须是 `LC_EVENT_avatar_frame_new`（或新建 `LC_IAP_avatar_frame_actv_title`）；
        │   ❌ 此 row 不可挂 `LC_IAP_map_emoji_actv_title`（那是表情礼包正用 LC，挂头像框上会渲染"表情上新"，P2DEV-142485 凭证）
        │   注：表情礼包/特效礼包的 2013 row 各有自己的正确 pkg_title，本步骤不约束它们
        └─ other_items 末尾有 item 11114316 ×1（帮派礼物）
Step 2  读 1142.11421XXX，确认 get_from(K) + access(M) **两列都**指向本节日 frame_get_through key
Step 3  读 1011 MENU 是否有 frame_get_through_<节日>_<年>_<after/before>
Step 4  读 1168 col A，搜 21129XXX（头像框礼包 actv_id）至少 1 行命中
Step 5  读 1011 ITEM 是否有头像框 name/desc 18 语
```

### 1142 K + M 双字段写入避坑（P2DEV-142599 踩坑沉淀）

**字段含义对应**：
- **K 列 `C_MAP_lc_get_from`** → 玩家**已获得后**详情显示，必须挂 `LC_MENU_frame_get_through_<节日>_<年>_after`（带 `{0}` 日期占位符的模板）
- **M 列 `C_MAP_access`** → 玩家**未获得时**面板提示，结构 `{"typ":"others","args":[{"typ":"lc","txt":"...before"}]}`，内层必须挂 `LC_MENU_frame_get_through_<节日>_<年>_before`（不带 `{0}`）

**两列绝对不能搞混 after/before**——交叉错挂会导致已获得玩家看到"通过 X 获得"无日期，未获得玩家看到"于{0}通过 X 获得"出现 `{0}` 字面量。

**写入 API 必须逐列 update + 单独 read-back**（不要用 `values().batchUpdate`）：

```python
# ❌ 错：batchUpdate 可能静默部分写失败，verify 即时读回也可能拿到 stale 值
svc.values().batchUpdate(spreadsheetId=SH, body={
    'valueInputOption':'RAW',
    'data':[
        {'range': 'avatar_frame!K{row}', 'values':[[new_K]]},
        {'range': 'avatar_frame!M{row}', 'values':[[new_M]]},
    ]
})

# ✅ 对：逐列 update + 各自 read-back
for col, new_val in [('K', new_K), ('M', new_M)]:
    svc.values().update(spreadsheetId=SH, range=f'avatar_frame!{col}{row}',
        valueInputOption='RAW', body={'values':[[new_val]]}).execute()
    after = svc.values().get(spreadsheetId=SH, range=f'avatar_frame!{col}{row}').execute()['values'][0][0]
    assert after == new_val, f'{col}{row} not patched!'
```

P2DEV-142599 现场：batchUpdate 调用，K 写成功 M 静默失败但**返回成功且 verify 也假阳**，用户在 sheet UI 里发现 M 列没改才暴露。

### 同节日多包型 1168 全套（保证「前往」按钮全部生效）

每个新节日联动礼包系列在 1168 至少要有 4 行（**头像框礼包是 2026 后新增的第 4 类**）：

| 包型 | label | access_group | 参考行 |
|---|---|---|---|
| 行军表情礼包 | `non_item` | `[{"id":11531001,"args":["<2112_emoji_pkg_id>"]}]` | 11684842 复活节模板 |
| 低级行军特效礼包 | `13650<节日低级套 ID>` | `[{"id":11531001,"args":["<2112_effect_pkg_id>"]}]` | 11684860 复活节模板 |
| 高级行军特效（跳本季主玩法）| `13650<节日高级套 ID>` | `[{"id":11531001,"args":["<本季主玩法 actv_id>"]}]` | 11684884 拓荒节模板（跳钓鱼活动 21127700）|
| 头像框礼包 | `non_item` | `[{"id":11531001,"args":["<2112_avatar_pkg_id>"]}]` | 11684905 拓荒节模板（2026-05 新建）|

> **2025 及更早节日做联动礼包时只配前 3 类，2026 起增加头像框礼包 → 第 4 行必须新增**。

---

## 已知坑（Do Not Repeat）

1. **BP 升级道具槽易漏**：2013 other_items 某位看似"散装通用小物件"其实是节日 BP 升级道具（每节日独立 id）。Step 0 必查。详见 `p2-unite-gift-config` §4.5 BP 道具映射表。
2. **头像框 1142 表**：配头像框除了 7 张主链路表还要动 1142 avatar_frame 表。
3. **LC key 禁止复用历史节日**：拓荒节 2026 头像框曾误复用黑五 `2025blafri` key。每节日**新建**独立 key。
4. **iap_status 留空**：换档时 2011.iap_status 先留 `[]`，等累充活动排好后用 `iap-leichong-sync` 回填。
5. **禁止 values.append 到底部**：所有 QA 写入必走 §ID 顺序规则的 insertDimension 流程，即使前驱在表尾也不可 append。
5b. **2011 新号段 `2011610000+`**：节日礼包 iap_config 分配 id 默认从 `2011610000` 起（向后递增），别再用 `20115xxxxxx` / `20114xxxxxx` 段。2026 拓荒节曾与 `武装通行证bp-schema3-5/6` 撞号，已迁至新号段。详见 `p2-unite-gift-config` §5.4。
6. **联动礼包的 2111.calendar=0**：不影响"是否要在 2111 建日历行"的判断，按当季节日整体规划走。
7. **2112.base_activity_id 占位**：配置时沿用同节日其他包的值做占位，档期确定后替换。
8. **values.update 遇 grid 限制**：如果目标行数超过当前 sheet 行数（values.update 会报 "exceeds grid limits"），先用 `appendDimension` 扩表再 insertDimension，或者直接 `insertDimension` 到 max_row + 1（API 允许此行为）。
9. **1011 翻译永远走暂存区**：任何 1011 表写入（包括覆盖已有 key 的 cn-cns）都必须先入 AI翻译暂存让用户 review，禁止 sheets API 直接 update 主表。详见 memory `feedback_translation_always_staging`。
10. **`values().batchUpdate` 静默部分失败**（P2DEV-142599）：批量改多 cell 时，可能某条 range 静默写入失败但 API 整体返回成功，且即时 batchGet read-back 也假阳。**多 cell 改写一律改用单条 `values().update` + 单独 `values().get` 校验**，特别是 1142 K + M 这种"成对必须同步"的场景。

---

## 输出总结模板（Skill 结束时必输出）

```markdown
## {节日}{年} {类型}礼包 全流程完成

### Phase 1 配置
| 表 | 新 ID | 落点 |
| --- | --- | --- |
| 2112 | 21129xxx | QA!A{行号} |
| 2135 | ... | ... |

### Phase 3 翻译（1011 主表 AI翻译暂存）
| 行号 | key | cn |
| --- | --- | --- |
| 102 | sea_avatar_name_2026 | 深海冰皇 |

### 待你做
1. 去 1011 `AI翻译暂存` 勾选 → 本地化工具 > 提交选中行
2. 美术补全：1512 prefab / 1142 dynamic / banner URL（列出具体字段位置）
3. 累充活动开了之后说"跑累充同步"触发 `iap-leichong-sync`
4. 【测试页签模式才有】说"合到 QA"触发 Phase 4

### 遗留风险
（如 LC key 是否需要二次核对、美术是否已 ready 等）
```

---

## TODO

- [ ] 等用户反馈第一个端到端真实触发后迭代
- [ ] 节日英文代号表遇到新节日时补进本文件 §Phase 2→3a
- [ ] Phase 4 考虑做成子命令 `/合到QA` 而不是自然语言触发
