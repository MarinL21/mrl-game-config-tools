# 图表模块

图表是 Dashboard 的核心数据组件。分为两种类型：

| 类型 | 脚本 | 数据来源 | 开发方式 | 适用场景 |
|------|------|---------|---------|---------|
| SQL 图表 | chart.py | Trino/Doris 任意表 | 手写 SQL | 自定义取数、明细日志、非标准指标 |
| Cube 图表 | cube.py | 平台 ClickHouse 聚合宽表 | 选维度 + 选指标 | 标准运营指标（DNU/DAU/留存/付费/Cohort） |

两种图表都可以添加到同一个 Dashboard 中，共享全局参数筛选。

---

## SQL 图表（chart.py）

### 创建

```bash
python3 skills/dashboard-skill/scripts/chart.py create --name "【X1】每日DAU趋势" --sql "SELECT ..." --datasource TRINO_AWS [--tags "X1"] [--sql-file path] [--description "描述"] [--catalog hive]
```

⚠️ 创建后必须执行两项检查：

1. **参数类型校验**：`skills/dashboard-skill/scripts/chart.py create` 会自动推断参数，但所有参数都归为 CUSTOM 源。对 DIMENSION 类参数（如 game_cd）是错的（CUSTOM 默认加单引号，integer 列会类型不匹配）。
   - 创建后用 `skills/dashboard-skill/scripts/chart.py detail <chart_id>` 检查 arguments
   - 如果是往已有 Dashboard 添加图表，先查看已有图表的 arguments，确保同名参数的 source/quotation/dataType 一致
   - game_cd 等维度参数必须用 DIMENSION 源，不能用 CUSTOM
   - 参数类型不对时，用 `skills/dashboard-skill/scripts/chart.py update <chart_id> --arguments 'JSON'` 修正

2. **查询验证**：
   ```bash
   python3 skills/dashboard-skill/scripts/chart.py query <chart_id> --args '{"report_date":["2026-03-18","2026-03-25"]}'
   # 如果图表属于某个 Dashboard，必须带 --dashboard
   python3 skills/dashboard-skill/scripts/chart.py query <chart_id> --dashboard <id> --args '{...}'
   ```
   图表必须查询成功且返回数据才能进入下一步。

### 更新

```bash
python3 skills/dashboard-skill/scripts/chart.py update <chart_id> [--name "名称"] [--sql "SQL"] [--sql-file path] [--datasource TRINO_AWS] [--catalog hive] [--tags "标签"] [--arguments 'JSON数组']
```

⚠️ 更新 SQL 必须通过 `skills/dashboard-skill/scripts/chart.py update` 命令，不要直接调用 `PUT /sql-lab/{id}` — 直接调 API 不传 `arguments` 字段会清空已有参数，`skills/dashboard-skill/scripts/chart.py update` 会自动推断并保留参数。

### 详情

```bash
python3 skills/dashboard-skill/scripts/chart.py detail <chart_id> [--from-dashboard <dashboard_id>]
```

### 查询

```bash
# 单图表查询
python3 skills/dashboard-skill/scripts/chart.py query <chart_id> [--args '{"key":["v1","v2"]}'] [--async] [--no-cache] [--max-rows 500]

# Dashboard 下查询（推荐，走 dashboard-query 路径）
python3 skills/dashboard-skill/scripts/chart.py query <chart_id> --dashboard <id> [--args '{"key":["v1"]}']

# 批量查询（传 --dashboard 时不传 --args 会自动从 paramConfigs + defaultValues 构建参数）
# 缺失参数会自动从数据源（Filter SQL / 平台维度）查询所有候选值填入，无法获取时才跳过
python3 skills/dashboard-skill/scripts/chart.py query --batch c1,c2,c3 --dashboard d1 [--args '{"param1":["v1"]}']

# 临时覆盖数据源执行（不修改图表配置）
python3 skills/dashboard-skill/scripts/chart.py query <chart_id> --datasource TRINO_AWS --args '{...}'
```

⚠️ 查询已属于 Dashboard 的图表时，必须带 `--dashboard <id>`。不带 --dashboard 走直接查询路径，需要用户自己有底层 catalog 的访问权限，即使对 Dashboard 有查看权限也会报 Access Denied。

### 可视化配置

```bash
python3 skills/dashboard-skill/scripts/chart.py viz <chart_id> --type LINE --name "图表标题" --x-axis col1 --y-axis "col2,col3" [--group col] [--dashboard <id>]
```

轴配置：
```
[--x-axis-type category|time|value|log] [--x-axis-name "名称"] [--x-axis-rotation -45]
[--y-axis-name "名称"] [--y-axis-min 0] [--y-axis-max 100] [--y-axis-format "0.0%"]
```

双Y轴：
```
[--y-axis-right "col4,col5"] [--y-axis-right-name "比率"]
```

系列与样式：
```
[--series-type "col3:line,col4:bar"]  # 混合图
[--stacked] [--show-label]
```

