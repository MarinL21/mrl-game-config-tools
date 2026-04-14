# gws-workspace

通过 `gws` CLI 操作全套 Google Workspace，覆盖 Gmail、Sheets、Drive、Calendar、Docs、Slides、Tasks 七大服务。

## 功能概览

- **Gmail**：发送 HTML 邮件，支持中文标题、多附件、超大附件自动上传 Drive
- **Sheets**：读写、追加、清空、创建表格，支持公式写入
- **Drive**：上传、下载、列出、搜索文件，设置共享权限
- **Calendar**：查看日程、创建/删除日历事件，支持邀请人
- **Docs**：读取文档内容、追加文字
- **Slides**：读取演示文稿、批量替换文字、导出 PDF/PPTX
- **Tasks**：管理任务列表，创建/完成任务

## 快速开始

### 1. 安装凭据（一次性）

凭据文件已内置在本目录中，直接复制即可：

```bash
mkdir -p ~/Library/Application\ Support/gws
cp ./client_secret.json ~/Library/Application\ Support/gws/client_secret.json
```

### 2. 安装 gws CLI

```bash
npm install -g @googleworkspace/cli
```

### 3. 登录认证

```bash
gws auth login
```

浏览器弹出授权页后，允许全部权限即可。认证长期有效，无需反复登录。

## 技术说明

- OAuth 凭据来自自建 GCP 项目 `email-sent-dsy-2`，用户类型为**内部（Internal）**，refresh token 长期有效
- 全部 7 个 Google API 已在项目中启用
- 附带 R 语言封装函数（`r-functions/` 目录），可在 R 脚本中直接调用 Gmail 和 Sheets

## 文件结构

```
gws-workspace/
├── SKILL.md              # 完整操作指南（AI 读取）
├── README.md             # 本文件
├── client_secret.json    # OAuth 桌面应用凭据（内置）
├── r-functions/
│   ├── email_gws_fn.r    # Gmail 发送邮件函数
│   ├── email_gws.r       # 邮件业务逻辑示例
│   └── gws_sheets.r      # Sheets 操作封装函数
└── .gitignore
```

## 作者

duansiyi
