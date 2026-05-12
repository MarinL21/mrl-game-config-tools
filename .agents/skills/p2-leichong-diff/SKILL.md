---
name: p2-leichong-diff
description: P2 节日累充礼包覆盖核查工具——输入"节日 tab + 该节日全部活动 2112 ID 清单"，反向追溯每个活动到 2011 IAP 引用，与累充源表 C 列做差，输出"被活动引用但未录入累充表"的礼包清单。给 PM 在累充上线前查漏补缺。触发：差累充礼包、累充覆盖核查、累充漏配、累充表对照活动、{节日}累充查漏、recharge_actv 漏配。
---

P2 节日累充覆盖核查工具。和 `p2-leichong-package-summary` 配套：

| Skill | 方向 | 用途 |
|---|---|---|
| `p2-leichong-package-summary` | **正向**：活动 → 礼包 → 写 K 列 | PM 已经决定哪些礼包计入累充，生成 JSON 写回 2011.iap_status |
| `p2-leichong-diff` (本 skill) | **反向**：活动 → 礼包 → 对照源表 | 累充表上线前查漏：活动配了哪些礼包还没录入累充表 |

## 触发场景

- "你帮我看下拓荒节这些活动关联的礼包都进累充表了吗"
- "差累充礼包，列出 26拓荒节 漏的"
- "累充上线前检查 IAP 覆盖率"
- "{节日} 累充漏配"

## 解决的问题

PM 维护累充源表 `1RFAyBfpG3-8rm3ugNn3NHFdeDg8Erha0VttGzokIy6E` 的每个节日 tab，C 列列出"该节日所有应计入累充统计的 2011 IAP"。问题是：

- 礼包是 PM 一个个手动拷到 C 列的，容易漏
- 头部 row 11 有个"参考池"（逗号分隔的 IDs 串），通常 PM 先把所有 ID 倒到这里、再逐行整理填入 C 列；中途可能忘
- 一旦某个 IAP 漏录，玩家买它就不计入累充进度 → 玩家投诉

本 skill 反向校验：从节日活动 2112 出发，追溯每个活动引用到的 2011 IAP 集合，跟累充表 C 列做差，按"参考池命中/盲点"分类输出。

## 数据流

```
35 个活动 2112 IDs ──→ 2112.activity_qa components 字段
                             │
                             ├─ direct 2011 ──┐
                             ├─ 2121 → row scan + task_group→2115 + nested 2135/2013/2121/2115
                             ├─ 2122 → row scan + nested ──┤
                             ├─ 2135 → C 列 iap          ──┼─→ iap_set (set_B)
                             ├─ 2013 → C 列 iap          ──┤
                             └─ 2115 → row scan + nested ──┘
                                                            │
                          源表 26拓荒节 C 列 (set_A) ─────────┤
                          源表 26拓荒节 row 11 参考池 ────────┘
                                                            │
                                                  diff + 分类 → 报告
```

## 使用流程

### Step 0: 收集输入（必问用户）

写入 `scripts/inputs.yaml`（或 CLI 参数）：

```yaml
festival_tab: "26拓荒节"        # 累充源表里的节日 tab 名
activities:                     # 该节日所有活动的 2112 ID + 类型描述
  - {id: "21127892", type: "累充三件套(个人)", name: "拓荒节2026-主城特效累充-个人"}
  - {id: "21127895", type: "限时抢购S6", name: "拓荒节-限时抢购-S6-通用皮(1、2期)"}
  - ...
```

**收集来源**：用户直接给（一般从他们的活动清单截屏 / 文本贴入）。如果用户只给 ID 不给 type，**可以从 2112 表 LC_Name 列推断 type**，但要把推断结果回显让用户确认。

### Step 1: 拉取所有上游表（带 24h 缓存）

```bash
python3 scripts/coverage_check.py fetch --festival-tab "26拓荒节"
```

会拉这 7 张 QA 表到 `.cache/` 目录：

| 表 | Sheet ID | tab |
|---|---|---|
| 2112 | `1IKUBw678b2PU1m0md1vR9GxcH2uTNyLbR7VWgyAJ57E` | `activity_config_qa` |
| 2121 | `1sicvhfxZhagLVmpEg4HDcaCnPWPgsWkhgZKC-HxCCuc` | `activity_special_QA` |
| 2122 | `1zziy6nMR1DlhCykKBndwk6d6KNRrzj1PsOsFGbLYR4M` | `activity_rank_rule（QA）` |
| 2115 | `1K3-I4gCYKY-Zw5Ms05ozHtHKpOqYI-lp4kuuhqbWajY` | `activity_task_QA` |
| 2135 | `1KrcIA8jC4Aj6sFz44c_2lhtJ-lyD1OYu3QNpzaor8Mc` | `activity_event_pkg` |
| 2013 | `1sJzacpa0CBp1B8LQX1TboSBOA4T80_t8lH8eEzqHLbY` | `iap_template_QA` |
| 2011 | `1yS_BehT_Rfcc3sXjDPsSaQRcjPh8YepucYTnUQDpEMc` | `iap_config_QA` |
| 累充源表 | `1RFAyBfpG3-8rm3ugNn3NHFdeDg8Erha0VttGzokIy6E` | `{festival_tab}` |

缓存命名 `.cache/{table}_{tab}.json`，超过 24h 自动失效；CLI 加 `--no-cache` 强制重新拉。

### Step 2: 反向追溯每个活动

```bash
python3 scripts/coverage_check.py trace --inputs scripts/inputs.yaml
```

对每个活动：
1. 读 2112 行的 components（col 8 / `A_ARR_components`）
2. 解析 JSON 数组，对每个元素 dispatch 到对应表的递归 visit
3. visit 时整行 scan 8-10 位数字 ID（regex），按前缀分类继续追溯
4. 遇到合法 2011 IAP（在 iap_config_QA 中存在）就收集
5. 深度上限 4，visited 集合防环

