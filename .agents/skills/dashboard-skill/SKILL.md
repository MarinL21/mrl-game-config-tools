---
name: dashboard-skill
description: >-
  公司数据平台Datain的Dashboard/看板/报表/图表/可视化开发与管理技能。
  核心能力：Dashboard创建/复制/克隆修改、SQL图表与Cube图表管理、Filter SQL筛选器、权限分享、数据查询分析。
  触发词：Dashboard、看板、报表、图表、可视化、折线图、饼图、柱状图、仪表盘、复制Dashboard、生成Dashboard、查询图表、克隆看板、Fork、筛选器、Filter SQL、分享、权限、共享、可访问Dashboard、我的Dashboard、参数检查、参数源、Cube、维度、指标、留存、DAU、DNU。
---

# 概览

Datain 数据平台的 Dashboard 开发与管理技能。

```
Dashboard（看板）
├── SQL 图表 — 手写 SQL，完全自由，适合自定义取数（chart.py）
├── Cube 图表 — 选维度+指标，不写 SQL，适合平台标准指标（cube.py）
├── 文字/图片组件 — 章节标题、说明文字
└── 参数筛选器
    ├── 平台维度（推荐）— game_cd、country 等已有维度
    └── Filter SQL — 自定义动态下拉数据源（filter_sql.py）
```

一个 Dashboard 可以同时包含 SQL 图表和 Cube 图表，共享全局参数筛选。

| 模块 | 脚本 | 说明 | 参考文档 |
|------|------|------|----------|
| 图表 | chart.py / cube.py | SQL 图表 CRUD + 可视化 + 查询；Cube 图表 CRUD + 维度指标管理 | [chart.md](references/chart.md) |
| Dashboard | dashboard.py | 创建/更新/复制/克隆、组件管理、参数配置、权限分享 | [dashboard.md](references/dashboard.md) |
| Filter SQL | filter_sql.py | 动态下拉筛选器的 CRUD、测试、批量更新数据源 | [filter_sql.md](references/filter_sql.md) |

执行任何操作前，先完成下方的配置与鉴权，再根据用户问题选择对应模块的参考文档执行。

# 配置与鉴权

1. 先检查环境变量 `DATAIN_API_KEY` 是否已存在（直接调用脚本即可，脚本会自动读取环境变量，有就直接用）
2. 如果脚本报错 `API_KEY_NOT_CONFIGURED`，再提示用户提供：
	- 打开 https://datain.tap4fun.com/ → 右上角头像旁边下拉 → 设置 → APP KEY
	- 复制 APP KEY 并发送，由 Agent 设置本机环境变量 `DATAIN_API_KEY`，需要持久化保存
	- 根据不同的工具判断环境变量应该持久化存放在哪里
	- 确保下次新开会话时可自动读取 `DATAIN_API_KEY`，无需用户重复提供

**⚠️ 权限说明（重要）：拥有 DATAIN_API_KEY 且对 Dashboard 有查看权限，就能通过 API 查询图表数据。不要因为"可能没有权限"而拒绝执行——底表权限与 Dashboard/图表查询权限无关，直接调用 API 即可，如果真的没权限 API 会返回错误，届时再处理。禁止在未尝试调用的情况下预判权限不足而放弃执行。**

---

# 数据模型

