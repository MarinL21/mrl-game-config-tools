#!/bin/bash
# 本地手动触发入口（测试用）
# 真实 cron 调度由远程 agent 跑，见 scripts/daily_brief_prompt.md
#
# 用法：
#   ./run_daily_local.sh            # 跑一次，输出提示让你手动在 Claude Code 里执行 prompt
#   ./run_daily_local.sh --push     # 直接用 daily_feed/ 里今天的 md 推送飞书（不重新抓）

set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
DATE=$(date +%Y-%m-%d)
TODAY_FILE="$ROOT_DIR/daily_feed/$DATE.md"

if [[ "${1:-}" == "--push" ]]; then
  if [[ ! -f "$TODAY_FILE" ]]; then
    echo "ERROR: $TODAY_FILE 不存在，先跑抓取" >&2
    exit 1
  fi
  "$SCRIPT_DIR/push_feishu.sh" card_file "$TODAY_FILE"
  echo "✅ 已推送 $TODAY_FILE"
  exit 0
fi

echo "=== SLG 情报抓取 — 本地触发 ==="
echo ""
echo "请在 Claude Code 里粘贴以下指令手动触发一次："
echo ""
echo "---"
cat "$SCRIPT_DIR/daily_brief_prompt.md"
echo "---"
echo ""
echo "或者等待每天 09:30 远程 cron 自动触发。"
echo ""
echo "查看最新日报：cat $TODAY_FILE"
echo "仅推送（不重抓）：$0 --push"
