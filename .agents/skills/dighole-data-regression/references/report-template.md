# 挖孔数据回归 HTML 报告模板

## 输出格式

报告使用**暗色主题 HTML + Chart.js** 输出，在浏览器中直接查看。

---

## 技术规范

### Chart.js 引用

**必须使用本地文件**，CDN 在国内不稳定：

```html
<script src="chart.min.js"></script>
<script>if(!window.Chart)document.write('<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"><\/script>')</script>
```

首次生成报告时，需要先下载 Chart.js 到项目目录：
```powershell
Invoke-WebRequest -Uri "https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js" -OutFile "chart.min.js" -UseBasicParsing
```

### 字体

```html
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700;900&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
```

### CSS 配色方案

```css
:root {
  --bg: #0c0e14;
  --surface: #151821;
  --surface-2: #1c2030;
  --border: #2a2f42;
  --text: #e0e4f0;
  --text-dim: #8891a8;
  --accent: #6c8cff;
  --green: #34d399;
  --orange: #fb923c;
  --red: #f87171;
  --yellow: #facc15;
  --purple: #a78bfa;
  --cyan: #22d3ee;
}
```

### JS 配色常量

```javascript
const C = {
  accent:'#6c8cff', green:'#34d399', orange:'#fb923c',
  red:'#f87171', purple:'#a78bfa', yellow:'#facc15',
  cyan:'#22d3ee', dim:'#8891a8', border:'#2a2f42'
};
```

---

## 报告结构

### 1. Hero 区 — 活动概览

顶部全宽区域，包含：
- 标题：`挖孔{N}期数据回归 — {节日名}`
- 副标题：活动时间 + 期数
- 核心指标卡片（2行4列）：

| 指标 | 示例 |
|------|------|
| 触达用户 / 触达率 | 15,632 / 62.3% |
| 参与用户 / 参与率 | 13,915 / 55.4% |
| 付费用户 / 付费率 | 2,730 / 17.5% |
| 总收入 / ARPPU | $207,535 / $76.02 |

### 2. 与上期对比（如有上期数据）

- **核心指标对比表**：指标 / 上期 / 本期 / 变化 / 说明
- **分类收入对比柱状图**（`chartEditionCompare`）：上期 vs 本期的各分类收入
- **收入结构对比表**：各分类收入的上期/本期/差值
- **收入归因分析**：文字说明收入变化的原因

### 3. 分类收入分析

两列布局：
- 左：饼图 — 各分类收入占比（`chartCatPie`）
- 右：堆叠柱状图 — 每日分类收入趋势（`chartCatDaily`）

下方：分类收入明细卡片

### 4. 成就礼包档位分析

两列布局：
- 左：饼图 — 各档位收入占比（`chartAchieveTier`）
- 右：表格 — 档位 / 买家 / 次数 / 收入 / 占比

### 5. R级付费分析

两列布局：
- 左：饼图 — R级收入占比（`chartRlevel`）
- 右：表格 — R级 / 人数 / 总付费 / 人均 / 占比

### 6. 关卡通关分析

- **普通关卡漏斗**（`chartLevelFunnel`）：全宽柱状图
- **关卡通关率表**：关卡 / 通关人数 / 通关率 / 流失率
- **奖励关卡柱状图**（`chartRewardLevels`）：全宽
- **最高关卡分布**：水平柱状图（`chartMaxLevel`）+ 表格

### 7. 关卡奖励付费分析

两列布局：
- 左：水平柱状图 — 不同关卡完成者的人均付费（`chartRewardArpu`）
- 右：饼图 — 收入贡献占比（`chartRewardContrib`）

### 8. 历期关卡通关对比

- 全宽折线图（`chartHistoryLevels`），高度 420px
- 多条折线：每期一条，当期用填充色突出
- X轴：关卡 1~100，Y轴：通关人数

### 9. 结论

#### 核心发现（有序列表）

重点内容：
1. 总收入及环比变化 + 收入归因分析（锚点/成就/新增礼包各自的变化）
2. 付费人数/付费率变化
3. 关卡通关率变化
4. 新增礼包效果评估

#### 问题与风险

#### 优化建议（P0/P1/P2）

### 10. SQL 查询基准

表格展示关键 SQL，便于复查。

---

## 图表类型速查

| 图表 | Canvas ID | 类型 | 用途 |
|------|-----------|------|------|
| 分类收入对比 | `chartEditionCompare` | bar | 上期 vs 本期 |
| 分类收入占比 | `chartCatPie` | doughnut | 当期各分类占比 |
| 每日分类趋势 | `chartCatDaily` | bar(stacked) | 分天趋势 |
| 成就档位占比 | `chartAchieveTier` | doughnut | 成就礼包各档位 |
| R级收入占比 | `chartRlevel` | doughnut | 四级分布 |
| 普通关卡漏斗 | `chartLevelFunnel` | bar | 通关漏斗 |
| 奖励关卡 | `chartRewardLevels` | bar | 奖励关卡完成人数 |
| 人均付费对比 | `chartRewardArpu` | bar(horizontal) | 里程碑完成者付费 |
| 收入贡献占比 | `chartRewardContrib` | doughnut | 各组收入贡献 |
| 历期通关对比 | `chartHistoryLevels` | line | 多期折线对比 |
| 最高关卡分布 | `chartMaxLevel` | bar(horizontal) | 区间分布 |

---

## 撰写原则

1. **环比必须有**：每个核心指标都要与上期对比，标注变化（+X% / -X%）
2. **收入归因要具体**：不能只说"收入下降"，要拆分到每个礼包分类的变化
3. **量化具体**：避免"有所提升"，用具体数字和百分比
4. **变化着色**：正向用绿色 `.green`，负向用红色 `.red`，中性用橙色 `.orange`
5. **结论先行**：每个模块先给结论，再放图表
6. **优化建议可执行**：分 P0/P1/P2 优先级，给出具体操作
