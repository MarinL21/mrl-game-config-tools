/**
 * 独立仓库安装后可能无 node_modules：首次运行任意入口前在本 skill 根目录执行 npm install。
 */
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const SKILL_ROOT = path.join(__dirname, '..');
const DEPS_OK = path.join(SKILL_ROOT, 'node_modules', 'prompts', 'package.json');

function ensureSkillDependencies() {
  if (fs.existsSync(DEPS_OK)) return;

  console.error('[git-jira-commit-assist] 未检测到依赖，正在于 skill 根目录执行 npm install…');
  const isWin = process.platform === 'win32';
  const npm = isWin ? 'npm.cmd' : 'npm';
  const r = spawnSync(npm, ['install', '--no-fund', '--no-audit'], {
    cwd: SKILL_ROOT,
    stdio: 'inherit',
    shell: isWin,
  });
  if (r.status !== 0) {
    console.error('[git-jira-commit-assist] npm install 失败，请在 skill 根目录手动执行: npm install');
    process.exit(r.status == null ? 1 : r.status);
  }
  if (!fs.existsSync(DEPS_OK)) {
    console.error('[git-jira-commit-assist] 依赖仍未就绪，请检查网络后重试: npm install');
    process.exit(1);
  }
}

module.exports = ensureSkillDependencies;
