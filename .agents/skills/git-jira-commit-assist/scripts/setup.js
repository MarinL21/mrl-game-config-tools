#!/usr/bin/env node
/**
 * git-jira-commit-assist setup: 仅配置 Jira 认证并校验登录；通过后写入 ~/.git-jira-commit-assist-auth.json（与 login 一致）。
 * 真实终端下用 prompts TUI（↑↓ 选认证方式，Token/密码掩码）；非 TTY 时回退 readline。
 *
 * 与 git-jira-commit-assist.js login 共用落盘逻辑；可直接运行本脚本或运行 login（TTY 会进入相同交互）。
 */
require('./ensure-deps')();
const https = require('https');
const http = require('http');
const prompts = require('prompts');

const { loadOrInitConfig, applyCredentials, writeAuthFile, DEFAULT_BASE_URL } = require('./auth-utils');

const promptOpts = {
  onCancel: () => {
    console.log('\n已取消');
    process.exit(0);
  },
};

function request(url, options) {
  return new Promise((resolve, reject) => {
    const parsed = new URL(url);
    const lib = parsed.protocol === 'https:' ? https : http;
    const req = lib.request(
      {
        hostname: parsed.hostname,
        port: parsed.port || (parsed.protocol === 'https:' ? 443 : 80),
        path: parsed.pathname + parsed.search,
        method: options.method || 'GET',
        headers: options.headers || {},
        rejectUnauthorized: false,
      },
      (res) => {
        let data = '';
        res.on('data', (c) => (data += c));
        res.on('end', () => {
          try {
            resolve({ status: res.statusCode, body: JSON.parse(data) });
          } catch {
            resolve({ status: res.statusCode, body: data });
          }
        });
      }
    );
    req.on('error', reject);
    req.end();
  });
}

async function collectCredentialsReadline() {
  const readline = require('readline');
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  const ask = (q) => new Promise((r) => rl.question(q, r));

  const authType = (await ask('认证方式 [1] 用户名+密码  [2] PAT: ')).trim();
  let token;
  let username;
  let password;
  if (authType === '2') {
    token = (await ask('PAT Token: ')).trim();
  } else {
    username = (await ask('用户名: ')).trim();
    password = (await ask('密码: ')).trim();
  }
  rl.close();
  return { token, username, password };
}

async function collectCredentialsTui() {
  const auth = await prompts(
    {
      type: 'select',
      name: 'kind',
      message: '认证方式',
      choices: [
        { title: '用户名 + 密码', value: 'basic' },
        { title: 'Personal Access Token (PAT)', value: 'pat' },
      ],
      hint: '↑↓ 回车',
    },
    promptOpts
  );
  if (auth.kind === undefined) process.exit(0);

  if (auth.kind === 'pat') {
    const t = await prompts(
      {
        type: 'password',
        name: 'token',
        message: 'PAT Token',
        stdin: process.stdin,
        stdout: process.stdout,
      },
      promptOpts
    );
    if (t.token === undefined) process.exit(0);
    return { token: (t.token || '').trim(), username: '', password: '' };
  }

  const u = await prompts(
    { type: 'text', name: 'username', message: '用户名', validate: (x) => (x && String(x).trim() ? true : '必填') },
    promptOpts
  );
  if (u.username === undefined) process.exit(0);
  const p = await prompts(
    {
      type: 'password',
      name: 'password',
      message: '密码',
      stdin: process.stdin,
      stdout: process.stdout,
    },
    promptOpts
  );
  if (p.password === undefined) process.exit(0);
  return {
    token: '',
    username: String(u.username).trim(),
    password: String(p.password || ''),
  };
}

(async () => {
  console.log('\n=== git-jira-commit-assist 配置（仅登录）===\n');

  const useTty = process.stdin.isTTY && process.stdout.isTTY;
  let creds;
  if (useTty) {
    creds = await collectCredentialsTui();
  } else {
    console.log('（非交互终端，使用简易问答）\n');
    creds = await collectCredentialsReadline();
  }

  const trimmedToken = creds.token != null ? String(creds.token).trim() : '';
  if (trimmedToken) {
    creds = { token: trimmedToken, username: '', password: '' };
  } else {
    const u = String(creds.username || '').trim();
    if (!u) {
      console.error('用户名不能为空');
      process.exit(1);
    }
    creds = { token: '', username: u, password: creds.password != null ? String(creds.password) : '' };
  }

  let config;
  try {
    config = applyCredentials(loadOrInitConfig(), creds);
  } catch (e) {
    console.error(e.message || e);
    process.exit(1);
  }

  const headers = { 'Content-Type': 'application/json', Accept: 'application/json' };
  if (config.token) {
    headers['Authorization'] = `Bearer ${config.token}`;
  } else {
    headers['Authorization'] = `Basic ${Buffer.from(`${config.username}:${config.password}`).toString('base64')}`;
  }

  console.log('\n正在连接 Jira...');
  let loginOk = false;
  try {
    const res = await request(`${config.baseUrl}/rest/api/2/myself`, { headers });
    if (res.status === 200 && res.body && typeof res.body === 'object') {
      console.log(`连接成功。${res.body.displayName || res.body.name || ''}`);
      loginOk = true;
    } else {
      console.error(`连接失败 [${res.status}]，请检查认证信息`);
    }
  } catch (e) {
    console.error(`连接出错: ${e.message}`);
  }

  if (!loginOk) {
    process.exit(1);
  }

  writeAuthFile(config);
  console.log(`\n已写入本机配置（git-jira-commit-assist）`);
  console.log('需要默认项目或仓库映射时，直接编辑 ~/.git-jira-commit-assist-auth.json 即可（若曾用旧版，也可保留 ~/.git-jira-auth.json 直至迁移）。\n');
})();
