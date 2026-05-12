---
name: slg-event-library
description: SLG / 三消 / 合成 / 模拟经营 等手游节日活动素材知识库，含每日抓取最新活动资讯的能力。覆盖 YouTube / TapTap / B站 / 游戏资讯网多渠道。触发：SLG 活动、竞品调研、节日活动参考、抽奖玩法参考、Merge 合成活动、新游活动、活动知识库、最新活动资讯、类似 xxx 活动、竞品活动、活动玩法调研。
---

# SLG 活动知识库 + 每日情报推送

## 用途

给 P2 节日活动策划提供竞品素材库：活动类型、玩法机制、视频演示、奖池结构。

## 目录结构

```
.claude/skills/slg-event-library/
├── SKILL.md                    ← 本文件
├── taxonomy.md                 ← 分类体系
├── games/                      ← 按游戏沉淀（每款一个 md）
│   ├── whiteout_survival.md
│   ├── last_war.md
│   ├── rise_of_kingdoms.md
│   ├── call_of_dragons.md
│   ├── lords_mobile.md
│   ├── evony.md
│   ├── king_of_avalon.md
│   ├── state_of_survival.md
│   ├── puzzles_and_survival.md
│   └── gossip_harbor.md
├── events/                     ← 按活动类型沉淀（每类一个 md）
│   ├── lucky_wheel.md
│   ├── treasure_hunter.md
│   ├── lucky_cards.md
│   ├── frosty_fortune.md
│   └── ...
├── daily_feed/                 ← 每天 09:30 抓取归档
│   └── YYYY-MM-DD.md
├── scripts/                    ← 抓取脚本
│   ├── fetch_daily.sh          ← 总调度
│   ├── fetch_youtube.py        ← YouTube 抓取
│   ├── fetch_taptap.py         ← TapTap 抓取
│   ├── fetch_bilibili.py       ← B站 抓取
│   ├── fetch_gamenews.py       ← 游戏资讯网
│   └── push_feishu.py          ← 飞书推送
└── config/
    ├── games_watchlist.json    ← 游戏监控列表
    ├── feishu.json             ← 飞书 webhook（gitignore）
    └── keywords.json           ← 抓取关键词
```

## 使用场景

### 场景 1：查询活动参考
> "有没有类似 Whiteout Lucky Wheel 的活动"
> "Merge 合成类游戏有什么节日活动"

→ 检索 `events/` 或 `games/` 下对应 MD，返回玩法 + 视频链接 + P2 映射建议。

### 场景 2：每日情报（自动化）
每天 09:30 由远程 cron 触发：
1. 跑 `scripts/fetch_daily.sh` 抓取 4 渠道最新活动视频/资讯
2. 归档到 `daily_feed/YYYY-MM-DD.md`
3. 推送到飞书群（webhook）

### 场景 3：按需补档
> "帮我把 Gossip Harbor 的最新活动补进知识库"

→ 针对性抓取 + 更新 `games/gossip_harbor.md`。

## 监控游戏列表

见 `config/games_watchlist.json`。

## 飞书推送

配置在 `config/feishu.json`，gitignore。
