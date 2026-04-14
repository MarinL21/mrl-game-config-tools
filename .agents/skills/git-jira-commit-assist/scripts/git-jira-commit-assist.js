#!/usr/bin/env node
/**
 * git-jira-commit-assist: 规范化 Git 提交 + 自动关联 Jira
 *
 * 命令:
 *   commit                          终端 TUI 交互提交（须 TTY；↑↓ 回车选择）
 *   commit --message="…" …          无交互提交（供 Cursor Agent 代跑）
 *   plan                            输出 JSON 计划（变更、项目、相关 Issue）
 *   link <hash>                     兼容旧 hook（不再写入 Jira「链接到」）
 *   list-projects                   列出可创建 Issue 的项目
 *   search-issues                   搜索 Issue
 *   create-issue                    创建 Issue（默认分配给当前用户并转到处理中）
 *   verify-auth                     校验 Jira 会话（/myself），须先于 list-projects / plan 依赖的 Jira 步骤
 *   login                           建议在终端无参运行（TUI，等同 setup.js）；非 TTY 参数为脚本/自动化保留
 *   push                             git push + 自动检测 Skill 仓库（Step 7 + Step 8 合一）
 *   check-skill-repo                检查仓库 URL 是否为已知 Skill 仓库，返回匹配信息和另一仓库
 *   sync                            将 Skill 目录同步到另一个 Skill 仓库（克隆→复制→提交→推送→清理）
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');
const { execSync, spawnSync } = require('child_process');
require('./ensure-deps')();
const prompts = require('prompts');

const {
  AUTH_FILE,
  getAuthPathForRead,
  authFileExists,
  loadOrInitConfig,
  applyCredentials,
  writeAuthFile,
  DEFAULT_BASE_URL,
} = require('./auth-utils');

const ASSIST_CLI_JS = path.join(__dirname, 'git-jira-commit-assist.js');
const SETUP_JS = path.join(__dirname, 'setup.js');

/** 对外统一话术：请用户在本机终端复制执行（TUI 交互登录） */
function jiraAuthFixHint() {
  return `请在本机终端复制并执行：node ${ASSIST_CLI_JS} login`;
}

// ─── 工具函数 ────────────────────────────────────────────────────────────────

function loadAuth() {
  if (!authFileExists()) {
    console.error(`未找到认证配置。${jiraAuthFixHint()}`);
    process.exit(1);
  }
  const config = JSON.parse(fs.readFileSync(getAuthPathForRead(), 'utf8'));
  if (!config.baseUrl) config.baseUrl = DEFAULT_BASE_URL;
  return config;
}

function makeHeaders(auth) {
  const headers = { 'Content-Type': 'application/json', 'Accept': 'application/json' };
  if (auth.token) {
    headers['Authorization'] = `Bearer ${auth.token}`;
  } else {
    headers['Authorization'] = `Basic ${Buffer.from(`${auth.username}:${auth.password}`).toString('base64')}`;
  }
  return headers;
}

function request(url, options, body) {
  return new Promise((resolve, reject) => {
    const parsed = new URL(url);
    const lib = parsed.protocol === 'https:' ? https : http;
    const req = lib.request({
      hostname: parsed.hostname,
      port: parsed.port || (parsed.protocol === 'https:' ? 443 : 80),
      path: parsed.pathname + parsed.search,
      method: options.method || 'GET',
      headers: options.headers || {},
      rejectUnauthorized: false,
    }, (res) => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try { resolve({ status: res.statusCode, body: data ? JSON.parse(data) : {} }); }
        catch { resolve({ status: res.statusCode, body: data }); }
      });
    });
    req.on('error', reject);
    if (body) req.write(typeof body === 'string' ? body : JSON.stringify(body));
    req.end();
  });
}

function git(args, cwd) {
  try {
    return execSync(`git ${args}`, { cwd, encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] }).trim();
  } catch (e) {
    return '';
  }
}

function extractIssueKeys(message) {
  const matches = message.match(/[A-Z][A-Z0-9_]+-\d+/g);
  return matches ? [...new Set(matches)] : [];
}

/** 团队规范：Jira Key 单独作 footer，与上文空一行（subject ≤50、Key 不占首行） */
function appendJiraKeyAsFooter(message, issueKey) {
  const msg = (message || '').trim();
  const key = (issueKey || '').trim();
  if (!key) return msg;
  if (extractIssueKeys(msg).includes(key)) return msg;
  return `${msg}\n\n${key}`;
}

function getRepoName(repoUrl) {
  if (!repoUrl) return null;
  const match = repoUrl.match(/\/([^/]+?)(\.git)?$/);
  return match ? match[1].toLowerCase() : null;
}

// ─── Jira API ────────────────────────────────────────────────────────────────

async function getAllProjects(auth) {
  try {
    // 先尝试 /project/search（Jira 7.x+）
    const res = await request(
      `${auth.baseUrl}/rest/api/2/project/search?maxResults=200`,
      { headers: makeHeaders(auth) }
    );
    if (res.status === 200 && res.body.values) return res.body.values;
    // 降级
    const res2 = await request(`${auth.baseUrl}/rest/api/2/project`, { headers: makeHeaders(auth) });
    return res2.status === 200 && Array.isArray(res2.body) ? res2.body : [];
  } catch { return []; }
}

async function checkCreatePerm(auth, projectKey) {
  try {
    const res = await request(
      `${auth.baseUrl}/rest/api/2/mypermissions?projectKey=${projectKey}&permissions=CREATE_ISSUES`,
      { headers: makeHeaders(auth) }
    );
    return res.status === 200 &&
      res.body.permissions?.CREATE_ISSUES?.havePermission === true;
  } catch { return true; }
}

async function getAllProjectsWithPerm(auth) {
  const projects = await getAllProjects(auth);
  if (!projects.length) return [];
  const CONCURRENCY = 10;
  const results = [];
  for (let i = 0; i < projects.length; i += CONCURRENCY) {
    const chunk = projects.slice(i, i + CONCURRENCY);
    const perms = await Promise.all(chunk.map(p => checkCreatePerm(auth, p.key)));
    chunk.forEach((p, idx) => results.push({ key: p.key, name: p.name, canCreate: perms[idx] }));
  }
  return results;
}

async function getIssueTypes(auth, projectKey) {
  try {
    const res = await request(
      `${auth.baseUrl}/rest/api/2/project/${projectKey}`,
      { headers: makeHeaders(auth) }
    );
    if (res.status === 200 && Array.isArray(res.body.issueTypes)) {
      return res.body.issueTypes
        .filter(t => !t.subtask)
        .map(t => ({ id: t.id, name: t.name, description: t.description || '' }));
    }
  } catch { /* ignore */ }
  return [];
}

async function searchIssues(auth, projectKey, keyword) {
  try {
    const jql = encodeURIComponent(
      `project = ${projectKey} AND statusCategory != Done AND (summary ~ "${keyword}" OR description ~ "${keyword}") ORDER BY updated DESC`
    );
    const res = await request(
      `${auth.baseUrl}/rest/api/2/search?jql=${jql}&maxResults=5&fields=summary,status,assignee`,
      { headers: makeHeaders(auth) }
    );
    if (res.status === 200 && res.body.issues) return res.body.issues;
    return [];
  } catch { return []; }
}

async function getMyself(auth) {
  try {
    const res = await request(`${auth.baseUrl}/rest/api/2/myself`, { headers: makeHeaders(auth) });
    if (res.status === 200 && res.body && typeof res.body === 'object') return res.body;
  } catch { /* ignore */ }
  return null;
}

/** 调用 /myself 判断是否已登录；未登录时项目列表常为空中易误判为无权限 */
async function checkJiraSession(auth) {
  try {
    const res = await request(`${auth.baseUrl}/rest/api/2/myself`, { headers: makeHeaders(auth) });
    if (res.status === 200 && res.body && typeof res.body === 'object') {
      return {
        ok: true,
        user: {
          displayName: res.body.displayName || res.body.name || '',
          name: res.body.name || '',
          emailAddress: res.body.emailAddress || '',
        },
      };
    }
    const detail =
      typeof res.body === 'object' ? JSON.stringify(res.body).slice(0, 240) : String(res.body || '');
    return { ok: false, status: res.status, detail };
  } catch (e) {
    return { ok: false, status: 0, detail: e.message || 'network_error' };
  }
}

