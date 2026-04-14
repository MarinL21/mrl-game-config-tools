# ============================================================
# email_gws_fn.r — Gmail 发送核心函数（无业务逻辑，可安全 source）
# ============================================================
library(futile.logger)

# 用 shell 命令对字符串 base64 编码
shell_base64 <- function(text) {
  tmp <- tempfile()
  writeLines(text, tmp, useBytes = TRUE)
  result <- system(paste0("base64 < '", tmp, "' | tr -d '\\n'"), intern = TRUE)
  unlink(tmp)
  paste(result, collapse = "")
}

# 对文件进行 base64 编码
shell_base64_file <- function(filepath) {
  result <- system(paste0("base64 < '", filepath, "' | tr -d '\\n'"), intern = TRUE)
  paste(result, collapse = "")
}

# 将文件上传到 Drive 并返回可公开访问的链接（内部函数）
.upload_to_drive <- function(filepath) {
  att_name <- basename(filepath)
  upload_out <- system(
    paste0(
      "PATH=/usr/local/bin:$PATH gws drive +upload",
      " --params '{\"name\": \"", gsub("'", "'\\''", att_name), "\"}'",
      " --upload '", filepath, "'"
    ),
    intern = TRUE
  )
  result <- tryCatch(
    jsonlite::fromJSON(paste(upload_out, collapse = "\n")),
    error = function(e) NULL
  )
  if (is.null(result) || is.null(result$id)) {
    stop(paste("Drive 上传失败:", paste(upload_out, collapse = "\n")))
  }
  file_id <- result$id
  # 设为任何人可查看
  system(
    paste0(
      "PATH=/usr/local/bin:$PATH gws drive permissions create",
      " --params '{\"fileId\": \"", file_id, "\"}'",
      " --json '{\"type\": \"anyone\", \"role\": \"reader\"}'"
    ),
    intern = TRUE
  )
  paste0("https://drive.google.com/file/d/", file_id, "/view")
}

