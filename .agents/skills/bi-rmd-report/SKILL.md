---
name: bi-rmd-report
description: BI 分析报告标准化展示 Skill，用于 RMarkdown 报告开发。提供统一的图表（柱状图、折线图、箱线图）、表格（DT交互表、静态分页表）、交互图（Plotly）、Tabset 布局等组件，以及 MySQL/Presto 数据库连接和 Google Sheets 读写工具。触发词：写报告、Rmd报告、BI报告、R分析、画图、柱状图、折线图、箱线图、数据表格、report_standard_skills、bi_base_utils。
---

# BI 报告标准化展示 Skill

本 Skill 旨在统一 BI 分析报告的视觉风格与展示逻辑，提供标准化的图表、表格及布局组件。

## 1. 核心资源

- **脚本路径**: skill 安装目录下（如 `~/.openclaw/workspace/skills/bi-rmd-report/`）
- **基础变量**:
  - `colors2`: 统一的 20 色调色盘
  - `g_theme`: 统一的 ggplot2 主题（见下方字体说明）
- **CSS 模板**: 自行创建 `report.css`，或复制 skill 目录下的示例

---

## 2. 服务器环境配置（必读）

### 2.1 渲染命令

**必须加 locale 前缀**，否则中文变 Unicode 码点：

```bash
LC_ALL=C.UTF-8 LANG=C.UTF-8 Rscript -e "rmarkdown::render('report.Rmd')"
```

### 2.2 中文字体

服务器上没有 `STKaiti`，使用 `NotoSansCJK`，在 setup chunk 中覆盖 `g_theme`：

```r
library(showtext)
font_add("NotoSansCJK", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
showtext_auto()

source("/path/to/skills/bi-rmd-report/report_standard_skills.R")

# 覆盖字体
g_theme <- theme(
  text = element_text(family = "NotoSansCJK", size = 15),
  panel.background = element_blank(),
  axis.line = element_line(colour = "black"),
  axis.text.x = element_text(size = 12, angle = 0, hjust = 0.5, vjust = 0.5),
  axis.text.y = element_text(size = 12),
  axis.title = element_text(size = 15),
  legend.position = "top",
  legend.title = element_blank()
)
```

### 2.3 已安装 R 包

R 4.2.2 + Pandoc 2.17，已安装：
`rmarkdown`, `knitr`, `ggplot2`, `dplyr`, `tidyr`, `scales`, `DT`, `plotly`, `htmltools`, `htmlwidgets`, `kableExtra`, `showtext`

> ⚠️ `tidyverse` 整包安装失败（ragg 依赖缺失），按需加载子包：`library(dplyr)`, `library(tidyr)`, `library(ggplot2)` 等

---

## 3. YAML 头部模板

```yaml
---
title: "报告标题"
author: "BI Team"
date: "`r Sys.Date()`"
output:
  html_document:
    theme: flatly
    highlight: tango
    toc: true
    toc_depth: 2
    df_print: paged
    code_folding: hide
    css: report.css
---
```

- `toc_float: true` 会把目录放侧边栏，**不推荐**，改用 `toc: true` 顶部内嵌
- `css: report.css` 引用外部 CSS，不能内联在 yaml 里

---

## 4. 展示场景与函数用法

### 4.1 交互图表（推荐用 plotly 原生）

**⚠️ 不要用 `ggplotly()` 转换**，中文 legend/标题会乱码。直接用 plotly 原生 API：

```r
# 分组柱状图（带黑边）
plot_ly(df, x = ~x_col, y = ~y_col, color = ~group,
        colors = c("基准期" = "#00BFC4", "分析期" = "#F8766D"),
        type = "bar", barmode = "group",
        marker = list(line = list(color = "black", width = 0.8)),
        text = ~paste0(y_col, "%"), textposition = "outside",
        hovertemplate = "%{x}<br>值: %{y}<extra></extra>") %>%
  layout(
    xaxis = list(title = ""),
    yaxis = list(title = "留存率(%)"),
    legend = list(orientation = "h", x = 0, y = 1.1),
    margin = list(t = 30)
  )

# 水平条形图（贡献度排序）
plot_ly(df, x = ~value, y = ~label, type = "bar", orientation = "h",
        marker = list(color = ~color, line = list(color = "black", width = 0.8))) %>%
  layout(margin = list(l = 160))
```

**配色规范（ggplot2 经典红蓝双色）**：

```r
# 统一色板定义（放在 setup chunk）
COL_BLUE <- "#00BFC4"   # 青蓝 — 基准/对照/正向
COL_RED  <- "#F8766D"   # 红 — 分析/实验/负向
COLORS   <- scales::hue_pal()(16)  # 多线图用
```

