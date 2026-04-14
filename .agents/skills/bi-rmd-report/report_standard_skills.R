# report_standard_skills.R - Standardized BI reporting functions

# --- 1. Global Style & Theme ---
colors2 <- c("#FF6666", "#33CCCC", "#CC99FF", "#33CC99", "#FF9933", "#3399FF", "#FF33CC", 
             "#CAB2D6", '#B2DF8A', "springgreen4", "#cccc00", "#ff99ff", "#996699", 
             "#666699", "#FFDAB9", "#F5F5DC", "#FFFF33", "#E6E6FA", 'lightblue', 'yellow')
bi_single_fill_default <- "#4E79A7"

g_theme <- theme(
  text = element_text(family = 'STKaiti', size = 15), 
  panel.background = element_blank(),
  axis.line = element_line(colour = "black"),
  axis.text.x = element_text(size = 12, angle = 0, hjust = 0.5, vjust = 0.5),
  axis.text.y = element_text(size = 12),
  axis.title = element_text(size = 15),
  legend.position = "top",
  legend.title = element_blank()
)

#' Legend theme helper
#' @param position one of "top", "right", "bottom", "left", "none"
#' @return ggplot2 theme layer
bi_theme_legend <- function(position = "top") {
  position <- match.arg(position, c("top", "right", "bottom", "left", "none"))
  theme(
    legend.position = position,
    legend.title = element_blank()
  )
}

# --- 2. Data Formatting Helpers ---

#' Format large numbers with units (K, M, B) - Scalar
format_number <- function(x) {
  if (is.na(x) || !is.numeric(x)) return(as.character(x))
  if (x >= 1e9) return(sprintf("%.2fB", x/1e9))
  if (x >= 1e6) return(sprintf("%.2fM", x/1e6))
  if (x >= 1e3) return(sprintf("%.2fK", x/1e3))
  return(as.character(round(x, 2)))
}

#' Vectorized version of K/M/B formatting
format_unit_vec <- function(x) {
  sapply(x, format_number)
}

#' Convert numerical values to percentage strings (Vectorized)
#' @param x numeric vector (e.g., 0.123)
#' @param digits number of decimal places
#' @return character vector (e.g., "12.30%")
format_number_vec <- function(x, digits = 2) {
  if (is.null(x)) return(NULL)
  res <- ifelse(is.na(x), NA_character_, sprintf(paste0("%.", digits, "f%%"), as.numeric(x) * 100))
  return(res)
}

#' Convert percentage strings back to numerical values (Vectorized)
#' @param x character vector (e.g., "12.3%")
#' @return numeric vector (e.g., 0.123)
from_percent_vec <- function(x) {
  if (is.null(x)) return(NULL)
  # Remove % sign and divide by 100
  res <- as.numeric(sub("%", "", x)) / 100
  return(res)
}

#' Legacy alias for percentage formatting
percent_format <- format_number_vec

# --- 3. Plotting Functions (ggplot2 Based) ---

#' Standard BI bar plot with legend/color conventions
#' Rules:
#' 1) geom_bar edge color always black
#' 2) grouped bar uses fill mapping + unified palette colors2
#' 3) non-grouped bar uses fixed single fill color
bi_plot_bar_standard <- function(
  data, x_col, y_col, fill_col = NULL, title = "", x_lab = "", y_lab = "",
  position = c("dodge", "stack"), is_percent = FALSE,
  single_fill = bi_single_fill_default, legend_position = "top"
) {
  position <- match.arg(position)
  has_group <- !is.null(fill_col) && nzchar(fill_col)

  if (has_group) {
    p <- ggplot(data, aes(x = as.factor(!!sym(x_col)), y = !!sym(y_col), fill = !!sym(fill_col))) +
      geom_bar(stat = "identity", position = position, colour = "black")
  } else {
    p <- ggplot(data, aes(x = as.factor(!!sym(x_col)), y = !!sym(y_col))) +
      geom_bar(stat = "identity", position = position, colour = "black", fill = single_fill)
  }

  p <- p + g_theme + bi_theme_legend(legend_position) + labs(title = title, x = x_lab, y = y_lab)

  if (has_group) {
    p <- p + scale_fill_manual(values = colors2)
  }

  if (is_percent) {
    p <- p + geom_text(
      aes(label = format_number_vec(!!sym(y_col))),
      position = if (position == "dodge") position_dodge(0.9) else position_stack(vjust = 0.5),
      vjust = if (position == "dodge") -0.5 else 0.5,
      size = 3.5
    )
  } else {
    p <- p + geom_text(
      aes(label = format_unit_vec(!!sym(y_col))),
      position = if (position == "dodge") position_dodge(0.9) else position_stack(vjust = 0.5),
      vjust = if (position == "dodge") -0.5 else 0.5,
      size = 3.5
    )
  }
  p
}