### Step 3: 输出报告

```bash
python3 scripts/coverage_check.py report --inputs scripts/inputs.yaml --out report.md
```

输出 `report.md`：

- **第一段**：活动汇总表（活动 ID / 类型 / IAP 引用数 / 在 set_A 内 / 缺失数）
- **第二段**：所有活动并集去重后的缺失 IAP 总数
- **第三段**：按"参考池命中/盲点"分类列缺失 ID
  - **A. 已在 row 11 参考池**：PM 知道但还没拷到 C 列（"整理工作量"）
  - **B. 参考池也没有**：PM 完全没意识到（"真盲点，最高优先级"）
- **第四段**：0 IAP 引用的活动（信息列出，确认无需录入）
- **第五段**：解析失败的活动（schema 异常）

也输出 `report.json`（完整 trace log）。

## 重要业务知识

### 哪些活动类型有"trace 数字虚高 vs 0"差异

- **累充活动本身** (`累充三件套` `机甲累充`): trace 数字会**虚高**（通常 200+ IAP）。
  - 原因：累充活动有 task → 2122 rank → `A_ARR_score_rule.ids` 字段，里面枚举"应计入累充的 IAP 列表"，往往就是整个 set_A
  - 这是**反向**枚举（累充活动期望收到这些 IAP 的付费），不是活动本身卖的礼包
  - 实际表现：累充活动的 `missing = 0` 永远成立（因为 score_rule 就是从 set_A 编出来的）
  - 副作用：累充活动的"IAP 引用数"列虚高，不影响"漏配清单"主结论
- **常规签到/BP 卡包/对对碰 BP/挖矿累积任务/装饰兑换商店**: trace 结果为 0，正常。BP 类活动的 IAP 通过 1168 `access_group` 路由（不在 components）
- **累充服务器活动特例** (如拓荒节 21127893): components 有 `server_recharge_countdown` → 2135 → 2 个服务器档位 IAP，这部分会被 trace 到

### Components dispatch 规则

`components = [{"typ": "...", "id": N, "args": {...}}, ...]`

| typ 前缀/常见值 | id 落在 | 处理 |
|---|---|---|
| 8 位 `21121xxx`（直接） | 2011 IAP | 收集 |
| `212100xxxx` | 2121 | visit_2121 |
| `212120xxxx` | 2121 (long-id) | visit_2121 |
| `21220xxxx` | 2122 | visit_2122 |
| `2135xxxx` | 2135 | visit_2135（取 col 2 = iap） |
| `2013xxxxx` | 2013 | visit_2013（取 col 2 = iap） |
| `21158xxxxx` | 2115 task | visit_2115 |
| `city_skin / buff / create_entity / retake` | 不指向 IAP | 跳过 |

### 2121 task_group 二级展开

2121 col 2 = 'task_group' 时，col 10 (`array`) 是一个 JSON 数组 of 2115 task IDs。必须递归 visit_2115。

### IAP 校验

收集到的所有 `2011\d{6}` 必须**先匹配 `idx_2011` 集合**才收，否则误报（任何旧 ID 残留、占位符都会混入）。

## 输出报告样本

```markdown
# 26拓荒节 35 活动 → 2011 IAP 反向追溯报告
set_A (源表 26拓荒节 C 列): 246 IDs

## 全部 35 活动并集 - set_A = 40 个 IAP 缺失

### A. 已在参考池 row 11（PM 知道，待整理填 C 列）— 33 个
- 2011499900（挖孔常规礼包1）
- 2011499901（挖孔常规礼包2）
- ...

### B. 参考池也没有（真盲点，需 PM 重新评估）— 7 个
- 2011499920（挖孔成就礼包独漏的1个）
- 2011100482-485（机甲GACHA锚点+19.99/49.99/99.99）
- 2011400168-169（服务器累充折扣5/6）

## 按活动分组（仅含缺失活动）

### 21127899 (挖孔玩法) — 节日挖孔小游戏-新
- 引用 IAP 总数: 32
- 缺失 28 个：
  - 2011499900 ... 2011499928
```

## 与现有 skill 的关系

- 输入数据：35 活动清单一般由 PM 手工提供；如果用户先做了 `p2-config-diagnosis` 全节日活动 ID 扫描，可以直接喂给本 skill
- 输出后续：PM 看到"参考池命中"清单后，可以一键把这些 ID 拷到 C 列；看到"盲点"清单后，PM 决定是否要录入；录完之后下一步走 `p2-leichong-package-summary` 写回 2011.iap_status

## 不做的事

- 不直接修改累充源表（C 列由 PM 决定要不要补）
- 不修改 2011.iap_status（那是下一步 `p2-leichong-package-summary` 的事）
- 不重新分析活动类型（type 字段由用户给）
- 不展开 IAP 价格 / 礼包 type 内容（只关心"在不在累充表"）
- 不覆盖手动维护的累充活动 ID（活动列表里的 4 个累充活动本身正常 trace 出 0 IAP，不视为"漏"）

## CLI 总览

```bash
# 一条命令做完整流程
python3 scripts/coverage_check.py all \
  --festival-tab "26拓荒节" \
  --inputs scripts/inputs.yaml \
  --out report.md

# 分步骤（调试用）
python3 scripts/coverage_check.py fetch --festival-tab "26拓荒节"
python3 scripts/coverage_check.py trace --inputs scripts/inputs.yaml
python3 scripts/coverage_check.py report --inputs scripts/inputs.yaml --out report.md
```

依赖：`gws` CLI 已认证（同 p2-leichong-package-summary）；`pip install pyyaml` 用于读 inputs.yaml。
