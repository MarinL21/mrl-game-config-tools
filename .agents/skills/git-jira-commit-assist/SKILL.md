---
name: git-jira-commit-assist
description: "Git 提交/推送/上传代码到远端仓库，含分支推送与 Jira 关联、Issue 创建/更新。触发：用户提到 commit、push、提交、推送、上传代码、推送分支、branch，或提到 Jira、提交 Jira、关联 Issue、创建/更新 Issue、issue-xxx。"
---

# git-jira-commit-assist Skill

Git 提交 + Jira 关联一站式助手。自动分析变更、生成 commit、关联或新建 Issue，提交推送。

## 触发关键词

用户说以下任意内容时触发本 skill：

**提交类**
- 提交、git 提交、jira 提交、提交代码、我要提交、帮我提交、规范提交
- commit、git commit
- 把代码提交到…、将代码提交到…、提交到 git@…、提交到仓库

**推送类**
- push、git push、推送代码、推送到远端、推到仓库、推送到 git
- 把代码推送到…、将代码推到…、同步到远端、上传代码到…
- 提交到 git@…（含 SSH 地址 `git@` 开头）、提交到 https://…git
- 推送到 gitlab、推送到 github、推送到 gitee

**仓库初始化 + 推送意图**
- 初始化仓库并推送、add remote 并提交、关联远端仓库后推送
- 把项目上传到 git、把代码同步到仓库

**Jira 相关**
- 关联 jira、创建 jira、jira 任务、关联 issue、创建 issue

## Skill 包与 CLI（`SKILL_ROOT`）

- **触发 Skill**：Cursor / Claude 只会把本说明注入对话，**不会**替你执行本包里的脚本。
- **跑 CLI 时**：`verify-auth`、`commit --json`、`login` 等仍是本机 `node …/scripts/git-jira-commit-assist.js`。下文用 **SKILL_ROOT** 表示本 Skill **包根目录**（同时含 `SKILL.md` 与 `scripts/`）；不要求只会装在「当前仓库的 `.cursor/skills/...`」。常见位置：工作区内 `.cursor/skills/git-jira-commit-assist`、`~/.cursor/skills/git-jira-commit-assist`、或单独克隆的本仓库根——**以本机实际目录为准**。示例：`node "$SKILL_ROOT/scripts/git-jira-commit-assist.js" verify-auth --json`
- **Agent 解析路径**：用当前工作区、已加载 Skill 所在目录、或用户告知的单一绝对路径**直接拼出** `SKILL_ROOT`；**禁止**对 `$HOME` 无边界 `find`（慢且无输出、易错）。
- **独立 Git 仓库 / 带 `package.json` 的发布包**：根目录已有 `.gitignore`（含 `node_modules` 等）。用户克隆后**不必**先手动 `npm install`——首次跑 `git-jira-commit-assist.js` 或 `setup.js` 时，若缺依赖会在该包根目录自动 `npm install`（需本机 Node/npm 且可联网；离线请先在该目录手动安装）。

---

## Git 提交规范（强制）

最终用于 `git commit` 的说明须符合团队约定（Conventional Commits；**关联 Jira 时** footer 单独一行 Issue Key）。

### 信息结构

```text
<type>[(scope)]: <subject>

[optional body：可多行，说明动机、实现要点等]

<footer>
```

- **首行（header）**：`<type>[(scope)]: <subject>`  
  - **type**（必填）：`chore` | `docs` | `feat` | `fix` | `perf` | `refactor` | `revert` | `style` | `test`  
  - **scope**（可选）：影响范围，如路由、数据、模型、视图等，写在 **圆括号** 内，例如 `feat(router): …`；无 scope 则省略括号，如 `feat: …`  
  - **subject**（必填）：一句话说清目的，**不超过 50 个字符**（中英文均计），结尾不加句号  
- **body**（可选）：与 subject **空一行**；可换行分段，描述背景、细节、破坏性变更等  
- **footer**（**关联 Jira 时必填**）：与 body（或首行）**空一行**；**单独一行**写 Issue Key，格式 `PROJECT-123`（与 Jira 一致）。Key **可只出现在 footer**，不必重复写在 subject 里  

**示例：**

```text
feat: 新增视频功能开发

COST-150
```

有 body 时：

```text
fix(notification): 修正推送重复触发

根因：定时器未在卸载时清理

COST-150
```

### 与不关联 Jira 的例外

用户在第 2 轮回复 **`0`**、明确不关联 Jira 时：仍须满足 **type + subject**（及可选 scope/body）；**无 Jira Key 可不写 footer**（属规范例外）。其余路径**不得**省略 footer 中的 Key。

### Agent 执行时注意