async function assignIssueToSelf(auth, issueKey) {
  const myself = await getMyself(auth);
  if (!myself) return { ok: false, detail: 'no_myself' };
  let body = null;
  if (myself.accountId) body = { accountId: myself.accountId };
  else if (myself.name) body = { name: myself.name };
  if (!body) return { ok: false, detail: 'no_assignee_identifier' };
  const url = `${auth.baseUrl}/rest/api/2/issue/${encodeURIComponent(issueKey)}/assignee`;
  let res = await request(url, { method: 'PUT', headers: makeHeaders(auth) }, body);
  if (res.status === 204 || res.status === 200) return { ok: true };
  if (myself.accountId && myself.name) {
    res = await request(url, { method: 'PUT', headers: makeHeaders(auth) }, { name: myself.name });
    if (res.status === 204 || res.status === 200) return { ok: true };
  }
  const errText = typeof res.body === 'object' ? JSON.stringify(res.body) : String(res.body || '');
  return { ok: false, detail: errText.slice(0, 500), status: res.status };
}

async function getIssueTransitions(auth, issueKey) {
  try {
    const res = await request(
      `${auth.baseUrl}/rest/api/2/issue/${encodeURIComponent(issueKey)}/transitions`,
      { headers: makeHeaders(auth) }
    );
    if (res.status === 200 && Array.isArray(res.body.transitions)) return res.body.transitions;
  } catch { /* ignore */ }
  return [];
}

function pickInProgressTransition(transitions, auth) {
  if (!transitions.length) return null;
  const custom = auth.inProgressTransitionNames;
  const nameHints = Array.isArray(custom) && custom.length
    ? custom
    : ['处理中', 'In Progress', '进行中', 'Doing'];
  const norm = (s) => (s || '').trim();
  for (const t of transitions) {
    const toName = norm(t.to?.name);
    const trName = norm(t.name);
    for (const hint of nameHints) {
      if (!hint) continue;
      if (toName === hint || trName === hint) return t;
      if (toName.includes(hint) || trName.includes(hint)) return t;
    }
  }
  const fuzzy = /处理中|in\s*progress|进行中|\bdoing\b/i;
  for (const t of transitions) {
    if (fuzzy.test(`${t.to?.name || ''} ${t.name || ''}`)) return t;
  }
  for (const t of transitions) {
    if (t.to?.statusCategory?.key === 'indeterminate') return t;
  }
  return null;
}

async function doTransition(auth, issueKey, transitionId) {
  const res = await request(
    `${auth.baseUrl}/rest/api/2/issue/${encodeURIComponent(issueKey)}/transitions`,
    { method: 'POST', headers: makeHeaders(auth) },
    { transition: { id: String(transitionId) } }
  );
  return res.status === 204 || res.status === 200;
}

/**
 * 创建 Issue 之后：默认分配给当前登录用户，并转换到「处理中」类状态（与工作流可用转换匹配）。
 * ~/.git-jira-commit-assist-auth.json（或旧版 ~/.git-jira-auth.json）可设 assignToSelfOnCreate / transitionToInProgressOnCreate 为 false 关闭；
 * inProgressTransitionNames 可写死目标状态名数组以适配自定义工作流。
 */
async function postCreateIssueAssignAndTransition(auth, issueKey, execOpts = {}) {
  const quiet = !!execOpts.quiet;
  /** @type {{ assignedToSelf: boolean, transitionedToInProgress: boolean, assignDetail?: string, transitionDetail?: string }} */
  const meta = {
    assignedToSelf: false,
    transitionedToInProgress: false,
  };
  if (auth.assignToSelfOnCreate === false) {
    meta.assignDetail = 'skipped_by_config';
  } else {
    const ar = await assignIssueToSelf(auth, issueKey);
    if (ar.ok) meta.assignedToSelf = true;
    else {
      meta.assignDetail = ar.detail || 'assign_failed';
      if (!quiet) console.warn(`[git-jira-commit-assist] 创建后分配给本人失败: ${meta.assignDetail}`);
    }
  }
  if (auth.transitionToInProgressOnCreate === false) {
    meta.transitionDetail = 'skipped_by_config';
  } else {
    const transitions = await getIssueTransitions(auth, issueKey);
    const t = pickInProgressTransition(transitions, auth);
    if (!t) {
      meta.transitionDetail = 'no_matching_transition';
      if (!quiet) {
        console.warn('[git-jira-commit-assist] 未找到「处理中」类工作流转换，请在 Jira 中手动改状态');
      }
    } else {
      const ok = await doTransition(auth, issueKey, t.id);
      if (ok) meta.transitionedToInProgress = true;
      else {
        meta.transitionDetail = 'transition_request_failed';
        if (!quiet) console.warn('[git-jira-commit-assist] 转换到处理中失败');
      }
    }
  }
  return meta;
}

async function createIssue(auth, projectKey, summary, description, execOpts = {}) {
  const resolvedType = execOpts.issueType || auth.defaultIssueType || 'Task';
  const fields = {
    project: { key: projectKey },
    summary,
    description,
    issuetype: { name: resolvedType },
  };
  const byProj = auth.createIssueExtraFieldsByProject;
  if (byProj && typeof byProj === 'object' && byProj[projectKey]) {
    Object.assign(fields, byProj[projectKey]);
  }
  // COST 等事项类型强制「所属项目」；可用认证 JSON 中 costDefaultBelongProjectKey 覆盖
  if (projectKey === 'COST' && !fields.customfield_12914) {
    const k = auth.costDefaultBelongProjectKey || 'PUB';
    fields.customfield_12914 = { key: k };
  }
  const body = { fields };
  const res = await request(`${auth.baseUrl}/rest/api/2/issue`, { method: 'POST', headers: makeHeaders(auth) }, body);
  if (res.status !== 201) {
    const err = new Error(`创建 Issue 失败 [${res.status}]: ${JSON.stringify(res.body)}`);
    err.httpStatus = res.status;
    err.responseBody = res.body;
    // 判断是否为 issuetype 不兼容（400 且错误字段含 issuetype）
    const errs = res.body && res.body.errors;
    err.isIssueTypeIncompatible = res.status === 400 && !!(
      (errs && errs.issuetype) ||
      (res.body && JSON.stringify(res.body).toLowerCase().includes('issuetype'))
    );
    throw err;
  }
  const issue = res.body;
  if (!execOpts.skipPostCreate) {
    issue.postCreate = await postCreateIssueAssignAndTransition(auth, issue.key, execOpts);
  }
  return issue;
}

async function addComment(auth, issueKey, comment) {
  const res = await request(
    `${auth.baseUrl}/rest/api/2/issue/${issueKey}/comment`,
    { method: 'POST', headers: makeHeaders(auth) },
    { body: comment }
  );
  return res.status === 201;
}

// ─── AI 辅助（由 Claude 在 skill 流程中处理，此处提供数据收集工具）────────────

/**
 * 收集提交所需的上下文信息
 */
function collectGitContext(repoPath) {
  const repoUrl = git('remote get-url origin', repoPath);
  const branch = git('rev-parse --abbrev-ref HEAD', repoPath);

  // 优先用暂存区，没有则用工作区
  let diff = git('diff --cached', repoPath);
  let stat = git('diff --cached --stat', repoPath);
  let hasStaged = !!diff.trim();

  if (!hasStaged) {
    diff = git('diff', repoPath);
    stat = git('diff --stat', repoPath);
  }

  // 仅新增未跟踪文件时 git diff 为空，但仍应允许走 commit 流程
  if (!diff.trim()) {
    const porcelain = git('status --porcelain', repoPath);
    if (porcelain.trim()) {
      diff = porcelain;
      stat = porcelain
        .split('\n')
        .slice(0, 20)
        .join('\n');
    }
  }

  const recentCommits = git('log --oneline -5', repoPath);

  return { repoUrl, branch, diff, stat, hasStaged, recentCommits, repoName: getRepoName(repoUrl) };
}

