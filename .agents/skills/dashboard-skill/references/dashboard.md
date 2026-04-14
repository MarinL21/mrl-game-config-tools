# Dashboard 模块

## 功能介绍

Dashboard 是数据看板的容器，可以包含多个图表（SQL 图表和 Cube 图表混合）、文字说明和图片组件，通过全局参数筛选器联动所有图表。

核心能力：
- **CRUD**：创建、查看详情、更新、复制（fork）、克隆修改（clone-and-modify）
- **组件管理**：添加图表（SQL/Cube 混合）、添加文字说明、配置参数源、参数检查
- **权限分享**：搜索用户、分享（含图表权限）、查看已分享用户、取消分享
- **数据查询**：查询可访问列表、批量查询图表数据

关键概念：
- 一个 Dashboard 可同时包含 SQL 图表和 Cube 图表，共享全局参数筛选
- widgets + parameters 是全量替换，须同时发送完整数据
- paramConfigs 通过单独接口更新，PUT 接口不会保存 paramConfigs
- 布局网格：6 列，w=6 满行，w=3 半行
- autoQuery 建议关闭，避免打开时自动执行所有图表查询

---

## API 操作

### CRUD

#### 创建

```bash
python3 skills/dashboard-skill/scripts/dashboard.py create --name "【X1】每日运营数据总览" [--tags "X1"] [--description "描述"] [--auto-query]
```

默认关闭自动查询（autoQuery=false）。

#### 详情

```bash
# 基础详情（widgets 带 chartName/vizName）
python3 skills/dashboard-skill/scripts/dashboard.py detail <id>

# 含图表 SQL/参数/可视化完整信息
python3 skills/dashboard-skill/scripts/dashboard.py detail <id> --include-charts
```

widgets 中的 vizName 是用户在 Dashboard 上看到的标题，通过 vizName 找到目标图表的 chartsId。

#### 更新

```bash
python3 skills/dashboard-skill/scripts/dashboard.py update <id> [--name "名称"] [--tags "标签"] [--description "描述"]
  [--param-configs 'JSON']     # 更新筛选器当前值
  [--parameters 'JSON']        # Dashboard 级 parameters 全量替换（一般用 config-params 自动配置）
  [--auto-query | --no-auto-query]
```

#### 复制

```bash
# 完整复制（含图表）
python3 skills/dashboard-skill/scripts/dashboard.py fork <source_id>

# 只复制 Dashboard 结构（不含图表）
python3 skills/dashboard-skill/scripts/dashboard.py fork <source_id> --no-charts
```

Fork 是最安全的复制方式，完整复制 widgets/parameters/paramConfigs。

#### 克隆修改

基于已有 Dashboard 模板，克隆后批量替换 SQL 中的字符串、更新日期范围，快速生成新版本。

```bash
python3 skills/dashboard-skill/scripts/dashboard.py clone-and-modify <source_id> \
  --name "【KOW】2026-02新年活动数据" \
  --sql-mapping '{"christmas_event":"newyear_event","2025-12":"2026-02"}' \
  --date-range '["2026-02-01","2026-02-28"]'
```

适用场景："复制 Dashboard"、"基于 xxx 改一个"、"换个日期/游戏重新出一份"。

#### 查询可访问列表

```bash
# 我的 + 分享给我的 Dashboard
python3 skills/dashboard-skill/scripts/dashboard.py accessible [--keyword "关键词"]
```

### 组件管理

#### 添加图表

```bash
python3 skills/dashboard-skill/scripts/dashboard.py add-chart <dashboard_id> chart1 chart2 chart3
```

一个 Dashboard 可同时包含 SQL 图表和 Cube 图表。添加后必须执行 `config-params` 配置参数源。

#### 添加文字

```bash
# 章节标题（默认居中 + 24px 字号）
python3 skills/dashboard-skill/scripts/dashboard.py add-text <dashboard_id> --text "一、核心指标"

# 说明文字（保留原始格式）
python3 skills/dashboard-skill/scripts/dashboard.py add-text <dashboard_id> --text "以下图表展示..." --no-center

# 自定义尺寸
python3 skills/dashboard-skill/scripts/dashboard.py add-text <dashboard_id> --text "标题" [--width 6] [--height 2]
```

#### 配置参数源

```bash
python3 skills/dashboard-skill/scripts/dashboard.py config-params <dashboard_id>
```

⚠️ add-chart 后必须执行。自动完成：读取所有图表参数 → 构建全局参数 + widgetParams 关联 → 初始化 paramConfigs。

如需手动调整参数（如修改 defaultValues、显隐），再用 `update --param-configs 'JSON'`。

#### 参数检查

```bash
python3 skills/dashboard-skill/scripts/dashboard.py parameter-check <dashboard_id>
```