- **Step 0（`verify-auth --json`）未通过**：**本轮只处理登录**——短提示：失败类型（含 HTTP 码）+ **一行可复制命令**：`node $SKILL_ROOT/scripts/git-jira-commit-assist.js login`（请用户**在本机终端**粘贴执行）。**禁止**同条或后续紧接 §3ʹ、`plan`、`commit`、`list-projects`。  
- Step 0 **通过**后：先检测用户消息是否含 Issue Key → 再执行 `plan` + 历史 Key 检测 → 按**路径 A / B / C** 输出第 1 轮。  
- **路径 A**（用户消息含 Key）：第 1 轮用户确认 commit 后直接 commit → push，无需第 2 轮。  
- **路径 B**（无用户 Key，历史命中候选 Key）：第 1 轮同屏展示 commit + 候选 Key；用户回 `1` 关联直接 commit，回 `0` 进第 2 轮。  
- **路径 C**（无用户 Key，无历史 Key）：第 1 轮用户确认 commit 后**必须进入第 2 轮**（list-projects），**不得直接 commit**。  
- `--create-issue` 后 Key 须进 **footer**（脚本 `appendJiraKeyAsFooter` 已按空行分隔）。  
- **第 2 轮项目列表**：必须用 **Markdown 表格或逐行列表**，**禁止**顿号串 Key。  
- `commit` 成功后按 **Step 7**：**默认自动**执行 `git push`，**不要**再让用户回「推送」或「1」才推。  

---

## 执行策略（Agent 必读）

**核心三步规则（严格顺序，不得跳过或合并）**：

1. **路径 A — 用户消息已含 Issue Key**：`plan` 生成 commit 建议 → 用户确认 → commit（`--link-issue=KEY`）→ push
2. **路径 B — 无用户 Key，历史提交命中候选 Key**：`plan` + 历史检测 → 询问用户是否关联 → 确认则 commit → push；拒绝则进路径 C
3. **路径 C — 无用户 Key，无历史候选**：`plan` 生成 commit 建议 → 用户确认 → **列出有权限创建的 Jira 项目** → 用户选择 Key 新建 / 关联已有 / `0` 跳过 → commit → push

**流程**：先 **Step 0 校验登录**。**仅当 `ok: true`** 才继续 → Step 1 判断路径 → … → commit → **Step 7 默认 push**。**Step 0 失败则全流程中止**。

### 对话模式

- **触发提交类对话时，Agent 必须先跑 shell**：`node "$SKILL_ROOT/scripts/git-jira-commit-assist.js" verify-auth --json`（Step 0），**不得**跳过。未通过则停止，不得默示走无 Jira 分支。
- **在与 Jira 打交道之前**（含 `plan`、`list-projects`）须已通过 Step 0（`ok: true`）。若为 `jira_session_invalid` / `no_auth_file`，**不得**把空的 `list-projects` 说成「无创建权限项目列表」。
- **`plan` 仅在 Step 0 通过后**再跑；`plan` 若返回 `error: jira_auth_failed`，中止流程，等同 Step 0 失败。`plan` 输出不要整段贴用户。
- **强制：一轮只问一件事**，等用户回复再发下一轮。
- **禁止**把「确认 commit」与「Jira 列表 / 选 Key / 新建」塞进同一条回复。第 1 轮不出现项目表；第 2 轮再贴 `list-projects --json` + 固定引导一句。
- **登录**：失败时**首段**仅给出可复制命令：`node $SKILL_ROOT/scripts/git-jira-commit-assist.js login`（用户在**本机终端**执行）。成功后用户须重新说「提交」，再从 Step 0 起算。
- `commit` 成功后按 **Step 7**：**默认自动**执行 `git push`，**不要**再让用户回「推送」或「1」才推。

### 3) 对话模式：轮次 + 话术极简（强制）

**原则**：少字。不要解释「下一步会干什么」——用户回了 `1` 或发来整句 message 即视为采用建议，Agent 静默执行再开下一轮。

**用户快捷回复（全文统一）**：`1` = 同意 / 确认；`0` = 跳过 / 拒绝 / 不要（与 Key 数字混淆时可要求带格式如 `PUB-123`）。

**第 1 轮（Step 0 通过后）**：Agent **后台静默**执行 `plan` + 用户消息 Key 检测 + 历史 Key 检测，再按路径输出：

- **路径 A**（用户消息含 Key）→ 用变体 A 展示 commit 建议；用户确认后直接 → Step 5（commit `--link-issue=用户Key` + push）。
- **路径 B**（无用户 Key，有历史候选 Key）→ 用变体 B 展示 commit 建议 + 候选 Key：
  - 用户回 **`1`** → 以候选 Key 关联，直接 → Step 5
  - 用户发其他 Key → 以该 Key 关联，直接 → Step 5
  - 用户回 **`0`** 或「新建」→ 进入第 2 轮（Step 2）