// ─── AI 项目匹配（基于仓库名 + commit msg 关键词）────────────────────────────

function aiMatchProject(projects, repoName, commitMsg) {
  if (!projects.length) return null;

  const normalize = s => (s || '').toLowerCase().replace(/[-_\s]/g, '');
  const repoNorm = normalize(repoName);
  const msgNorm = normalize(commitMsg);

  // 1. projectMap 优先
  // （在 commit 流程中由 auth.projectMap 处理，这里做纯匹配）

  // 2. key 或 name 与仓库名精确/包含匹配
  for (const p of projects) {
    const keyNorm = normalize(p.key);
    const nameNorm = normalize(p.name);
    if (repoNorm && (keyNorm === repoNorm || nameNorm.includes(repoNorm) || repoNorm.includes(nameNorm))) {
      return p;
    }
  }

  // 3. commit msg 关键词匹配项目名
  for (const p of projects) {
    const nameNorm = normalize(p.name);
    if (msgNorm && msgNorm.includes(nameNorm) && nameNorm.length > 2) {
      return p;
    }
  }

  // 4. 仓库名前缀匹配 key
  if (repoNorm) {
    const prefix = repoNorm.substring(0, 4).toUpperCase();
    const found = projects.find(p => p.key.startsWith(prefix));
    if (found) return found;
  }

  return null;
}

function resolveMatchedProjectForSearch(auth, projects, ctx) {
  let matchedProject = null;
  if (auth.projectMap && ctx.repoName) {
    const mapped = auth.projectMap[ctx.repoName] || auth.projectMap[ctx.repoName.toLowerCase()];
    if (mapped) matchedProject = projects.find(p => p.key === mapped) || { key: mapped, name: mapped, canCreate: true };
  }
  if (!matchedProject) matchedProject = aiMatchProject(projects, ctx.repoName, '');
  if (!matchedProject && auth.defaultProject) {
    matchedProject = projects.find(p => p.key === auth.defaultProject) || { key: auth.defaultProject, name: auth.defaultProject, canCreate: true };
  }
  return matchedProject;
}

async function loadJiraPlanContext(repoPath) {
  const auth = loadAuth();
  const ctx = collectGitContext(repoPath);
  if (!ctx.diff.trim()) {
    return { error: 'no_changes', auth, ctx };
  }
  const session = await checkJiraSession(auth);
  if (!session.ok) {
    return {
      error: 'jira_auth_failed',
      auth,
      ctx,
      httpStatus: session.status,
      detail: session.detail || '',
    };
  }
  const projects = await getAllProjectsWithPerm(auth);
  const matchedProject = resolveMatchedProjectForSearch(auth, projects, ctx);
  let relatedIssues = [];
  if (matchedProject) {
    const keyword = (ctx.stat.match(/\w{4,}/g) || []).slice(0, 3).join(' ') || ctx.branch;
    relatedIssues = await searchIssues(auth, matchedProject.key, keyword);
  }
  const suggestedProject =
    aiMatchProject(projects.filter(p => p.canCreate), ctx.repoName, '') ||
    projects.find(p => p.canCreate) ||
    null;
  const suggestedMessage = `fix: ${ctx.branch}`;
  return { auth, ctx, projects, matchedProject, relatedIssues, suggestedProject, suggestedMessage };
}

async function runGitAddCommitAndLink(auth, ctx, repoPath, finalMsg) {
  execSync('git add -A', { cwd: repoPath });
  const result = spawnSync('git', ['commit', '-m', finalMsg], { cwd: repoPath, encoding: 'utf8' });
  if (result.status !== 0) {
    return { ok: false, error: result.stderr || result.stdout || 'git commit failed' };
  }
  const commitHash = git('rev-parse HEAD', repoPath);
  const allKeys = [...extractIssueKeys(finalMsg)];
  if (allKeys.length) {
    process.stdout.write(`\n正在关联 Jira Issue: ${allKeys.join(', ')}...`);
    for (const key of allKeys) {
      const comment = `*Git 提交关联*\n\nCommit: \`${commitHash.substring(0, 8)}\`\n分支: ${ctx.branch}\n\n{noformat}\n${finalMsg}\n{noformat}`;
      await addComment(auth, key, comment);
    }
    console.log(' 完成');
  }
  const urls = allKeys.map(k => `${auth.baseUrl}/browse/${k}`);
  return {
    ok: true,
    commitHash,
    stdout: result.stdout.trim(),
    linkedKeys: allKeys,
    urls,
  };
}

// ─── plan：供 Agent 拉 JSON，无终端交互 ────────────────────────────────────────

async function cmdPlan(repoPath) {
  const data = await loadJiraPlanContext(repoPath);
  if (data.error) {
    const err = { ok: false, error: data.error };
    if (data.error === 'jira_auth_failed') {
      err.httpStatus = data.httpStatus;
      err.detail = data.detail;
      err.hint = jiraAuthFixHint();
    }
    return err;
  }
  const { ctx, projects, matchedProject, relatedIssues, suggestedProject, suggestedMessage } = data;
  return {
    ok: true,
    repoPath: path.resolve(repoPath),
    branch: ctx.branch,
    stat: ctx.stat,
    repoUrl: ctx.repoUrl,
    repoName: ctx.repoName,
    suggestedMessage,
    matchedProject: matchedProject && { key: matchedProject.key, name: matchedProject.name },
    suggestedProjectForCreate: suggestedProject
      ? { key: suggestedProject.key, name: suggestedProject.name, canCreate: suggestedProject.canCreate !== false }
      : null,
    projects: projects.map(p => ({ key: p.key, name: p.name, canCreate: p.canCreate })),
    relatedIssues: relatedIssues.map(i => ({
      key: i.key,
      summary: i.fields.summary,
      status: i.fields.status?.name || '',
    })),
  };
}

// ─── commit --message=… 无交互：供 Agent 代跑，用户只在对话里确认 ─────────────

