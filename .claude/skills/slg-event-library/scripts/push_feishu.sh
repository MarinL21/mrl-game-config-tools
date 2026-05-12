#!/bin/bash
# 飞书自定义机器人推送器
# 用法：
#   echo "正文" | ./push_feishu.sh text
#   ./push_feishu.sh card < daily_feed/2026-04-21.md
#   ./push_feishu.sh card_file daily_feed/2026-04-21.md

set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CONFIG_FILE="$SCRIPT_DIR/../config/feishu.json"

if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "ERROR: feishu.json not found at $CONFIG_FILE" >&2
  exit 1
fi

WEBHOOK_URL=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['webhook_url'])")

MODE="${1:-text}"

case "$MODE" in
  text)
    CONTENT=$(cat)
    PAYLOAD=$(python3 -c "
import json, sys
text = sys.stdin.read()
print(json.dumps({'msg_type': 'text', 'content': {'text': text}}, ensure_ascii=False))
" <<< "$CONTENT")
    ;;

  card|card_file)
    if [[ "$MODE" == "card_file" ]]; then
      MD_CONTENT=$(cat "$2")
    else
      MD_CONTENT=$(cat)
    fi
    PAYLOAD=$(python3 -c "
import json, sys, datetime
md = sys.stdin.read()
lines = md.split('\n')
title = lines[0].lstrip('# ').strip() if lines else 'SLG情报'
# 截断太长的内容（飞书卡片 content 有长度限制）
body = '\n'.join(lines[1:]).strip()
if len(body) > 18000:
    body = body[:18000] + '\n\n...(内容过长，已截断，详见知识库)'

card = {
    'msg_type': 'interactive',
    'card': {
        'config': {'wide_screen_mode': True},
        'header': {
            'title': {'tag': 'plain_text', 'content': title},
            'template': 'blue'
        },
        'elements': [
            {'tag': 'markdown', 'content': body}
        ]
    }
}
print(json.dumps(card, ensure_ascii=False))
" <<< "$MD_CONTENT")
    ;;

  *)
    echo "Usage: $0 {text|card|card_file <file>}" >&2
    exit 2
    ;;
esac

RESP=$(curl -sS -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

echo "$RESP"

if echo "$RESP" | grep -q '"code":0'; then
  exit 0
else
  echo "推送失败" >&2
  exit 3
fi