专用配置：
```
# Counter
[--count-column col] [--target-column col] [--decimal-places 2] [--prefix "DAU: "] [--suffix " 人"]
# Heatmap
[--x-column col] [--y-column col] [--color-column col]
# Funnel
[--name-column col] [--value-column col]
# Pivot Table
[--show-totals]
```

高级 JSON 透传（覆盖以上所有选项）：
```
[--options-json '{"type":"line","xAxis":"date","yAxises":["dau"],"yAxisOption":{"left":{"name":"DAU"}}}']
```

标签格式模板：`{{@@name}}`系列名, `{{@@x}}`横轴值, `{{@@y}}`纵轴值, `{{@@yPercent}}`百分比, `{{@@column_name}}`任意列

### 复制

```bash
python3 skills/dashboard-skill/scripts/chart.py fork <chart_id> [--type SQL|CUBE]
```

### 取消查询

```bash
python3 skills/dashboard-skill/scripts/chart.py cancel <task_id>
```

### 批量详情

```bash
python3 skills/dashboard-skill/scripts/chart.py batch-detail <chart_id1> <chart_id2> [--from-dashboard <id>]
```

### 批量更新数据源

```bash
python3 skills/dashboard-skill/scripts/chart.py batch-update-ds <chart_id1> <chart_id2> --datasource A3_TRINO
```

数据源别名映射：TRINO_AWS → TRINO, TRINO_HF → A3_TRINO。平台展示名：TRINO AWS / TRINO A3 / TRINO_CN。

### 参数依赖（参数联动）

⚠️ 需谨慎使用，错误的联动 SQL 会导致图表参数无法替换、SQL 报错。使用前务必先通过 `arg-dep-values` 验证 SQL 正确性。

```bash
# 保存参数依赖
python3 skills/dashboard-skill/scripts/chart.py arg-dep-save <chart_id> --keywords "server_id" --sql "SELECT DISTINCT server_id as name, server_id as value FROM ... WHERE game_cd = '\${game_cd}'"

# 验证联动 SQL
python3 skills/dashboard-skill/scripts/chart.py arg-dep-values <chart_id> --sql "SELECT ..." [--datasource TRINO_AWS]

# 删除参数依赖
python3 skills/dashboard-skill/scripts/chart.py arg-dep-delete <chart_id> --keywords "server_id"
```

---

## Cube 图表（cube.py）

Cube 图表不写 SQL，通过选择平台维度和指标来定义查询，平台自动生成查询逻辑。适用于标准化的运营/市场数据分析。

### 元数据查询

```bash
# 查询可用维度
python3 skills/dashboard-skill/scripts/cube.py dimensions [--filter "游戏"] [--dashboard <id>]

# 查询可用指标
python3 skills/dashboard-skill/scripts/cube.py indicators [--filter "DAU"] [--dashboard <id>]

# 查询维度可选值
python3 skills/dashboard-skill/scripts/cube.py dim-values --alias game_cd [--dashboard <id>]
python3 skills/dashboard-skill/scripts/cube.py dim-values --id 60d0270962a4005e8b481e1f

# 获取图表所需维度与指标
python3 skills/dashboard-skill/scripts/cube.py need-data <chart_id> [--dashboard <id>]
```

### 创建

```bash
python3 skills/dashboard-skill/scripts/cube.py create --name "【X1】留存率趋势" --dimensions "dim_id1,dim_id2" --indicators '[{"id":"指标ID"}]' [--tags "X1"]
```

### 详情

```bash
python3 skills/dashboard-skill/scripts/cube.py detail <chart_id> [--from-dashboard <id>]
```

### 查询

```bash
python3 skills/dashboard-skill/scripts/cube.py query <chart_id> [--dashboard <id>] [--args '{"game_cd":["1047"]}'] [--no-cache] [--max-rows 500]
```

### 更新配置

```bash
python3 skills/dashboard-skill/scripts/cube.py update <chart_id> [--dimensions "dim1,dim2"] [--arguments 'JSON数组'] [--wheres 'JSON数组'] [--full-day-limit 30]
```

⚠️ **不要通过 update 传 indicators**：cube-lab PUT 会清空指标的 id 字段导致查询只返回 bi_default。如需添加筛选条件，只传 arguments。

### 扩展配置

```bash
python3 skills/dashboard-skill/scripts/cube.py config <chart_id> --full-day-limit 30
```

### 派生列

```bash
python3 skills/dashboard-skill/scripts/cube.py derived-columns <chart_id> --ids "d1,d2"
```

### Cube 注意事项

- **disableGroupBy=true** 的维度不能放在 dimensions 参数中，只能用于 dimensionFilters 过滤
- **维度有 games 限制**时，该维度只能用于指定游戏
- **Cohort 指标**（cohort=true）需要指定 cohortUtil（DAY/WEEK/MONTH）和 cohortValue（1,2,3,7,14,30,60,90）

### AI 操作标识