async function cmdCommitAutomation(repoPath, opts) {
  const data = await loadJiraPlanContext(repoPath);
  if (data.error) {
    const err = { ok: false, error: data.error };
    if (opts.json) console.log(JSON.stringify(err));
    else console.error('没有检测到代码变更');
    process.exit(1);
  }
  const { auth, ctx } = data;
  const projects = data.projects;

  const rawMsg = opts.message;
  const message = typeof rawMsg === 'string' ? rawMsg.trim() : '';
  if (!message) {
    const err = { ok: false, error: 'missing_message' };
    console.log(opts.json ? JSON.stringify(err) : '无交互提交需要 --message="..."');
    process.exit(1);
  }

  const skipJira = !!opts['skip-jira'];
  const linkIssue = opts['link-issue'] || opts['issue-key'] || '';
  const wantCreate = !!(opts['create-issue'] || opts['create']);

  if (wantCreate && linkIssue) {
    const err = { ok: false, error: 'conflict_create_and_link' };
    console.log(opts.json ? JSON.stringify(err) : '不能同时指定 --create-issue 与 --link-issue');
    process.exit(1);
  }

  let finalMsg = message;
  let createdIssueKey = null;
  let jiraPostCreate = null;

  if (wantCreate) {
    let projectKey = opts.project || '';
    if (!projectKey) {
      const err = { ok: false, error: 'missing_project_for_create' };
      console.log(opts.json ? JSON.stringify(err) : '创建 Issue 需要 --project=KEY');
      process.exit(1);
    }
    const p = projects.find(x => x.key === projectKey);
    if (!p || !p.canCreate) {
      const err = { ok: false, error: 'bad_project_or_no_create_perm' };
      console.log(opts.json ? JSON.stringify(err) : `项目 ${projectKey} 不可创建 Issue`);
      process.exit(1);
    }
    const firstLine = message.split('\n')[0].substring(0, 200);
    const summary = (opts.summary && String(opts.summary).trim()) || firstLine;
    const description = `由 Git 提交自动创建（Agent 无交互）\n\n分支: ${ctx.branch}\n\n${message}`;
    const issueType = opts['issue-type'] || opts['issuetype'] || null;
    try {
      const created = await createIssue(auth, projectKey, summary, description, { quiet: !!opts.json, issueType });
      createdIssueKey = created.key;
      jiraPostCreate = created.postCreate || null;
      finalMsg = appendJiraKeyAsFooter(message, createdIssueKey);
    } catch (e) {
      // 类型不兼容时返回可用类型列表，让 Agent 引导用户重选
      if (e.isIssueTypeIncompatible) {
        const availableTypes = await getIssueTypes(auth, projectKey);
        const err = {
          ok: false,
          error: 'issue_type_incompatible',
          usedType: issueType || auth.defaultIssueType || 'Task',
          detail: e.message,
          availableTypes,
          hint: availableTypes.length
            ? `请用 --issue-type=<类型名> 重试，可选：${availableTypes.map(t => t.name).join('、')}`
            : '请检查项目配置或在 Jira 中确认支持的 Issue 类型',
        };
        console.log(opts.json ? JSON.stringify(err) : `创建 Issue 失败：类型「${err.usedType}」与项目不兼容。\n${err.hint}`);
        process.exit(1);
      }
      const err = { ok: false, error: 'create_issue_failed', detail: e.message };
      console.log(opts.json ? JSON.stringify(err) : e.message);
      process.exit(1);
    }
  } else if (linkIssue) {
    const keysIn = extractIssueKeys(message);
    if (!keysIn.includes(linkIssue)) {
      finalMsg = appendJiraKeyAsFooter(message, linkIssue);
    }
  } else if (!skipJira) {
    const keys = extractIssueKeys(message);
    if (!keys.length) {
      const err = { ok: false, error: 'no_issue_key_use_skip_or_create_or_link' };
      console.log(
        opts.json
          ? JSON.stringify(err)
          : 'message 中无 Issue Key：请使用 --link-issue=KEY、或 --create-issue --project=…、或 --skip-jira'
      );
      process.exit(1);
    }
  }

  const result = await runGitAddCommitAndLink(auth, ctx, repoPath, finalMsg);
  if (!result.ok) {
    const err = { ok: false, error: 'git_commit_failed', detail: result.error };
    console.log(opts.json ? JSON.stringify(err) : result.error);
    process.exit(1);
  }

  const urlSet = new Set(result.urls || []);
  if (createdIssueKey) urlSet.add(`${auth.baseUrl}/browse/${createdIssueKey}`);
  const out = {
    ok: true,
    commitHash: result.commitHash,
    commitShort: result.commitHash.substring(0, 8),
    message: finalMsg,
    createdIssueKey,
    linkedKeys: result.linkedKeys,
    issueUrls: [...urlSet],
  };
  if (jiraPostCreate) out.jiraPostCreate = jiraPostCreate;

  if (opts.json) {
    console.log(JSON.stringify(out, null, 2));
  } else {
    console.log(result.stdout);
    console.log('\n──────────────────────────────────────────────');
    console.log(`✓ 提交成功: ${out.commitShort}`);
    if (createdIssueKey) {
      console.log(`✓ 已创建 Jira: ${createdIssueKey}\n  ${auth.baseUrl}/browse/${createdIssueKey}`);
      if (jiraPostCreate) {
        if (jiraPostCreate.assignedToSelf) console.log('  · 已分配给本人');
        if (jiraPostCreate.transitionedToInProgress) console.log('  · 已转换到处理中');
      }
    }
    out.linkedKeys.forEach(k => console.log(`✓ 已关联: ${auth.baseUrl}/browse/${k}`));
    console.log('──────────────────────────────────────────────\n');
  }
}

// ─── 主流程：终端 TUI 交互式提交（↑↓ 选择，回车确认；confirm 用 Y/n）────────

const promptOpts = {
  onCancel: () => {
    console.log('\n已取消');
    process.exit(0);
  },
};

