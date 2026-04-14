---
name: datain-skill
description: >
  Datain 数据平台查询工具，面向 SLG 手游的数据分析场景。支持三大能力：
  (1) 游戏数据查询 — 基于 ClickHouse 聚合宽表，通过指定维度、指标、标签查询运营与市场数据（DNU、留存、付费、Cohort 成长等）；
  (2) 发行素材查询 — 以素材为粒度的投放数据统计，分析展示、点击、花费、ROAS 等市场投放效果；
  (3) Datain 知识库 — 基于文档 RAG 检索回答 Datain 平台使用相关问题。
  触发词：游戏数据、留存、付费、DNU、Cohort、收入、ROI、DAU、
  素材分析、投放效果、ROAS、Datain、datain 帮助。
---

# 概览

Datain 是公司数据部的游戏数据分析平台，本 Skill 封装了其 Public API，提供以下三个功能模块：

| 模块         | 说明                                 | 参考文档                                              |
|------------|------------------------------------|---------------------------------------------------|
| 游戏数据查询     | 从 ClickHouse 聚合宽表中按维度+指标查询游戏整体数据情况 | [query_game.md](references/query_game.md)         |
| 发行素材查询     | 从市场素材投放角度查询投放数据，分析素材效果             | [query_material.md](references/query_material.md) |
| Datain 知识库 | 通过 RAG 检索回答平台使用问题                  | [help.md](references/help.md)                     |

执行任何查询前，先完成下方的配置与鉴权，再根据用户问题选择对应模块的参考文档执行。

# 配置与鉴权

1. 如果之前已经鉴权过, 可以不用重复执行该步骤
2. 获取环境变量 `DATAIN_API_KEY`; 如果 `DATAIN_API_KEY` 不存在, 提示用户
	- 打开 https://datain.tap4fun.com/ → 右上角头像旁边下拉 → 设置 → APP KEY
	- 复制 APP KEY 并发送，由 Agent 设置本机环境变量 `DATAIN_API_KEY`，需要持久化保存
3. 持久化保存
	- 根据不同的工具判断环境变量应该持久化存放在哪里
	- 确保下次新开会话时可自动读取 `DATAIN_API_KEY`，无需用户重复提供

# 游戏编码

```bash
python3 skills/datain-skill/scripts/query_game.py -c games
```
返回格式如下
```json
{"游戏编码": ["游戏别名1", "游戏别名2"]}
```

一个游戏编码可对应多个游戏别名, 如果已知当前问题对应的游戏编码, 不用重复请求

# 功能模块

根据用户问题判断所属模块，阅读对应参考文档后执行。

## 查询游戏数据

基于 ClickHouse 聚合宽表，通过 API 指定维度、指标、标签查询游戏数据。支持两种算法视角：open_udid（市场分析：展示→点击→安装→留存→收入）和 user_id（运营分析：Cohort 成长、服务器生态）。
默认算法使用 open_udid

- 详见：[游戏数据指南](references/query_game.md)

## 查询发行素材

以发行素材为粒度的投放数据统计，用于分析市场素材的展示、点击、花费、ROAS 等投放效果。

- 详见：[发行素材指南](references/query_material.md)

## Datain 知识库

基于文档 RAG 检索，回答 Datain 平台功能使用、配置操作等相关问题。

- 详见：[知识库指南](references/help.md)