---
name: gws-workspace
description: 使用 gws CLI 工具操作全套 Google Workspace，包括：发送 Gmail 邮件（HTML正文/中文标题/多附件）、操作 Google Sheets（读写/追加/清空/创建）、管理 Google Drive 文件（上传/列表/权限）、Google Calendar 日历事件（创建/查看日程）、Google Docs 文档（读取/追加文字）、Google Slides 演示文稿（读取）、Google Tasks 任务管理。无需 R OAuth 认证，通过 gws auth login 统一认证。当用户需要发邮件、操作表格、上传文件、管理日历、读写文档、管理任务时使用此技能。
---

# gws Google Workspace 操作指南

> **开发者**：duansiyi　**最后更新**：2026-04-01（配置流程调整：改为使用自建 GCP 项目 `email-sent-dsy-2` 的 OAuth 桌面应用凭据，不再依赖周帆申请；全部 7 个 API 已启用）

通过 `gws` CLI 操作全套 Google Workspace，无需 R OAuth 认证。

## 初次配置流程

### 第零步：获取 OAuth 桌面应用凭据（只需做一次）

这是最源头的步骤，`gws auth login` 依赖这个凭据文件才能运行。

**使用自建 GCP 项目 `email-sent-dsy-2`（项目编号 540508935156）的 OAuth 桌面应用凭据。**

> ✅ 该项目用户类型为**内部（Internal）**，无需 Google 审核，refresh token 长期有效，组织内账号均可使用。

**凭据文件已内置在本 skill 目录中（`client_secret.json`），只需一条命令即可完成配置：**

```bash
mkdir -p ~/Library/Application\ Support/gws && cp "$(dirname "$0")/client_secret.json" ~/Library/Application\ Support/gws/client_secret.json
```

或者手动操作：将本目录下的 `client_secret.json` 复制到 `~/Library/Application Support/gws/client_secret.json`（`gws` 目录不存在时手动创建）。

> 如果 AI 代为执行初次配置，应直接运行以下命令（使用 skill 目录的绝对路径）：
> ```bash
> mkdir -p "$HOME/Library/Application Support/gws" && cp /path/to/.agents/skills/gws-workspace/client_secret.json "$HOME/Library/Application Support/gws/client_secret.json"
> ```

**已启用的 API（全部 7 个均已在项目中开启，无需额外操作）：**
- Gmail API
- Google Sheets API
- Google Drive API
- Google Calendar API
- Google Docs API
- Google Slides API
- Tasks API

