# Filter SQL 筛选器模块

Filter SQL 为图表参数提供动态下拉列表数据源。当平台已有维度（如 game_cd、bd_country）无法满足需求时，通过自定义 SQL 查询生成下拉选项。

**优先使用平台维度**，仅在无现成维度时创建 Filter SQL。

## 格式要求

- 必须返回两列：`name`（下拉列表显示值）和 `value`（传入后台的实际值）
- 通常添加 ALL 选项：`SELECT 'ALL' as name, 'ALL' as value UNION ALL SELECT ...`

---

## 命令

### 列表

```bash
python3 skills/dashboard-skill/scripts/filter_sql.py list [--name "关键词"]
```

### 详情

```bash
python3 skills/dashboard-skill/scripts/filter_sql.py get <id>
```

### 创建

```bash
python3 skills/dashboard-skill/scripts/filter_sql.py create --name "服务器筛选" --sql "SELECT server_name as name, server_id as value FROM ..." [--datasource TRINO_AWS] [--db hive]
```

### 更新

```bash
python3 skills/dashboard-skill/scripts/filter_sql.py update <id> [--name "名称"] [--sql "SQL"] [--datasource TRINO_AWS] [--db hive]
```

### 执行

```bash
python3 skills/dashboard-skill/scripts/filter_sql.py execute <id>
```

执行已保存的 Filter SQL，返回下拉列表数据。

### 测试

```bash
python3 skills/dashboard-skill/scripts/filter_sql.py test --sql "SELECT 'ALL' as name, 'ALL' as value" [--datasource TRINO_AWS]
```

保存前测试 SQL 是否正确，不创建记录，仅执行验证。

### 批量更新数据源

```bash
python3 skills/dashboard-skill/scripts/filter_sql.py batch-update-ds <id1> <id2> --datasource A3_TRINO
```

数据源别名映射：TRINO_AWS → TRINO, TRINO_HF → A3_TRINO。

### AI 操作标识

Filter SQL 的创建和更新操作自动携带 `aiAction: true`，涉及的 API：
- `POST /filter-sql`（创建）→ aiActions 记录 `CREATED`
- `PUT /filter-sql/{id}`（更新）→ aiActions 追加 `UPDATED`

平台通过资源的 `aiActions` 字段追踪哪些 Filter SQL 是由 AI 创建或修改的。
