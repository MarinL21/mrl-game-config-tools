# ============================================================
# gws_sheets.r — 基于 gws CLI 的 Google Sheets 通用工具函数
# 用法类似 googlesheets4，但无需 R OAuth 认证
# ============================================================

# 把 R 的 data.frame / matrix / list 转成 Sheets API 需要的二维 JSON 数组
.to_values_json <- function(data, col_names = TRUE) {
  if (is.data.frame(data) || is.matrix(data)) {
    rows <- if (col_names) {
      list(as.list(colnames(data)))
    } else {
      list()
    }
    for (i in seq_len(nrow(data))) {
      rows <- c(rows, list(as.list(as.character(unname(data[i, ])))))
    }
  } else if (is.list(data)) {
    rows <- data
  } else {
    stop("data 必须是 data.frame、matrix 或 list")
  }
  jsonlite::toJSON(list(values = rows), auto_unbox = TRUE)
}

GWS_BIN <- "/usr/local/bin/gws"

# 调用 gws 并返回结果（内部函数）
.gws_call <- function(cmd) {
  cmd <- sub("^gws ", paste0(GWS_BIN, " "), cmd)
  result <- system(
    paste0("PATH=/usr/local/bin:$PATH ", cmd),
    intern = TRUE
  )
  output <- paste(result, collapse = "\n")
  if (grepl('"error"', output)) {
    stop(paste("gws 返回错误：", output))
  }
  output
}

#' 创建新的 Google Sheets 表格
#'
#' @param title       表格标题
#' @param sheet_names 工作表名称向量，默认只有 "Sheet1"
#' @return 包含 spreadsheetId 和 spreadsheetUrl 的 list
gws_create_sheet <- function(title, sheet_names = "Sheet1") {
  sheets_json <- jsonlite::toJSON(
    lapply(sheet_names, function(name) list(properties = list(title = name))),
    auto_unbox = TRUE
  )
  body <- jsonlite::toJSON(
    list(properties = list(title = title)),
    auto_unbox = TRUE
  )
  # 手动拼接 sheets 字段（避免嵌套 toJSON 问题）
  body <- sub("\\}$", paste0(', "sheets": ', sheets_json, "}"), body)

  cmd <- paste0("gws sheets spreadsheets create --json '", gsub("'", "'\\''", body), "'")
  output <- .gws_call(cmd)
  result <- jsonlite::fromJSON(output)
  base::message("✓ 表格创建成功：", result$properties$title)
  base::message("  ID  : ", result$spreadsheetId)
  base::message("  链接: https://docs.google.com/spreadsheets/d/", result$spreadsheetId, "/edit")
  invisible(list(
    spreadsheetId  = result$spreadsheetId,
    spreadsheetUrl = paste0("https://docs.google.com/spreadsheets/d/", result$spreadsheetId, "/edit")
  ))
}

#' 读取 Google Sheets 指定范围
#'
#' @param sheet_id  表格 ID（URL 中 /d/ 后面的部分）
#' @param range     范围，如 "Sheet1!A1:E10" 或 "A1:E10"
#' @param as_df     TRUE 时返回 data.frame（第一行作为列名），FALSE 返回原始 list
#' @return data.frame 或 list
gws_range_read <- function(sheet_id, range, as_df = TRUE) {
  params <- jsonlite::toJSON(
    list(spreadsheetId = sheet_id, range = range),
    auto_unbox = TRUE
  )
  cmd <- paste0("gws sheets spreadsheets values get --params '", params, "'")
  output <- .gws_call(cmd)
  parsed <- jsonlite::fromJSON(output)
  values <- parsed$values

  if (is.null(values) || length(values) == 0) {
    base::message("范围内没有数据")
    return(if (as_df) data.frame() else list())
  }

  if (as_df) {
    header <- unlist(values[[1]])
    rows   <- lapply(values[-1], function(r) {
      row <- unlist(r)
      length(row) <- length(header)  # 补齐 NA
      row
    })
    df <- as.data.frame(do.call(rbind, rows), stringsAsFactors = FALSE)
    colnames(df) <- header
    return(df)
  }
  values
}

#' 写入数据到 Google Sheets 指定范围（覆盖）
#'
#' @param sheet_id          表格 ID
#' @param range             起始单元格或范围，如 "Sheet1!A1"
#' @param data              data.frame、matrix 或二维 list
#' @param col_names         TRUE 时将列名作为第一行写入
#' @param value_input_option "RAW"（原样写入）或 "USER_ENTERED"（支持公式计算）
gws_range_write <- function(sheet_id, range, data, col_names = TRUE,
                             value_input_option = "RAW") {
  params <- jsonlite::toJSON(
    list(spreadsheetId = sheet_id, range = range, valueInputOption = value_input_option),
    auto_unbox = TRUE
  )
  body <- .to_values_json(data, col_names = col_names)
  cmd <- paste0(
    "gws sheets spreadsheets values update",
    " --params '", params, "'",
    " --json '", gsub("'", "'\\''", body), "'"
  )
  output <- .gws_call(cmd)
  base::message("✓ 写入成功：", range)
  invisible(jsonlite::fromJSON(output))
}

#' 追加数据到 Google Sheets 末尾
#'
#' @param sheet_id          表格 ID
#' @param range             定位追加位置的范围，如 "Sheet1!A1"
#' @param data              data.frame、matrix 或二维 list
#' @param col_names         TRUE 时将列名作为第一行追加
#' @param value_input_option "RAW"（原样写入）或 "USER_ENTERED"（支持公式计算）
gws_range_append <- function(sheet_id, range, data, col_names = FALSE,
                              value_input_option = "RAW") {
  params <- jsonlite::toJSON(
    list(spreadsheetId = sheet_id, range = range, valueInputOption = value_input_option),
    auto_unbox = TRUE
  )
  body <- .to_values_json(data, col_names = col_names)
  cmd <- paste0(
    "gws sheets spreadsheets values append",
    " --params '", params, "'",
    " --json '", gsub("'", "'\\''", body), "'"
  )
  output <- .gws_call(cmd)
  base::message("✓ 追加成功：", range)
  invisible(jsonlite::fromJSON(output))
}

#' 清空 Google Sheets 指定范围
#'
#' @param sheet_id  表格 ID
#' @param range     要清空的范围，如 "Sheet1!A1:Z100"
gws_range_clear <- function(sheet_id, range) {
  params <- jsonlite::toJSON(
    list(spreadsheetId = sheet_id, range = range),
    auto_unbox = TRUE
  )
  cmd <- paste0(
    "gws sheets spreadsheets values clear",
    " --params '", params, "'",
    " --json '{}'"
  )
  output <- .gws_call(cmd)
  base::message("✓ 清空成功：", range)
  invisible(jsonlite::fromJSON(output))
}

# ============================================================
# 使用示例（取消注释即可运行）
# ============================================================

# library(jsonlite)
# source("gws_sheets.r")
#
# SHEET_ID <- "你的表格ID"   # URL 中 /d/ 后面的部分
#
# # 读取
# df <- gws_range_read(SHEET_ID, "Sheet1!A1:E20")
# print(df)
#
# # 写入（覆盖，含列名）
# gws_range_write(SHEET_ID, "Sheet1!A1", df)
#
# # 追加一行
# new_row <- data.frame(col1 = "新值1", col2 = "新值2")
# gws_range_append(SHEET_ID, "Sheet1!A1", new_row)
#
# # 清空范围
# gws_range_clear(SHEET_ID, "Sheet1!A1:Z100")
