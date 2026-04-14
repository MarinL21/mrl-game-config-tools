---
name: ai-to-sql
description: >-
  公司数据平台Datain的AI 自然语言生成 Trino SQL 技能。2个核心能力：
  1. 根据用户的自然语言描述，生成SQL（默认只返回SQL，不自动执行）
  2. 仅当用户明确要求执行查询或获取结果时，才执行SQL并返回数据
  覆盖游戏玩家明细日志（登录、行为、活动、资产变动、付费订单、战斗等）的取数场景。
  内置指标参考 SQL 检索、公司 wiki 知识库检索、表结构探索、权限校验等辅助能力，确保生成的 SQL 准确可执行。
  用户提到的业务概念、游戏活动、数据定义等，优先通过本技能的知识库检索，不要去外部网页搜索。
  触发词：写SQL、生成SQL、数仓查询、trino、玩家日志、登录日志、资产变动、活动参与、游戏行为、wiki、文档、业务定义、活动说明。
---

## 1. 技能概述

### 1.1 适用场景

- 查询游戏内玩家明细日志（登录时间、游戏行为、参与活动、资产变动等）
- 根据自然语言描述生成 Trino SQL，默认只返回 SQL 代码，不自动执行
- 检索公司内部 wiki 文档（业务定义、游戏活动说明、技术文档、数据字典等）
- 检索历史指标参考 SQL，复用已有取数模板
- 探索数仓表结构（字段、类型、分区）
- 按游戏维度筛选数据和知识

### 1.2 核心工具

```
skills/ai-to-sql/scripts/
  _datain_api.py      # Datain API 公共模块（鉴权、游戏列表、表权限、SQL 执行）
  get_game_info.py    # 获取当前用户的游戏列表和表权限列表（每次会话开始必须先执行）
  search_tables.py    # 关键字模糊搜索权限内的表（确认表名和 catalog）
  rag_search.py       # 检索向量库（指标参考 SQL + 公司文档）
  explore_tables.py   # 探索 Trino 表结构（字段、类型、分区，自动处理 catalog 前缀）
  query_trino.py      # 执行 Trino SQL 并返回结果
```

