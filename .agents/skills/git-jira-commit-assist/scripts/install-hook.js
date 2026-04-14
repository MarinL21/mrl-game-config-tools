#!/usr/bin/env node
/**
 * git-jira-commit-assist install-hook: 为当前 Git 仓库安装 post-commit hook
 */
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const skillRoot = path.dirname(__dirname);
const hookSrc = path.join(skillRoot, 'scripts', 'post-commit.sh');

const HOOK_MARKER = 'git-jira-commit-assist';

let gitRoot;
try {
  gitRoot = execSync('git rev-parse --show-toplevel', { encoding: 'utf8' }).trim();
} catch {
  console.error('当前目录不是 Git 仓库');
  process.exit(1);
}

const hooksDir = path.join(gitRoot, '.git', 'hooks');
const hookDest = path.join(hooksDir, 'post-commit');

function hookAlreadyHasAssist(contents) {
  return (
    contents.includes('git-jira-commit-assist') ||
    contents.includes('# git-jira\n') ||
    contents.includes('# git-jira ')
  );
}

if (fs.existsSync(hookDest)) {
  const existing = fs.readFileSync(hookDest, 'utf8');
  if (hookAlreadyHasAssist(existing)) {
    console.log('git-jira-commit-assist hook 已安装，无需重复安装');
    process.exit(0);
  }
  // 追加到已有 hook
  fs.appendFileSync(hookDest, `\n# ${HOOK_MARKER}\n${fs.readFileSync(hookSrc, 'utf8')}\n`);
  console.log(`已追加 git-jira-commit-assist hook 到: ${hookDest}`);
} else {
  fs.copyFileSync(hookSrc, hookDest);
  fs.chmodSync(hookDest, 0o755);
  console.log(`已安装 git-jira-commit-assist hook 到: ${hookDest}`);
}