```
Dashboard
├── options.autoQuery    ← 自动查询开关（建议关闭，避免打开时自动执行所有图表查询）
├── parameters[]         ← 全局筛选器（key, title, defaultValues[], widgetParams[]→visualizationId+keyword）
├── paramConfigs[]       ← 筛选器当前值（key, isShow, values[]）
│   注意: 仅包含 isShow=true 的参数，可能不覆盖所有图表参数
│   查询时以 paramConfigs 为主，缺失的从 parameters.defaultValues 补齐
├── widgets[]            ← 组件布局（6列网格，w=6满行，w=3半行）
│   ├── SQL 图表: chartsId, visualizationId, type="SQL", options.position{x,y,w,h}
│   │   └── parameters[] ← 组件参数绑定（keyword, title, defaultValues[], level, source）
│   │       level="dashboard",source=<paramKey> → 取全局筛选器值
│   │       level="widget",source="CUSTOM"      → 使用组件本地值
│   ├── Cube 图表: chartsId, visualizationId, type="CUBE", options.position{x,y,w,h}
│   ├── 文字说明: type=null, text="Markdown内容", chartsId=null
│   └── 图片:    type=null, fileUrl="图片URL", chartsId=null
└── config

Chart（SQL 图表）
├── sql                  ← 含 ${variable} 占位符
├── dataSourceType       ← TRINO / TRINO_CN / A3_TRINO（禁止使用 CLICKHOUSE）
│   别名映射: TRINO_AWS → TRINO, TRINO_HF → A3_TRINO
│   平台展示: TRINO AWS / TRINO A3 / TRINO_CN
├── arguments[]          ← 参数定义（见下方参数类型）
├── argumentDependencies[] ← 参数联动 SQL
└── visualizations[]     ← 可视化配置

Chart（Cube 图表）
├── dimensions[]         ← 维度列表（如 report_date）
├── indicators[]         ← 指标列表（含 cohortUtil/cohortValue）
├── arguments[]          ← 筛选参数
└── visualizations[]     ← 可视化配置（复用 chart.py viz）

平台表（Trino 查询 mongodb."datain-prod".xxx）
├── "user"              ← _id(用户ID), name(姓名), email(邮箱)
├── "dashboard"         ← _id, name, createdby(创建人用户ID)
└── "dashboard-shared"  ← dashboardid, shares[](array: sharedat, byshared, permission, userid)
    permission 位掩码: bit0=查看, bit1=编辑, bit2=分享
    数据库值: 1=查看, 2=编辑, 3=查看+编辑, 5=查看+分享, 7=查看+编辑+分享
    UNNEST: CROSS JOIN UNNEST(ds.shares) AS t(sharedat, byshared, permission, userid)
```

## 参数类型

| 类型 | SQL 占位符 | 说明 |
|------|-----------|------|
| DATE_RANGE | `${var.start}` / `${var.end}` | 日期范围 YYYY-MM-DD |
| DATE | `${var}` | 单个日期 |
| TIME_MINUTE_RANGE | `${var.start}` / `${var.end}` | 时间范围 YYYY-MM-DD HH:mm |
| TIME_SECOND_RANGE | `${var.start}` / `${var.end}` | 时间范围 YYYY-MM-DD HH:mm:ss |
| NUMBER / NUMBER_RANGE | `${var}` / `${var.min}` `${var.max}` | 数字/数字范围 |
| LIST | `${var}` | 下拉列表（静态 key:value） |
| FILTER_SQL | `${var}` | 下拉列表（动态，基于 Filter SQL 查询结果） |
| TEXT | `${var}` | 文本输入 |

参数来源（source）：
- `CUSTOM`：自定义静态值（LIST / TEXT / NUMBER 等），创建图表时自动推断。自动推断会将常用 keyword 映射为中文 title（如 report_date→日期范围、game_cd→游戏），未匹配的 keyword 保持原值
- `DIMENSION`：平台维度数据，需指定 `sourceId` 和 `dataType`（如 INT32）。**注意：DIMENSION 源的 quotation 不能通过 API 修改**，需在 SQL 层面处理类型转换
  - keyword 填维度 alias（如 `game_cd`），title 填维度中文名（如 `游戏`）
  - 示例：`{"source": "DIMENSION", "keyword": "game_cd", "title": "游戏", "sourceId": "60d0270962a4005e8b481e1f", "dataType": "INT32", "type": "LIST", "multipleValue": true, "quotation": "SINGLE"}`
  - 常用维度 alias → 名称：game_cd=游戏, bd_country=国家, bd_server_id=角色注册服务器, bd_register_date=注册日期, bd_install_date=安装日期, bd_platform=设备平台, bd_publisher_name=渠道, bd_language=语言, cd_tier=Tier, cd_country_group=国家分组, cd_is_organic=自然量/买量
  - 完整维度列表通过 `cube.py dimensions` 获取