> 如需确认或管理已启用的 API，访问 [API 控制台](https://console.cloud.google.com/apis/dashboard?project=email-sent-dsy-2)。

### 第一步：安装 gws

```bash
npm install -g @googleworkspace/cli
```

### 第二步：登录认证（一次性，长期有效）

```bash
gws auth login
```

执行后会自动打开浏览器，用 Google 账号授权，完成后终端显示：

```json
{
  "status": "success",
  "message": "Authentication successful. Encrypted credentials saved.",
  "scopes": ["gmail.modify", "spreadsheets", "drive", "calendar", "documents", "presentations", "tasks"]
}
```

默认一次性开通全部 7 个权限，无需额外配置。

### 凭证说明

- 凭证加密存储于 `~/Library/Application Support/gws/credentials.enc`
- 有 `refresh_token` 自动续期，长期无需重新登录
- 以下情况需重新执行 `gws auth login`：
  - 在 Google 账号安全设置里手动撤销授权
  - 长时间（6个月以上）完全未使用
  - 更换电脑或删除凭证文件
- **发件人身份由认证账号决定**，`from` 字段写其他邮箱无效，Gmail API 会强制使用认证账号发送；换人使用需重新 `gws auth login`

### 验证认证状态

```bash
gws auth status
```

`token_valid: true` 且 `has_refresh_token: true` 表示认证正常。

### 运行环境限制

gws 凭证依赖 macOS **系统钥匙串（Keychain）**，Cursor IDE 内置沙盒 shell 无权访问，直接运行会报 401。

**正确运行方式（任选其一）：**
1. **让 AI 代为执行**：AI 调用 Shell 工具时弹出授权提示，点击同意即可
2. **系统终端运行**：打开 Terminal.app 或 iTerm 直接执行
3. **cron 定时任务**：通过系统级 cron 调用

---

## 已开通服务总览

| 服务 | gws 命令前缀 | 主要用途 |
|------|------------|---------|
| Gmail | `gws gmail` | 发送/读取邮件 |
| Sheets | `gws sheets` | 读写表格数据 |
| Drive | `gws drive` | 上传/下载/管理文件 |
| Calendar | `gws calendar` | 创建/查看日历事件 |
| Docs | `gws docs` | 读取/追加 Google 文档 |
| Slides | `gws slides` | 读取/更新 PPT 演示文稿 |
| Tasks | `gws tasks` | 管理任务列表和任务 |

---

## 模块一：Google Drive 文件管理

### 上传文件

```bash
# 上传文件（自动识别 MIME 类型）
gws drive +upload --params '{"name": "文件名.html"}' --upload /path/to/file.html

# 上传到指定文件夹
gws drive files create \
  --params '{"uploadType": "multipart"}' \
  --json '{"name": "文件名", "parents": ["文件夹ID"]}' \
  --upload /path/to/file
```

### 列出文件

```bash
# 列出最近文件
gws drive files list --params '{"pageSize": 20}' --format table

# 搜索文件
gws drive files list --params '{"q": "name contains '\''关键词'\'' and trashed=false", "pageSize": 10}'
```

### 下载文件

```bash
gws drive files get --params '{"fileId": "文件ID", "alt": "media"}' --output /path/to/save
```

### 设置共享权限

```bash
# 共享给指定邮箱（可编辑）
gws drive permissions create \
  --params '{"fileId": "文件ID"}' \
  --json '{"type": "user", "role": "writer", "emailAddress": "xxx@example.com"}'

# 设置为任何人可查看
gws drive permissions create \
  --params '{"fileId": "文件ID"}' \
  --json '{"type": "anyone", "role": "reader"}'
```

---

## 模块二：Google Calendar 日历

### 查看近期日程

```bash
# 查看今明两天日程
gws calendar +agenda

# 查看指定时间范围事件
gws calendar events list \
  --params '{"calendarId": "primary", "timeMin": "2026-03-11T00:00:00Z", "timeMax": "2026-03-18T00:00:00Z", "singleEvents": true, "orderBy": "startTime"}'
```

### 创建日历事件

```bash
# 快速创建事件
gws calendar +insert \
  --json '{"summary": "会议标题", "start": {"dateTime": "2026-03-12T10:00:00+08:00"}, "end": {"dateTime": "2026-03-12T11:00:00+08:00"}}'

# 创建带邀请人的事件
gws calendar events insert \
  --params '{"calendarId": "primary"}' \
  --json '{
    "summary": "会议标题",
    "start": {"dateTime": "2026-03-12T14:00:00+08:00", "timeZone": "Asia/Shanghai"},
    "end":   {"dateTime": "2026-03-12T15:00:00+08:00", "timeZone": "Asia/Shanghai"},
    "attendees": [{"email": "xxx@example.com"}],
    "description": "会议说明"
  }'
```

### 删除事件

```bash
gws calendar events delete --params '{"calendarId": "primary", "eventId": "事件ID"}'
```

---

## 模块三：Google Docs 文档

### 读取文档内容

```bash
gws docs documents get --params '{"documentId": "文档ID"}'
```

文档 ID 取自 URL：`https://docs.google.com/document/d/【文档ID】/edit`

### 追加文字到文档末尾

```bash
gws docs +write --params '{"documentId": "文档ID"}' --json '{"text": "追加的文字内容\n"}'
```

### 在 R 中读取文档文字

```r
output <- system(
  "PATH=/usr/local/bin:$PATH gws docs documents get --params '{\"documentId\": \"文档ID\"}'",
  intern = TRUE
)
doc <- jsonlite::fromJSON(paste(output, collapse = "\n"))
# 提取纯文本（遍历 body.content）
```

---

## 模块四：Google Tasks 任务

### 查看任务列表

```bash
# 列出所有任务列表
gws tasks tasklists list

# 列出某个任务列表下的任务
gws tasks tasks list --params '{"tasklist": "任务列表ID"}'
```

### 创建任务

```bash
gws tasks tasks insert \
  --params '{"tasklist": "@default"}' \
  --json '{"title": "任务标题", "due": "2026-03-15T00:00:00Z", "notes": "备注说明"}'
```

### 标记任务完成

```bash
gws tasks tasks patch \
  --params '{"tasklist": "@default", "task": "任务ID"}' \
  --json '{"status": "completed"}'
```

---

## 模块五：Gmail 发送邮件（R）

R 函数文件（skill 内已附）：
- [`r-functions/email_gws_fn.r`](r-functions/email_gws_fn.r) — 函数定义，可安全 `source`，不触发任何发送
- [`r-functions/email_gws.r`](r-functions/email_gws.r) — 业务逻辑示例（周报发送）

使用时将文件复制到本地项目目录，然后：

### 核心函数 `send_email_gws`

```r
library(futile.logger)
source("<项目路径>/email_gws_fn.r")  # 只加载函数，不触发发送

send_email_gws(
  from            = "your@email.com",        # 实际由认证账号决定
  to              = c("a@example.com", "b@example.com"),
  cc              = c("c@example.com"),      # 可省略
  subject         = "邮件标题（支持中文）",
  body_text       = "<strong>您好</strong><br>正文内容（HTML格式）",
  attachments     = c("/path/to/file.html"), # 可省略，支持多附件
  drive_threshold = 15,                      # 超过 15MB 自动上传 Drive 改发链接
  dry_run         = FALSE                    # TRUE 时只打印不发送
)
```

### 工作原理

1. 将中文 subject 用 Base64 编码为 `=?UTF-8?B?...?=` 格式
2. 检查每个附件大小，超过 `drive_threshold`（默认 15MB）的自动上传 Drive 并设为任何人可查看，将链接追加到正文末尾
3. 构造 MIME multipart/mixed 邮件（支持 HTML 正文 + 正常大小附件）
4. 将整个 MIME 报文 Base64url 编码后写入临时 JSON 文件
5. 调用 `gws gmail users messages send` 发送

### 收件人简写规则

所有 nibirutech 同事的邮箱格式统一为 `姓名拼音@nibirutech.com`。

指定收件人时可以直接说中文姓名或拼音，AI 自动转换为完整邮箱：
- 「发给 songweihua」→ `songweihua@nibirutech.com`
- 「发给宋威华」→ 先将中文姓名转为拼音，再拼接 `@nibirutech.com`
- 「发给 duansiyi 和 zhangjinge」→ `["duansiyi@nibirutech.com", "zhangjinge@nibirutech.com"]`

如果拼音不确定，询问用户确认后再发送。

---

## 模块六：Google Sheets 操作（R）

R 封装函数文件：[`r-functions/gws_sheets.r`](r-functions/gws_sheets.r)

使用时将文件复制到本地项目目录，然后：

```r
library(jsonlite)
source("<项目路径>/gws_sheets.r")

SHEET_ID <- "URL中/d/后面的部分"
```

### 函数速查

| 函数 | 用途 |
|------|------|
| `gws_create_sheet(title, sheet_names)` | 创建新表格，返回 `spreadsheetId` 和 URL |
| `gws_range_read(sheet_id, range, as_df=TRUE)` | 读取范围，默认返回 data.frame（首行为列名） |
| `gws_range_write(sheet_id, range, data, col_names=TRUE, value_input_option="RAW")` | 覆盖写入 |
| `gws_range_append(sheet_id, range, data, col_names=FALSE, value_input_option="RAW")` | 追加到末尾 |
| `gws_range_clear(sheet_id, range)` | 清空范围 |

### 常用示例

```r
# 创建表格
sheet_info <- gws_create_sheet("我的表格", sheet_names = c("Sheet1", "数据"))
SHEET_ID <- sheet_info$spreadsheetId

# 读取
df <- gws_range_read(SHEET_ID, "Sheet1!A1:E20")

# 覆盖写入（含列名）
gws_range_write(SHEET_ID, "Sheet1!A1", df)

# 写入含公式（必须用 USER_ENTERED）
df_formula <- data.frame(名称 = c("A", "合计"), 收入 = c(1000, "=SUM(B2:B2)"))
gws_range_write(SHEET_ID, "Sheet1!A1", df_formula, value_input_option = "USER_ENTERED")

# 追加一行
gws_range_append(SHEET_ID, "Sheet1!A1", data.frame(col1 = "新值1", col2 = "新值2"))

# 清空
gws_range_clear(SHEET_ID, "Sheet1!A1:Z100")
```

### value_input_option 说明

| 值 | 说明 |
|----|------|
| `"RAW"` | 原样写入，公式当普通文本 |
| `"USER_ENTERED"` | 像用户手动输入，**公式会被执行** |

### range 格式

- 普通：`Sheet1!A1:E10`
- 中文工作表名：`'数据表'!A1:E10`

---

## 模块七：Google Slides 演示文稿

演示文稿 ID 取自 URL：`https://docs.google.com/presentation/d/【演示文稿ID】/edit`

### 读取演示文稿信息

```bash
# 获取演示文稿完整结构（含所有幻灯片、文字、图片元素）
gws slides presentations get --params '{"presentationId": "演示文稿ID"}'

# 只获取基本信息（标题、幻灯片数量等）
gws slides presentations get \
  --params '{"presentationId": "演示文稿ID", "fields": "title,slides.objectId,slides.pageElements"}'
```

### 读取单张幻灯片

```bash
# 获取指定页面（pageObjectId 从 presentations get 结果中的 slides[].objectId 取得）
gws slides presentations pages get \
  --params '{"presentationId": "演示文稿ID", "pageObjectId": "页面ObjectId"}'
```

### 批量更新（替换文字）

```bash
# 全局替换文字（适合批量更新模板中的占位符）
gws slides presentations batchUpdate \
  --params '{"presentationId": "演示文稿ID"}' \
  --json '{
    "requests": [
      {
        "replaceAllText": {
          "containsText": {"text": "{{占位符}}", "matchCase": false},
          "replaceText": "替换后的文字"
        }
      }
    ]
  }'
```

### 在 R 中读取幻灯片文字

```r
# 获取演示文稿 JSON
output <- system(
  "PATH=/usr/local/bin:$PATH gws slides presentations get --params '{\"presentationId\": \"演示文稿ID\"}'",
  intern = TRUE
)
pres <- jsonlite::fromJSON(paste(output, collapse = "\n"), simplifyVector = FALSE)

# 提取所有幻灯片的文字内容
extract_slide_text <- function(pres) {
  slides <- pres$slides
  result <- lapply(seq_along(slides), function(i) {
    slide <- slides[[i]]
    texts <- c()
    for (elem in slide$pageElements) {
      if (!is.null(elem$shape$text$textElements)) {
        for (te in elem$shape$text$textElements) {
          if (!is.null(te$textRun$content)) {
            texts <- c(texts, te$textRun$content)
          }
        }
      }
    }
    list(slide = i, text = paste(texts, collapse = ""))
  })
  do.call(rbind, lapply(result, as.data.frame))
}

df_slides <- extract_slide_text(pres)
print(df_slides)
```

### 在 R 中批量替换文字

```r
replace_slide_text <- function(presentation_id, find_text, replace_text) {
  payload <- jsonlite::toJSON(list(
    requests = list(list(
      replaceAllText = list(
        containsText = list(text = find_text, matchCase = FALSE),
        replaceText = replace_text
      )
    ))
  ), auto_unbox = TRUE)

  tmp <- tempfile(fileext = ".json")
  writeLines(payload, tmp)

  cmd <- sprintf(
    "PATH=/usr/local/bin:$PATH gws slides presentations batchUpdate --params '{\"presentationId\": \"%s\"}' --json '%s'",
    presentation_id, payload
  )
  output <- system(cmd, intern = TRUE)
  jsonlite::fromJSON(paste(output, collapse = "\n"))
}

# 使用示例
replace_slide_text("演示文稿ID", "{{日期}}", "2026-03-11")
```

### 注意事项

- `presentations get` 返回的 JSON 较大，建议用 `fields` 参数按需过滤字段
- `batchUpdate` 支持多个 `requests` 合并为一次调用，减少 API 请求次数
- Slides API 目前不支持直接导出为 PDF/PPTX，如需导出请通过 Drive API：
  ```bash
  # 导出为 PPTX
  gws drive files export \
    --params '{"fileId": "演示文稿ID", "mimeType": "application/vnd.openxmlformats-officedocument.presentationml.presentation"}' \
    --output /path/to/output.pptx

  # 导出为 PDF
  gws drive files export \
    --params '{"fileId": "演示文稿ID", "mimeType": "application/pdf"}' \
    --output /path/to/output.pdf
  ```

---

## 常见错误

| 错误 | 解决方法 |
|------|---------|
| 401 authError | 凭证过期则重新运行 `gws auth login`；沙盒环境则让 AI 执行时点击同意 |
| 403 accessNotConfigured | GCP 项目未启用对应 API → 见下方说明 |
| 403 insufficientPermissions | 认证时未授权对应 scope → 见下方说明 |
| 附件不存在 | 检查文件路径，函数会自动跳过并记录 warn 日志 |
| 邮件发送失败（附件过大） | Gmail API 限制邮件总大小 25MB（含 Base64 编码膨胀约 33%），请压缩附件或先用 `gws drive +upload` 上传到 Drive，再在正文中附上共享链接 |
| 范围格式错误 | 确认 range 格式，中文 sheet 名加单引号，如 `'数据表'!A1:E10` |
| Mac 日历 App 报 400 | 进入系统设置 → 互联网账户，找到 Google 账号，将日历开关关闭再打开；若仍失败则删除账号重新添加 |

### 403 accessNotConfigured：API 未启用

报这个错说明对应的 Google API 还没在 GCP 项目里开启。

**【AI 引导规则】遇到此错误时，直接将以下链接发送给用户，告知他们点击对应链接、进入页面后点「启用」按钮（链接已指向自建项目 `email-sent-dsy-2`）：**

- 👉 Gmail API：https://console.cloud.google.com/apis/library/gmail.googleapis.com?project=email-sent-dsy-2
- 👉 Google Sheets API：https://console.cloud.google.com/apis/library/sheets.googleapis.com?project=email-sent-dsy-2
- 👉 Google Drive API：https://console.cloud.google.com/apis/library/drive.googleapis.com?project=email-sent-dsy-2
- 👉 Google Calendar API：https://console.cloud.google.com/apis/library/calendar-json.googleapis.com?project=email-sent-dsy-2
- 👉 Google Docs API：https://console.cloud.google.com/apis/library/docs.googleapis.com?project=email-sent-dsy-2
- 👉 Google Slides API：https://console.cloud.google.com/apis/library/slides.googleapis.com?project=email-sent-dsy-2
- 👉 Tasks API：https://console.cloud.google.com/apis/library/tasks.googleapis.com?project=email-sent-dsy-2

不要只说"去启用 API"，要把上面的链接直接列出来给用户，让他们一键跳转。

> 正常情况下全部 7 个 API 已在项目中启用。如果仍遇到此错误，请确认 `client_secret.json` 来自正确的项目（`email-sent-dsy-2`）。

### 403 insufficientPermissions：scope 权限不足

报这个错说明 `gws auth login` 授权时没有勾选对应权限（scope）。重新执行登录并在浏览器授权页面**允许全部权限**：

```bash
gws auth login
```

浏览器弹出授权页后，确认所有权限都已勾选（Gmail、Sheets、Drive、Calendar、Docs、Slides、Tasks），然后点击**允许**。