- **路径 C**（无用户 Key，无历史候选）→ 用变体 A 展示 commit 建议；用户确认后**必须进入第 2 轮**（Step 2），**不得直接 commit**。

> ⚠️ **路径 C 强制**：变体 A 用户回 `1` 或发无 Key 的自定义 message 后，**不得立即 commit**，必须先走 Step 2（list-projects）。若用户自定义 message 已含 Issue Key，视为路径 A，直接 → Step 5。

**第 2 轮（路径 C，或路径 B 用户选 `0`）**：执行 `list-projects --json`，展示可创建 Issue 的项目表（**Markdown 表格或逐行列表**，**禁止**顿号串 Key）+ 固定话术：

- 发 issue-key（如 `COST-150`）→ Step 5（`--link-issue=KEY`）
- 发项目 Key（如 `PUB`）→ Step 4（新建 Issue 流程）
- 回 `0` → Step 5（`--skip-jira`，不关联 Jira）

**排版强制**：项目须以 **Markdown 表格**或**逐行列表**展示，一行一个，须含 **Key** 与 **名称**（`name`）。**固定话术**（照抄，接在表后）：`Jira：发 issue-key；或上表项目 Key 新建；跳过回 0`。

**新建**：用户选定项目 → 下一轮照 **§4.2** 处理类型（如需）→ **§4.3** 确认标题 → **§4.4** 执行。

**最后**：执行 `commit --message=…` 等，结果用一两行带过（hash + 链接）。

### 3ʹ) 第 1 轮模板（照结构，字少）

**当 Step 0 未通过时**（**仅此一段**，随后结束；`$SKILL_ROOT` 换成本仓绝对路径）：

```text
Jira 登录校验未通过（no_auth_file）。请在本机终端复制并执行：
node $SKILL_ROOT/scripts/git-jira-commit-assist.js login
完成后请重新发起提交。
```

**当 Step 0 已通过时**，根据路径选用以下变体：

**变体 A（路径 A 用户消息含 Key，或路径 C 无任何候选 Key）**：

```text
请确认提交信息：

feat: …

同意回「1」，或回复自定义提交信息。
```

**变体 B（路径 B 有历史候选 Key）**：

```text
请确认提交信息：

feat: …

检测到关联 Issue：KEY 「Issue 标题」
1 同时关联 / 0 不关联（进入选项目）/ 或直接发其他 issue-key
```

（建议行按实际 diff 换 type/subject≤50；Issue 标题为从 Jira 拉取的 `summary`，拉取失败时只保留 Key；有 Key 时 footer 由脚本执行时自动补入，本轮不写。）

### 4) 无交互一条命令（收集齐用户选择后）

```text
node "$SKILL_ROOT/scripts/git-jira-commit-assist.js" commit --repo-path="$REPO_PATH" --message="…" [--link-issue=KEY | --create-issue --project=KEY --summary="…" | --skip-jira] --json
```

若不能执行 shell：给用户**一条**可复制命令即可；**不要**长摘要。

### 5) 写操作门禁

未获用户**当轮**答复前，不得 `commit` / `create-issue`。下一句话续接同一流程。

**路径 C 专项禁止**：用户在第 1 轮回 `1`（确认 commit message）且 message **不含 Issue Key** 时，**不得**直接执行 `commit`；必须先进入第 2 轮展示 Jira 项目表，等用户明确回复（发 issue-key / 项目 Key 新建 / `0` 跳过）后才可执行 commit。

**删除类**：未走完「行为规范 → Jira 删除类 API」所载**至少三轮**确认前，**不得**发起任何 Jira 删除请求。

---

## 行为规范

- 写操作前有简短反馈（已开始 / 完成 / 失败原因）；**§3 第 1 轮**不要夹与 Step 0 / §3ʹ 无关的长篇进度散文
- 分轮对话 + `plan` 内部用 + 最后 `commit --message --json`
- 认证未配置或失效时，引导用户在本机终端执行 `node $SKILL_ROOT/scripts/git-jira-commit-assist.js login`
- 出错时告知原因和下一步操作，不自动重试

### Jira 删除类 API（强制拦截）

- **默认不执行**：在本 Skill 场景下，Agent **不得**调用会**删除或永久移除** Jira 资源的接口（含 REST、MCP、`curl`、自写脚本等）。包括但不限于：删除 Issue、删评论、删附件、删 worklog、删除 Issue Link / 远程链接、批量删除、purge、等价「不可从界面直接撤销」的操作。
- **先拦截**：用户只说「删掉」「清掉」「移除任务」等未指名对象时，**不调用任何删除 API**；一句说明 Skill 不代做删除，建议 **Jira Web** 或自行在安全环境处理。
- **用户明确坚持删除**：须 **分多轮、每轮单独确认**，**禁止**把多步确认压在同一回合；**至少三轮**用户消息后才可考虑代执行（仍须确有可用且安全的调用方式，否则继续引导 Web）：
  1. **第一轮**：用户写清 **操作类型** + **完整 Issue Key**（或资源标识）。
  2. **第二轮**：Agent **逐字复述**将做的破坏性动作与 Key，并提示风险；用户须回 **`1`** 表示知悉仍要执行。
  3. **第三轮**：用户 **再发一次同一 Issue Key**（或与第二轮约定一致的**确认口令**）作为最终授权；缺一 **不执行**。
