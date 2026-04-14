# 查询游戏数据

## 执行流程

1. 根据问题, 确定 算法、时间范围、游戏编码列表
	- 如果无法确定指定的 游戏编码, 提示用户选择指定的游戏(多选)
2. 获取参数列表, 确定与问题相关的 维度、指标、标签, 构造查询数据的参数
	- 如果已确定, 可跳过该步骤
	- 无法确定使用哪一个时, 需要列出可选项供用户筛选(多选)
		- 语义相近: 如不存在 花费, 但存在语义相近的 广告费、万盟推广花费
		- 名字相近: 如 维度[国家分组、国家分组2024、国家分组2025]
		- 描述相近: 如 维度[渠道、设备注册服务器]+指标[付费额], 指标[各渠道付费额(服务器)]
3. 查询游戏数据, 展示返回的查询结果, 同时结合问题得出分析结论

## 规则说明

### 算法(algorithmId)

- open_udid: 更偏向 市场 的分析，从展示、点击、安装、注册、留存、收入等发行的各个阶段分析转化、收益情况
- user_id: 更偏向 运营 的分析，分析 cohort成长情况，服务器生态，资产的使用、消耗、存量等，便于运营活动开展

### 时间范围

- 涉及 近 1 个月、截至今天、至今 等时间计算时，一律以当前北京时间（Asia/Shanghai）为准
- 没有指定时间范围时, 默认取最近7天

### 特殊时间维度

| name | id | 时间范围 |
|---|---|---|
| 日 | `report_date` | 当天 |
| 周 | `report_week`| 周一 到 周末 |
| 月 | `report_month` | 月初 到 月底 |
| 年 | `653795a16182e654535b779b` | 年初 到 年底 |

- 特殊时间维度 不能出现在 dimensionFilters 参数中
- 特殊时间维度 不能同时出现在 dimensions 参数中
- 如果 dimensions 参数中包含 特殊时间维度, 需要适当调整 startAt 和 endAt 的取值范围
	- 示例: 2026年1月 对应 2026-01-01 ~ 2026-01-31
	- 按照 周 进行对比, 应该是 --startAt 2025-12-29 --endAt 2026-02-01
	- 按照 年 进行对比, 应该是 --startAt 2026-01-01 --endAt 2026-12-31

### Cohort指标

- 当指标的 `cohort=true`，需要根据指标已有的 `cohortUtil` , 生成特殊格式：`指标ID_时间值时间单位`的ID

| 时间单位 | cohortUtil | 含义 | 示例 ID | 说明 |
|---|---|---|---|---|
| f | MINUTE |分钟, 只能取 1~100 | 指标ID_30f | 30 分钟 |
| c | COUNT |次 | 指标ID_3c | 3次 |
| d | DAY | 日 | 指标ID_7d | 7 日 |
| w | WEEK | 周 | 指标ID_2w | 2 周 |
| m | MONTH | 月 | 指标ID_1m | 1 月 |
| y | YEAR | 年 | 指标ID_1y | 1 年 |
| 0n | TO_DATE | 至今 | 指标ID_0n | 至今 |

### Cohort足天限制(fullDayLimit)

- 当 Cohort指标 的所有返回结果都是为空, 可以尝试 `--fullDayLimit 0` 获取不足天的 Cohort指标 数据; 同时提示用户, 当前获取的 Cohort指标 天数可能不全

### 过滤操作符(operator)

| 过滤操作符 | 含义 | 适用类型 |
|--------|------|----------|
| LESS_THAN / LESS_THEN_OR_EQUAL | 小于 / 小于等于 | 数值 |
| GREATER_THAN / GREATER_THEN_OR_EQUAL | 大于 / 大于等于 | 数值 |
| CONTAINS / NOT_CONTAINS | 包含 / 不包含多个值 | 所有类型 |
| EQUAL / NOT_EQUAL | 等于 / 不等于一个值 | 所有类型 |
| LIKE / NOT_LIKE | 字符串模糊匹配 | 字符串 |
| STARTS_WITH / ENDS_WITH | 匹配开头或结尾 | 字符串 |

## 命令说明

### 获取参数列表

1、列表中只包含名字(name), 用于快速定位维度、指标、标签

```bash
python3 skills/datain-skill/scripts/query_game.py -c get_param_names -g 游戏编码1,游戏编码2
```

| 可选参数 |格式 |说明 |
|------|------|------|
| `--funcs` | "参数类型1,参数类型2" | 默认全选; 参数类型可选: dimensions,indicators,map_indicators,derived_indicators,tags  |
| `--algorithmId` | open_udid | 算法, open_udid 或 user_id |

返回格式如下 
```json
{
	"dimensions": ["维度名"], "tags": ["标签名"],
	"indicators": ["常规指标名"], "derived_indicators": ["派生指标名"], "map_indicators": ["指标分类名"],
}
```

2、列表中包含所有属性, 用于构造查询数据的参数