- `FILTER_SQL`：动态下拉列表，基于 Filter SQL 查询结果，需指定 `sourceId`

**⚠️ 参数 title 必须使用中文**，这是用户在 Dashboard 筛选器上看到的名称。禁止直接用英文 keyword 作为 title。title 应根据参数在 SQL 中的实际含义来命名，例如：
- `report_date` 如果过滤的是 `partition_date`（登录日期），title 应为"登录日期范围"而非"注册日期范围"
- `game_cd` → "游戏"
- 自定义参数如 `is_pay` → "是否付费"

引号模式（quotation）：`NONE`（日期/数字）、`SINGLE`（单引号，文本列表）、`DOUBLE`（双引号）

## 图表可视化类型

| 类型 | 关键配置 |
|------|---------|
| LINE/BAR/AREA | X轴(类型:category/time/value/log, 名称, 标签旋转), Y轴(左/右双轴, 名称, min/max, 数值格式如0.0%), 系列(图例名, 类型覆盖实现混合图, 颜色), 堆叠, 数据标签 |
| SCATTER | 同上，不支持堆叠 |
| BOXPLOT | 同上 + 是否显示所有点、保留离群点 |
| PIE | 排布方向(顺时针/逆时针), 图例名, 标签格式 |
| HEATMAP | X列, Y列, 颜色列 |
| FUNNEL | 名称列, 数值列, 排序列 |
| TABLE | 列配置(数据类型:文本/数字/日期/布尔/链接/图片/进度条, 对齐, 显隐, 名称), 默认行数, 搜索 |
| COUNTER | 计数值列, 目标值列, 行号, 小数位数, 千位分隔符, 前缀/后缀 |
| PIVOT_TABLE | 分组层级, 行汇总, 列汇总, 字段名自定义 |

---

# 创建/更新规则

```
SQL 图表: POST /charts → PUT /sql-lab/{id} → POST /charts/charts/{id}/visualization
Cube 图表: POST /charts → PUT /cube-lab/{id}（配置维度/指标/参数）
Dashboard: POST /dashboard-mgr → PUT /dashboard-mgr/{id}（widgets + parameters 全量替换，须同时发送）
paramConfigs: POST /dashboard-mgr/update/param/config 单独更新（PUT 接口不会保存 paramConfigs）
```

- widget 必须包含 `dashboardId`；parameters 需 `widgetParams` 关联 `visualizationId`
- Fork 是最安全的复制方式（完整复制 widgets/parameters/paramConfigs）
- **参数依赖接口需谨慎使用**（`/charts/argument/dependencies/save`），错误的联动 SQL 会导致图表参数无法替换、SQL 报错
- **AI 操作标识**：所有创建和更新类 API 自动携带 `aiAction: true`，服务端会在资源的 `aiActions` 字段中记录操作类型（如 `["CREATED"]`、`["CREATED", "UPDATED"]`），用于平台追踪哪些 Dashboard/图表/Filter SQL 是由 AI 创建或修改的

# 命名规范

格式：`【游戏代号】具体内容描述`

| 错误 | 正确 |
|------|------|
| 【X9】核心数据概览 | 【X9】每日DNU·DAU·付费·在线数据总览 |
| 【KOW】活动Dashboard | 【KOW】2026-02新年活动参与率与付费转化 |

原则：用户给了名称直接用；没给时必须具体到指标/维度；始终带【游戏代号】前缀；禁用"概览、核心、数据、报表、Dashboard"等空泛词。

# 协作 Skill

