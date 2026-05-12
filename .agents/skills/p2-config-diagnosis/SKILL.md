---
name: p2-config-diagnosis
description: >-
  P2 配置表 bug 诊断助手。根据现象描述或 Jira 工单，定位 10/11/13/19/20/21 六大文件夹（302 张表）可能的配置错位、字段错配、枚举错、跨表引用断链，并用 gws 去真实表验证。
  覆盖节日活动、礼包、任务、排行、弹窗、道具、建筑、科技、兵种、英雄、IAP、VIP、主城皮肤、行军特效、头像框、集卡、酒馆、地图 NPC、竞技场、大富翁、挖孔、钓鱼等全品类。
  触发：查bug、配置诊断、Jira工单、为什么不生效、xxx不显示、xxx不发货、活动没开、任务卡0、排行0分、礼包买完没东西、玩家反馈、QA报的、LC显示原文、弹窗不出、头像框穿不上、主城皮肤变默认、科技无法研究。
---

# P2 配置 Bug 诊断 Skill

## 定位

**输入**：玩家/QA 反馈的现象、Jira 工单描述、"xxx 为什么不生效" 这类问题。
**输出**：最可能的 3 个假设 + 每个假设的验证步骤 + 自动/手动查哪张表哪行哪字段。
**边界**：只诊断**配置层** bug。代码逻辑 bug、美术资源本身问题、服务端运维问题，会显式说明"超出 scope，请转其它渠道"。

## Jira 集成（读工单）

**Jira 实例**：`https://jira.tap4fun.com`
**认证文件**：`~/.git-jira-commit-assist-auth.json`（已存在，由 `git-jira-commit-assist` skill 建的）

文件格式：
```json
{"baseUrl":"https://jira.tap4fun.com", "token":"<PAT>", "defaultIssueType":"Task"}
```
（或 `username` + `password` 基本认证）

**读工单标准命令**（用户给 Jira ID 如 `P2-12345` 时直接跑）：
```bash
AUTH=~/.git-jira-commit-assist-auth.json
TOKEN=$(python3 -c "import json;print(json.load(open('$AUTH')).get('token',''))")
BASE=$(python3 -c "import json;print(json.load(open('$AUTH')).get('baseUrl',''))")
# Bearer token 认证
curl -s -H "Authorization: Bearer $TOKEN" "$BASE/rest/api/2/issue/P2-12345?fields=summary,description,status,priority,comment" \
  | python3 -m json.tool
```

如果是 username/password：
```bash
USER=$(python3 -c "import json;print(json.load(open('$AUTH')).get('username',''))")
PASS=$(python3 -c "import json;print(json.load(open('$AUTH')).get('password',''))")
curl -s -u "$USER:$PASS" "$BASE/rest/api/2/issue/P2-12345?fields=summary,description,status,priority,comment"
```

**硬性规则**：用户给 Jira ID 时 **不要反问 token**——直接读 `~/.git-jira-commit-assist-auth.json`，拿 summary + description + 最新 3 条 comment 作为诊断输入，再进入 Phase 0。

如果认证文件不存在或过期（curl 返回 401）：告诉用户"Jira token 失效，请重跑 `git-jira-commit-assist` skill 的认证，或手动粘贴工单内容给我"。

## 知识源

所有字段级规范存放在 `references/` 下，是 `docs/p2_config_spec/` 的软链接（一处维护，两处生效）：