所有脚本通过 Datain API 访问数仓，需要环境变量 `DATAIN_API_KEY`，详见 [1.7 配置与鉴权](#17-配置与鉴权)。

### 1.3 知识库

本技能依赖两个向量知识库（通过 rag-service 检索）：

| 知识库 | 集合 | 用途 |
|--------|------|------|
| **指标参考（核心）** | `ai_to_sql.sql_key_metrics_define` | 历史指标 SQL 示例，包含指标名、SQL、游戏编码等。**大量业务查询都能在此找到现成的 SQL 逻辑，是生成 SQL 最重要的参考来源，必须优先检索** |
| 公司文档 | `hr_ai.wiki_doc` | 公司内部文档，包含业务定义、数据字典、流程说明等 |

### 1.4 数据环境

公司存在两套 Trino 环境，历史遗留原因，老游戏和新游戏的数据分别存放：

| 环境 | 说明 | 判断条件 |
|------|------|----------|
| `TRINO_AWS` | 默认环境，老游戏数据 | games API 返回 `datasource=TRINO_AWS` |
| `TRINO_HF` | TRINO_HF 环境，新游戏数据（曾用名 TRINO_A3） | games API 返回 `datasource=TRINO_HF` |

所有脚本通过 `--datasource TRINO_AWS|TRINO_HF` 参数指定环境，默认 TRINO_AWS。
游戏识别方法及常见游戏编码详见 [第 4 章 游戏识别](#4-游戏识别)。

- 各游戏通过 `game_cd`（4位数字）区分
- 其他层（如 dw 汇总层、sheets Google Sheet 映射表、dm 分析表）可能出现在参考 SQL 中，按需使用

**Trino catalog 规则（重要）：**

Trino 是多数据源查询引擎，数仓表分布在不同 catalog 中：

- **TRINO_AWS 环境**：所有表在 hive catalog，默认连接 hive，SQL 中**无需加 catalog 前缀**
- **TRINO_HF 环境**：默认连接 iceberg catalog，但部分表在 hive catalog 中
  - stg 层的表在 hive catalog → 需写 `hive.stg.user_login`
  - 其他层大部分在 iceberg → 直接写 `dl.user_login`
  - 部分表只在 hive 而非 iceberg → 需加 `hive.` 前缀

**如何判断是否需要加 `hive.` 前缀：**
1. 通过 `get_game_info.py` 返回的 `tables` 列表查看表的 catalog 前缀
2. 或用 `search_tables.py` 搜索表名，返回结果包含完整的 `catalog.layer.table` 格式
3. TRINO_HF 环境下：表在 `iceberg.xxx.xxx` → 不加前缀；表在 `hive.xxx.xxx`（且不在 iceberg 中）→ 加 `hive.` 前缀
4. `explore_tables.py` 已内置此逻辑，会自动处理 catalog 前缀

### 1.5 权限系统

数仓权限通过 Datain API 的 tables 接口自动获取。`get_game_info.py` 返回的 `tables` 列表即为当前用户有权限访问的所有表（格式 `catalog.layer.table`）。

**权限规则：**

1. **不在 tables 列表中的表 = 无权限**，遇到无权限的表时，停止探索并告知用户无权访问
2. 无权限的表提交到 Trino 后台会自然报错，无需客户端重复校验
3. 不确定表名时，先用 `search_tables.py` 搜索确认表全名和权限

**表名转换规则（重要）：**

`get_game_info.py` 返回的 `tables` 列表已根据用户权限自动转换：

- **`full_access=true`（全权限用户）**：tables 返回提示文字（无表限制），通过 `search_tables.py` 按关键字搜索确认具体表名和 catalog
- **`full_access=false`（特定游戏权限用户）**：tables 已自动转换为视图占位格式 `{catalog}.v{game_cd}.{layer}_{table}`
  - 例如：`hive.ods.user_login` → `hive.v{game_cd}.ods_user_login`
  - 使用 `v{game_cd}` 占位符避免多游戏时表列表膨胀，已去重排序
  - **生成 SQL 时，将 `{game_cd}` 替换为用户实际查询的游戏编码**
  - SQL 中所有表引用都必须使用视图格式，包括 JOIN 的表、子查询的表
  - `v{game_cd}` 视图已内置 `game_cd` 过滤，SQL 中**无需再加 `WHERE game_cd = xxx`**
  - 不同层的表转换示例：`ods.user_login` → `v1012.ods_user_login`，`dl.user_order` → `v1012.dl_user_order`，`dim.game` → `v1012.dim_game`
  - **sheets 层例外**：sheets 层不会主动建立游戏视图，优先直接查原表（如 `sheets.kvk_1047`），无权限时再尝试游戏视图（如 `v1047.sheets_kvk_1047`）

### 1.6 数仓分层详解

本技能主要使用以下 4 个数仓层，按使用频率排序：

#### ods 层 — 原始日志层（最常用）

游戏客户端/服务端上报的原始玩家行为日志，是查询玩家明细数据的主要来源。

- 更新频率：每小时
- 分区字段：`game_cd=xxxx, partition_date='yyyy-MM-dd'`（还有 `create_time` 分区但一般用 `partition_date` 过滤即可）
- 公共字段：`created_at`（事件时间）、`user_id`、`open_udid`（设备ID）、`server_id`、`platform`、`session_id`、`game_cd`、`partition_date`
- 时区：UTC+8

| 表名 | 用途 | 关键字段 |
|------|------|----------|
| `user_login` | 玩家登录日志 | country, app_version, device_name, ip, login相关 |
| `user_logout` | 玩家登出日志 | 在线时长相关 |
| `user_register` | 玩家注册日志 | 新用户首次注册 |
| `user_asset` | 资产变动明细 | asset_id, change_type, change_count, balance, reason_id |
| `user_order` | 付费订单明细 | iap_id, pay_price, pay_count, order_id, currency_type |
| `user_battle` | 战斗日志 | battle_type, battle_result, battle_role, lost_power, opponent_user_id |
| `user_activity` | 活动参与日志 | activity_id, activity_type, activity_score, activity_rank, activity_step |
| `user_event` | 通用事件日志 | event_name, event_paramter（JSON），灵活扩展 |
| `user_daily` | 每日快照 | snapshot_type, snapshot_value（玩家每日状态快照） |
| `user_gather` | 采集日志 | 资源采集行为 |
| `user_chat` | 聊天日志 | 玩家聊天记录 |
| `user_fte` | 新手引导日志 | 新手引导步骤完成情况 |
| `user_task` | 任务日志 | 任务完成情况 |
| `user_click` | 点击事件 | UI 点击行为埋点 |
| `user_hero` | 英雄相关 | 英雄数据变动 |
| `user_power_change` | 战力变动 | 战力变化记录 |
| `user_rlevel` | 等级变动 | 玩家等级变化 |
| `server_ccu` | 服务器在线人数 | 实时在线统计 |

#### stg 层 — 实时日志层

ods 层的实时版本，表结构与 ods 基本一致，适用于需要查看最近几小时数据的场景。

- 更新频率：每 5 分钟
- 分区字段：`game_cd=xxxx, create_date='yyyy-MM-dd_HH'`（注意分区格式与 ods 不同，精确到小时，用下划线连接）
- **时区：stg 层的分区 `create_date` 和 `created_at` 字段均为 UTC+0**，用户提到的时间需减 8 小时转换
- 使用场景：查看当天实时数据、近几小时的玩家行为、线上问题排查
- 常用表：与 ods 同名，如 `stg.user_login`、`stg.user_asset`、`stg.user_order` 等
- **权限限制：stg 层的表权限取决于 tables 列表，不在列表中则无权访问**
- **⚠️ 默认不使用 stg 层**：stg 层数据未经清洗，默认优先使用 ods/dl 层；仅当用户明确要求查实时数据、当天最新数据或特别指定 stg 层时才使用

> 查询 stg 层时 WHERE 条件示例：`create_date = '2026-03-18_05'`（UTC+0，对应北京时间 13 点）
> 用户说"今天下午1点"，需要减 8 小时转为 UTC+0 即 `05` 点

#### dl 层 — 明细汇总层

在 ods 基础上做了清洗、去重、聚合的明细数据，查询性能优于 ods。

- 更新频率：每小时
- 分区字段：`game_cd=xxxx, partition_date='yyyy-MM-dd'`
- 适用场景：需要汇总统计（如日活、日付费）而非逐条明细时，优先使用 dl 层

| 表名 | 用途 | 关键字段 |
|------|------|----------|
| `user_login_sum` | 每日登录汇总 | login_times, online_minutes, login_hour, day_interval |
| `user_order` | 付费订单（清洗后） | pay_price, shared_pay_price, total_pay_price, iap_rank |
| `user_asset_d` | 每日资产汇总 | asset_id, add_times, add_num, use_times, use_num, balance |
| `user_asset_h` | 每小时资产汇总 | 同上，按小时粒度 |
| `user_battle` | 战斗汇总 | 战斗统计 |
| `user_basic_info_d` | 玩家每日基础信息 | 等级、战力、VIP等每日快照 |
| `install` | 安装归因 | 安装来源、渠道 |
| `new_user` | 新增用户 | 每日新增用户明细 |

#### dim 层 — 维度表

静态或低频更新的维度数据，用于关联查询时补充维度信息。

- 更新频率：按需（通常每日或手动更新）
- 分区字段：无分区（数据量小，直接全表查询）
- 适用场景：关联游戏名称、国家、资产类型等维度信息

| 表名 | 用途 |
|------|------|
| `game` | 游戏列表（game_cd, game_name, game_alias, company_id） |
| `country` | 国家/地区映射 |
| `asset` | 资产 ID 与名称映射 |
| `asset_type` | 资产类型分类 |
| `goods` / `goods_detail` | 商品信息 |
| `building` | 建筑信息 |
| `battle_type` / `battle_role` | 战斗类型/角色映射 |
| `device_info` | 设备信息 |
| `currency_exchange` | 汇率 |

#### sheets 层 — Google Sheet 映射表

Google Sheet 同步到数仓的配置表、活动表等，通常由策划或运营维护。

- 更新频率：改动后几分钟内自动同步
- 分区字段：无分区
- 表名通常带游戏编码或别名，如 `sheets.kvk_1047`、`sheets.vehicle_level_cost_1096`
- **sheets 层不会主动在各游戏 `v{game_cd}` 视图下建立对应视图**，查询时优先直接查原表（如 `sheets.kvk_1047`），若无权限再尝试游戏视图下的表（如 `v1047.sheets_kvk_1047`）

---

## 2. 完整查询流程

> **重要：每次会话开始时，必须先执行 `get_game_info.py` 获取当前用户的游戏权限和游戏列表，后续所有操作基于此信息进行。**

```
会话开始
    ↓
┌─────────────────────────────────────────┐
│ Step 0: 初始化 — 获取游戏权限信息        │
│ python3 skills/ai-to-sql/scripts/get_game_info.py        │
│ - 获取 full_access / game_cds / games   │
│ - 获取每个游戏的 datasource 环境         │
│ - 获取 tables（用户有权限的表列表）       │
│ - 后续无需再查 dim.game 识别游戏         │
└─────────────────────────────────────────┘
    ↓
用户提问
    ↓
┌─────────────────────────────────────────┐
│ Step 1: 识别游戏、环境与意图              │
│ - 从 Step 0 结果中匹配游戏               │
│ - 确定环境：直接使用 datasource 字段      │
│ - 提取关键词（指标、维度、时间等）         │
│ - 确定输出形式（SQL / 数据 / 分析结论）   │
│ - 不确定时主动询问用户                    │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Step 2: 检索知识库（必须执行）            │
│ - **指标参考（必查）**：大量业务查询都有  │
│   现成 SQL 逻辑，必须优先检索参考 SQL    │
│ - 公司文档：理解业务概念和数据定义         │
│ - 任何取数需求，都先查指标参考再动手写 SQL│
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Step 3: 探索表结构 + 数据验证             │
│ - explore_tables.py 获取字段和分区信息    │
│ - 必要时用 query_trino.py 抽样验证数据    │
│ - 结合参考 SQL 确认表和字段的正确性        │
│ - 参考 SQL 中的表名、字段名优先采信       │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Step 4: 生成 SQL                        │
│ **优先基于参考 SQL 改写**，而非从零编写   │
│ 结合参考 SQL + 表结构 + SQL 规范         │
│ 生成高性能 Trino SQL（注意分区过滤）      │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Step 5: 执行与输出                       │
│ **默认行为：只输出 SQL，不自动执行**      │
│ - 生成 SQL 后先执行验证语法正确性         │
│ - 验证通过后，将 SQL 展示给用户           │
│ - 仅当用户明确要求"执行"/"查询"/"拿结果" │
│   时，才用 query_trino.py 执行并返回数据  │
│ - 执行查询后如数据较多，做简要分析解读    │
└─────────────────────────────────────────┘
```

---

## 3. 工具命令详解

### 3.1 获取游戏权限信息

查询当前用户权限范围内的游戏列表及环境信息。**每次会话开始必须先执行此脚本。**

```bash
python3 skills/ai-to-sql/scripts/get_game_info.py
```

无需参数，通过 Datain API 获取当前用户的游戏权限和游戏列表。

**输出示例：**
```json
{
  "full_access": true,
  "game_cds": [1047, 1038, 1096, 1012, ...],
  "games": [
    {"game_cd": 1012, "name": "(BA) Brutal Age", "datasource": "TRINO_AWS"},
    {"game_cd": 1096, "name": "(k1d23) top girl", "datasource": "TRINO_HF"}
  ],
  "stg_access": true,
  "tables": ["hive.ods.user_login", "iceberg.dl.user_login_sum", ...]
}
```

**字段说明：**
- `full_access`：是否拥有全权限
- `game_cds`：用户拥有的游戏编码列表
- `games`：每个游戏的详细信息（game_cd、name、datasource）
- `stg_access`：是否可查询 stg 层
- `tables`：`full_access=true` 时为提示文字（全权限无表限制，通过 `search_tables.py` 按需搜索）；`full_access=false` 时为视图占位格式列表 `catalog.v{game_cd}.{layer}_{table}`（去重排序，生成 SQL 时替换 `{game_cd}` 为实际游戏编码）

### 3.2 搜索权限内的表

关键字模糊搜索当前用户有权限的表，返回完整的 `catalog.layer.table` 格式。

```bash
python3 skills/ai-to-sql/scripts/search_tables.py --keyword "关键字"
```

**参数：**
- `--keyword`：**必填**，搜索关键字，如 `login`、`asset`、`order`

**输出示例：**
```json
["hive.ods.user_login", "hive.dl.user_login_sum", "iceberg.ods.user_login", ...]
```

**使用场景：**
- 不确定表名时，先搜索确认
- 确认表在哪个 catalog（hive/iceberg），判断 TRINO_HF 环境下是否需要加 `hive.` 前缀
- 确认用户是否有某张表的权限

### 3.3 检索知识库

从向量库中检索指标参考 SQL 和公司文档。自动使用混合检索（向量 0.5 + 关键词 0.5）、分词、重排。

```bash
python3 skills/ai-to-sql/scripts/rag_search.py --query "检索关键词" [--game_cd 游戏编码,多个逗号分隔] [--top_n 返回条数] [--source metrics|wiki|all]
```

**参数：**
- `--query`：**必填**，检索关键词
- `--game_cd`：**强烈建议传入**，游戏编码，多个用逗号分隔（如 `1012,1038`）。仅对 metrics 生效，自动包含 1000（通用指标）。传入 game_cd 可获得该游戏专属的参考 SQL，检索结果更精准。wiki 文档无 game_cd 概念，此参数对 wiki 不生效
- `--top_n`：可选，每个知识库返回条数，默认 40，最大 100
- `--source`：可选，检索来源。`metrics`=指标参考，`wiki`=公司文档，`all`=全部（默认）

**权限隔离：**
- 指标参考库已内置权限隔离，非全权限用户只能检索 `game_cd=1000`（通用）和自己有权限的游戏的参考 SQL
- 未传入 `--game_cd` 时，脚本自动使用用户全部有权限的 game_cds 进行过滤
- `full_access=true` 的用户不受此限制

**检索逻辑说明：**
- 指标参考库中 `game_cd=1000` 的记录是通用参考 SQL（登录、付费等基础取数），适用于所有游戏
- 传入 `--game_cd 1012` 时，底层 where 条件为 `game_cd IN ('1000','1012')`，确保通用指标始终被检索到
- 传入 `--game_cd 1012,1038` 时，底层 where 条件为 `game_cd IN ('1000','1012','1038')`

**输出示例（--source all）：**
```json
{
  "metrics": [
    {"title": "每日活跃用户数DAU", "sql": "SELECT ...", "game_cd": "1012", "source_type": "sql"}
  ],
  "wiki": [
    {"title": "DAU 定义", "text": "DAU 指每日登录的独立设备数..."}
  ]
}
```

**使用建议：**
- **任何取数需求，都必须先检索指标参考（metrics）**，大量业务查询都有现成 SQL 逻辑可直接复用或改写
- **检索 metrics 时务必传入 `--game_cd`**，可获得该游戏专属的参考 SQL，检索结果更精准
- 业务概念不清楚时，同时检索 wiki 理解定义
- 不要跳过检索直接写 SQL，参考 SQL 中包含了大量经过验证的业务逻辑和字段用法

### 3.4 探索表结构

获取 Trino 表的字段名、类型、注释和分区信息。TRINO_HF 环境自动处理 catalog 前缀。

```bash
python3 skills/ai-to-sql/scripts/explore_tables.py --tables "表名1,表名2" [--datasource TRINO_AWS|TRINO_HF]
```

**参数：**
- `--tables`：**必填**，逗号分隔的表名，如 `ods.user_login,dl.user_daily`
- `--datasource`：可选，`TRINO_AWS`（默认）或 `TRINO_HF`，根据游戏所属环境选择

### 3.5 执行 SQL 查询

在 Trino 上执行 SQL 并返回结果。仅允许 SELECT / EXPLAIN / SHOW / DESCRIBE 语句。

```bash
python3 skills/ai-to-sql/scripts/query_trino.py --sql "SELECT语句" [--limit 返回行数] [--datasource TRINO_AWS|TRINO_HF]
```

**参数：**
- `--sql`：**必填**，待执行的 SQL 语句
- `--limit`：可选，返回行数限制，默认 100
- `--datasource`：可选，`TRINO_AWS`（默认）或 `TRINO_HF`，根据游戏所属环境选择

> **超时设置：** Trino SQL 执行可能耗时较长，执行 `query_trino.py` 时，调用 exec/shell 工具的超时需设置为 **10 分钟（600秒）**，避免查询被提前中断。

---

## 4. 游戏识别

### 4.1 识别游戏与环境

会话开始时已通过 `get_game_info.py` 获取了用户权限范围内的游戏列表（含 game_cd、game_name、game_alias、datasource），直接从该结果中匹配用户提到的游戏即可。

- 匹配时注意大小写不敏感（用户输入大小写随意）
- 如果 `full_access=true`，返回结果包含所有游戏，直接按名称/别名匹配
- 如果 `full_access=false`，返回结果仅包含用户有权限的游戏，匹配不到说明用户无权查询该游戏

### 4.2 常见游戏编码

| game_cd | 别名 | 环境 |
|---------|------|------|
| 1001 | 301 | TRINO_AWS |
| 1012 | ba | TRINO_AWS |
| 1022 | 301me | TRINO_AWS |
| 1038 | kow, b2 | TRINO_AWS |
| 1041 | p2 | TRINO_AWS |
| 1047 | k1 | TRINO_AWS |
| 1076 | p2cn | TRINO_AWS |
| 1088 | x1 | TRINO_HF |
| 1089 | x2 | TRINO_HF |
| 1090 | x3 | TRINO_HF |
| 1096 | top girl, k1d23 | TRINO_HF |

> `1000` 不是真实游戏，Trino 中无此 game_cd 的数据。它仅用于 RAG 指标检索（标记通用参考 SQL）。

### 4.3 不确定时主动询问

如果无法确定用户要查哪个游戏，**主动询问**，不要猜测。

---

## 5. SQL 生成规范

### 5.1 基本规范

1. **生成 SQL 前必须先检索指标参考**，优先基于参考 SQL 改写，而非从零编写；参考 SQL 中包含经过验证的业务逻辑、表名、字段用法
2. 所有表必须加别名，别名小写，SQL 结尾不加分号
2. 字段别名包含中文时用双引号包裹，如 `count(*) as "活跃用户数"`
3. 浮点型数据保留两位小数，除法用 `1.00 * 被除数 / 除数`
4. 适当使用 WITH 子查询，同一源表尽量只出现一次
5. 子查询中注意数据去重后再 JOIN，避免笛卡尔积
6. 注重 SQL 可读性，适当缩进和换行

### 5.2 分区与性能

7. 有分区字段的表**必须**通过 WHERE 加分区过滤
8. 常见分区格式：ods/dl 层 `partition_date='yyyy-MM-dd'`，stg 层 `create_date='yyyy-MM-dd_HH'`
9. **如果用户未指定日期，默认查询近 7 天数据**
10. 大表查询务必加 LIMIT，避免全表扫描
11. **stg 层时区为 UTC+0**，用户提到的时间需减 8 小时转换；ods/dl 等其他层为 UTC+8，无需转换

### 5.3 权限与表名

12. **生成的所有 SQL 中引用的表必须在用户的 tables 权限列表中**
13. 不在权限列表中的表，停止探索并告知用户无权访问
14. 参考 SQL 中出现的表，需确认在用户权限列表中，不在则不能使用
15. 参考 SQL 中 `game_cd=1000` 的通用逻辑，生成实际 SQL 时必须替换为用户指定的真实 game_cd（1000 在 Trino 中无实际数据）
16. **TRINO_HF 环境**：如果表在 hive catalog（非 iceberg），SQL 中需加 `hive.` 前缀（如 `hive.stg.user_login`）
17. 不确定表名时，先用 `search_tables.py` 搜索确认表全名和 catalog
18. **表名转换（关键）**：`full_access=false` 的用户，tables 为视图占位格式（如 `hive.v{game_cd}.ods_user_login`），生成 SQL 时将 `{game_cd}` 替换为实际游戏编码；`full_access=true` 的用户可直接查原表
19. 使用 `v{game_cd}` 视图时，视图已内置 game_cd 过滤，SQL 中**无需再加 `WHERE game_cd = xxx`**

### 5.4 质量要求

18. 严格参照表结构，不能使用表结构里没有的字段
19. 参考指标 SQL 有语法问题时，修复后使用
20. 不使用 redshift 库下的表
21. stg 层可以用于查询实时数据，但注意分区格式是 `create_date='yyyy-MM-dd_HH'`
22. 聚合函数表达式的筛选写在 HAVING 中
23. 先输出 SQL，后输出自然语言伪代码解释逻辑

---

## 6. 实战示例

### 示例 1：查询 DAU（TRINO_AWS 环境老游戏）

**用户问题：** "ba 游戏最近一周每天的 DAU"

**执行步骤：**

```bash
# 1) ba=1012 → TRINO_AWS 环境
# 2) 检索指标参考和文档
python3 skills/ai-to-sql/scripts/rag_search.py --query "DAU 活跃用户" --game_cd 1012

# 3) 探索涉及的表结构
python3 skills/ai-to-sql/scripts/explore_tables.py --tables "ods.user_login" --datasource TRINO_AWS

# 4) 执行查询（TRINO_AWS 环境）
# ── full_access=true（全权限）→ 直接查原表，需加 WHERE game_cd ──
python3 skills/ai-to-sql/scripts/query_trino.py --datasource TRINO_AWS --sql "
SELECT partition_date, count(distinct open_udid) as DAU
FROM ods.user_login a
WHERE a.game_cd = 1012
  AND a.partition_date BETWEEN '2026-03-11' AND '2026-03-18'
GROUP BY partition_date
ORDER BY partition_date
" --limit 100

# ── full_access=false（特定游戏权限）→ 必须用 v{game_cd} 视图，无需 WHERE game_cd ──
python3 skills/ai-to-sql/scripts/query_trino.py --datasource TRINO_AWS --sql "
SELECT partition_date, count(distinct open_udid) as DAU
FROM v1012.ods_user_login a
WHERE a.partition_date BETWEEN '2026-03-11' AND '2026-03-18'
GROUP BY partition_date
ORDER BY partition_date
" --limit 100
```

### 示例 2：查询 TRINO_HF 环境新游戏

**用户问题：** "x1 游戏昨天的登录人数"

**执行步骤：**

```bash
# 1) x1=1088 → TRINO_HF 环境
# 2) 检索指标参考
python3 skills/ai-to-sql/scripts/rag_search.py --query "登录人数" --game_cd 1088 --source metrics

# 3) 探索表结构（TRINO_HF 环境，脚本自动处理 catalog 前缀）
python3 skills/ai-to-sql/scripts/explore_tables.py --tables "ods.user_login" --datasource TRINO_HF

# 4) 执行查询（TRINO_HF 环境）
# ── full_access=true → 直接查原表 ──
python3 skills/ai-to-sql/scripts/query_trino.py --datasource TRINO_HF --sql "
SELECT count(distinct user_id) as \"登录人数\"
FROM ods.user_login a
WHERE a.game_cd = 1088
  AND a.partition_date = '2026-03-17'
" --limit 100

# ── full_access=false → 用 v{game_cd} 视图 ──
python3 skills/ai-to-sql/scripts/query_trino.py --datasource TRINO_HF --sql "
SELECT count(distinct user_id) as \"登录人数\"
FROM v1088.ods_user_login a
WHERE a.partition_date = '2026-03-17'
" --limit 100
```

### 示例 3：查询业务概念或游戏名词

**用户问题：** "ba 的先锋服是什么"

**执行步骤：**

```bash
# 用户问的是游戏内业务名词，优先检索公司知识库，不要去外部网页搜索
# 1) 检索 wiki 文档理解"先锋服"概念
python3 skills/ai-to-sql/scripts/rag_search.py --query "ba 先锋服" --source wiki

# 2) 检索指标参考，看是否有先锋服相关的取数逻辑
python3 skills/ai-to-sql/scripts/rag_search.py --query "先锋服" --game_cd 1012 --source metrics
```

### 示例 4：不确定业务概念时

**用户问题：** "kow 游戏的 ARPPU 是多少"

**执行步骤：**

```bash
# 1) 先检索公司文档理解 ARPPU 定义
python3 skills/ai-to-sql/scripts/rag_search.py --query "ARPPU" --source wiki

# 2) 再检索指标参考获取 SQL 模板
python3 skills/ai-to-sql/scripts/rag_search.py --query "ARPPU 付费" --game_cd 1038 --source metrics

# 3) 探索表结构、生成 SQL、执行
```

### 示例 5：探索性查询

**用户问题：** "帮我看看有哪些 login 相关的表"

```bash
python3 skills/ai-to-sql/scripts/search_tables.py --keyword "login"
```

---

## 7. 注意事项

### 7.1 交互原则

- 如果用户未指定游戏，**主动询问**要查哪个游戏的数据
- 如果问题不明确或条件不充分，**主动询问**而不是猜测
- **默认只返回生成的 SQL，不自动执行**；仅当用户明确说"执行"、"查一下"、"帮我跑一下"、"拿到结果"等时，才执行 SQL
- 执行结果较多时，做简要的数据分析和解读

### 7.2 知识库使用策略

- **任何取数需求，必须先检索指标参考（metrics）**，大量业务查询都有现成 SQL 可直接复用或改写，不要跳过检索直接写 SQL
- 游戏业务名词、活动名称、服务器类型等 → **优先检索 wiki 文档，不要去外部网页搜索**
- 业务概念不清楚 → 先查 wiki 文档
- 复杂需求 → metrics + wiki 都查，交叉验证
- 检索结果不理想 → 换同义词或更细粒度的关键词，多次检索
- 参考 SQL 中的表名、字段名、业务逻辑优先采信，是最可靠的取数依据

### 7.3 多轮对话

- 支持在同一会话中多次提问，后续问题可以引用之前的上下文
- 如果用户要求修改 SQL，基于之前生成的 SQL 进行调整
- 保持对话中游戏选择的一致性，除非用户明确切换

### 7.4 性能建议

- 大表查询务必加分区过滤和 LIMIT
- 避免 SELECT *，只查需要的字段
- 子查询去重后再 JOIN
- 使用 EXPLAIN 验证复杂 SQL 的执行计划

### 1.7 配置与鉴权

本技能通过 Datain API 访问数仓，需要环境变量 `DATAIN_API_KEY`。

**获取 DATAIN_API_KEY 的步骤：**

1. 获取环境变量 `DATAIN_API_KEY`
2. 如果 `DATAIN_API_KEY` 不存在，提示用户：
   - 权限申请：钉钉工作台 -> T4F审批 -> datain 权限申请
   - 已有权限用户：打开 https://datain.tap4fun.com/ -> 个人中心 -> 设置 -> APP KEY
   - 复制 APP KEY 发送给你，你来设置本机的环境变量 `DATAIN_API_KEY`，需要持久保存下来
3. 持久化保存 `DATAIN_API_KEY`
   - 确保下次新开会话时，你能自动读取到 `DATAIN_API_KEY`，不要让用户再重复发送给你
   - 根据不同的工具判断环境变量应该持久化存放在哪里：
     - 比如 Claude Code 之类的，你可以放在本机的环境变量配置文件中
     - OpenClaw 之类的，通常你需要放在 openclaw.json 的 env.vars 配置中
