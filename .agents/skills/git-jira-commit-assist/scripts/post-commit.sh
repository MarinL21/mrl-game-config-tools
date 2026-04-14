#!/bin/bash
# git-jira-commit-assist post-commit hook（可选）
# 曾在此调用 link 写入 Jira「链接到」；已停用。请用 skill 的 commit / commit --message，由脚本在 Issue 下发评论关联。
# 安装方式: 复制到 .git/hooks/post-commit 并 chmod +x

# SKILL_ROOT="…/git-jira-commit-assist"
# COMMIT_HASH=$(git rev-parse HEAD)
# COMMIT_MSG=$(git log -1 --pretty=%B)
# node "$SKILL_ROOT/scripts/git-jira-commit-assist.js" link "$COMMIT_HASH" --message="$COMMIT_MSG"