所有图表创建和更新类操作自动携带 `aiAction: true`，涉及的 API：
- `POST /charts`（创建图表）→ aiActions 记录 `CREATED`
- `PUT /sql-lab/{id}`（保存/更新 SQL）→ aiActions 追加 `UPDATED`
- `PUT /charts/{id}`（更新图表元数据）→ aiActions 追加 `UPDATED`
- `POST /charts/{id}/visualizations`（创建可视化）→ aiActions 追加操作记录
- `PUT /charts/visualization/{vizId}`（更新可视化）→ aiActions 追加操作记录
- `PUT /cube-lab/{id}`（更新 Cube 配置）→ aiActions 追加 `UPDATED`

平台通过资源的 `aiActions` 字段（如 `["CREATED"]`、`["CREATED", "UPDATED"]`）追踪哪些图表是由 AI 创建或修改的。

---

## SQL 开发流程

编写 SQL 图表时，使用 ai-to-sql 技能的工具链。**禁止跳过检索直接写 SQL**。

```
Step 1: 获取游戏权限（每次会话仅需一次）
    python3 skills/ai-to-sql/scripts/get_game_info.py
    → 获取 full_access / game_cds / datasource / tables
    ↓
Step 2: 检索知识库（必须执行）
    python3 skills/ai-to-sql/scripts/rag_search.py --query "关键词" --game_cd 游戏编码 --source metrics
    → 优先基于参考 SQL 改写
    ↓
Step 3: 探索表结构
    python3 skills/ai-to-sql/scripts/explore_tables.py --tables "表名1,表名2" --datasource TRINO_AWS|TRINO_HF
    ↓
Step 4: 生成 SQL 并验证
    python3 skills/ai-to-sql/scripts/query_trino.py --sql "SELECT ..." --datasource TRINO_AWS|TRINO_HF --limit 100
    → SQL 必须执行不报错才能进入下一步
    ↓
Step 5: 创建图表 → 查询验证 → 配置可视化
    python3 skills/dashboard-skill/scripts/chart.py create --name "图表名" --sql "验证通过的SQL" --datasource TRINO_AWS
    python3 skills/dashboard-skill/scripts/chart.py query <chart_id> --args '{...}'
    python3 skills/dashboard-skill/scripts/chart.py viz <chart_id> --type LINE --name "标题" --x-axis col1 --y-axis "col2"
```

### SQL 开发规范

1. 必须先检索指标参考，优先基于参考 SQL 改写
2. 所有表必须加别名（小写），SQL 结尾不加分号
3. 有分区字段的表必须加分区过滤（ods/dl: `partition_date`，stg: `create_date`）
4. 用户未指定日期时，默认查询近 7 天
5. `full_access=false` 时，tables 已转换为视图格式 `{catalog}.v{game_cd}.{layer}_{table}`，将 `{game_cd}` 替换为实际编码，无需 `WHERE game_cd = xxx`
6. `full_access=true` 时直接查原表，需加 `WHERE game_cd = xxx`
7. TRINO_HF 环境下 stg 层表需加 `hive.` 前缀
8. 字段别名含中文用双引号，浮点除法用 `1.00 * 被除数 / 除数`
9. 日期参数使用 `${变量名.start}` / `${变量名.end}` 占位符
10. 更新 SQL 必须通过 `skills/dashboard-skill/scripts/chart.py update`，不要直接调 `PUT /sql-lab/{id}`

### 完整示例：KOW DAU 趋势图

```bash
# 1) 获取权限
python3 skills/ai-to-sql/scripts/get_game_info.py

# 2) 检索参考 SQL
python3 skills/ai-to-sql/scripts/rag_search.py --query "DAU 活跃用户 趋势" --game_cd 1038 --source metrics

# 3) 探索表结构
python3 skills/ai-to-sql/scripts/explore_tables.py --tables "ods.user_login" --datasource TRINO_AWS

# 4) 验证 SQL（固定日期）
python3 skills/ai-to-sql/scripts/query_trino.py --datasource TRINO_AWS --sql "
SELECT partition_date as report_date,
       count(distinct open_udid) as dau
FROM ods.user_login a
WHERE a.game_cd = 1038
  AND a.partition_date BETWEEN '2026-03-13' AND '2026-03-20'
GROUP BY partition_date
ORDER BY partition_date
" --limit 100

# 5) 创建图表（固定日期替换为占位符）
python3 skills/dashboard-skill/scripts/chart.py create \
  --name "【KOW】每日DAU趋势" \
  --sql "SELECT partition_date as report_date, count(distinct open_udid) as dau FROM ods.user_login a WHERE a.game_cd = 1038 AND a.partition_date BETWEEN '\${report_date.start}' AND '\${report_date.end}' GROUP BY partition_date ORDER BY partition_date" \
  --datasource TRINO_AWS --tags "KOW"

# 6) 查询验证
python3 skills/dashboard-skill/scripts/chart.py query <chart_id> --args '{"report_date":["2026-03-13","2026-03-20"]}'

# 7) 配置可视化
python3 skills/dashboard-skill/scripts/chart.py viz <chart_id> --type LINE \
  --name "【KOW】每日DAU趋势" --x-axis report_date --y-axis dau \
  --x-axis-type time --x-axis-name "日期" --y-axis-name "DAU"
```