确认 `problematicCount=0`（无缺失参数源的组件）。

⚠️ parameter-check 只检查参数源是否绑定，不检查图表自身 arguments 的 source/quotation/dataType 是否正确。参数类型问题（如 game_cd 用了 CUSTOM 而非 DIMENSION）不会被检出，必须在创建图表时就校验正确。

### 权限分享

#### 搜索用户

```bash
python3 skills/dashboard-skill/scripts/dashboard.py search-user "张三"
```

#### 查询用户 Dashboard

```bash
python3 skills/dashboard-skill/scripts/dashboard.py user-dashboards "张三"  # 查询用户拥有 + 被分享的所有 Dashboard
```

#### 分享

```bash
# 按用户 ID 分享
python3 skills/dashboard-skill/scripts/dashboard.py share <dashboard_id> <uid1> [uid2] [--permission 1|2|3] [--no-share-charts]

# 按姓名自动查找并分享（唯一匹配时直接分享，多人匹配返回候选列表）
python3 skills/dashboard-skill/scripts/dashboard.py share <dashboard_id> --name "张三" [--permission 1]
```

permission 说明：1=查看（默认）, 2=编辑, 3=编辑+分享。

分享 Dashboard 时默认同时分享其下所有图表的对应权限。传 `--no-share-charts` 则只分享 Dashboard 本身，不分享图表（用户能看到 Dashboard 但图表会显示无权限）。

重复分享同一用户会覆盖权限（幂等），无需先取消再重新分享。升级/降级权限直接传新 permission 即可。

#### 查看已分享用户

```bash
python3 skills/dashboard-skill/scripts/dashboard.py shared-users <dashboard_id>
```

#### 取消分享

```bash
python3 skills/dashboard-skill/scripts/dashboard.py cancel-share <dashboard_id> <uid>  # 完全移除权限，不是降级
```

### AI 操作标识

所有 Dashboard 创建和更新类操作自动携带 `aiAction: true`，涉及的 API：
- `POST /dashboard-mgr`（创建 Dashboard）→ aiActions 记录 `CREATED`
- `PUT /dashboard-mgr/{id}`（更新 Dashboard、添加图表、添加文字、配置参数）→ aiActions 追加 `UPDATED`

平台通过资源的 `aiActions` 字段（如 `["CREATED"]`、`["CREATED", "UPDATED"]`）追踪哪些 Dashboard 是由 AI 创建或修改的。

---

## 从 0 到 1 开发规范

### 需求分析与开发计划（每次开发前必须执行）

收到 Dashboard 开发需求后，禁止直接开始开发。必须先完成以下分析，输出开发计划给用户确认：

```
Phase 1: 理解需求
    - 明确要展示什么数据、给谁看、解决什么问题
    - 阅读用户提供的数据源代码/文档/表名，理解数据流和表结构
    - 如果用户提供了 ETL 代码，重点关注最终产出表和关键字段
    ↓
Phase 2: 梳理数据源
    - 确定目标表及其所在数据源（Trino 直查 / Doris 通过 doris.库名.表名 访问）
    - 列出关键字段、数据粒度、分区方式
    - 如需探索表结构，使用 ai-to-sql 的 explore_tables.py
    ↓
Phase 3: 规划图表
    - 列出每个图表：名称、类型（LINE/BAR/TABLE/PIE 等）、数据来源表、关键列
    - 明确哪些是趋势图、哪些是明细表、哪些是汇总统计
    - 判断每个图表适合用 SQL 图表还是 Cube 图表
    ↓
Phase 4: 规划参数与筛选
    - 确定全局参数（日期范围、游戏筛选等）
    - 优先使用平台已有维度（如 game_cd：维度→基础属性→游戏），仅在无现成维度时创建 Filter SQL
    - 游戏筛选规则：
      · 统一使用平台维度，类型为下拉列表
      · 是否允许多选取决于实际数据场景（SQL 中用 IN 则多选，用 = 则单选）
      · 用户明确指定了目标游戏 → 在候选项中只勾选指定的游戏
      · 用户未指定游戏 → 候选项使用"默认为全部"
    - 明确每个参数的类型（DATE_RANGE / LIST / FILTER_SQL 等）和引号模式
    ↓
Phase 5: 输出开发计划（必须包含以下内容）
    - 数据源：表名、数据源类型、关键字段
    - 图表清单：每个图表的名称、类型、SQL 数据来源、关键列
    - 参数清单：参数名、类型、来源（平台维度 or 自建 Filter SQL）
    - Dashboard 名称
    - 执行步骤概要
    ↓
Phase 6: 提出待确认问题
    - 数据源访问方式不确定时提问
    - 业务逻辑有歧义时提问
    - 图表展示方式有多种选择时列出选项
    - 筛选维度是否有现成的平台维度可用
```