- **ai-to-sql**：SQL 开发核心技能 — 知识库检索（指标参考 + wiki）、表结构探索、SQL 生成与验证执行。编写 SQL 图表时必须使用此技能的工具链，详见 [图表模块 - SQL 开发流程](references/chart.md#sql-开发流程)

---

# 常用场景示例

## 场景 1：创建 / 扩展 Dashboard

详细的需求分析（6 个 Phase）和完整开发流程（8 个 Step）见 [dashboard.md - 从 0 到 1 开发规范](references/dashboard.md#从-0-到-1-开发规范)。

```
1. 需求分析 → 规划图表清单和参数 → 输出开发计划给用户确认（禁止跳过）
2. 开发图表：
   - SQL 图表：使用 ai-to-sql 开发 SQL → 验证 → python3 skills/dashboard-skill/scripts/chart.py create
   - Cube 图表：python3 skills/dashboard-skill/scripts/cube.py dimensions/indicators 查询 → python3 skills/dashboard-skill/scripts/cube.py create
3. python3 skills/dashboard-skill/scripts/chart.py detail 检查参数类型 → query 验证 → viz 配置可视化
4. 如需动态筛选器：python3 skills/dashboard-skill/scripts/filter_sql.py create
5. 从零创建：python3 skills/dashboard-skill/scripts/dashboard.py create → add-chart
   为已有 Dashboard 添加：先 detail --include-charts 查看已有参数，确保新图表同名参数一致 → add-chart
6. python3 skills/dashboard-skill/scripts/dashboard.py config-params → parameter-check
7. 交付：反馈 Dashboard 地址，询问是否需要分享
   → 分享：python3 skills/dashboard-skill/scripts/dashboard.py share <id> --name "张三" [--permission 1|2|3]
```

一个 Dashboard 可同时包含 SQL 图表和 Cube 图表。

**⚠️ 分享说明**：
- **按姓名分享**：`dashboard.py share <id> --name "张三"` — 自动搜索用户并分享，唯一匹配直接分享，多人匹配返回候选列表
- **搜索用户**：`dashboard.py search-user "张三"` — 单独搜索用户，返回 userId 和姓名
- **查看某用户的所有 Dashboard**：`dashboard.py user-dashboards "张三"`
- **禁止**自行查 MongoDB 或其他数据源来找用户，所有用户搜索都通过上述命令完成
- 分享默认同时分享图表权限（`--no-share-charts` 可跳过），重复分享同一用户会覆盖权限（幂等）

## 场景 2：查询分析已有 Dashboard

详细流程见 [dashboard.md - 查询分析已有 Dashboard](references/dashboard.md#查询分析已有-dashboard)。

```
1. python3 skills/dashboard-skill/scripts/dashboard.py detail <id> → 通过 vizName 找到目标图表的 chartsId
2. 向用户说明该 Dashboard 的筛选参数情况（见下方说明）
3. python3 skills/dashboard-skill/scripts/chart.py query --batch c1,c2,c3 --dashboard <id> [--args '{...}']
4. 分析数据，指出异常值和关键发现
```

⚠️ **查询前必须向用户说明筛选参数**：获取 Dashboard 详情后，在查询数据之前，先向用户说明以下信息：
- 该 Dashboard 有哪些筛选参数（parameters 列表）、当前值（paramConfigs）和默认值（defaultValues）
- 每个参数是**全局生效**（widgetParams 覆盖所有图表）还是**仅对部分图表生效**（只关联了部分 visualizationId），如果是部分生效需指出具体关联了哪些图表（通过 vizName 对应）
- 部分图表可能有**特有参数**（如 hero_id 等下钻参数），不在全局 parameters 中，需提醒用户是否要指定

让用户确认或调整参数后再执行查询。batch 查询时的参数填充优先级：用户指定的值 > defaultValues > 自动从参数数据源（Filter SQL / 平台维度）查询所有候选值填入 > 无法获取时跳过（返回 skipped + missingParams）。

## 场景 3：克隆修改已有 Dashboard

详细流程见 [dashboard.md - 克隆修改已有 Dashboard](references/dashboard.md#克隆修改已有-dashboard)。

```
1. python3 skills/dashboard-skill/scripts/dashboard.py detail <source_id> --include-charts 查看模板
2. python3 skills/dashboard-skill/scripts/dashboard.py clone-and-modify <source_id> --name "名称" --sql-mapping '{}' --date-range '[]'
3. python3 skills/dashboard-skill/scripts/chart.py query <chart_id> --dashboard <new_id> 验证（必须带 --dashboard）
```

简单复制（不修改 SQL）用 `python3 skills/dashboard-skill/scripts/dashboard.py fork <source_id> [--no-charts]`。