async function cmdCommit(repoPath) {
  const auth = loadAuth();

  if (!process.stdin.isTTY || !process.stdout.isTTY) {
    console.error(
      '交互式 TUI 需要真实 TTY（stdin/stdout 均为终端）。\n' +
        'Cursor Agent「代跑命令」的环境通常不是 TTY，此处无法使用 ↑↓ 选单。\n\n' +
        '请任选其一：\n' +
        '  1) 在本机 Cursor 集成终端或「Tasks: Run Task → git-jira-commit-assist: commit」里运行本命令（无 --message）；\n' +
        '  2) 或使用无交互：node git-jira-commit-assist.js commit --repo-path=... --message="..." [--link-issue=KEY|--create-issue ...|--skip-jira] --json\n'
    );
    process.exit(1);
  }

  // Step 1: 收集 git 上下文
  const ctx = collectGitContext(repoPath);

  if (!ctx.diff.trim()) {
    console.log('没有检测到代码变更（暂存区和工作区均为空）');
    return;
  }

  console.log('\n── 代码变更摘要 ──────────────────────────────');
  console.log(ctx.stat || '（无统计信息）');
  console.log('──────────────────────────────────────────────\n');
  console.log('终端操作: 列表用 ↑↓ 移动，回车确认；多选用空格切换。\n');

  process.stdout.write('正在校验 Jira 登录...');
  const session = await checkJiraSession(auth);
  if (!session.ok) {
    console.log(`\nJira 登录无效或已过期（HTTP ${session.status}）。${jiraAuthFixHint()}`);
    process.exit(1);
  }
  console.log(' 通过');

  // Step 2: 拉取 Jira 项目列表
  process.stdout.write('正在拉取 Jira 项目列表...');
  const projects = await getAllProjectsWithPerm(auth);
  console.log(` 找到 ${projects.length} 个项目`);

  const matchedProject = resolveMatchedProjectForSearch(auth, projects, ctx);

  // Step 3: 搜索相关 open issues
  let relatedIssues = [];
  if (matchedProject) {
    process.stdout.write(`正在搜索 ${matchedProject.key} 相关 Issue...`);
    const keyword = (ctx.stat.match(/\w{4,}/g) || []).slice(0, 3).join(' ') || ctx.branch;
    relatedIssues = await searchIssues(auth, matchedProject.key, keyword);
    console.log(` 找到 ${relatedIssues.length} 个`);
  }

  let pickedIssueKey = '';
  if (relatedIssues.length) {
    const issueChoices = relatedIssues.map(issue => {
      const status = issue.fields.status?.name || '';
      const sum = issue.fields.summary || '';
      return {
        title: `${issue.key}  ${sum}`.slice(0, 120),
        description: status ? `状态: ${status}` : undefined,
        value: issue.key,
      };
    });
    issueChoices.push({ title: '— 不关联已有 Issue —', value: '__none__' });

    const ans = await prompts({
      type: 'select',
      name: 'picked',
      message: '关联已有 Jira Issue',
      choices: issueChoices,
      hint: '↑↓ 回车',
    }, promptOpts);
    if (ans.picked === undefined) return;
    pickedIssueKey = ans.picked === '__none__' ? '' : ans.picked;
  }

  const initialMsg =
    pickedIssueKey ||
    `fix: ${ctx.branch}`;

  const msgAns = await prompts({
    type: 'text',
    name: 'userMsg',
    message: 'Commit message',
    initial: initialMsg,
  }, promptOpts);

  let userMsg = (msgAns.userMsg || '').trim();
  if (!userMsg) {
    console.log('已取消（message 不能为空）');
    return;
  }
  if (pickedIssueKey) {
    const keysIn = extractIssueKeys(userMsg);
    if (!keysIn.includes(pickedIssueKey)) {
      userMsg = appendJiraKeyAsFooter(userMsg, pickedIssueKey);
    }
  }

  let finalMsg = userMsg;
  let createdIssueKey = null;
  let jiraPostCreateTui = null;
  let issueKeys = extractIssueKeys(userMsg);

  if (issueKeys.length > 0) {
    console.log(`\n检测到 Issue Key: ${issueKeys.join(', ')} → 将关联后提交`);
  } else {
    const suggestedProject = aiMatchProject(projects.filter(p => p.canCreate), ctx.repoName, userMsg)
      || projects.find(p => p.canCreate);

    let targetProject = null;

    if (suggestedProject && suggestedProject.canCreate !== false) {
      const c = await prompts({
        type: 'confirm',
        name: 'yes',
        message: `在 [${suggestedProject.key}] ${suggestedProject.name} 创建新 Issue？`,
        initial: true,
      }, promptOpts);
      if (c.yes) targetProject = suggestedProject;
    }

    if (!targetProject) {
      const creatableProjects = projects.filter(p => p.canCreate);
      if (!creatableProjects.length) {
        console.log('\n没有可创建 Issue 的项目，将不关联 Jira 继续提交。');
      } else {
        const skipTitle = '— 不创建 Issue，仅提交 —';
        const sel = await prompts({
          type: 'select',
          name: 'projKey',
          message: '选择要创建 Issue 的项目',
          choices: [
            ...creatableProjects.map(p => ({
              title: `[${p.key}] ${p.name}`.slice(0, 100),
              value: p.key,
            })),
            { title: skipTitle, value: '__skip__' },
          ],
          hint: '↑↓ 回车',
        }, promptOpts);
        if (sel.projKey === undefined) return;
        if (sel.projKey !== '__skip__') {
          targetProject = creatableProjects.find(p => p.key === sel.projKey) || null;
        }
      }
    }

    if (targetProject) {
      const firstLine = userMsg.split('\n')[0].substring(0, 200);

      const titleAns = await prompts({
        type: 'text',
        name: 'summary',
        message: '新 Issue 标题',
        initial: firstLine,
      }, promptOpts);
      const summary = (titleAns.summary || '').trim() || firstLine;
      const description = `由 Git 提交自动创建\n\n分支: ${ctx.branch}\n\n${userMsg}`;
      process.stdout.write(`\n正在创建 Jira 任务 [${targetProject.key}]...`);
      try {
        // 先用默认类型尝试，失败且为类型不兼容时才让用户选择
        let issueTypeToUse = auth.defaultIssueType || 'Task';
        let created;
        try {
          created = await createIssue(auth, targetProject.key, summary, description, { quiet: true, issueType: issueTypeToUse });
        } catch (typeErr) {
          if (!typeErr.isIssueTypeIncompatible) throw typeErr;
          // 类型不兼容：拉取可用类型让用户选
          console.log(`\n默认类型「${issueTypeToUse}」与项目不兼容，正在获取可用类型...`);
          const issueTypes = await getIssueTypes(auth, targetProject.key);
          if (!issueTypes.length) throw typeErr;
          const typeAns = await prompts({
            type: 'select',
            name: 'issueType',
            message: '选择 Issue 类型',
            choices: issueTypes.map(t => ({
              title: t.description ? `${t.name}  (${t.description})` : t.name,
              value: t.name,
            })),
            hint: '↑↓ 回车',
          }, promptOpts);
          if (typeAns.issueType === undefined) return;
          issueTypeToUse = typeAns.issueType;
          process.stdout.write(`\n正在创建 Jira 任务 [${targetProject.key}] (${issueTypeToUse})...`);
          created = await createIssue(auth, targetProject.key, summary, description, { quiet: true, issueType: issueTypeToUse });
        }
        createdIssueKey = created.key;
        jiraPostCreateTui = created.postCreate || null;
        finalMsg = appendJiraKeyAsFooter(userMsg, createdIssueKey);
        const pc = jiraPostCreateTui;
        let extra = '';
        if (pc?.assignedToSelf) extra += ' · 已分配本人';
        if (pc?.transitionedToInProgress) extra += ' · 已处理中';
        console.log(` 已创建 ${createdIssueKey}${extra}`);
      } catch (e) {
        console.log(`\n创建失败: ${e.message}，继续提交（无新 Key）`);
        finalMsg = userMsg;
      }
    }
  }

  issueKeys = extractIssueKeys(finalMsg);
  console.log(`\n── 准备提交 ──────────────────────────────────\n${finalMsg}\n`);

  const doCommit = await prompts({
    type: 'confirm',
    name: 'go',
    message: '执行 git add -A 并 commit？',
    initial: true,
  }, promptOpts);

  if (!doCommit.go) {
    console.log('已取消');
    return;
  }

  console.log('已暂存所有变更 (git add -A)');

  const commitResult = await runGitAddCommitAndLink(auth, ctx, repoPath, finalMsg);
  if (!commitResult.ok) {
    console.error('提交失败:', commitResult.error);
    process.exit(1);
  }
  console.log(commitResult.stdout.trim());

  const commitHash = commitResult.commitHash;
  const allKeys = commitResult.linkedKeys;

  console.log('\n──────────────────────────────────────────────');
  console.log(`✓ 提交成功: ${commitHash.substring(0, 8)}`);
  if (createdIssueKey) {
    console.log(`✓ 已创建 Jira 任务: ${createdIssueKey}`);
    console.log(`  链接: ${auth.baseUrl}/browse/${createdIssueKey}`);
    if (jiraPostCreateTui?.assignedToSelf) console.log('  · 已分配给本人');
    if (jiraPostCreateTui?.transitionedToInProgress) console.log('  · 已转换到处理中');
  }
  if (allKeys.length) {
    allKeys.forEach(k => console.log(`✓ 已关联: ${auth.baseUrl}/browse/${k}`));
  }
  console.log('──────────────────────────────────────────────\n');
}

// ─── link 命令 ───────────────────────────────────────────────────────────────

/** 兼容旧 post-commit：不再调用 Jira remotelink（界面「链接到」）。关联改由 commit 流程内评论完成。 */
async function cmdLink({ message }) {
  const issueKeys = extractIssueKeys(message || '');
  if (!issueKeys.length) {
    console.log('[git-jira-commit-assist] commit msg 中未找到 Issue Key，跳过关联');
  }
}

function readStdinUtf8() {
  return new Promise((resolve, reject) => {
    const chunks = [];
    process.stdin.setEncoding('utf8');
    process.stdin.on('data', (c) => chunks.push(c));
    process.stdin.on('end', () => resolve(chunks.join('').trim()));
    process.stdin.on('error', reject);
  });
}

/**
 * TUI：无参数且 stdin/stdout 为 TTY 时委派 setup.js（↑↓ 选单 + 掩码输入）。
 * 非 TTY / Agent：--stdin 接收一行 JSON（username+password 或 token），或命令行 --token / --username+--password。
 */