- 任一轮用户回 **`0`** 或明确撤回：**立即中止**，不得调用删除 API。

### 提交范围（强制）

- **默认提交仓库内全部变更**：执行 `git add -A`（或等价「暂存全部」）后再 `git commit`。
- **禁止**向用户确认「要不要包含某某文件」「只提交 staged 还是加上 liquid」等；**不要**把文件清单拆成多项让用户勾选。
- 仅当用户**主动说明**「不要提交某路径」「排除某某文件」时，再改用用户指定的 add 范围。

### 对话内交付

- 未获用户当轮答复前不执行写操作；下一条消息续接。
- **分轮**：每轮单一主题；**话术极简**（见 §3）。

---

## 流程图

```
用户触发关键词
      │
      ▼
 [Step 0] verify-auth
      │
      ├─ 失败 ──► 提示 login 命令，结束本轮
      │
      ▼ ok: true
 [Step 1] 用户消息含 Issue Key?
      │
      ├─ 是（路径 A）─────────────────────────────────────────┐
      │                                                       │
      ▼ 否                                                    │
 plan + 历史 Key 检测                                         │
      │                                                       │
      ├─ 命中候选 Key（路径 B）                                │
      │       │                                               │
      │   [第 1 轮：变体 B]                                   │
      │   commit 建议 + 候选 Key                          [第 1 轮：变体 A]
      │       │                                           commit 建议
      │       ├─ 回 1 关联 ──► Step 5（link 候选 Key）        │
      │       ├─ 发其他 Key ─► Step 5（link 其他 Key）    用户确认（1）
      │       └─ 回 0 / 新建 ──┐                             │
      │                        │                              │
      ▼ 无候选 Key（路径 C）   │                              │
  [第 1 轮：变体 A]            │                              │
  commit 建议                  │                              │
      │                        │                              │
  用户确认（message 无 Key）   │                    Step 5（link 用户Key）
      │                        │                              │
      └────────────────────────┘                              │
                   │                                          │
                   ▼                                          │
            [Step 2] list-projects                            │
            展示项目表                                         │
                   │                                          │
                   ├─ 发 issue-key ──► Step 5（link KEY）     │
                   ├─ 发项目 Key ────► Step 4（新建 Issue）   │
                   └─ 回 0（跳过）──► Step 5（skip-jira）     │
                                           │                  │
                                           └──────────────────┘
                                                    │
                                                    ▼
                                           [Step 5] git commit
                                                    │
                                                    ▼
                                     [Step 7] 推送前自检
                                     commit message 含 Key?
                                                    │
                                 ┌──────────────────┴──────────────────┐
                                 │                                       │
                          含 Key ✓                           不含 Key 且非 skip-jira ✗
                    或 skip-jira 路径                                    │
                                 │                             禁止推送，告知补充 Key
                                 ▼                             回到 Step 2
                            git push
                                 │
                                 ▼
                               结束
```

---

## 完整执行流程

### Step 0（最先）：Jira 登录与配置文件

**在用户说要提交 / 关联 Jira 时，Agent 最先**确认能连上 Jira（先于 `plan`、`list-projects`）。

1. **配置文件**：若尚无可用认证（新文件 `~/.git-jira-commit-assist-auth.json` 与旧版 `~/.git-jira-auth.json` 均无，或 `verify-auth` 会话无效）→ **只**提示用户在本机终端执行 `node $SKILL_ROOT/scripts/git-jira-commit-assist.js login`。本轮不解读任何「空项目列表」。
2. **会话有效**：执行：
   ```bash
   node $SKILL_ROOT/scripts/git-jira-commit-assist.js verify-auth --json
   ```
   - 返回 `ok: true` → 再进入 Step 1 及后续步骤。  
   - 返回 `no_auth_file` / `jira_session_invalid`（常见 401）→ **只**提示终端执行 `node $SKILL_ROOT/scripts/git-jira-commit-assist.js login`，**结束本轮流程**（不确认提交、不 `commit`、不 `plan`），**禁止**粉饰为「没有可创建 Issue 的项目」。

`list-projects` 与 `plan`（有代码变更时）内部也会校验会话；Agent 仍须 **优先**执行 Step 0，以便失败时话术正确、不把未登录当成无权限。

---

### Step 1：Issue Key 检测 + 变更分析 + 路径判断