| 场景 | 颜色 |
|------|------|
| 基准期/对照组 | `COL_BLUE` (#00BFC4) |
| 分析期/实验组 | `COL_RED` (#F8766D) |
| 正向变化 | `COL_BLUE` (#00BFC4) |
| 负向变化 | `COL_RED` (#F8766D) |
| 多线图 | `COLORS[1:N]` |
| 卡片/摘要框边框 | `COL_BLUE` |

- **单色柱状图**：`marker = list(color = COL_BLUE, line = list(color = "black", width = 0.6))`
- **分组柱状图**：`colors = c(COL_BLUE, COL_RED)`
- **所有柱状图必须加黑色边框**：`marker = list(line = list(color = "black", width = 0.6))`
- **禁止使用** `colors2`、`bi_single_fill_default`、Tableau 色或其他非 ggplot2 色板
- **Y 轴动态上限**（防止标签截断）：柱状图 `range = c(0, max * 1.15)`

**Y 轴动态上限**（防止标签被截断）：

```r
auto_ymax <- function(vals, expand = 1.15) {
  mx <- max(vals, na.rm = TRUE)
  if (mx == 0) return(1)
  magnitude <- 10 ^ floor(log10(mx))
  ceiling(mx * expand / magnitude) * magnitude
}

# 用法
layout(yaxis = list(range = c(0, auto_ymax(df$value))))
```

### 4.2 表格（推荐用 DT）

**⚠️ 不要用 Markdown 表格**（`| col | col |` 语法），在 rmarkdown html_document 中行间距大、列宽不可控、长文本换行难看。

**静态展示表格（行高一致、列宽可控）推荐用 `htmltools::HTML()` 输出 HTML 表格**：

> ⚠️ 不要用内联 HTML 或 `cat()` + `results='asis'`，pandoc 会重新格式化 `<td>` 内容，在单元格内插入换行导致行高被撑大。必须用 `htmltools::HTML()` 包裹，才能绕过 pandoc 处理。

```r
# 在 R chunk 中（不需要 results='asis'）
htmltools::HTML('<table style="width:100%;border-collapse:collapse;font-size:14px"><thead><tr style="background:#f6f8fa;border-bottom:2px solid #dee2e6"><th style="padding:8px 12px;text-align:left;width:70px">列1</th><th style="padding:8px 12px;text-align:left">列2</th></tr></thead><tbody><tr style="border-bottom:1px solid #dee2e6"><td style="padding:7px 12px">值</td><td style="padding:7px 12px">值</td></tr></tbody></table>')
```

整个表格必须写成一行字符串，不能有换行符。

**交互表格（可排序/搜索/导出）用 `DT::datatable`**（见下方）。

**⚠️ 不要用 `kableExtra`**，在 `LC_ALL=C` 环境下中文列名会变 Unicode 码点。改用 `DT::datatable`：

```r
# 简洁展示（无分页/搜索）
DT::datatable(df, rownames = FALSE, options = list(dom = 't', pageLength = 10))

# 完整功能（含导出按钮）
DT::datatable(df, rownames = FALSE,
              extensions = 'Buttons',
              options = list(dom = 'Blfrtip', buttons = c('copy','csv','excel')))
```

**中文列名处理**：计算时用 ASCII 列名，最后用 `transmute()` 直接赋中文名输出：

```r
show_df <- df %>%
  transmute(
    渠道 = channel,
    基准期留存 = percent_format(ret_base),
    分析期留存 = percent_format(ret_cur),
    贡献度 = round(contrib, 4)
  )
DT::datatable(show_df, rownames = FALSE, options = list(dom = 't'))
```

### 4.3 分析背景 Info Cards

用 HTML grid 替代 Markdown 表格，更美观：

```html
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:24px">
<div style="background:#f8f9fa;border-left:4px solid #4E79A7;padding:12px 16px;border-radius:4px">
  <div style="font-size:1rem;color:#888;margin-bottom:4px">字段名</div>
  <div style="font-weight:700;font-size:1.4rem">字段值</div>
</div>
<!-- 重复以上 div ... -->
</div>
```

> **规范**：card-label `font-size:14px; color:#555; font-weight:600`，card-value `font-weight:700; font-size:13px`，padding `12px 16px`。border 颜色统一用 `COLORS[1]`（单色），不要用多个颜色区分 card。

### Cohort 窗口过滤规范

**D0-DN 分析必须过滤注册满 N+1 天的用户**，确保每个用户的 D0~DN 数据都完整可观测：

```r
# N = cohort 最大天数（如 D0-D3 则 N=3）
N <- 3
today <- Sys.Date()

# 只保留注册满 N+1 天的用户
valid_users <- users %>%
  filter(as.integer(today - register_date) >= N + 1) %>%
  pull(user_id)

# 过滤所有相关数据
orders  <- orders  %>% filter(user_id %in% valid_users)
pay_tot <- pay_tot %>% filter(user_id %in% valid_users)
pay_log <- pay_log %>% filter(user_id %in% valid_users)
all_log <- all_log %>% filter(user_id %in% valid_users)
users   <- users   %>% filter(user_id %in% valid_users)
```

> **规则**：D0-DN 窗口需满 N+1 天。例如 D0-D3 需满4天，D0-D6 需满7天，D0-D30 需满31天。

### 4.4 Tabset 布局

```markdown
## 归因拆解 {.tabset .tabset-fade}

### iOS · 国家

### Android · 渠道

### 贡献度汇总
```

### 4.5 ggplot2 函数（静态图）

仍可用 `bi_` 系列函数，但需确保 `g_theme` 已覆盖为 NotoSansCJK：

```r
bi_plot_bar_grouped(data, x_col, y_col, fill_col, title, is_percent = FALSE)
bi_plot_bar_stacked(data, x_col, y_col, fill_col, title)
bi_plot_line_standard(data, x_col, y_col, group_col, is_percent = FALSE)
bi_plot_boxplot(data, x_col, y_col, fill_col, show_outliers = FALSE)
```

---

## 5. 数据格式化

```r
format_number_vec(x)      # K/M/B 单位格式化（向量）
percent_format(x, digits=2)  # 小数转百分比字符串，如 0.123 -> "12.30%"
from_percent_vec(x)       # 百分比字符串转小数
```

---

## 6. 数据库连接（bi_base_utils.R）

```r
source("/path/to/skills/bi-rmd-report/bi_base_utils.R")  # 需自行创建，包含数据库连接配置

con_mysql  <- get_mysql_conn("mysql_a3")      # MySQL
con_presto <- get_presto_conn("presto_query") # Trino/Presto
```

---

## 7. 部署到 demo

将生成的 HTML 上传到内部 demo 服务器：

```bash
# 上传端口 9258，访问端口 9257，两者不同勿混用
curl -sS -X POST "http://172.20.90.123:9258/upload/Demo-tap4fun/<目录名>" \
  -F "file=@report.html;filename=index.html" \
  -w "\nHTTP: %{http_code}"
```

访问地址：`https://demo.tap4fun.com/<目录名>/`

---

## 8. 已知问题与解决方案

| 问题 | 原因 | 解决方案 |
|---|---|---|
| 中文变 Unicode 码点 | locale=C | 渲染命令加 `LC_ALL=C.UTF-8` |
| ggplotly 中文 legend 乱码 | ggplotly 转换丢失编码 | 改用 plotly 原生 API |
| kableExtra 表格中文乱码 | locale 问题 | 改用 `DT::datatable` |
| STKaiti 字体找不到 | 服务器无该字体 | 改用 NotoSansCJK + showtext |
| tidyverse 安装失败 | ragg 依赖缺失 | 按需加载子包 |
| toc_float 目录在侧边 | 默认行为 | 去掉 `toc_float: true` |
| CSS 内联在 yaml 报错 | pandoc 不支持 | 写到 `report.css` 文件引用 |
| plotly subplot 模块重叠 | `layout(height=...)` 已废弃，容器高度失效 | 用 `p$height <- N` 直接设置（见 8.1） |
| `cat()` 输出的 Markdown 表格不渲染 | `results='asis'` 中 `cat()` 产生额外空行，pandoc 无法识别表格语法 | 改用 `DT::datatable` 输出表格（见 8.2） |
| tabset 中 `cat(renderTags(p)$html)` 颜色/交互丢失 | `renderTags()$html` 不含 plotly 完整依赖 | 改用 `cat(knitr::knit_print(p))`（见 8.3） |

### 8.1 Plotly subplot 高度设置（必须遵守）

**⚠️ 禁止在 `layout()` 中设置 `height`**，该参数已废弃，会导致 plotly 容器高度为 0，后续模块叠在图表上方。

```r
# 错误 — 高度不生效，模块重叠
subplot(plots, nrows = 4) %>% layout(height = 1000)

# 正确 — 直接设置 plotly 对象的 $height 属性
p <- subplot(plots, nrows = 4) %>%
  layout(legend = list(orientation = "h", x = 0, y = 1.02))
p$height <- 1000
p
```

经验公式：`p$height <- 行数 * 250`（每行子图约 250px）。

### 8.2 禁止用 `cat()` 输出 Markdown 表格

在 `results='asis'` 的 R chunk 中，`cat("| A | B |\n")` 会在行间插入额外空行，导致 pandoc 无法将其识别为表格，最终以纯文本 `|` 分隔符显示。

```r
# 错误 — 表格不渲染
cat("| 维度 | V0 | V2 |\n")
cat("|------|----|----|------|\n")
cat("| 收敛速度 | 35.6 | 35.1 |\n")

# 正确 — 用 DT 交互表格
DT::datatable(df, rownames = FALSE, options = list(dom = 't'))
```

**规则**：报告中所有表格统一使用 `DT::datatable`，禁止使用 Markdown 表格语法和 `kableExtra`。

### 8.3 Tabset 中动态输出 plotly 图表

在 `results='asis'` 循环中输出 plotly 到动态 tabset 时，**禁止使用 `htmltools::renderTags(p)$html`**（会丢失 plotly JS 依赖和颜色绑定）。

```r
# 错误 — 图表颜色和交互功能丢失
cat(htmltools::renderTags(p)$html)

# 正确 — 使用 knitr::knit_print 保留完整 widget
cat(knitr::knit_print(p))
```

完整 tabset 动态生成模板：

```r
## 分析明细 {.tabset .tabset-fade}

```{r, results='asis'}
for (group in groups) {
  cat(sprintf("\n### %s\n\n", group))
  
  p <- plot_ly(...) %>% layout(...)
  p$height <- 600
  
  cat(knitr::knit_print(p))
  cat("\n\n")
}
```
