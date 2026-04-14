# 查询发行素材

## 执行流程

1. 根据问题, 确定 时间范围、游戏编码列表
	- 如果无法确定指定的 游戏编码, 提示用户选择指定的游戏(多选)
2. 获取参数列表, 确定与问题相关的 维度、指标, 构造查询数据的参数
	- 如果已确定, 可跳过该步骤
	- 无法确定使用哪一个时, 需要列出可选项供用户筛选(多选)
3. 查询发行素材数据, 展示返回的查询结果, 同时结合问题得出分析结论

## 规则说明

### 时间范围

- 涉及 近 1 个月、截至今天、至今 等时间计算时，一律以当前北京时间（Asia/Shanghai）为准
- 没有指定时间范围时, 默认取最近7天

### 特殊时间维度

- 特殊时间维度 不能出现在 dimensionFilters 参数中
- 特殊时间维度 不能同时出现在 dimensions 参数中
- 如果 dimensions 参数中包含 特殊时间维度, 需要适当调整 startAt 和 endAt 的取值范围
	- 示例: 2026年1月 对应 2026-01-01 ~ 2026-01-31
	- 按照 周 进行对比, 应该是 --startAt 2025-12-29 --endAt 2026-02-01
	- 按照 年 进行对比, 应该是 --startAt 2026-01-01 --endAt 2026-12-31

| 维度名 | 维度ID | 时间范围 |
|---|---|---|
| 日 | `report_date` | 当天 |
| 周 | `report_week`| 周一 到 周末 |
| 月 | `report_month` | 月初 到 月底 |

### 过滤操作符(operator)

**dimensionFilters 字段说明**（维度筛选条件）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| field | string | 是 | 维度ID |
| operator | string | 是 | 操作符，支持：`in`（包含）、`!in`（不包含）、`contains`（模糊匹配）、`!contains`（模糊排除）、`between`（范围）、`eq`（等于）、`gt`（大于）、`lt`（小于） |
| value | array\<string\> | 是 | 条件值列表。`in`/`!in` 传多个值；`contains`/`!contains`/`eq`/`gt`/`lt` 传单个值；`between` 传两个值（起止） |
| type | int | 否 | 字段数据类型：`1` 表示数值，`2` 表示字符串（默认 `2`） |

**indicatorFilters 字段说明**（指标筛选条件）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| field | string | 是 | 指标ID |
| operator | string | 是 | 操作符，支持：`eq`（等于）、`gt`（大于）、`lt`（小于） |
| value | array\<string\> | 是 | 条件值，传单个数值字符串，如 `["100"]` |

## 命令说明

### 获取参数列表

1、列表中包含所有属性, 用于构造查询数据的参数

```bash
python3 skills/datain-skill/scripts/query_material.py -c get_params --funcs dimensions
```

| 可选参数 |格式 |说明 |
|------|------|------|
| `--funcs` | "参数类型1,参数类型2" | 默认全选; 参数类型可选: dimensions,indicators  |

返回格式如下
```json
{
	"dimensions": [ {"key": "维度ID", "name": "维度名", "provider":1} ],  "indicators": [ {"key": "指标ID", "name": "指标名"} ]
}
```

- 用于 dimensions 和 dimensionFilters 参数
	- dimensions 列表中的 id 和 name
	- provider不为空, 可获取维度的可选列表
- 用于 indicators 和 indicatorFilters 参数
	- indicators 列表中的 key 和 name

2、指定维度的可选列表

- 针对出现在 dimensions 参数或 dimensionFilters 参数, 且 provider 属性不为空的维度

```bash
python3 skills/datain-skill/scripts/query_material.py -c dimension_keys -g 游戏编码1,游戏编码2 -i '维度ID_1,维度ID_2'
```

返回格式如下
```json
{ "维度ID": ["实际值"], "维度ID####游戏编码": ["实际值:展示值"]}
``` 

- 实际值 用于 dimensionFilters 的 过滤值; 如果存在展示值, 在展示结果时, 需要将实际值转化成展示值
- `维度ID####游戏编码`: 不同游戏编码的可选列表不一样; `维度ID`: 所有游戏编码的可选列表都一样

### 查询发行素材

```bash
python3 skills/datain-skill/scripts/query_material.py -c query \
    --startAt '开始日期' --endAt '结束日期' -g 游戏编码1,游戏编码2 
```

| 可选参数 |格式 |说明 |
|------|------|------|
| `--dimensions` | '["维度ID1","维度ID2"]' | 维度对比项列表 |
| `--indicators` | '["指标ID1","指标ID2"]' | 指标列表, 不传默认返回所有指标 |
| `--dimensionFilters` | '[{"field":"维度ID","operator":"过滤操作符","value":["过滤值"]}]' | 维度过滤列表 |
| `--indicatorFilters` | '[{"field":"指标ID","operator":"过滤操作符","value":["过滤值"]}]' | 指标过滤列表 |

返回格式如下
```json
{
  "result": [
    { "sc_material_name": "video_summer_01", "indicator_roas": 10 }
  ],
  "columns": [
    { "key": "sc_material_name", "name": "素材名称" },
    { "key": "indicator_roas", "name": "ROAS" }
  ]
}
```
