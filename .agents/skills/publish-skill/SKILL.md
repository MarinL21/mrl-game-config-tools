---
name: publish-skill
description: 帮你发布 skill 到 T4F skills 平台，建议下载～
triggers:
  - 发布 skill
  - 上传 skill
  - publish skill
  - upload skill
  - 分享 skill
  - 提交 skill
---

# 发布 Skill 到内部平台 (Publish Skill)

帮助用户将本地开发好的 Skill 规范化并上传到 `git.tap4fun.com/skills` 组，使其能在 SkillsMP 网站上展示。

## 核心流程

### 1. 完整性检查 (Pre-flight Check)

在进行任何上传操作前，必须按顺序检查当前目录：

1.  **文件检查**:
    *   ❌ 检查 `SKILL.md` 是否存在（可在**仓库根目录**或**任意子目录**；一个仓库可有多个 `SKILL.md`，SkillsMP 会为每个文件各生成一条技能）。若当前目录没有，停止并提示用户参考 `skill-creator` 创建，或切换到含 `SKILL.md` 的子目录再发布。
    *   ⚠️ 检查 `README.md` 是否存在。虽然 specification 中非必需，但强烈建议创建以展示详细文档。
    *   ⚠️ 检查 `.gitignore`。如果没有，建议创建一个，忽略 `node_modules`, `.env`, `.DS_Store` 等。

2.  **内容检查 (SKILL.md)**:
    *   读取 `SKILL.md` 内容。
    *   **Description**: 必须包含 `description` 字段。这是 SkillsMP 列表页展示的关键。如果缺失，**必须**要求用户补充。**注意：description 长度限制为 1024 字符（参考 [agentskills.io spec](https://agentskills.io/specification)）。**
    *   **Name**: 确认 `name` 字段。如果未填，默认使用当前目录名称。必须符合 spec 要求：仅包含小写字母、数字和连字符，且不能以连字符开头或结尾 (regex: `^[a-z0-9]([a-z0-9-]*[a-z0-9])?$`)，最大 64 字符。**`npx skills add` 的 `--skill` 必须与这里的 `name` 一致**（与仓库子路径无关）。
    *   **ignore（与 SkillsMP 对齐）**: 可选；**默认不写即 `false`**，会正常上站。仅当需要 **`ignore: true`** 时，SkillsMP 同步会**跳过**该 `SKILL.md`、**不出现在网站列表**（例如仓库内路由、仅随仓分发不需展示）。
    *   **路径与安装命令（与 SkillsMP 对齐）**: 根目录 `SKILL.md` 的安装命令使用 **SSH** `git@git.tap4fun.com:skills/<repo>.git`；**子目录** `SKILL.md` 的安装命令使用 **GitLab 目录树 HTTPS**（`https://git.tap4fun.com/skills/<repo>/-/tree/<默认分支>/<子路径>`）。推送仍是**整个仓库**一次 `git push`，无需为子技能单独建仓库。

3.  **安全检查 (高危)**:
    *   🚨 **警告**: 此仓库是 **Internal (全公司公开)** 的，**严禁提交任何密钥、密码或 Token**。
    *   自动扫描目录下是否有：
        *   `.env` 文件 (必须添加到 `.gitignore`)
        *   包含 `KEY`, `TOKEN`, `SECRET`, `PASSWORD` 等敏感字样的文件。
    *   如果有任何可疑文件，**必须立即停止流程**，要求用户清理或确认安全后才能继续。

4.  **规则确认**:
    *   **Visibility Level**: 必须选 **Internal 🔐**。提醒用户在创建或检查 GitLab 仓库时务必遵守此规则。

### 2. GitLab 仓库准备

**重要提示 (向用户强调)**:
> 1. **权限**: 你需要 `skills` 组的 **Maintainer** 权限才能创建仓库。如果权限不足，请前往 [钉钉 - T4F 审批](dingtalk://dingtalkclient/action/openapp?container_type=work_platform&corpid=ding055f194a57d1af67&app_id=0_1183983372&redirect_type=jump&redirect_url=https%3A%2F%2Fapply.tap4fun.com%2Fhome%3FauditFlowId%3D21%26prefillId%3D6982eaf75a4cea0ce970f52b) 申请。
> 2. **可见性**: 仓库可见性 **必须** 设置为 **Internal** (内部公开)。
>    - ❌ **Private**: 严禁使用。后端服务无法读取，网站上无法显示，会导致 Skill 发布失败。
>    - ✅ **Internal**: 必须选择。确保公司内部全员可见，后端服务可正常抓取。

**操作步骤**:
1.  询问用户 Skill 的目标名称 (默认: 当前目录名)。
2.  构造 GitLab 仓库地址: `git@git.tap4fun.com:skills/[skill-name].git`
3.  **优先尝试自动化**: 尝试使用 `curl` 检查仓库是否存在。
4.  **引导创建**: 如果仓库不存在，提供直达链接让用户去网页创建 (因为 API 创建通常需要更高权限或复杂配置):
    - 🔗 创建链接: `https://git.tap4fun.com/projects/new?namespace_id=1871` (1871 是 skills 组 ID)
    - 📝 **注意事项清单**:
      - Project name: `[skill-name]`
      - Project URL: 选择 `skills` group
      - **Visibility Level**: 必须选 **Internal** 🔐
      - **Project Configuration**: 取消勾选 "Initialize repository with a README" (因为本地已有)

### 3. 推送代码 (Git Push)

当用户确认仓库已在 GitLab 上创建好后，执行以下命令：

```bash
# 1. 初始化 (如果需要)
git init

# 2. 配置用户信息 (如果未配置，提示用户设置为公司邮箱)
git config user.name "Your Name"
git config user.email "your.name@tap4fun.com"

# 3. 添加远程仓库
# 先尝试移除旧的 origin (防止冲突)
git remote remove origin 2>/dev/null
git remote add origin git@git.tap4fun.com:skills/[skill-name].git

# 4. 提交并推送
git add .
git commit -m "feat: initial release of [skill-name]"
git push -u origin master
```

**分支处理**:
- GitLab 默认分支可能是 `main` 或 `master`。如果推送 `master` 失败，尝试推送 `main`。

### 4. 验证与完成

1.  推送成功后，提示用户访问 SkillsMP 网站。
2.  链接: `http://skillsmp.tap4fun.com`
3.  提醒: "进入网站后，点击右上角的**刷新**按钮，即可看到你的 Skill。"
4.  若设置了 **`ignore: true`**：说明不会在列表出现属预期；需要上站则按上文修改后重新推送并刷新。
5.  子目录技能：在网站上用**复制**得到的安装命令为准（HTTPS 树形地址）；勿用手写根目录 SSH 去装子目录技能。