async function cmdLogin(opts) {
  const jsonOut = !!opts.json;
  const isUiTty = process.stdin.isTTY && process.stdout.isTTY;

  const tokenArg = typeof opts.token === 'string' ? opts.token.trim() : '';
  const userArg = typeof opts.username === 'string' ? opts.username.trim() : '';
  const hasTokenArg = tokenArg.length > 0;
  const hasUserPassArg =
    userArg.length > 0 && opts.password !== undefined && opts.password !== true;
  const passwordArg =
    opts.password !== undefined && opts.password !== true ? String(opts.password) : '';

  const hasArgCreds = hasTokenArg || hasUserPassArg;

  if (isUiTty && !opts.stdin && !hasArgCreds) {
    const r = spawnSync(process.execPath, [SETUP_JS], { stdio: 'inherit' });
    process.exit(r.status === 0 ? 0 : r.status || 1);
    return;
  }

  let creds;
  const shouldReadStdin = opts.stdin || (!isUiTty && !hasArgCreds);

  if (shouldReadStdin && !hasArgCreds) {
    const raw = await readStdinUtf8();
    if (!raw) {
      const err = {
        ok: false,
        error: 'empty_stdin',
        hint: jiraAuthFixHint(),
      };
      if (jsonOut) console.log(JSON.stringify(err));
      else console.error('stdin 为空');
      process.exit(1);
      return;
    }
    try {
      creds = JSON.parse(raw);
    } catch (e) {
      const err = { ok: false, error: 'invalid_json_stdin', detail: e.message || String(e) };
      if (jsonOut) console.log(JSON.stringify(err));
      else console.error(`JSON 无效: ${err.detail}`);
      process.exit(1);
      return;
    }
    if (!creds || typeof creds !== 'object' || Array.isArray(creds)) {
      const err = { ok: false, error: 'invalid_stdin_object' };
      if (jsonOut) console.log(JSON.stringify(err));
      else console.error('stdin JSON 须为对象');
      process.exit(1);
      return;
    }
  } else if (hasTokenArg) {
    creds = { token: tokenArg };
  } else if (hasUserPassArg) {
    creds = { username: userArg, password: passwordArg };
  } else {
    const err = {
      ok: false,
      error: 'login_needs_credentials',
      hint: jiraAuthFixHint(),
    };
    if (jsonOut) console.log(JSON.stringify(err));
    else console.error(jiraAuthFixHint());
    process.exit(1);
    return;
  }

  const base = loadOrInitConfig();
  if (creds.baseUrl != null && String(creds.baseUrl).trim()) {
    base.baseUrl = String(creds.baseUrl).trim();
  }

  const normalized = {
    token: creds.token != null ? String(creds.token).trim() : '',
    username: creds.username != null ? String(creds.username).trim() : '',
    password: creds.password != null ? String(creds.password) : '',
  };

  let config;
  try {
    config = applyCredentials(base, normalized);
  } catch (e) {
    const err = { ok: false, error: 'bad_credentials', detail: e.message || String(e) };
    if (jsonOut) console.log(JSON.stringify(err));
    else console.error(err.detail);
    process.exit(1);
    return;
  }

  const session = await checkJiraSession(config);
  if (!session.ok) {
    const err = {
      ok: false,
      error: 'jira_auth_failed',
      httpStatus: session.status,
      detail:
        typeof session.detail === 'string'
          ? session.detail.slice(0, 300)
          : session.detail,
      hint: jiraAuthFixHint(),
    };
    if (jsonOut) console.log(JSON.stringify(err));
    else console.error(`Jira 校验失败（HTTP ${session.status}）`);
    process.exit(1);
    return;
  }

  writeAuthFile(config);
  const ok = { ok: true, baseUrl: config.baseUrl, user: session.user };
  if (jsonOut) console.log(JSON.stringify(ok));
  else {
    console.log(`已保存: ${AUTH_FILE}`);
    const u = session.user;
    if (u.displayName || u.name) console.log(`当前用户: ${u.displayName || u.name}`);
  }
}

// ─── Skill 多仓库同步 ────────────────────────────────────────────────────────

/**
 * Skill 仓库配置:
 * - openclaw: 单仓库，所有 skill 在同一 repo 的子目录中（mono 模式）
 * - skillsmp: GitLab Group，每个 skill 是独立的 repo（multi 模式）
 */
const SKILL_REPOS = [
  {
    label: 'openclaw',
    type: 'mono',           // 单仓库，skill 是子目录
    baseUrl: 'https://git.tap4fun.com/bi-web/yuandan/skills',
    baseUrlAlt: 'git@git.tap4fun.com:bi-web/yuandan/skills',
    // clone URL 固定: baseUrl + .git
    // skill 文件路径: <repo>/<skill-name>/
  },
  {
    label: 'skillsmp',
    type: 'multi',          // 每个 skill 独立 repo
    baseUrl: 'https://git.tap4fun.com/skills/bi-web',
    baseUrlAlt: 'git@git.tap4fun.com:skills/bi-web',
    // clone URL 动态: baseUrl + /<skill-name>.git
    // skill 文件路径: <repo>/ (根目录)
  },
];

function matchSkillRepo(repoUrl) {
  if (!repoUrl) return null;
  const norm = repoUrl.replace(/\/$/, '').replace(/\.git$/, '').toLowerCase();
  for (const r of SKILL_REPOS) {
    const base = r.baseUrl.toLowerCase();
    const baseAlt = r.baseUrlAlt.toLowerCase();
    if (r.type === 'mono') {
      // mono: URL 精确匹配
      if (norm === base || norm === baseAlt) return r;
    } else {
      // multi: URL 以 baseUrl/<xxx> 匹配（每个 skill 是独立 repo）
      if (norm.startsWith(base + '/') || norm.startsWith(baseAlt + '/')) return r;
    }
  }
  return null;
}

function getOtherSkillRepo(repoUrl) {
  const matched = matchSkillRepo(repoUrl);
  if (!matched) return null;
  return SKILL_REPOS.find(r => r.label !== matched.label) || null;
}

/** 根据仓库类型构造 clone URL */
function buildCloneUrl(repo, skillName) {
  if (repo.type === 'mono') return repo.baseUrl + '.git';
  return repo.baseUrl + '/' + skillName + '.git';
}

/** 根据仓库类型确定 skill 文件在 repo 中的目标路径 */
function getSkillTargetDir(repoRoot, repo, skillName) {
  if (repo.type === 'mono') return path.join(repoRoot, skillName);
  return repoRoot; // multi: 文件直接放在 repo 根目录
}

