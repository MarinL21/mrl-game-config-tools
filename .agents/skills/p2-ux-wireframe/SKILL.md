---
name: p2-ux-wireframe
description: >-
  把 P2 / AOA 的策划案或竞品做成「交互流程稿」——按项目真实排布规则搭 1920×1080 单屏，
  全流程状态逐屏画全（正常态 / 结算态 / 付费转化态 / 边界态），产出自包含 HTML 给评审，
  再用 Figma 的 HTML 导入插件落成可自由调整的图层。
  chrome（导航条 / 页签 / 按钮 / 奖励格 / 面板）一律引真实游戏切图，不用 CSS 仿造。
  触发：出交互稿、画交互流程、UX 布局、活动界面布局、把案子做成界面、
  按竞品改成我们的界面、interaction flow、UX flow。
---

# P2 交互流程稿产出 Skill

## 这个 skill 解决什么

策划案定版之后，要给开发和 UX 一份**看得懂怎么走**的界面稿。
产物不是线框，是**按真实游戏切图拼出来的高保真交互流程板**——
跟项目组现有的《分层累充-新累充》那类 Figma 稿同一形态。

**⛔ 最容易犯的错**：把它做成深色扁平的后台管理面板。
P2 是「满屏场景 + 厚描边卡通控件」，不是 Material Design。
动笔前先读 `references/layout-rules.md`。

## 工作流

```
① 读案子 + 读排布规则  →  ② 出布局，用户确认  →  ③ 跑槽位切图  →  ④ 交付
```

### Step 0　读规则
`references/layout-rules.md` —— 三段式比例、导航条母版、面板结构、文字规范、
色值（全部取样自真实稿）。**这是第一权威**，比 `p2-game-ux` skill 的正文更贴近实际。
`p2-game-ux` 写的 `1376×768` 已确认作废，**单屏一律 1920×1080**。

### Step 1　列全状态，别只画正常态
用户明确要求过：「像别人的交互一样，所有流程状态都要表示出来」。
按案子的「活动流程」逐步拆，再补三类必画的：

| 类 | 至少要有 |
|---|---|
| 主链路 | 进入 → 操作前 → 操作中 → 结算 → 领奖 |
| 付费转化 | 触发弹窗、礼包弹窗（倒计时 / 限购 / ROI 标签三件同屏） |
| 边界态 | 资源不足（禁用态**必须带原因与获取入口**）、活动结束、数据加载失败 |

### Step 2　搭构件器，不要手写每一屏
一屏 ~200 行 HTML，8 屏手写必错且改不动。
写一个 `renderScreen(state)`，屏与屏之间只差 state。参考 `docs/…/ux/marble.js`。

每个结构块都要带 `data-layer="名字" data-name="名字"`：
前者给 `svgbake.js` 烘焙 SVG，后者给 Figma 的 HTML 导入插件识别图层名。
美术槽位用 `data-slot="名字"`，标注块用 `data-note`（会被收进独立的「标注层」）。

### Step 3　出图 + 强校验
```bash
python3 render_ux.py flow_xxx.html     # → SVG + PNG，并断言每一屏都是 1920×1080
python3 bundle_html.py flow_xxx.html   # → 单文件自包含 HTML（CSS/图片/JS 全内联）
open flow_xxx.bundle.html              # 给用户评审
```
`render_ux.py` 会逐屏核对像素——规范原文「出图后必须校验最终文件像素尺寸，
而不是只在提示词里声明尺寸」。不达标直接非零退出。

### Step 4　导入 Figma
把 `*.bundle.html` 的内容粘进 Figma 的 HTML 导入插件（html.to.design 一类）。
**必须用 bundle 版**：插件不会去拉相对路径的资源，外链图片一律丢失。
`*.svg` 是备胎——拖进 Figma 也能自动成图层树，但没有 AutoLayout。

## 文件

```
scripts/
  p2ux19.css      画布 1920×1080 + P2 文字描边 + 板式（黑底/青标注/箭头/状态序列）
  svgbake.js      DOM → 分组命名 SVG；图片转 data URI，文字带描边
  render_ux.py    出 SVG + PNG + 逐屏像素断言
  bundle_html.py  打包单文件自包含 HTML（含运行时拼路径的资源兜底）
  p2uxkit.css     ⚠ v1 浅色线框版，已被 p2ux19 取代，仅作历史参考
assets/p2ui/      真实 P2 UI 切图库（nav / task / floor），从项目组 Figma 稿抓取
references/
  layout-rules.md ★ 排布规则，动笔前必读
```

## 素材从哪来

`assets/p2ui/` 里的切图是用 Figma MCP 的 `download_assets` 从项目组真稿抓的。
需要新组件时同样走这条路：`get_metadata` 找节点 → `download_assets` 下原图 → 按真实角色命名。

⚠ **Figma MCP 读文件要 Editor 权限**，只有 View 会报 “don't have edit access”。
读别人的文件前，先让用户把文件 Duplicate 到自己草稿，或让所有者授予编辑权。

## 缺件登记

- **金色主按钮**：规范要求主 CTA 为黄/橙/金，素材库目前只有绿（领取）与青蓝（前往）。
  暂借绿按钮并在图上标注，需美术补一版。