**仅当 Step 0 已通过。** Agent 后台静默同时执行（不告知用户）：

1. **检测用户消息是否含 Issue Key**：在用户的触发消息中匹配 `[A-Z][A-Z0-9]+-\d+` 格式。
2. 跑 `node $SKILL_ROOT/scripts/git-jira-commit-assist.js plan --repo-path="$REPO_PATH"` 获取变更与 commit 建议；**勿**把完整输出贴给用户。
3. 若第 1 步**无 Key**，执行历史 Key 检测（纯 git 命令）：
   ```bash
   git -C "$REPO_PATH" diff --name-only HEAD
   git -C "$REPO_PATH" diff --name-only --cached
   git -C "$REPO_PATH" log -10 --format="%H|||%B"
   # 对每条含 Key 的候选提交：
   git -C "$REPO_PATH" show --name-only --format="" <hash>
   ```
   **匹配规则**：从 `git log` 提取含 `[A-Z][A-Z0-9]+-\d+` 的最近 **3 条**提交；计算文件交集 = 候选提交文件 ∩ 当前变更文件；**命中（满足任一）**：交集 ≥ 1 且占比 ≥ 30%，或交集 ≥ 3；取分数最高且最近一条为**候选 Key**。
4. 有候选 Key 后，静默拉取 Issue 标题：
   ```bash
   node "$SKILL_ROOT/scripts/git-jira-commit-assist.js" search-issues --keyword=<KEY> --json
   ```
   取与 Key 精确匹配的 `summary` 作为标题；失败或无匹配则标题留空。

**路径判断（按优先级）**：

| 条件 | 路径 | 第 1 轮模板 | 下一步 |
| --- | --- | --- | --- |
| 用户消息含 Issue Key | **路径 A** | 变体 A（仅 commit 建议） | 用户确认 → Step 5（`--link-issue=用户Key`） |
| 用户消息无 Key，历史命中候选 Key | **路径 B** | 变体 B（commit 建议 + 候选 Key） | 用户回 `1` → Step 5；回 `0` → Step 2 |
| 用户消息无 Key，无历史候选 | **路径 C** | 变体 A（仅 commit 建议） | 用户确认 → **Step 2**（必须） |

`list-projects --json` 可后台预拉；**表只在 Step 2 轮**贴出。

---

### Step 2：Jira 项目选择（路径 C，或路径 B 用户选 `0`）

执行 `list-projects --json`（**仅**含 `canCreate` 为真的项目），展示项目表 + 固定话术，等用户回复。

**排版强制**：项目须以 **Markdown 表格**或**逐行列表**展示，一行一个，须含 **Key** 与 **名称**（`name`）。**禁止**顿号、逗号横向堆砌。

示例（二选一）：

```
| Key  | 名称     |
| ---- | -------- |
| PUB  | 公共项目 |
| COST | 成本管理 |
```

或逐行：`- **PUB** — 公共项目`

**固定话术**（照抄，接在表后）：`Jira：发 issue-key；或上表项目 Key 新建；跳过回 0`

逻辑分支：

- 用户发已有 Issue Key（如 `COST-150`）→ **Step 5**（`--link-issue=KEY`）
- 用户发项目 Key（如 `PUB`）→ **Step 4**（新建 Issue 流程）
- 用户回 `0`（不关联 Jira）→ **Step 5**（`--skip-jira`）

用户说「列出项目 / 换项目」时再次 `list-projects`，**排版规则相同**。

> **⚠️ 写操作门禁**：须等用户对当前这一问回复后再继续；下一条消息续接。

---

### Step 3：检查 commit msg 是否包含 Issue Key / 是否已关联

在**完整 message**（含 footer）中匹配 `[A-Z][A-Z0-9]+-\d+` 格式的 Issue Key（如 `AUTH-42`、`COST-150`）。**Key 在 footer 单独一行即视为符合规范**。

**已包含 Issue Key**（用户粘贴或 Step 2 已选定）→ **Step 5**（`git add -A` + commit；脚本在 Issue **评论**里带提交信息，**不**再创建 Jira「链接到」）

**不包含 Issue Key**，且用户走新建流程（已选项目等）→ **Step 4**（流式新建 Issue：项目 → 类型 → 标题 → 执行）

**不包含 Issue Key**，且用户回复 **`0`**（不关联 Jira）→ **Step 5** 仅 commit

---

### Step 4：无 Issue Key — 流式新建 Issue（不中断会话）

AI 根据仓库与 diff 匹配**推荐项目**（如 `PUB`；以 `list-projects` 返回的**可创建**项目为准）。按**顺序**确认，每步只问一件事，用户回复后立刻进入下一步。

#### 4.1 确认项目（若第 2 轮已选定项目可跳过本节）

若未选项目：一行 `「PUB」新建？1/0，或发 Key`。