```bash
python3 skills/datain-skill/scripts/query_game.py -c get_param_details -g 游戏编码1,游戏编码2 -n "维度名1,指标名2,指标分类名3,标签名4"
```

| 可选参数 |格式 |说明 |
|------|------|------|
| `-n` 或 `--names` | "维度名1,指标名2,标签名4" | 筛选指定名字的参数 |
| `-i` 或 `--ids` | "维度ID1,指标ID2,标签ID4" | 筛选指定ID的参数 |

返回格式如下
```json
{
	"dimensions": [
		{"id": "维度ID", "name": "维度名", "disableGroupBy": true, "provider":1},
		{"id": "JSON维度ID", "json_value": [
			{"name":"JSON维度名_1", "type": "text", "values": ["JSON维度描述"]}, 
			{"name":"JSON维度名_2", "type": "select", "values": ["单选项1","单选项2"]}, 
			{"name":"JSON维度名_3", "type": "multi_select", "values": ["多选项1","多选项2"]}
		]}
	],
	"indicators": [ {"id": "指标ID", "name": "指标名", "cohort": true, "cohortUtils": ["DAY", "WEEK", "MONTH", "YEAR", "TO_DATE"]} ],
	"derived_indicators": [ {"id": "指标ID", "name": "指标名", "rely_id":["依赖指标ID"]} ],
	"map_indicators": [ {"type":"指标分类", "ids":[{"id": "指标ID", "name": "指标名"}]} ],
	"tags": [ {"id": "标签ID", "name": "标签名"} ],
}
```

- 通用属性: 每个列表的JSON中都有可能带有的属性
	- games: 被限制的游戏编码列表; 如果不为空, 说明这个 `id` 只能用于指定游戏编码
	- algorithmId: 被限制的算法列表; 如果不为空, 说明这个 `id` 只能用于指定算法
- 用于 dimensions、jsonDimensions、dimensionFilters 参数
	- dimensions 列表中的 id 和 name
	- provider不为空, 可获取维度的可选列表
	- `disableGroupBy=true`, 不能出现在 dimensions 参数中
- 用于 indicators 和 indicatorFilters 参数
	- indicators、derived_indicators、map_indicators 列表中的 id 和 name
	- 如果 derived_indicators 的`id`出现在 indicators 参数中, 对应的`rely_ids`也需要出现在 indicators 参数
- 用于 tagDimensions 和 tagFilters 参数
	- tags 列表中的 id 和 name, 仅限单游戏时使用

3、获取维度的可选列表

- 针对出现在 dimensions 参数或 dimensionFilters 参数, 且 provider 属性不为空的维度
- `-i "维度ID1,维度ID2"` 或 `-n "维度名1,维度名2"` 至少有一个, 用于限制指定维度

```bash
# 通过维度ID过滤
python3 skills/datain-skill/scripts/query_game.py -c dimension_values -g 游戏编码1,游戏编码2 -i "维度ID1,维度ID2"
# 通过维度名过滤
python3 skills/datain-skill/scripts/query_game.py -c dimension_values -g 游戏编码1,游戏编码2 -n "维度名1,维度名2"
```

返回格式如下
```json
{ "维度ID": ["实际值"], "维度ID####游戏编码": ["实际值:展示值"]}
``` 

- 实际值 用于 dimensionFilters 的 过滤值; 如果存在展示值, 在展示结果时, 需要将实际值转化成展示值
- `维度ID####游戏编码`: 不同游戏编码的可选列表不一样; `维度ID`: 所有游戏编码的可选列表都一样

### 查询游戏数据

```bash
python3 skills/datain-skill/scripts/query_game.py -c query \
	-g 游戏编码1,游戏编码2 --startAt '开始日期' --endAt '结束日期' \
    --indicators '[{"id":"指标ID","name":"指标名"}]' 
```

| 可选参数 |格式 |说明 |
|------|------|------|
| `--dimensions` | '[{"id":"维度ID","name":"维度名"}]' | 维度对比项列表 |
| `--tagDimensions` | '[{"id":"标签ID","name":"标签名"}]' | 标签对比项列表 |
| `--jsonDimensions` | '[{"id":"JSON维度ID","name":"JSON维度名"}]' | JSON维度对比项列表 |
| `--indicatorFilters` | '[{"id":"指标ID","name":"指标名","operator":"过滤操作符","value":["过滤值"]}]' | 指标过滤列表 |
| `--dimensionFilters` | '[{"id":"维度ID","name":"维度名","operator":"过滤操作符","value":["过滤值"]}]' | 维度过滤列表 |
| `--tagFilters` | '[{"id":"标签ID","name":"标签名","operator":"过滤操作符"}]' | 标签过滤列表 |
| `--fullDayLimit` | 1 | Cohort足天限制, 0 或 1 |
| `--algorithmId` | open_udid |算法, open_udid 或 user_id |

返回格式如下
```json
{
    "result": [ {"is_current":1, "bi_dnu":1234} ], 
    "columns": [ {"key":"bi_dnu","name": "DNU"} ]
}
```
