#!/usr/bin/env bash
# 运营策划工作台 · 启动
# 用法: ./run.sh          前台跑 (Ctrl+C 停)
#       ./run.sh -d       后台跑，日志 data/server.log
#       ./run.sh stop     停
#       WB_PORT=8791 ./run.sh   换端口
set -e
cd "$(dirname "$0")"
PY="${PYTHON:-/Library/Frameworks/Python.framework/Versions/3.14/bin/python3}"
[ -x "$PY" ] || PY=python3
export WB_PORT="${WB_PORT:-8790}"
export WB_HOST="${WB_HOST:-127.0.0.1}"
mkdir -p data inbox

if [ "$1" = "stop" ]; then
  [ -f data/server.pid ] && kill "$(cat data/server.pid)" 2>/dev/null && echo "stopped" || echo "没在跑"
  rm -f data/server.pid; exit 0
fi
if [ -f data/server.pid ] && kill -0 "$(cat data/server.pid)" 2>/dev/null; then
  echo "已在跑 pid=$(cat data/server.pid) → http://$WB_HOST:$WB_PORT"; exit 0
fi
if [ "$1" = "-d" ]; then
  nohup "$PY" server.py > data/server.log 2>&1 &
  echo $! > data/server.pid
  sleep 1.5
  echo "started pid=$(cat data/server.pid)  →  http://$WB_HOST:$WB_PORT"
else
  echo "→ http://$WB_HOST:$WB_PORT"
  exec "$PY" server.py
fi