- **`1`** → **4.2**
- **`0`** / 换项目 → 再列项目表后进入 **4.2**

若用户中途说「列出项目」「换项目」，同样执行 `list-projects`，保留当前 commit message 与 diff 上下文，从选项目继续。

> **⚠️ 写操作门禁**：未获用户对「在哪个项目创建」的明确选择前，不得 `create-issue`。

#### 4.2 Issue 类型（失败时触发，成功跳过）

**正常路径**：脚本直接用 `defaultIssueType`（默认 `Task`）创建 Issue，**成功则跳过本节，进入 4.3**。

**仅当**脚本返回 `error: "issue_type_incompatible"` 时（即默认类型与该项目不兼容），才进入本节：

- 脚本的 JSON 响应中已携带 `availableTypes` 列表，**无需**再执行 `list-issuetypes`，直接展示给用户：

```text
默认类型「Task」与该项目不兼容，请选择：
- Bug
- Story
- 需求
（回复类型名）
```

- 用户回复类型名 → 记录，携带 `--issue-type=<类型名>` 重新执行 `commit --create-issue …` → 进入 **4.3**

> **⚠️ 写操作门禁**：用户选定类型前不得重试 `create-issue`。

#### 4.3 确认 Issue 标题

照抄结构（第一行里的引号内为建议标题，按实际替换）：

```text
请确认 ISSUE 标题：「……」
确认回「1」，或直接发新标题。
```

示例：

```text
请确认 ISSUE 标题：「Shopify 仓库：忽略 .cursor 与 todo 清单」
确认回「1」，或直接发新标题。
```

- **`1`** 或回车 → 进入 **4.4 执行**
- 用户输入新标题 → 以用户输入为准，进入 **4.4**

> **⚠️ 写操作门禁**：未确认标题前不得 `create-issue`。

#### 4.4 执行：创建 Issue + 提交全部文件 + 关联

`create-issue` / `commit --create-issue` 在 Jira **创建成功后默认会**：把 Issue **分配给当前登录用户**，并在工作流中**做一次转换**，尽量落到「处理中」类状态（按转换名 / 目标状态名 / `indeterminate` 类别匹配，因项目工作流而异）。失败不阻断创建，仅写入 `postCreate` 字段或终端告警。可在 `~/.git-jira-commit-assist-auth.json` 中关闭或定制：

- `assignToSelfOnCreate`: 设 `false` 则创建后不分配本人。
- `transitionToInProgressOnCreate`: 设 `false` 则创建后不自动改状态。
- `inProgressTransitionNames`: 字符串数组，按你们工作流精确定义目标状态名（如 `["处理中"]`）。

用户确认标题后**推荐一条命令**（含 add/commit，且会给 Issue **写评论**；不要先 `create-issue` 再纯 `git commit`，后者不会走脚本的评论逻辑）：

```bash
node $SKILL_ROOT/scripts/git-jira-commit-assist.js commit \
  --repo-path="$REPO_PATH" \
  --message="<与平时相同的 commit 首行等；脚本会在创建 Issue 后把 Key 写入 footer>" \
  --create-issue --project=<PUB 等> --summary="<4.3 确认的标题>" \
  --issue-type="<4.2 选定的类型，如 Bug>" \
  --json
```

向用户返回 **Issue 链接**与提交摘要（见 Step 6）。标题与类型已在 4.2/4.3 确认过，**不要**再开额外轮次。

> **⚠️ 写操作门禁**：仅在 4.1、4.2、4.3 均确认后才执行上述命令。

---

### Step 5：执行 git commit + 关联 Jira（已有 Issue Key）

```bash
# 推荐（一步：add + commit + Issue 评论，message 须含 Key）
node $SKILL_ROOT/scripts/git-jira-commit-assist.js commit --repo-path="$REPO_PATH" --message="<最终 commit msg>" --json

# 若坚持仅用 git：下方两行不会写 Jira，需自行在 Issue 备注
git -C "$REPO_PATH" add -A
git -C "$REPO_PATH" commit -m "<最终 commit msg>"
```

---

### Step 6：返回结果

向用户展示（新建 Issue 路径须突出 **Issue 链接**）：
```
✓ 提交成功：abc1234f
✓ Jira 任务已关联：AUTH-99
  链接：https://jira.tap4fun.com/browse/AUTH-99
```

然后 **Step 7**（见下）：**默认自动推送**，无需用户再说「推送」或「1」。

### Step 7：推送远端（commit 成功后，默认自动）

**时机**：`git commit` 已成功（`git-jira-commit-assist.js … --json` 返回成功）。

**推送前自检（强制）**：在执行 push 之前，Agent 必须检查最终 commit message 是否包含 `[A-Z][A-Z0-9]+-\d+` 格式的 Issue Key：

