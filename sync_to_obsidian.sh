#!/bin/bash
# 将游戏运营策划工具内容同步到 Obsidian Vault (~/mrclaude)

PROJECT="/Users/marinl/游戏运营策划工具"
VAULT="/Users/marinl/mrclaude"

echo "🔄 开始同步到 Obsidian..."

# ── 1. 清空并重建目录结构 ─────────────────────────────────
rm -rf "$VAULT/游戏运营工具"
mkdir -p "$VAULT/游戏运营工具/工具"
mkdir -p "$VAULT/游戏运营工具/数据回归"
mkdir -p "$VAULT/游戏运营工具/Skills"

# ── 2. 工具（3个）────────────────────────────────────────
echo "🔧 同步工具..."

cat > "$VAULT/游戏运营工具/工具/礼包配置工具.md" << 'EOF'
# 🎁 礼包配置工具

快速配置礼包奖励 JSON，支持自定义物品和固定配置。

**功能**
- 自定义物品和数量
- 自动计算 XP 和帮派宝箱
- 可选固定配置、拖拽排序
- 一键复制压缩格式

**文件路径**
`/Users/marinl/游戏运营策划工具/礼包配置工具.html`
EOF
echo "  ✅ 礼包配置工具"

cat > "$VAULT/游戏运营工具/工具/掉落配置工具.md" << 'EOF'
# 🎲 掉落配置工具

配置随机掉落奖励，实时显示概率分布。

**功能**
- 设置权重和抽取次数
- 实时显示掉落概率
- 拖拽排序
- JSON 格式输出

**文件路径**
`/Users/marinl/游戏运营策划工具/掉落配置工具.html`
EOF
echo "  ✅ 掉落配置工具"

cat > "$VAULT/游戏运营工具/工具/挖孔关卡配置工具.md" << 'EOF'
# ⛏️ 挖孔关卡配置工具

可视化点选棋盘格子配置障碍物，自动生成关卡 JSON 配置。

**功能**
- 可视化棋盘格子编辑
- 障碍物类型配置
- 自动生成关卡 JSON

**文件路径**
`/Users/marinl/游戏运营策划工具/挖孔关卡配置工具.html`
EOF
echo "  ✅ 挖孔关卡配置工具"

# ── 3. 数据回归 ───────────────────────────────────────────
echo "📊 同步数据回归..."
# 同步已有 MD 的报告
for f in "$PROJECT/reports/"*.md; do
  [ -f "$f" ] && cp "$f" "$VAULT/游戏运营工具/数据回归/" && echo "  ✅ $(basename $f)"
done
# 为纯 HTML 报告创建 MD 入口
cat > "$VAULT/游戏运营工具/数据回归/挖孔五期数据回归_科技节.md" << 'EOF'
# 挖孔五期数据回归 · 科技节

**报告文件**
`/Users/marinl/游戏运营策划工具/reports/挖孔五期数据回归_科技节.html`

> 用浏览器打开查看完整图表报告
EOF
cat > "$VAULT/游戏运营工具/数据回归/黑五省省卡数据回顾.md" << 'EOF'
# 黑五省省卡数据回顾

**报告文件**
`/Users/marinl/游戏运营策划工具/reports/黑五省省卡数据回顾.html`

> 用浏览器打开查看完整图表报告
EOF
echo "  ✅ 挖孔五期数据回归_科技节"
echo "  ✅ 黑五省省卡数据回顾"

# ── 4. Skills ─────────────────────────────────────────────
echo "🛠 同步 Skills..."
for skill_dir in "$PROJECT/.agents/skills/"/*/; do
  skill_name=$(basename "$skill_dir")
  [ -f "$skill_dir/SKILL.md" ] && \
    cp "$skill_dir/SKILL.md" "$VAULT/游戏运营工具/Skills/${skill_name}.md" && \
    echo "  ✅ $skill_name"
done

# ── 5. 目录索引 ───────────────────────────────────────────
echo "📑 生成目录索引..."
cat > "$VAULT/游戏运营工具/🗂 目录.md" << 'INDEXEOF'
# 🗂 目录

## 🎮 游戏运营工具

### 🔧 工具
- [[礼包配置工具]]
- [[掉落配置工具]]
- [[挖孔关卡配置工具]]

### 📊 数据回归
- [[挖孔五期数据回归_科技节]]
- [[黑五省省卡数据回顾]]

### 🛠 Skills

#### 数据分析
- [[ai-to-sql]]
- [[bi-rmd-report]]
- [[dashboard-skill]]
- [[datain-skill]]
- [[dighole-data-regression]]

#### 游戏运营
- [[igame-skill]]
- [[iap-jiji-fincond-replace]]
- [[iap-leichong-sync]]
- [[git-jira-commit-assist]]
- [[p2-translation-automatic]]

#### 效率工具
- [[gws-workspace]]
- [[login-oauth2]]
- [[publish-skill]]
INDEXEOF

echo ""
echo "✅ 同步完成！共 $(find "$VAULT/游戏运营工具" -name "*.md" | wc -l | tr -d ' ') 个文件"