async function cmdSync(opts) {
  const sourcePath = opts['source-path'];
  const targetLabel = opts['target-repo'];   // 可以是 label（如 "openclaw"/"skillsmp"）或完整 URL
  const skillName = opts['skill-name'];
  const message = opts.message;
  let branch = opts.branch;
  const baseBranch = opts['base-branch'] || 'dev';
  const json = !!opts.json;

  if (!sourcePath || !targetLabel || !skillName || !message || !branch) {
    const err = { ok: false, error: 'missing_args', hint: '需要 --source-path, --target-repo, --skill-name, --message, --branch' };
    if (json) console.log(JSON.stringify(err));
    else console.error(err.hint);
    process.exit(1);
  }

  // 验证 source 目录存在
  if (!fs.existsSync(sourcePath)) {
    const err = { ok: false, error: 'source_not_found', hint: `源目录不存在: ${sourcePath}` };
    if (json) console.log(JSON.stringify(err));
    else console.error(err.hint);
    process.exit(1);
  }

  // 解析目标仓库：支持 label 或完整 URL
  let targetRepo = SKILL_REPOS.find(r => r.label === targetLabel);
  let targetRepoUrl;
  if (targetRepo) {
    targetRepoUrl = buildCloneUrl(targetRepo, skillName);
  } else {
    // 当作完整 URL，尝试匹配已知仓库
    targetRepo = matchSkillRepo(targetLabel);
    targetRepoUrl = targetLabel;
  }

  // openclaw（mono）不允许直接推送到 main/dev/master，自动生成新分支名
  // skillsmp（multi）每个 skill 独立仓库，可以推送到任何分支
  const PROTECTED_BRANCHES = new Set(['main', 'dev', 'master']);
  if (targetRepo && targetRepo.type === 'mono' && PROTECTED_BRANCHES.has(branch)) {
    const ts = new Date().toISOString().slice(0, 10).replace(/-/g, '');
    branch = `sync_${skillName}_${ts}`;
    if (!json) console.log(`openclaw 不允许直接推送到受保护分支，自动改为: ${branch}`);
  }

  const tmpDir = path.join(require('os').tmpdir(), `skill-sync-${Date.now()}`);
  try {
    // 1. 浅克隆目标仓库（优先克隆目标分支，不存在则从 baseBranch 新建）
    let branchExists = false;
    if (!json) process.stdout.write(`正在克隆目标仓库...`);
    let cloneResult = spawnSync('git', ['clone', '--depth', '1', '--branch', branch, targetRepoUrl, tmpDir], { encoding: 'utf8', timeout: 30000 });
    if (cloneResult.status === 0) {
      branchExists = true;
      if (!json) console.log(` 已有分支 ${branch}`);
    } else {
      // 目标分支不存在，从 baseBranch 克隆
      try { fs.rmSync(tmpDir, { recursive: true, force: true }); } catch {}
      cloneResult = spawnSync('git', ['clone', '--depth', '1', '--branch', baseBranch, targetRepoUrl, tmpDir], { encoding: 'utf8', timeout: 30000 });
      if (cloneResult.status !== 0) {
        const err = { ok: false, error: 'clone_failed', detail: (cloneResult.stderr || '').trim(), cloneUrl: targetRepoUrl };
        if (json) console.log(JSON.stringify(err));
        else console.error(`\n克隆失败: ${err.detail}`);
        process.exit(1);
      }
      if (!json) console.log(` 从 ${baseBranch} 新建分支`);
    }

    // 2. 切换/创建分支
    if (!branchExists) {
      execSync(`git checkout -b ${branch}`, { cwd: tmpDir, encoding: 'utf8' });
    }

    // 3. 复制 skill 文件（排除 credentials、__pycache__、.pyc）
    // mono 模式: skill 是子目录，清理多余文件保持同步
    // multi 模式: 目标是 repo 根目录，不删除额外文件（如 .gitignore、README.md）
    const targetSkillDir = targetRepo ? getSkillTargetDir(tmpDir, targetRepo, skillName) : path.join(tmpDir, skillName);
    const deleteExtras = !targetRepo || targetRepo.type === 'mono';
    if (!fs.existsSync(targetSkillDir)) fs.mkdirSync(targetSkillDir, { recursive: true });
    copyDirSync(sourcePath, targetSkillDir, deleteExtras);

    // 4. 检测变更
    const status = execSync('git status --porcelain', { cwd: tmpDir, encoding: 'utf8' }).trim();
    if (!status) {
      const result = { ok: true, skipped: true, reason: 'no_changes', message: '目标仓库已是最新，无需同步' };
      if (json) console.log(JSON.stringify(result));
      else console.log('目标仓库已是最新，无需同步。');
      return;
    }

    // 5. 暂存 + 提交
    execSync('git add -A', { cwd: tmpDir, encoding: 'utf8' });
    const commitResult = spawnSync('git', ['commit', '-m', message], { cwd: tmpDir, encoding: 'utf8' });
    if (commitResult.status !== 0) {
      const err = { ok: false, error: 'commit_failed', detail: (commitResult.stderr || commitResult.stdout || '').trim() };
      if (json) console.log(JSON.stringify(err));
      else console.error(`提交失败: ${err.detail}`);
      process.exit(1);
    }

    // 6. 推送
    if (!json) process.stdout.write('正在推送...');
    const pushResult = spawnSync('git', ['push', '-u', 'origin', branch], { cwd: tmpDir, encoding: 'utf8', timeout: 30000 });
    if (pushResult.status !== 0) {
      const err = { ok: false, error: 'push_failed', detail: (pushResult.stderr || '').trim() };
      if (json) console.log(JSON.stringify(err));
      else console.error(`\n推送失败: ${err.detail}`);
      process.exit(1);
    }
    if (!json) console.log(' 完成');

    const commitHash = execSync('git rev-parse HEAD', { cwd: tmpDir, encoding: 'utf8' }).trim();
    const diffStat = execSync('git diff HEAD~1 --stat', { cwd: tmpDir, encoding: 'utf8' }).trim();
    const result = {
      ok: true,
      commitHash: commitHash.substring(0, 8),
      branch,
      targetRepo: targetRepoUrl,
      stat: diffStat,
      pushOutput: (pushResult.stderr || '').trim(),
    };
    if (json) console.log(JSON.stringify(result, null, 2));
    else {
      console.log(`\n同步成功！`);
      console.log(`  提交: ${result.commitHash}`);
      console.log(`  分支: ${branch}`);
      console.log(`  目标: ${targetRepoUrl}`);
    }
  } finally {
    // 7. 清理临时目录
    try { fs.rmSync(tmpDir, { recursive: true, force: true }); } catch {}
  }
}

/** 递归复制目录，排除 credentials、__pycache__、.pyc、.git
 *  @param {boolean} deleteExtras - 是否删除目标中源不存在的文件（mono 模式开启，multi 模式关闭）
 */