| 文件 | MD | 核心覆盖 |
|---|---|---|
| **00_cross_table_map** ⭐ **先读这份** | [references/00_cross_table_map.md](references/00_cross_table_map.md) | 设计哲学（3 件事）+ 六文件夹定位 + 三种隐蔽引用 + 九条主链 + 跨文件夹边汇总 |
| 10_p2_const | [references/10_p2_const.md](references/10_p2_const.md) | i18n LC、全局常量、AB 测试、功能开关、弹窗、渠道、DLC 资源 |
| 11_p2_asset | [references/11_p2_asset.md](references/11_p2_asset.md) | 道具、资源、货币、建筑、科技、兵种、头像、酒馆、集卡、行军表情 |
| 13_p2_map | [references/13_p2_map.md](references/13_p2_map.md) | 大地图、NPC、联盟矿、行军特效、主城皮肤、竞技场、过关、探索 |
| 19_p2_hero | [references/19_p2_hero.md](references/19_p2_hero.md) | 英雄、技能、天赋、装备、词条、皮肤、招募 gacha |
| 20_p2_iap | [references/20_p2_iap.md](references/20_p2_iap.md) | IAP、VIP、累充、成就礼包、破冰、红包、BI 推荐 |
| 21_p2_event | [references/21_p2_event.md](references/21_p2_event.md) | 节日活动、任务、排行、礼包、BP、大富翁、挖孔、钓鱼 |

**通用字段前缀约定（A_/S_/C_/N_ + INT_/FLT_/STR_/ARR_/MAP_）写在 10_p2_const.md 顶部**，诊断时默认用户已理解这些。

**强制调用顺序**：Phase 0 前**必须先读 00_cross_table_map.md 的"设计哲学"+"六文件夹定位"+"三种隐蔽引用"三段**（顶部不到 100 行），建立系统边界后再进 Phase 0 映射文件夹，否则会漏识别 [ENUM]/[EMBED]/[ARR+混装] 这类隐蔽断链。

## 触发规则

### 必触发（用户明确提到）
- "查 bug" / "帮我查" / "帮我诊断" / "诊断配置"
- "Jira" / "工单" + 描述
- "为什么 xxx 不 xxx" 的疑问句（xxx 是配置相关的行为）
- 现象 + "怎么回事" / "什么原因"

### 主动识别触发（隐式现象描述）
用户没说"查 bug"但描述了这些现象 → 主动上手：
- **文案类**：`LC_xxx` 显示原 key / 文案没翻译 / 文案字有问号
- **活动类**：活动没开 / 开错时间 / 活动图标不显示 / 节日弹窗不弹
- **礼包类**：买完没发货 / 充值无响应 / 购买按钮灰 / 礼包在付费墙找不到
- **任务类**：任务卡 0 / 进度不计 / 任务奖励不发
- **排行类**：排行榜 0 分 / 个人榜变联盟榜 / 入榜阈值异常
- **外观类**：头像框/主城皮肤/行军特效穿不上 / 变回默认 / 套装羁绊不触发
- **道具类**：用了没效果 / 找不到来源 / 背包分类错
- **建筑/科技类**：无法升级 / 前置失效 / 按钮灰 / 时长异常
- **英雄类**：技能不触发 / 招募抽不出 / 天赋加点失效 / 装备属性错
- **弹窗类**：弹窗顺序错 / 海报没更新 / 弹窗空白
- **国服/海外分支**：国服独有开关没开 / 海外显示了国服专用内容

### 不触发（超出 scope，主动告知用户）
- 需要读/写代码：让用户去找开发
- 非 6 文件夹内的配置（如 14_quest / 22_notification / 23_situation / 17_features / 18_union / 25-80 玩法模块）：说明"本 skill 只覆盖 10/11/13/19/20/21，其它文件夹配置请手动查表或另起 skill"
- 美术资源本身缺失/错误（如图被美术删了）：让用户找美术
- 性能/崩溃/服务器报错：不是配置问题

## 诊断流程

### Phase -1（强制）：读 00_cross_table_map.md 顶部三段

**在任何文件夹映射前**，先读 `references/00_cross_table_map.md` 顶部约 100 行：
- **设计哲学** — 认知 1111 是"可获得物"抽象中枢、effect.typ 是路由、requirement 是通用 DSL
- **六文件夹定位** — 定位症状落哪个文件夹
- **三种隐蔽引用** — [ENUM] / [EMBED] / [ARR+混装]，bug 最高频来源

**跳过这一步会**：漏识别嵌入式 id（1111.use_labels / 2011.iap_status）、typ 枚举路由错位（category_param.typ 写错）、混装数组缺件（1389.items 漏装饰）。