- **含 Issue Key** → 正常推送。
- **不含 Issue Key 且非 `--skip-jira` 路径** → **禁止推送**，告知用户「commit message 缺少 Jira Issue Key，请补充后重新提交」，并回到 Step 2 让用户选择关联 / 新建。
- **不含 Issue Key 且用户明确选择了 `--skip-jira`（回 `0` 跳过）** → 允许推送（规范例外，已有用户授权）。

**默认行为（Agent 路径）**：自检通过后，**必须使用 `push` 命令**（自动包含 Step 8 Skill 仓库检测），不要停顿询问：

```bash
node $SKILL_ROOT/scripts/git-jira-commit-assist.js push --repo-path="$REPO_PATH" --json
```

返回 JSON 包含：
- `ok`: 是否成功
- `branch`: 当前分支
- `pushOutput`: push 输出
- `skillRepo.isSkillRepo`: 是否为 Skill 仓库
- `skillRepo.matched`: 当前仓库信息（label/type）
- `skillRepo.other`: 另一个 Skill 仓库信息

`push` 命令会自动处理有无 upstream 的情况（有则 `git push`，无则 `git push -u origin <branch>`）。

**禁止**再提示「回复 1 / 说推送才 push」。**例外**：用户**事先明确说**不要推送、或仓库策略禁止代推时，跳过 Step 7。

> **⚠️ 禁止使用裸 `git push` 代替 `push` 命令**：裸 `git push` 不会触发 Step 8 的 Skill 仓库检测，会导致遗漏同步。

### Step 8：Skill 多仓库同步（push 命令自动检测，Agent 必须处理）

**时机**：Step 7 `push` 命令返回结果后，**Agent 必须检查** `skillRepo.isSkillRepo` 字段。

- 返回 `isSkillRepo: false` → **跳过 Step 8**，流程结束。
- 返回 `isSkillRepo: true` → **必须**进入同步询问，**禁止跳过**。

**已知 Skill 仓库**（脚本内置，无需配置）：
- **openclaw**: `https://git.tap4fun.com/bi-web/yuandan/skills.git`（mono 仓库，skill 是子目录）
- **skillsmp**: `https://git.tap4fun.com/skills/bi-web/<skill-name>.git`（multi 仓库，每个 skill 独立 repo）

**询问用户**（仅当 `isSkillRepo: true` 时）：
```text
检测到当前仓库为 Skill 仓库（openclaw），是否同步到另一个仓库？
1. 同步到 skillsmp（skills/bi-web）
0. 不同步

回序号选择。
```

（若当前推的是 skillsmp，则反过来提示同步到 openclaw。）

**用户回 `1`** → Agent 需要确定 skill 目录名（从本次提交变更的文件路径中提取顶级目录名，如 `moka-hr/SKILL.md` → `moka-hr`）和源文件路径（`$REPO_PATH/<skill-name>/`），然后执行：

```bash
node $SKILL_ROOT/scripts/git-jira-commit-assist.js sync \
  --source-path="$REPO_PATH/<skill-name>" \
  --target-repo="<另一个仓库 URL>" \
  --skill-name="<skill-name>" \
  --message="<与本次相同的 commit message>" \
  --branch="<与本次相同的分支名>" \
  --base-branch="dev" \
  --json
```

向用户展示同步结果（成功/跳过/失败）。

**用户回 `0`** → 跳过，流程结束。

**注意事项**：
- `sync` 命令会自动浅克隆目标仓库到临时目录，完成后清理，不留痕迹。
- 复制时会排除 `credentials`、`__pycache__`、`.pyc`、`node_modules`、`.git` 目录。
- 若目标仓库中该 skill 目录已是最新（无变更），脚本会返回 `skipped: true`，Agent 告知用户「目标仓库已是最新」。

---

## 首次使用：配置 Jira 连接

在本机终端（Cursor 集成终端亦可）复制执行：

```bash
node $SKILL_ROOT/scripts/git-jira-commit-assist.js login
```

等同 `node $SKILL_ROOT/scripts/setup.js`，二者写入同一 `~/.git-jira-commit-assist-auth.json`。

**迁移**：若本机仍有旧版 `~/.git-jira-auth.json`，脚本会**自动读取**；再次执行 `login` 成功后会把配置写到新路径（可稍后手动删旧文件）。

向导**只做**：录入认证 → 调 `/myself` 校验 → 写入配置文件。**不再**在向导里选默认项目或仓库映射；若需 `defaultProject`、`projectMap` 等，保存后**直接编辑**该 JSON。重跑 `login` / `setup` 会更新账号/Token，并尽量保留其它键。

认证文件 `~/.git-jira-commit-assist-auth.json` 示例：
```json
{
  "baseUrl": "https://jira.tap4fun.com",
  "username": "your-username",
  "password": "your-password",
  "defaultProject": "PROJ",
  "defaultIssueType": "Task",
  "assignToSelfOnCreate": true,
  "transitionToInProgressOnCreate": true,
  "inProgressTransitionNames": ["处理中", "In Progress"]
}
```

