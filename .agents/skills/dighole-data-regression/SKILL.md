---
name: dighole-data-regression
description: >-
  P2挖孔小游戏数据回归技能。自动化完成挖孔活动的数据回归分析，覆盖触达率、参与率、付费率、ARPU、通关率、
  各R级付费深度、礼包分类收入（锚点/成就/存钱罐/集结）、关卡ROI等核心指标。
  自动从配置表读取任务ID和礼包ID，通过wiki获取上期数据做环比对比。
  输出暗色主题HTML可视化报告（Chart.js）。
  触发场景：挖孔数据回归、挖孔活动分析、挖孔付费分析、挖孔通关率、挖孔ARPU、
  小游戏数据回归、节日挖孔回归、dig hole regression。
---

# P2 挖孔小游戏数据回归

## 1. 技能概述

本技能用于 P2 游戏（game_cd=1041）挖孔小游戏活动的数据回归分析。挖孔是 P2 核心运营活动，已迭代至第五期，连续多期 MVP。

### 1.1 游戏与环境

| 项目 | 值 |
|------|-----|
| 游戏 | P2 (game_cd=1041) |
| Trino 环境 | TRINO |
| 数据表前缀 | `v1041.ods_user_xxx`（无需 game_cd 条件） |
| 活动类型 | 节日循环活动（挖孔小游戏） |

### 1.2 活动迭代历史

| 期数 | 节日 | 时间 | activity_id | Wiki Page ID | 核心改动 |
|------|------|------|------------|-------------|----------|
| 一期 | 2025感恩节 | 2025-11 | — | 229399936 | 首次挖孔，验证活动形式可行性 |
| 二期 | 2025圣诞节 | 2025-12 | — | 233082274 | 加设关卡扩充付费深度，调整挂机产出 |
| 三期 | 2026春节 | 2026-01 | — | 233087719 | 关卡加至100关，装饰物10级，增加自选箱 |
| 四期 | 2026情人节 | 2026-02-16~02-23 | 21127588, 21127589 | 233096315 | 行军特效替换主城特效，新增$99.99成就礼包 |
| 五期 | 2026科技节 | 2026-03-27~04-03(UTC) | 21127575 | — | 新增存钱罐+集结礼包，增加49/99关成就礼包挡位，增加投放 |

> **注意**：一个活动可能有多个 activity_id（如四期情人节有两个：schema3-5 和 schema6），必须全部覆盖。

## 2. 执行流程

### 2.1 确认基础参数

向用户确认以下信息（已提供则跳过）：

| 参数 | 必填 | 说明 | 示例 |
|------|------|------|------|
| **活动名称/节日** | 是 | 本次挖孔所属节日 | `科技节`、`复活节` |
| **活动日期范围（UTC）** | 是 | UTC 时间，活动按 UTC 开关 | `UTC 2026-03-27 00:00 ~ 2026-04-03 00:00` |
| **activity_id** | 是 | 活动配置表中的 ID，可能有多个 | `21127575` |
| **期数** | 否 | 第几期挖孔 | `五期` |
| **改动说明** | 否 | 本次活动相比上期的改动点 | `新增存钱罐和集结礼包` |
| **对比上期wiki** | 否 | 上一期的 wiki 页面 ID | `pageId=233096315` |

### 2.2 自动获取任务ID和礼包ID

**不要让用户手动提供 task_id 和 iap_id**，从配置表自动读取。

#### 步骤 A：从活动配置表读取组件

**表**: `2112_p2_activity_config`
**Sheet ID**: `1IKUBw678b2PU1m0md1vR9GxcH2uTNyLbR7VWgyAJ57E`
**gid**: `1308621827`

使用 `gws` 认证 + Google Sheets API 读取（参考项目中 `read_sheet.py` 的模式）：

1. 根据 `A_INT_id`（列B）找到 activity_id 对应的行
2. 读取该行的 `A_ARR_activity_components`（列J）
3. 解析 JSON 数组，按 `typ` 分类提取：
   - `{"typ":"task","id":211584701}` → 任务/关卡
   - `{"typ":"iap","id":2013505000}` → 礼包
   - 其他类型（exchange, chest 等）按需记录

#### 步骤 B：查任务表获取关卡描述

**表**: `2115_p2_activity_task`
**Sheet ID**: `1K3-I4gCYKY-Zw5Ms05ozHtHKpOqYI-lp4kuuhqbWajY`
**gid**: `1484652723`

