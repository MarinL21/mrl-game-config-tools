# 闯关弹珠 · 主界面交互稿 v4 + 交互流程板

2026-09-15 定版。对象 = 新玩法「闯关弹珠」（原名宇宙弹弹乐）的主界面交互稿与全流程交互示意。**两份东西同源**：流程板的每一屏都是主界面稿在对应步骤的真实渲染，不是另画的。

## 交付物

| 文件 | 用途 |
|---|---|
| **marble_main_v4.bundle.html** | 主界面交互稿（可玩）。工具条 4 个模式：演示 / 标注 / 编辑 / **流程**（19 步逐步演示）。单文件 3.6 MB，双击即开 |
| **flow_marble4.bundle.html** | 交互流程板：19 屏 = v4 真实截图 + 标注；点任一屏打开 v4 并跳到该步。单文件 6.8 MB |
| flow4/flow_marble4_board.jpg | 整板一张图（半尺寸 2280×7670），GitHub 上直接能看 |
| flow4/step_01 … step_19.jpg | 19 张单屏 1920×1080，贴案子表 / Jira 用 |
| marble_main_v4.html + assets/ | 源文件。界面、状态、流程 19 步（`FLOW` 数组）全在这一份里维护 |
| build_flow_board.py | 改完 v4 后一键重出流程板：`python3 build_flow_board.py`（逐步 headless 截图 → 拼板；板文案从 v4 取） |
| inject_zoom.py | 给任何大板 bundle 补缩放条：`python3 inject_zoom.py xxx.bundle.html` |

## 发同事的链接（公开仓库，免登录直接开）

**主界面交互稿**（可玩，3.6 MB 单文件，第一次打开等两三秒）：
https://rawcdn.githack.com/MarinL21/mrl-game-config-tools/ea49fd2/docs/myriad_city_design/ux/marble_main_v4.bundle.html

**同上，打开直接进「流程」模式**：
https://rawcdn.githack.com/MarinL21/mrl-game-config-tools/ea49fd2/docs/myriad_city_design/ux/marble_main_v4.bundle.html?mode=flow

**交互流程板**（19 屏 + 标注，6.8 MB，点任一屏跳进可玩稿）：
https://rawcdn.githack.com/MarinL21/mrl-game-config-tools/ea49fd2/docs/myriad_city_design/ux/flow_marble4.bundle.html

**整板一张图**（不想点的人看这个）：
https://github.com/MarinL21/mrl-game-config-tools/blob/main/docs/myriad_city_design/ux/flow4/flow_marble4_board.jpg

**目录**：https://github.com/MarinL21/mrl-game-config-tools/tree/main/docs/myriad_city_design/ux

> githack 链接里那段 `ea49fd2` 是 commit sha，**换稿后要换成新 sha** 才是新版本（sha 版永久缓存、不会串版）。
> `raw.githack.com`（不带 cdn 那个域）会 403，别用。

## 怎么看

- **流程模式**：工具条点「流程」→ 右栏 19 步 6 段，点步骤画面即切到该状态；← → 翻页，P 自动播放；点发射钮或按空格 = 从当前状态接手试玩。`?step=N` 可直达某一步。
- **缩放**：工具条 − / % / +、适应窗口、100%；⌘/Ctrl + 滚轮以鼠标为中心缩放；放大后拖空白平移。流程板右上角同款缩放条。
- **标注模式**：每个元素编号 + 功能 / 交互 / 状态 / UI 替换说明，悬停条目高亮元素。
- **编辑模式**：拖元素改位置尺寸，导出布局 JSON 给 UI / 程序。

## 口径（0915 定版，以此为准）

- 撞柱按**次数**加分（7 根柱全同，次数全盘共用），第 11 次把本发累计 **×2 封顶**；落槽倍数 ×1 ×2 ×3 ×10 ×3 ×2 ×1 再乘一次；高级弹珠最终 ×5；发射倍数同倍放大得分与消耗。
- 本场进度满 → 领**一件**奖励（就是进度条右侧奖励格那件）→ 进下一场，进度重置、奖励升级。
- 弹珠落入 ⚡ 金框触发槽累计充能，满 8 → **随机抽 1 个** Buff（触发礼包 / 阶段积分 / 弹珠返还）。⛔ 不是三选一，是抽。抽后充能清零、触发槽重随。触发礼包只售高级弹珠，是核心付费转化位。
- 边界态：弹珠不足（发射钮置灰 + 写明原因 + 前往获取）/ 活动结束（名次奖励与剩余弹珠折算金币走邮件）/ 加载失败（说明本次发射结果已保留 + 重试）。
- ⛔ 旧 `flow_marble3.*` / `marble3.js` 已废弃（另一套渲染器，与 v4 对不上），别再改。

## 流程 19 步

| 段 | 步 |
|---|---|
| (1) 进入与准备 | ① 首次进入 ② 切倍数 ×10 / 高级弹珠 |
| (2) 发射 | ③ 下拉蓄力 ④ 沿槽上冲 |
| (3) 计分核心循环 | ⑤ 撞柱 7/11 ⑥ 第 11 次 ×2 封顶 ⑦ 落触发槽 ×3 + 充能 ⑧ 落 ×10 补满 |
| (4) 闯关 | ⑨ 本场达成 ⑩ 第 4 场开始 |
| (5) 充能 Buff 与付费转化 | ⑪ 弹出抽取 ⑫ 抽中阶段积分 ⑬ 抽中弹珠返还 ⑭ 抽中触发礼包 ⑮ 限时礼包 |
| (6) 排行与边界态 | ⑯ 排行榜 ⑰ 弹珠不足 ⑱ 活动结束 ⑲ 加载失败 |