PAT 版本：
```json
{
  "baseUrl": "https://jira.tap4fun.com",
  "token": "your-pat-token",
  "defaultProject": "PROJ",
  "assignToSelfOnCreate": true,
  "transitionToInProgressOnCreate": true
}
```

---

## CLI 命令速查

```bash
# 最先：校验 Jira 登录（Agent 在 plan / list-projects 之前跑）
node $SKILL_ROOT/scripts/git-jira-commit-assist.js verify-auth --json

# 登录（在本机终端执行）
node $SKILL_ROOT/scripts/git-jira-commit-assist.js login

# Agent 自动化：拉 JSON 计划（变更、项目、相关 Issue、建议 message）
node $SKILL_ROOT/scripts/git-jira-commit-assist.js plan --repo-path=PATH

# 提交（Agent 代跑，勿让用户粘贴）
node $SKILL_ROOT/scripts/git-jira-commit-assist.js commit --repo-path=PATH --message="..." --link-issue=KEY --json
node $SKILL_ROOT/scripts/git-jira-commit-assist.js commit --repo-path=PATH --message="..." --create-issue --project=KEY --summary="标题" --issue-type="Bug" --json
node $SKILL_ROOT/scripts/git-jira-commit-assist.js commit --repo-path=PATH --message="..." --skip-jira --json

# Step 7+8：推送 + 自动检测 Skill 仓库（commit 成功后必须用此命令，禁止裸 git push）
node $SKILL_ROOT/scripts/git-jira-commit-assist.js push --repo-path=PATH --json

# 列出可创建 Issue 的项目（无权限者不返回）
node $SKILL_ROOT/scripts/git-jira-commit-assist.js list-projects

# 获取项目支持的 Issue 类型（仅在 issue_type_incompatible 错误后需要手动查询时使用；正常流程由脚本自动返回）
node $SKILL_ROOT/scripts/git-jira-commit-assist.js list-issuetypes --project=PROJ --json

# Step 1 历史 Jira Key 自动检测（与 commit 建议同步执行，Agent 内部用，纯 git）
git -C "$REPO_PATH" diff --name-only HEAD                        # 未暂存变更文件
git -C "$REPO_PATH" diff --name-only --cached                    # 已暂存变更文件
git -C "$REPO_PATH" log -10 --format="%H|||%B"                   # 近 10 条提交（含完整 body/footer）
git -C "$REPO_PATH" show --name-only --format="" <hash>          # 某提交的变更文件

# 搜索 Issue
node $SKILL_ROOT/scripts/git-jira-commit-assist.js search-issues --project=PROJ --keyword=登录

# 创建 Issue（--issue-type 可选，不传则用 defaultIssueType 或 Task）
node $SKILL_ROOT/scripts/git-jira-commit-assist.js create-issue --project=PROJ --summary="标题" --issue-type="Bug"

# link：兼容旧 hook，无 Jira 写操作（可不装 post-commit）
node $SKILL_ROOT/scripts/git-jira-commit-assist.js link <commit-hash> --message="msg"

# 初始化配置（与 login 相同）
node $SKILL_ROOT/scripts/setup.js

# Step 8：检查当前仓库是否为 Skill 仓库（push 成功后 Agent 自动调用）
node $SKILL_ROOT/scripts/git-jira-commit-assist.js check-skill-repo --repo-url="https://git.tap4fun.com/bi-web/yuandan/skills.git"

# Step 8：同步 Skill 到另一个仓库
node $SKILL_ROOT/scripts/git-jira-commit-assist.js sync --source-path=/path/to/skill --target-repo="https://git.tap4fun.com/skills/bi-web.git" --skill-name=moka-hr --message="feat: ..." --branch=feat_xxx --base-branch=dev --json
```

---

## 常见问题

**要删 Jira Issue / 评论 / 附件？** 本 Skill **默认不代调删除 API**；坚持删除须按「行为规范 → Jira 删除类 API」完成**至少三轮**分轮确认，否则一律拦截。

**401 认证失败**：在本机终端重新执行 `node $SKILL_ROOT/scripts/git-jira-commit-assist.js login`（`verify-auth --json` 会先暴露会话问题，避免空项目列表误判）

**list-projects 为空**：仅在 `verify-auth` 已通过后，才可解读为账号在可见项目上无 CREATE_ISSUES；未校验前应先完成 Step 0

**创建 Issue 失败 400**：该项目无编辑权限，选择其他项目

**自签名证书**：已设置 `rejectUnauthorized: false`，支持内网环境

**工作区有未暂存变更**：按本 Skill 默认执行 `git add -A`，不向用户确认文件范围
