# bi-rmd-report

BI 分析报告标准化展示 Skill，用于 RMarkdown 报告开发。

## 功能

- 统一图表风格（柱状图、折线图、箱线图）
- 交互图表（Plotly 原生 API，中文无乱码）
- 表格展示（DT 交互表）
- Tabset 布局
- 数据格式化工具函数

## 安装

```bash
npx skills add git@git.tap4fun.com:skills/bi-rmd-report.git --skill 'bi-rmd-report'
```

## 使用

在 Rmd 的 setup chunk 中引入：

```r
library(showtext)
font_add("NotoSansCJK", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
showtext_auto()

source("/root/.openclaw/workspace/skills/bi-rmd-report/report_standard_skills.R")

# 覆盖字体（服务器环境）
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

## 数据库连接

数据库连接配置需自行创建 `bi_base_utils.R`，参考以下模板：

```r
get_mysql_conn <- function(envir = "mysql_a3") {
  DBI::dbConnect(
    RMariaDB::MariaDB(),
    host = "your_host",
    user = "your_user",
    password = "your_password",
    dbname = "your_dbname"
  )
}
```

## 渲染命令

```bash
LC_ALL=C.UTF-8 LANG=C.UTF-8 Rscript -e "rmarkdown::render('report.Rmd')"
```

## 环境要求

R 4.2+，已安装：`rmarkdown`, `knitr`, `ggplot2`, `dplyr`, `tidyr`, `scales`, `DT`, `plotly`, `htmltools`, `showtext`
