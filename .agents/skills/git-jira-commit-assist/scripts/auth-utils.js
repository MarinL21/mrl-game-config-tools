/**
 * 共享：认证配置的读取、合并凭据、落盘（不负责联网校验）。
 * 主路径 ~/.git-jira-commit-assist-auth.json；兼容读取旧版 ~/.git-jira-auth.json。
 */
const fs = require('fs');
const path = require('path');

const AUTH_FILE = path.join(process.env.HOME, '.git-jira-commit-assist-auth.json');
/** 旧版 git-jira skill 使用的路径，仅用于读取兼容 */
const LEGACY_AUTH_FILE = path.join(process.env.HOME, '.git-jira-auth.json');
const DEFAULT_BASE_URL = 'https://jira.tap4fun.com';

function getAuthPathForRead() {
  if (fs.existsSync(AUTH_FILE)) return AUTH_FILE;
  if (fs.existsSync(LEGACY_AUTH_FILE)) return LEGACY_AUTH_FILE;
  return AUTH_FILE;
}

function authFileExists() {
  return fs.existsSync(AUTH_FILE) || fs.existsSync(LEGACY_AUTH_FILE);
}

function loadOrInitConfig() {
  const p = getAuthPathForRead();
  let config = {};
  if (fs.existsSync(p)) {
    try {
      config = JSON.parse(fs.readFileSync(p, 'utf8'));
    } catch {
      config = {};
    }
  }
  if (!config.baseUrl) config.baseUrl = DEFAULT_BASE_URL;
  if (!config.defaultIssueType) config.defaultIssueType = 'Task';
  return config;
}

/**
 * @param {object} base - loadOrInitConfig() 结果
 * @param {{ token?: string, username?: string, password?: string }} creds
 */
function applyCredentials(base, creds) {
  const config = { ...base };
  const tok = creds.token != null ? String(creds.token).trim() : '';
  if (tok) {
    config.token = tok;
    delete config.username;
    delete config.password;
    return config;
  }
  const username = creds.username != null ? String(creds.username).trim() : '';
  if (!username) {
    const err = new Error('需要用户名 + 密码，或 PAT token');
    err.code = 'bad_creds';
    throw err;
  }
  config.username = username;
  config.password = creds.password != null ? String(creds.password) : '';
  delete config.token;
  return config;
}

/** 始终写入新路径；下次登录会统一到 ~/.git-jira-commit-assist-auth.json */
function writeAuthFile(config) {
  fs.writeFileSync(AUTH_FILE, JSON.stringify(config, null, 2), { mode: 0o600 });
}

module.exports = {
  AUTH_FILE,
  LEGACY_AUTH_FILE,
  DEFAULT_BASE_URL,
  getAuthPathForRead,
  authFileExists,
  loadOrInitConfig,
  applyCredentials,
  writeAuthFile,
};