1. 用步骤A提取的 task_id 列表，在列C（`A_INT_id`）中查找
2. 读取对应行的列D（`N_STR_comment`）得到关卡描述
3. 从描述中区分：普通关卡（如"关卡1"~"关卡100"）和奖励关卡（如"奖励关卡1"~"奖励关卡15"）

#### 步骤 C：IAP 分类确认

将提取到的 IAP ID 列表展示给用户，请用户确认每个 IAP 的分类。常见分类：

| 分类 | 说明 |
|------|------|
| 锚点礼包 | 引导付费的基础礼包 |
| 成就礼包 | 通关对应关卡触发的礼包，核心付费驱动 |
| 存钱罐礼包 | 累计储蓄型礼包（五期新增） |
| 集结礼包 | 一次性购买礼包（五期新增） |

> **每期配置可能不同，必须向用户确认分类，不能沿用上期。**

### 2.3 数据采集

使用 `ai-to-sql` 技能执行 Trino SQL。详细 SQL 模板见 [references/sql-patterns.md](references/sql-patterns.md)。

**关键规则：**
- 表名使用 `v1041.ods_user_xxx`，无需 `game_cd` 条件
- 时间过滤：活动按 UTC 时间开关，收入查询用 `timestamps`（Unix 时间戳，UTC）精确过滤
- `partition_date` 适当扩大范围确保不遗漏（因为 partition_date 基于 UTC+8）

**必须采集的数据维度（按执行顺序）：**

#### 1) 活动服活跃人数
- **不能用全服活跃**，必须只算活动开放的服务器
- 先从 `v1041.ods_user_task` 获取活动服务器列表：
  ```sql
  SELECT DISTINCT server_id
  FROM v1041.ods_user_task
  WHERE task_id = '{第一个task_id}'
    AND attribute1 LIKE '%{activity_id}%'
    AND status = 1
  ```
- 再用服务器列表关联 `v1041.ods_user_login` 统计活跃人数

#### 2) 触达人数
- 从 `v1041.ods_user_click` 查询
- `control_id = 'UiActivityMain.ActivityItem_{activity_id}'`
- **注意大小写**：`UiActivityMain.ActivityItem_` 是实际格式

#### 3) 关卡通关数据
- 从 `v1041.ods_user_task` 查询
- 条件：`task_id` 在任务ID范围内 + `attribute1 LIKE '%{activity_id}%'` + `status = 1`
- `status = 1` 表示任务完成/解锁
- 分别统计普通关卡和奖励关卡

#### 4) 付费数据
- 从 `v1041.ods_user_order` 查询
- 按 IAP 分类（锚点/成就/存钱罐/集结）分别统计
- **时间过滤用 `timestamps`**（Unix UTC）：
  ```sql
  WHERE timestamps >= {utc_start_unix} AND timestamps < {utc_end_unix}
    AND iap_id IN ({iap_ids})
  ```
- `partition_date` 适当扩大 1 天范围

#### 5) 分R级付费
- 按活动期间累计付费分级（P2 标准）：

| R级 | 累计付费区间 |
|-----|-------------|
| 小R | $0.01 ~ $9.99 |
| 中R | $10 ~ $99.99 |
| 大R | $100 ~ $499.99 |
| 超R | $500+ |

#### 6) 每日收入趋势（UTC）
- 将 `timestamps` 转换为 UTC 日期后按天分组
- 按 IAP 分类拆分每日收入

#### 7) 关卡完成与付费关联
- 分析完成特定里程碑关卡的玩家平均付费 vs 未完成玩家
- 里程碑关卡根据奖励投放确定（如60关行军特效、100关主城皮肤）

### 2.4 获取历史对比数据

#### 上一期数据（从 wiki 获取）
- 通过 Confluence MCP 的 `get_confluence_page` 工具读取上期 wiki 页面
- 提取：总收入、付费人数、ARPPU、触达人数、触达率、活动服活跃、关卡参与等
- 提取上期 IAP 分类收入明细
- **如果 wiki 数据和 SQL 查询有出入，以 wiki 为准**

#### 历期关卡通关数据（从 Google Sheet 获取）
- 通过 `gws` 读取历期关卡通关人数
- 参考表: https://docs.google.com/spreadsheets/d/1wRnbpUytVpOUYjireni0FKrryefgYUrl26rphBIEeLw/edit?gid=797984644
- 用于绘制各期通关人数对比折线图

### 2.5 生成 HTML 可视化报告

**输出格式：暗色主题 HTML + Chart.js**，不用 Markdown。