用户确认开发计划后，再进入完整开发流程执行。

### 完整开发流程

```
Step 1: 探索数据 → 开发 SQL → 执行验证
    使用 ai-to-sql 技能完成 SQL 开发（详见 chart.md SQL 开发流程）
    SQL 必须执行不报错才能进入下一步
    Cube 图表则通过 skills/dashboard-skill/scripts/cube.py dimensions/indicators 查询可用维度和指标
    ↓
Step 2: 创建图表 → 校验参数 → 查询验证
    SQL 图表：
    python3 skills/dashboard-skill/scripts/chart.py create --name "图表名" --sql "验证通过的SQL" --datasource TRINO_AWS
    Cube 图表：
    python3 skills/dashboard-skill/scripts/cube.py create --name "图表名" --dimensions "dim1,dim2" --indicators '[...]'

    - 设置名称：简明扼要，格式【游戏代号】具体内容
    - 设置 tag：最多 1 个，项目组用游戏编码（如 X1），平台用平台名（如 onehub）

    ⚠️ 参数类型校验（必须，SQL 图表）：
    skills/dashboard-skill/scripts/chart.py create 会自动推断参数，但自动推断把所有参数归为 CUSTOM 源，
    对 DIMENSION 类参数（如 game_cd）是错的（CUSTOM 默认加单引号，integer 列会类型不匹配）。
    创建后立即用 skills/dashboard-skill/scripts/chart.py detail <chart_id> 检查 arguments：
    - 如果是往已有 Dashboard 添加图表：先查看已有图表的 arguments，确保同名参数一致
    - game_cd 等维度参数必须用 DIMENSION 源，不能用 CUSTOM
    - 参数类型不对时，用 skills/dashboard-skill/scripts/chart.py update <chart_id> --arguments 'JSON' 修正

    创建后立即查询验证（必须）：
    python3 skills/dashboard-skill/scripts/chart.py query <chart_id> --args '{"report_date":["2026-03-18","2026-03-25"]}'
    python3 skills/dashboard-skill/scripts/cube.py query <chart_id> --args '{"game_cd":["1047"]}'
    - 如果图表属于某个 Dashboard，查询时必须带 --dashboard <id>（避免 Access Denied）
    - 图表必须查询成功且返回数据才能进入下一步
    - 查询失败则检查 SQL 并用 skills/dashboard-skill/scripts/chart.py update 修复后重新验证
    ↓
Step 3: 配置可视化（必须设置名称和坐标含义）
    python3 skills/dashboard-skill/scripts/chart.py viz <chart_id> --type LINE --name "图表标题" --x-axis col1 --y-axis "col2,col3"
    - 必须设置 --name：图表在 Dashboard 中显示的标题
    - 必须设置 --x-axis-name 和 --y-axis-name：横纵坐标含义
    - 百分比数据用 --y-axis-format "0.0%"（自动将 0.1234 显示为 12.3%）
    - 需要双Y轴时用 --y-axis-right 指定右轴列
    - 混合图（折线+柱状）用 --series-type "col1:line,col2:bar"
    ↓
Step 4: 创建 Filter SQL（仅在平台无现成维度时）
    python3 skills/dashboard-skill/scripts/filter_sql.py create --name "筛选器名" --sql "SELECT name, value FROM ..."
    - 优先使用平台已有维度数据（如 game_cd）
    - 只有当平台维度不满足需求时，才自己创建 Filter SQL
    - 必须返回 name 和 value 两列
    ↓
Step 5: 创建 Dashboard 并添加图表
    python3 skills/dashboard-skill/scripts/dashboard.py create --name "【X1】xxx数据分析"
    python3 skills/dashboard-skill/scripts/dashboard.py add-chart <dashboard_id> chart1 chart2 chart3
    注意：创建时默认关闭自动查询（autoQuery=false）
    一个 Dashboard 可同时添加 SQL 图表和 Cube 图表
    ↓
Step 6: 配置参数源 + 验证（add-chart 后必须执行）
    python3 skills/dashboard-skill/scripts/dashboard.py config-params <dashboard_id>
    - 自动完成：读取所有图表参数 → 构建全局参数 + widgetParams 关联 → 初始化 paramConfigs
    - add-chart 不会自动配置参数源，必须手动执行此命令
    - 如需手动调整参数（如修改 defaultValues、显隐），再用 update --param-configs 'JSON'

    配置后验证 Dashboard 参数是否完整（必须）：
    python3 skills/dashboard-skill/scripts/dashboard.py parameter-check <dashboard_id>
    - 确认 problematicCount=0（无缺失参数源的组件）
    - ⚠️ parameter-check 只检查参数源是否绑定，不检查图表自身 arguments 的
      source/quotation/dataType 是否正确。参数类型问题必须在 Step 2 创建图表时就校验正确
    ↓
Step 7: 分章节与文字说明
    python3 skills/dashboard-skill/scripts/dashboard.py add-text <dashboard_id> --text "一、核心指标"
    python3 skills/dashboard-skill/scripts/dashboard.py add-text <dashboard_id> --text "以下图表展示..." --no-center
    - 默认居中 + 24px 字号（适合章节标题），--no-center 保留原始文本（适合长段说明）
    ↓
Step 8: 交付反馈
    确认无错误后，反馈给用户：
    - Dashboard 名称及访问地址
    - 创建了哪些图表内容
    - 创建或使用了哪些 Filter SQL
    - 询问用户是否需要将此 Dashboard 分享给其他人
```