### Phase 0：解析现象 → 映射到文件夹

**不要只看症状描述的表面词，看底层行为类**：

| 现象关键词 | 最可能的文件夹 | 次要可能 |
|---|---|---|
| LC_ / 文案 / 翻译 | 10 (1011 i18n) | 所有表 |
| 活动没开/时间错 | 21 (2111 calendar + 2112 config) | 10 (1013 常量) |
| 礼包/充值/vip | 20 (2011/2013/2017) | 21 (2135 活动礼包) |
| 主城/建筑/城市皮肤 | 11 (1118 building) + 13 (1312 city_skin) | 21 (2148 节日装饰) |
| 行军特效/主城特效 | 13 (1365/1387/1389) | 21 (2148 装饰) |
| 头像框/铭牌/旗帜 | 11 (1142/1173/1143/1144) | - |
| 行军表情 | 11 (1180 map_emoji) + 13 (1393/1394) | - |
| 英雄/技能/天赋/装备 | 19 (1920-1952) | - |
| 任务/排行 | 21 (2115/2122) | 10 (1014 counter) |
| NPC/野怪/集结 | 13 (1313-1317) | - |
| 联盟矿/部落 | 13 (1337/1338/1345) | - |
| 竞技场 | 13 (1357-1364 / 1373-1376) | 21 (2162/2170) |
| 大富翁/挖孔/钓鱼 | 21 (2151/2174/2176) | - |
| 弹窗 | 10 (1023) | 21 (2159) |
| 功能开关 | 10 (1022 function_switch) | - |
| AB 测试 | 10 (1018 ab_test) | - |
| 国服 vs 海外 | 所有表的 `country_use_type` | 10 (1022) |
| 渠道/bundle | 10 (1026/1027) | - |

### Phase 1：打开对应 MD 的"Jira 自检路径表"

每个 MD 末尾都有一张 `## Jira 工单常见自检路径`。**先读这张表**，不要凭记忆回答。

用 Read 工具读对应 MD 的底部段（每个 MD 400 行+，用 offset 定位末尾 150 行即可）。

### Phase 2：输出 3 个假设

按可能性排序，每个假设包含：

```
Hypothesis N: <一句话说明>
  - 涉及表：<表号> <字段>
  - 具体含义：<字段在 MD 中的定义>
  - 常见错误模式：<根据 bug 模式列表>
  - 验证方法：<gws 命令 OR 手动查表位置>
  - 修复方向：<改什么字段为什么值>
```

### Phase 3：用 gws 验证（可选但强烈推荐）

**触发 gws 验证的条件**：用户给了具体 ID（活动 id、道具 id、礼包 id 等）。

**不要盲 gws**：没有具体 id 时，只给验证步骤让用户自己查，不要浪费 API 调用读整表。

验证命令模板：
```bash
# 读取指定表某范围
gws sheets spreadsheets values get --params '{"spreadsheetId":"<SHEET_ID>","range":"<TAB>!A:Z"}'

# Sheet ID 见 memory project_p2_config_system.md 或 docs/p2_config_spec/ 各 MD 里引用
```

如果用户装了 `id-lookup-plugin`，可以直接在表里用侧边栏查跨表引用（见 reference_id_lookup_plugin memory）。

### Phase 4：如果假设 1 被否决，推进假设 2

不要假设确定就停止——**明确告诉用户"这是 hypothesis 1，如果验证不中再试 hypothesis 2"**，引导用户迭代。

## 诊断输出模板

```markdown
## 诊断：<一句话问题归纳>

**映射到文件夹**：<N_p2_xxx>
**最相关的表**：<表号> / <表号> / <表号>

### 假设 1（概率最高）：XX
- **涉及**：`<表>.<字段>` — <字段定义>
- **常见错误**：<bug 模式>
- **验证**：
  ```bash
  <gws 命令>
  ```
- **如果确实是这个问题**：<修复动作>

### 假设 2：YY
...

### 假设 3：ZZ
...

### 超出 scope 的可能（排除这些才回来找我）
- <代码层 / 美术层 / 其它文件夹的可能>
```