#' 发送邮件（支持 HTML 正文 + 多附件）
#'
#' @param from            发件人邮箱（实际由 gws 认证账号决定）
#' @param to              收件人，字符向量
#' @param cc              抄送人，字符向量（可为空）
#' @param subject         邮件标题（支持中文）
#' @param body_text       正文内容（HTML 格式字符串）
#' @param attachments     附件文件路径向量（可为空）
#' @param drive_threshold 单个附件超过此 MB 数时自动上传 Drive 并改发链接，默认 15
#' @param dry_run         TRUE 时只打印不发送
send_email_gws <- function(from, to, cc = character(0), subject,
                           body_text, attachments = character(0),
                           drive_threshold = 15,
                           dry_run = FALSE) {

  boundary <- paste0("boundary_", format(Sys.time(), "%Y%m%d%H%M%S"))

  # 编码标题（用 printf 避免 echo -n 在 macOS sh 下输出 "-n"）
  subject_encoded <- paste0(
    "=?UTF-8?B?",
    system(
      paste0("printf '%s' '", gsub("'", "'\\''", subject),
             "' | base64 | tr -d '\\n'"),
      intern = TRUE
    ),
    "?="
  )

  to_str <- paste(to, collapse = ", ")
  cc_str <- if (length(cc) > 0) {
    paste0("Cc: ", paste(cc, collapse = ", "), "\n")
  } else {
    ""
  }

  # 处理附件：超过阈值的上传 Drive，链接追加到正文末尾
  drive_links <- character(0)
  inline_attachments <- character(0)
  for (att in attachments) {
    if (!file.exists(att)) {
      flog.warn("附件不存在，跳过: %s", att)
      next
    }
    size_mb <- file.info(att)$size / 1024 / 1024
    if (size_mb > drive_threshold) {
      flog.info(
        "附件 %s (%.1fMB) 超过 %dMB，自动上传 Drive",
        basename(att), size_mb, drive_threshold
      )
      url <- tryCatch(
        .upload_to_drive(att),
        error = function(e) {
          flog.error(
            "Drive 上传失败，跳过附件 %s: %s",
            basename(att), conditionMessage(e)
          )
          NULL
        }
      )
      if (!is.null(url)) {
        drive_links <- c(
          drive_links,
          paste0("<a href='", url, "'>", basename(att), "</a>")
        )
        flog.info("Drive 链接: %s", url)
      }
    } else {
      inline_attachments <- c(inline_attachments, att)
    }
  }

  # 将 Drive 链接追加到正文
  if (length(drive_links) > 0) {
    body_text <- paste0(
      body_text,
      "<br><br><b>以下附件因超过 ", drive_threshold, "MB 已上传至 Google Drive：</b><br>",
      paste(drive_links, collapse = "<br>")
    )
  }

  # 构造 MIME 邮件头
  mime_parts <- paste0(
    "From: ", from, "\n",
    "To: ", to_str, "\n",
    cc_str,
    "Subject: ", subject_encoded, "\n",
    "MIME-Version: 1.0\n",
    "Content-Type: multipart/mixed; boundary=\"", boundary, "\"\n",
    "\n",
    "--", boundary, "\n",
    "Content-Type: text/html; charset=UTF-8\n",
    "Content-Transfer-Encoding: base64\n",
    "\n",
    shell_base64(body_text), "\n"
  )

  # 添加正常大小的附件
  for (att in inline_attachments) {
    att_name <- basename(att)
    mime_parts <- paste0(
      mime_parts,
      "--", boundary, "\n",
      "Content-Type: application/octet-stream\n",
      "Content-Disposition: attachment; filename=\"", att_name, "\"\n",
      "Content-Transfer-Encoding: base64\n",
      "\n",
      shell_base64_file(att), "\n"
    )
  }

  mime_parts <- paste0(mime_parts, "--", boundary, "--\n")

  # 写入临时文件再整体编码（避免 shell 参数过长）
  tmp_mime <- tempfile(fileext = ".eml")
  writeLines(mime_parts, tmp_mime, useBytes = TRUE)

  encoded <- system(
    paste0("base64 < '", tmp_mime, "' | tr '+/' '-_' | tr -d '\\n='"),
    intern = TRUE
  )
  encoded <- paste(encoded, collapse = "")
  unlink(tmp_mime)

  if (dry_run) {
    flog.info("[dry_run] 邮件已构造，标题: %s，收件人: %s", subject, to_str)
    return(invisible(NULL))
  }

  # 写入 JSON 后用 bash 子进程读取发送（避免 shell 参数过长及单引号嵌套问题）
  tmp_json <- tempfile(fileext = ".json")
  tmp_sh   <- tempfile(fileext = ".sh")
  writeLines(paste0('{"raw": "', encoded, '"}'), tmp_json, useBytes = TRUE)
  writeLines(c(
    "#!/bin/bash",
    "export PATH=/usr/local/bin:$PATH",
    paste0("JSON=$(cat '", tmp_json, "')"),
    "gws gmail users messages send --params '{\"userId\": \"me\"}' --json \"$JSON\""
  ), tmp_sh, useBytes = TRUE)
  system(paste("chmod +x", tmp_sh))

  result <- system(paste("bash", tmp_sh), intern = TRUE)
  unlink(c(tmp_json, tmp_sh))

  output <- paste(result, collapse = "\n")
  if (grepl('"id"', output)) {
    flog.info("✓ 邮件发送成功：%s -> %s", subject, to_str)
  } else {
    flog.error("✗ 邮件发送失败：%s", output)
  }

  invisible(output)
}

# 读取结论文本文件的辅助函数
read_conclude_text <- function(filepath, game_name) {
  if (file.exists(filepath)) {
    text <- paste(readLines(filepath, encoding = "UTF-8"), collapse = "\n")
    flog.info("成功读取%s结论文本文件", game_name)
    text
  } else {
    flog.error("结论文本文件不存在: %s", filepath)
    paste0("未能找到", game_name, "结论文本文件，请检查文件路径。")
  }
}