多图表开发时：Step 1-3 的权限获取、知识库检索、表结构探索只需执行一次，每个图表分别执行 SQL 验证和创建，最后批量 add-chart。

### 查询分析已有 Dashboard

```
Step 1: 获取 Dashboard 详情
    python3 skills/dashboard-skill/scripts/dashboard.py detail <id>
    → widgets 已包含 chartName（图表名）和 vizName（可视化名称，即用户在 Dashboard 上看到的标题）
    → 通过 vizName 找到目标图表的 chartsId
    → 如需查看 SQL/参数定义等完整信息，加 --include-charts
    ↓
Step 2: 向用户说明筛选参数（查询前必须执行，禁止跳过）
    获取详情后、查询数据前，必须先向用户说明该 Dashboard 的筛选参数情况：
    a) 列出所有参数：key、title（用户看到的名称）、类型（DATE_RANGE/LIST 等）
    b) 当前值与默认值：paramConfigs 中的 values（当前值）和 parameters 中的 defaultValues
    c) 参数作用范围：
       - 全局参数：widgetParams 覆盖所有图表（关联了所有 widget 的 visualizationId）
       - 局部参数：只关联了部分图表，需指出具体影响哪些图表（通过 vizName 对应）
    d) 图表特有参数：部分图表可能有不在全局 parameters 中的独有参数
       （如 hero_id、shipID、asset_id 等下钻参数），需提醒用户是否要指定
    → 让用户确认或调整参数后再执行查询
    ↓
Step 3: 确认查询参数
    - 默认使用 paramConfigs 的当前值作为查询参数
    - 如用户指定了筛选条件，覆盖对应参数
    - 检查所有图表参数是否都有值覆盖（paramConfigs 可能不完整，缺失的从 parameters.defaultValues 补齐）
    - ⚠️ 参数填充优先级：用户指定的值 > defaultValues > 自动从参数数据源（Filter SQL / 平台维度）查询所有候选值填入
      → 无法获取时才跳过并返回 skipped + missingParams
      → 自动填充的参数会在返回结果中标注 autoFilled 字段
    ↓
Step 4: 批量查询图表数据
    python3 skills/dashboard-skill/scripts/chart.py query --batch chart1,chart2 --dashboard <id> [--args '{"param1":["v1"]}']
    - 传 --dashboard 时不传 --args 会自动从 paramConfigs + defaultValues 构建参数
    - 如需覆盖特定参数值，通过 --args 显式传入
    - 单图表查询: skills/dashboard-skill/scripts/chart.py query <chart_id> --dashboard <id> --args '{...}'
    ↓
Step 5: 数据分析与汇报
    - 从汇总到明细，多维度拆解
    - 指出异常值和关键发现
    - 给出可操作建议
```

### 克隆修改已有 Dashboard

```
Step 1: 查看模板详情
    python3 skills/dashboard-skill/scripts/dashboard.py detail <source_id> --include-charts
    → 了解模板的图表结构、SQL、参数配置
    ↓
Step 2: 克隆并修改
    python3 skills/dashboard-skill/scripts/dashboard.py clone-and-modify <source_id> \
      --name "【KOW】2026-02新年活动数据" \
      --sql-mapping '{"christmas_event":"newyear_event","2025-12":"2026-02"}' \
      --date-range '["2026-02-01","2026-02-28"]'
    ↓
Step 3: 验证图表查询（必须带 --dashboard，否则可能因 catalog 权限报 Access Denied）
    python3 skills/dashboard-skill/scripts/chart.py query <chart_id> --dashboard <new_dashboard_id> --args '{"report_date":["2026-02-01","2026-02-28"]}'
```

简单复制（不修改 SQL）用 `python3 skills/dashboard-skill/scripts/dashboard.py fork <source_id> [--no-charts]`。