function copyDirSync(src, dest, deleteExtras = true) {
  const EXCLUDE = new Set(['credentials', '__pycache__', '.git', 'node_modules']);
  const entries = fs.readdirSync(src, { withFileTypes: true });
  for (const entry of entries) {
    if (EXCLUDE.has(entry.name) || entry.name.endsWith('.pyc')) continue;
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    if (entry.isDirectory()) {
      if (!fs.existsSync(destPath)) fs.mkdirSync(destPath, { recursive: true });
      copyDirSync(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
  // 删除目标中多余的文件（仅 deleteExtras=true 时执行，multi 模式下跳过以保留 .gitignore 等仓库文件）
  if (deleteExtras && fs.existsSync(dest)) {
    const srcNames = new Set(fs.readdirSync(src).filter(n => !EXCLUDE.has(n) && !n.endsWith('.pyc')));
    for (const name of fs.readdirSync(dest)) {
      if (EXCLUDE.has(name) || name.endsWith('.pyc')) continue;
      if (!srcNames.has(name)) {
        const p = path.join(dest, name);
        fs.rmSync(p, { recursive: true, force: true });
      }
    }
  }
}

// ─── CLI 入口 ────────────────────────────────────────────────────────────────

const parseArgs = (args) => {
  const result = { _: [] };
  for (const arg of args) {
    if (arg.startsWith('--')) {
      const [k, ...v] = arg.slice(2).split('=');
      result[k] = v.join('=') || true;
    } else {
      result._.push(arg);
    }
  }
  return result;
};

const [,, cmd, ...rawArgs] = process.argv;
const opts = parseArgs(rawArgs);

(async () => {
  if (cmd === 'commit') {
    const repoPath = opts['repo-path'] || process.cwd();
    const msgOpt = opts.message;
    const useAuto = typeof msgOpt === 'string' && msgOpt.trim().length > 0;
    if (useAuto) {
      await cmdCommitAutomation(repoPath, opts);
    } else {
      await cmdCommit(repoPath);
    }

  } else if (cmd === 'plan') {
    const repoPath = opts['repo-path'] || process.cwd();
    const payload = await cmdPlan(repoPath);
    console.log(JSON.stringify(payload, null, 2));
    if (!payload.ok) process.exit(1);

  } else if (cmd === 'link') {
    const commitHash = opts._[0];
    if (!commitHash) {
      console.error(
        '用法: git-jira-commit-assist.js link <commit-hash> [--message="..."] [--repo-url=URL] [--repo-path=PATH]'
      );
      process.exit(1);
    }
    await cmdLink({
      commitHash,
      message: opts.message || '',
      repoUrl: opts['repo-url'] || '',
      repoPath: opts['repo-path'] || process.cwd(),
    });

  } else if (cmd === 'login') {
    await cmdLogin(opts);

  } else if (cmd === 'verify-auth') {
    if (!authFileExists()) {
      const err = { ok: false, error: 'no_auth_file', hint: jiraAuthFixHint() };
      if (opts.json) console.log(JSON.stringify(err));
      else console.error(`未找到认证配置。${jiraAuthFixHint()}`);
      process.exit(1);
    }
    const auth = loadAuth();
    const session = await checkJiraSession(auth);
    if (!session.ok) {
      const err = {
        ok: false,
        error: 'jira_session_invalid',
        httpStatus: session.status,
        hint: jiraAuthFixHint(),
      };
      if (opts.json) console.log(JSON.stringify(err));
      else console.error(`Jira 登录无效或已过期（HTTP ${session.status}）。${jiraAuthFixHint()}`);
      process.exit(1);
    }
    const ok = { ok: true, baseUrl: auth.baseUrl, user: session.user };
    if (opts.json) console.log(JSON.stringify(ok));
    else {
      const u = session.user;
      console.log(`Jira 已连接: ${auth.baseUrl}`);
      if (u.displayName || u.name) console.log(`当前用户: ${u.displayName || u.name}`);
    }

  } else if (cmd === 'list-projects') {
    const auth = loadAuth();
    if (opts.json) {
      const session = await checkJiraSession(auth);
      if (!session.ok) {
        console.log(
          JSON.stringify({
            ok: false,
            error: 'jira_session_invalid',
            httpStatus: session.status,
            hint: jiraAuthFixHint(),
          })
        );
        process.exit(1);
      }
    } else {
      process.stdout.write('正在校验 Jira 登录...');
      const session = await checkJiraSession(auth);
      if (!session.ok) {
        console.log(
          `\nJira 登录无效或已过期（HTTP ${session.status}）。${jiraAuthFixHint()}`
        );
        process.exit(1);
      }
      console.log(' 通过');
    }
    if (!opts.json) process.stdout.write('正在拉取项目列表并检测权限...');
    const all = await getAllProjectsWithPerm(auth);
    if (!opts.json) console.log('');
    const projects = all.filter((p) => p.canCreate);
    if (!projects.length) {
      if (opts.json) {
        console.log(JSON.stringify([]));
      } else {
        console.log('未找到可创建 Issue 的项目（当前账号在可见项目上均无 CREATE_ISSUES 权限，或列表为空）');
      }
      return;
    }
    if (opts.json) {
      console.log(JSON.stringify(projects));
    } else {
      console.log(`\n你可创建 Issue 的项目 (共 ${projects.length} 个):\n`);
      projects.forEach((p, i) => {
        const idx = String(i + 1).padStart(3);
        console.log(`  ${idx}. [${p.key.padEnd(12)}] ${p.name}`);
      });
    }

  } else if (cmd === 'list-issuetypes') {
    const auth = loadAuth();
    const projectKey = opts.project;
    if (!projectKey) { console.error('需要 --project=KEY'); process.exit(1); }
    const types = await getIssueTypes(auth, projectKey);
    if (!types.length) {
      if (opts.json) console.log(JSON.stringify([]));
      else console.log(`未能获取项目 ${projectKey} 的 Issue 类型（可能无权限或网络异常）`);
      return;
    }
    if (opts.json) {
      console.log(JSON.stringify(types));
    } else {
      console.log(`\n项目 [${projectKey}] 支持的 Issue 类型:\n`);
      types.forEach((t, i) => {
        const desc = t.description ? `  — ${t.description}` : '';
        console.log(`  ${String(i + 1).padStart(2)}. ${t.name}${desc}`);
      });
    }

  } else if (cmd === 'search-issues') {
    const auth = loadAuth();
    const projectKey = opts.project;
    const keyword = opts.keyword || '';
    if (!projectKey) { console.error('需要 --project=KEY'); process.exit(1); }
    const issues = await searchIssues(auth, projectKey, keyword);
    if (!issues.length) { console.log('未找到相关 Issue'); return; }
    console.log(`\n${projectKey} 相关 Issue:\n`);
    issues.forEach(issue => {
      const status = issue.fields.status?.name || '';
      console.log(`  ${issue.key.padEnd(12)} [${status}] ${issue.fields.summary}`);
    });

  } else if (cmd === 'create-issue') {
    const auth = loadAuth();
    const projectKey = opts.project;
    const summary = opts.summary;
    if (!projectKey || !summary) { console.error('需要 --project=KEY --summary="标题"'); process.exit(1); }
    const description = opts.description || '';
    const issueType = opts['issue-type'] || opts['issuetype'] || null;
    const created = await createIssue(auth, projectKey, summary, description, { quiet: !!opts.json, issueType });
    const browseUrl = `${auth.baseUrl}/browse/${created.key}`;
    if (opts.json) {
      console.log(JSON.stringify({
        key: created.key,
        url: browseUrl,
        postCreate: created.postCreate || null,
      }, null, 2));
    } else {
      console.log(`已创建: ${created.key}`);
      console.log(`链接: ${browseUrl}`);
      const pc = created.postCreate;
      if (pc?.assignedToSelf) console.log('已分配给本人');
      if (pc?.transitionedToInProgress) console.log('已转换到处理中');
    }

  } else if (cmd === 'push') {
    // push 命令：git push + 自动检测 Skill 仓库（Step 7 + Step 8 合一）
    const repoPath = opts['repo-path'] || process.cwd();
    const json = !!opts.json;
    const result = { ok: true };

    // Step 7: git push
    try {
      const branch = git('branch --show-current', repoPath);
      result.branch = branch;
      let hasUpstream = false;
      try { git('rev-parse --verify @{u}', repoPath); hasUpstream = true; } catch {}
      if (hasUpstream) {
        result.pushOutput = execSync('git push', { cwd: repoPath, encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] }).trim();
      } else {
        let remote = 'origin';
        try { remote = git('remote', repoPath).split('\n')[0] || 'origin'; } catch {}
        result.pushOutput = execSync(`git push -u ${remote} ${branch}`, { cwd: repoPath, encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] }).trim();
      }
    } catch (e) {
      // git push 的有用信息常在 stderr
      result.pushOutput = (e.stderr || e.stdout || e.message || '').trim();
    }

    // Step 8: 自动检测是否为 Skill 仓库
    try {
      const repoUrl = git('remote get-url origin', repoPath);
      result.repoUrl = repoUrl;
      const matched = matchSkillRepo(repoUrl);
      const other = getOtherSkillRepo(repoUrl);
      result.skillRepo = { isSkillRepo: !!matched, matched: matched || undefined, other: other || undefined };
    } catch {
      result.skillRepo = { isSkillRepo: false };
    }

    if (json) {
      console.log(JSON.stringify(result, null, 2));
    } else {
      console.log(`✓ 已推送分支: ${result.branch}`);
      if (result.skillRepo?.isSkillRepo) {
        console.log(`⚠ 检测到 Skill 仓库（${result.skillRepo.matched.label}），可同步到 ${result.skillRepo.other.label}`);
      }
    }

  } else if (cmd === 'check-skill-repo') {
    const repoUrl = opts['repo-url'] || '';
    const skillName = opts['skill-name'] || '';
    const matched = matchSkillRepo(repoUrl);
    const other = getOtherSkillRepo(repoUrl);
    const result = { isSkillRepo: !!matched, matched, other };
    if (other && skillName) result.otherCloneUrl = buildCloneUrl(other, skillName);
    console.log(JSON.stringify(result));

  } else if (cmd === 'sync') {
    await cmdSync(opts);

  } else {
    console.log(`
git-jira-commit-assist - 规范化 Git 提交 + 自动关联 Jira

用法:
  node git-jira-commit-assist.js plan [--repo-path=PATH]
      输出 JSON：变更摘要、项目列表、相关 Issue、建议 message（供 Agent 用）

  node git-jira-commit-assist.js commit [--repo-path=PATH]
      终端 TUI 交互提交（须 TTY）

  node git-jira-commit-assist.js commit --message="..." --repo-path=PATH
      无交互提交（Agent 代跑），须配合以下之一：
      --link-issue=KEY           关联已有 Issue（自动追加 Key）
      --create-issue --project=KEY [--summary="..." ]  新建 Issue 再提交
      --skip-jira                仅提交，不关联 Jira
      --json                     结果 JSON 输出

  node git-jira-commit-assist.js link <hash> [--repo-path=PATH]  兼容旧 hook，不写入 Jira 网页链接
  node git-jira-commit-assist.js login …  终端无参为 TUI；如需 JSON 输出等见脚本说明
  node git-jira-commit-assist.js verify-auth [--json]             校验 Jira 登录（建议最先执行）
  node git-jira-commit-assist.js list-projects                   列出可创建 Issue 的项目
  node git-jira-commit-assist.js search-issues --project=KEY     搜索 Issue
  node git-jira-commit-assist.js create-issue --project=KEY      创建 Issue
  node git-jira-commit-assist.js push [--repo-path=PATH] [--json]  git push + 自动检测 Skill 仓库（Step 7+8 合一）
  node git-jira-commit-assist.js check-skill-repo --repo-url=URL 检查是否为 Skill 仓库
  node git-jira-commit-assist.js sync --source-path=PATH --target-repo=URL --skill-name=NAME --message="..." --branch=BRANCH [--base-branch=dev] [--json]
      将 Skill 同步到另一个仓库（浅克隆→复制→提交→推送→清理）

选项:
  --repo-path=PATH    指定仓库路径（默认当前目录）
  --message="..."     commit message
  --repo-url=URL      （已忽略，保留兼容）
  --project=KEY       Jira 项目 Key
  --summary="..."     Issue 标题
  --keyword="..."     搜索关键词
`);
  }
})().catch(e => {
  console.error('[git-jira-commit-assist] 错误:', e.message);
  process.exit(1);
});