#' Standard Grouped Bar Chart (Dodge)
bi_plot_bar_grouped <- function(data, x_col, y_col, fill_col, title = "", x_lab = "", y_lab = "", is_percent = FALSE) {
  bi_plot_bar_standard(
    data = data, x_col = x_col, y_col = y_col, fill_col = fill_col,
    title = title, x_lab = x_lab, y_lab = y_lab, position = "dodge", is_percent = is_percent
  )
}

#' Standard Stacked Bar Chart
bi_plot_bar_stacked <- function(data, x_col, y_col, fill_col, title = "", x_lab = "", y_lab = "") {
  bi_plot_bar_standard(
    data = data, x_col = x_col, y_col = y_col, fill_col = fill_col,
    title = title, x_lab = x_lab, y_lab = y_lab, position = "stack", is_percent = FALSE
  ) + 
    guides(fill = guide_legend(override.aes = list(alpha = 0.8)))
}

#' Standard Line Chart (Trend/Cohort Curves)
bi_plot_line <- function(data, x_col, y_col, group_col, title = "", x_lab = "", y_lab = "", is_percent = FALSE) {
  p <- ggplot(data, aes(x = !!sym(x_col), y = !!sym(y_col), color = !!sym(group_col), group = !!sym(group_col))) +
    geom_line(size = 1) +
    geom_point(size = 2) +
    g_theme +
    scale_color_manual(values = colors2) +
    expand_limits(y = 0) +
    labs(title = title, x = x_lab, y = y_lab)
  
  if (is_percent) {
    p <- p + scale_y_continuous(labels = scales::percent_format(accuracy = 0.1))
  }
  return(p)
}

#' Standard line chart with optional grouping
#' Grouped mode: map color to group and apply unified colors2
#' Non-grouped mode: fixed single color
bi_plot_line_standard <- function(
  data, x_col, y_col, group_col = NULL, title = "", x_lab = "", y_lab = "",
  is_percent = FALSE, single_color = bi_single_fill_default, legend_position = "top"
) {
  has_group <- !is.null(group_col) && nzchar(group_col)

  if (has_group) {
    p <- ggplot(data, aes(x = !!sym(x_col), y = !!sym(y_col), color = !!sym(group_col), group = !!sym(group_col))) +
      geom_line(size = 1) +
      geom_point(size = 2) +
      scale_color_manual(values = colors2)
  } else {
    p <- ggplot(data, aes(x = !!sym(x_col), y = !!sym(y_col), group = 1)) +
      geom_line(size = 1, color = single_color) +
      geom_point(size = 2, color = single_color)
  }

  p <- p + g_theme + bi_theme_legend(legend_position) + expand_limits(y = 0) +
    labs(title = title, x = x_lab, y = y_lab)

  if (is_percent) {
    p <- p + scale_y_continuous(labels = scales::percent_format(accuracy = 0.1))
  }
  p
}