详细模板见 [references/report-template.md](references/report-template.md)。

报告章节结构：

1. **活动概览** — Hero 区核心指标卡片
2. **与上期对比** — 核心指标环比表 + 分类收入对比柱状图 + 收入归因分析
3. **分类收入分析** — 饼图（占比）+ 堆叠柱状图（每日趋势）
4. **成就礼包档位分析** — 各档位买家/次数/收入表 + 饼图
5. **R级付费分析** — 饼图 + 表格
6. **关卡通关分析** — 普通关卡漏斗柱状图 + 奖励关卡柱状图 + 最高关卡分布
7. **关卡奖励付费分析** — 完成里程碑关卡玩家的人均付费对比
8. **历期关卡通关对比** — 多期100关完成人数折线图
9. **结论** — 核心发现 + 问题与风险 + 优化建议（P0/P1/P2）

技术要点：
- **Chart.js 使用本地文件**（`chart.min.js`），避免 CDN 在国内加载失败
- CDN 作为备用：`if(!window.Chart) document.write(...)`
- 字体：Noto Sans SC + JetBrains Mono
- 配色方案统一使用 CSS 变量

### 2.6 用户审核与迭代

- 用浏览器打开 HTML 报告供用户审核
- 根据反馈修正数据/结论/排版
- 常见修正：IAP 分类、收入归因解释、排版细节

### 2.7 上传 Git

- `git add` + `git commit` + `git push`
- commit message 格式：`feat: 挖孔{N}期{节日}数据回归报告，含与第{N-1}期{上期节日}对比分析`

## 3. 关键数据表与字段

### 3.1 核心数据表

| 数据维度 | 表 | 关键字段/条件 |
|----------|-----|-------------|
| 活动入口点击 | `v1041.ods_user_click` | `control_id = 'UiActivityMain.ActivityItem_{activity_id}'` |
| 付费订单 | `v1041.ods_user_order` | `iap_id`, `pay_price`, `timestamps`(Unix UTC), `created_at`(UTC+8) |
| 关卡/任务完成 | `v1041.ods_user_task` | `task_id`, `attribute1 LIKE '%{activity_id}%'`, `status = 1` |
| 玩家登录 | `v1041.ods_user_login` | `user_id`, `server_id`, `partition_date` |
| 资产变动 | `v1041.ods_user_asset` | `reason_id`, `asset_id`, `change_type`, `change_count` |

### 3.2 配置表（Google Sheets）

| 表名 | Sheet ID | 用途 |
|------|----------|------|
| `2112_p2_activity_config` | `1IKUBw678b2PU1m0md1vR9GxcH2uTNyLbR7VWgyAJ57E` | 读取 `A_ARR_activity_components` 获取 task/iap ID |
| `2115_p2_activity_task` | `1K3-I4gCYKY-Zw5Ms05ozHtHKpOqYI-lp4kuuhqbWajY` | 查 `N_STR_comment` 获取关卡描述 |
| 历期通关数据 | `1wRnbpUytVpOUYjireni0FKrryefgYUrl26rphBIEeLw` | 各期关卡通关人数对比 |

### 3.3 时间处理要点

| 字段 | 时区 | 用途 |
|------|------|------|
| `partition_date` | UTC+8 | 数据分区，查询时适当扩大范围 |
| `timestamps` | Unix UTC | 精确的 UTC 时间过滤（用于收入等需要精确时间的场景） |
| `created_at` | UTC+8 | 可读时间戳，但注意时区转换 |

## 4. 历史数据基准

详见 [references/historical-data.md](references/historical-data.md)。

## 5. 注意事项

1. **任务ID和礼包ID必须从配置表自动读取**，不要硬编码或让用户提供
2. **IAP 分类必须向用户确认**，每期配置可能不同
3. **活跃人数只算活动服**，不能用全服活跃
4. **收入时间用 UTC timestamps 过滤**，不要只靠 partition_date
5. **control_id 大小写敏感**：`UiActivityMain.ActivityItem_`，不是全小写
6. **一个活动可能有多个 activity_id**，需全部覆盖
7. **status = 1 表示任务完成**，这是关卡通关的判定条件
8. **报告用 HTML + Chart.js**，Chart.js 必须下载到本地（`chart.min.js`），避免 CDN 问题
9. **wiki 数据优先**：如果 SQL 查询结果与 wiki 数据有出入，以 wiki 为准
10. **集结礼包限购1次**，所以付费会随玩家购买而自然衰减，不是缺少触发点