## 示例对话

### 示例 1：用户症状描述

**用户**：玩家反馈拓荒节行军表情礼包买完没东西

**Skill 反应**：
1. 映射：21_event（礼包） + 11_asset（表情+道具）
2. 读 21_p2_event.md 的"Jira 自检路径" → "礼包买完没发货 → 2135 + 1111"
3. 读 11_p2_asset.md 的"Jira 自检路径" → "使用道具无效果 → 1111.category_param.effect"
4. 输出 3 个假设：
   - H1: 2135.A_ARR_get_items 的 item id 在 1111 被删/换
   - H2: 1111 的对应 item.category_param.effect 里 1180 emoji id 失效
   - H3: 2135.A_INT_iap（若非 0）指向的 2013 template 有效但 other_items 未配
5. 给出 gws 命令查 2135 对应行

### 示例 2：Jira 工单

**用户**：Jira P2-12345 说"KVK5 服看不到周年庆主城套装"

**Skill 反应**：
1. 映射：13_map（主城套装 1389）+ 21_event（节日活动 2112）
2. 读 13_p2_map.md → "主城套装羁绊不触发 → 1389 A_ARR_items"
3. 输出假设：
   - H1: 2112.S_MAP_server_info 的 schema 不含 KVK5 服
   - H2: 1312.A_ARR_status_active 或 1389.A_INT_suit 配置错
   - H3: 2011.S_MAP_server_info（如果是内购礼包解锁）漏 KVK5
4. 提供 gws 命令读对应行

### 示例 3：排除外的问题

**用户**：为什么战斗死兵多

**Skill 反应**：
"这是战斗数值/兵种配置问题，超出本 skill scope（我只覆盖 10/11/13/19/20/21）。
可能涉及 16_battle 文件夹，或 1121 soldier 兵种定义（这个在 11_asset 我覆盖了）。
你说的是兵种基础属性问题，还是战斗系数问题？如果是后者需要 16_battle。"

## 与其他 skill 的协作

| 其它 skill | 关系 |
|---|---|
| `p2-unite-gift-pack` / `p2-unite-gift-config` | **配置时**用它们；**诊断已配置的 bug** 用本 skill |
| `id-lookup-plugin` | 本 skill 推荐用户用 ID 插件去表里查跨表引用 |
| `p2-translation-style` / `p2-translation-automatic` | LC 文案类 bug 诊断到 1011 后，如需改文案转这两个 skill |
| `datain-skill` / `ai-to-sql` | 如果 bug 涉及数据表现（DAU/留存/付费），配合数据查询 |
| `igame-skill` | 如果诊断结论是"需要运维操作"（如发邮件/GM 操作），转 igame skill 执行 |

## 维护原则

1. **任何配置 bug 定位到新的踩坑点**：回写到对应 `docs/p2_config_spec/*.md` 的"常见 bug"段，而不是往 skill 里加。
2. **MD 更新自动生效**：SKILL.md 只是调度器，知识在 MD 里。
3. **不要凭记忆**：每次诊断打开对应 MD 的"Jira 自检路径表"读一遍，即使看起来熟悉。
4. **跨 MD 引用断链**：遇到 MD 里标的 id 范围和实际不符（如表扩了新字段），**用 gws 读真实表校准后回写 MD**。

## 硬性规则

- 输出必须分 3 个假设，不要直接下结论（避免误导用户只查一处）。
- 每个假设必须附带**验证方法**（gws 命令或手动查表坐标）。
- 如果用户提供了具体 id（活动/道具/礼包/玩家），**主动用 gws 去真实表验证 H1**，不要让用户自己跑命令。
- 如果 3 个假设都不符合任何 MD 里记录的 bug 模式，说明"这是新的 bug 类型，定位后请补充到对应 MD 的常见 bug 段"。