#' Standard Boxplot
bi_plot_boxplot <- function(data, x_col, y_col, fill_col = NULL, title = "", x_lab = "", y_lab = "", show_outliers = FALSE) {
  aes_mapping <- if(is.null(fill_col)) aes(x = as.factor(!!sym(x_col)), y = !!sym(y_col)) 
                 else aes(x = as.factor(!!sym(x_col)), y = !!sym(y_col), fill = !!sym(fill_col))
  
  p <- ggplot(data, aes_mapping) +
    geom_boxplot(outlier.shape = if(show_outliers) 19 else NA, width = 0.6, alpha = 0.7) +
    g_theme +
    labs(title = title, x = x_lab, y = y_lab)
  
  if(!is.null(fill_col)) {
    p <- p + scale_fill_manual(values = colors2)
  }
  
  # Add median labels
  p <- p + stat_summary(fun = median, geom = "text", aes(label = format_unit_vec(..y..)),
                        position = position_dodge(0.6), vjust = -0.5, color = "black", size = 3.5)
  return(p)
}

# --- 4. Interactive & Dynamic Functions ---

#' Convert ggplot to interactive Plotly
bi_to_interactive <- function(p, tooltip = "all") {
  plotly::ggplotly(p, tooltip = tooltip) %>% 
    plotly::layout(legend = list(orientation = "h", x = 0, y = 1.1))
}

#' Simple Plotly Animation (e.g., trend over time)
bi_plot_animated <- function(data, x_col, y_col, frame_col, group_col, title = "") {
  p <- data %>%
    plot_ly(
      x = ~get(x_col), 
      y = ~get(y_col), 
      color = ~get(group_col), 
      frame = ~get(frame_col), 
      text = ~paste0("Value: ", get(y_col)),
      hoverinfo = "text",
      type = 'scatter',
      mode = 'lines+markers'
    ) %>%
    layout(title = title, xaxis = list(title = x_col), yaxis = list(title = y_col))
  return(p)
}

# --- 5. Table Rendering ---

#' Standard DT Datatable
bi_render_datatable <- function(df, page_length = 10, scroll_x = TRUE, buttons = TRUE) {
  opts <- list(
    pageLength = page_length,
    scrollX = scroll_x,
    dom = if(buttons) 'Blfrtip' else 'lfrtip',
    buttons = if(buttons) c('copy', 'csv', 'excel') else NULL
  )
  
  DT::datatable(df, 
                extensions = if(buttons) 'Buttons' else list(),
                options = opts,
                class = 'cell-border stripe',
                rownames = FALSE)
}

#' Static paged HTML table fallback for nested tabsets in Rmd
#' Avoids DT/paged_table rendering issues in hidden tabs.
#' @return htmltools::tagList object
bi_render_static_paged_table <- function(df, page_size = 10, table_title = "明细表") {
  if (is.null(df) || nrow(df) == 0) {
    return(htmltools::tagList(htmltools::p("暂无数据")))
  }

  total_pages <- ceiling(nrow(df) / page_size)
  blocks <- lapply(seq_len(total_pages), function(i) {
    start_idx <- (i - 1) * page_size + 1
    end_idx <- min(i * page_size, nrow(df))
    page_df <- df[start_idx:end_idx, , drop = FALSE]

    table_html <- knitr::kable(page_df, format = "html", align = "c") %>%
      kableExtra::kable_styling(
        bootstrap_options = c("striped", "hover", "condensed"),
        full_width = TRUE,
        position = "left",
        font_size = 12
      )

    htmltools::tagList(
      htmltools::tags$h5(sprintf("%s - 第 %d/%d 页", table_title, i, total_pages)),
      htmltools::HTML(as.character(table_html))
    )
  })

  do.call(htmltools::tagList, blocks)
}

# --- 6. RMarkdown Utility (Tabs) ---

#' Create Tabset Header (Returns string to be cat'd in Rmd)
#' Usage: `cat(bi_tabset_start("My Analysis"))`
bi_tabset_start <- function(title, level = "###", type = ".tabset-fade") {
  paste0("\n", level, " ", title, " {", type, "}\n\n")
}

#' Create Individual Tab (Returns string)
bi_tab_item <- function(tab_name, level = "####") {
  paste0("\n", level, " ", tab_name, "\n\n")
}
