# p2-festival-art-brief

P2 节日美需包装工具 —— 给 Claude Code 装上这个 skill 后，说"包装 {节日}"或"写 {节日} 的主城皮肤美需"，它会：

1. 从 `knowledge/` 下的 13 份节日 MD 读历年档期 / 命名 / 避坑
2. 结合互联网创意池和 P2 命名范式产出新美需（模块拓扑 + 名称 + 描述 + 参考链接）
3. 自动在**节日本地化文案主表**建新页签，按日历顺序紧贴前一月节日 tab 插入

## 安装

```bash
npx skills add --skill p2-festival-art-brief
```

装完在 Claude Code 里直接说"包装 2027 科技节（蒸汽朋克方向）"之类即可触发。

## 前置依赖

- **Claude Code**（这个 skill 在 Claude Code 里跑）
- **gws CLI**（操作 Google Sheets；`scripts/create_art_brief_tab.py` 调它建 tab）
- 节日本地化文案主表读写权限

## 目录结构

```
p2-festival-art-brief/
├── SKILL.md              # 入口：Claude 照着这里的 7 步流程工作
├── README.md             # 你现在看的这份
├── knowledge/            # 知识库正本 —— 13 份节日 MD + 竞品样本 + README
│   ├── 00_备用节日.md
│   ├── 01_春节.md ~ 12_圣诞节.md
│   ├── 09_音乐节_2026行军特效.md
│   ├── _competitor_base_skin_samples.md
│   └── README.md
└── scripts/
    └── create_art_brief_tab.py   # 建 Sheet 页签的脚本（带富文本参考链接）
```

## 覆盖节日

| 月 | 节日 | 循环身份 |
|---|---|---|
| 1 | 春节 | 行军特效套装循环 |
| 2 | 情人节 | 机甲皮肤循环 |
| 3 | 科技节 | 主城套装循环 |
| 4 | 复活节 | 主题型 |
| 5 | 拓荒节 | 主题型 |
| 6 | 深海节 | 主题型 |
| 7 | 登月节 | 主题型 |
| 8 | 周年庆 | 年度头号节日 |
| 9 | 音乐节 | 主题型 |
| 10 | 万圣节 | 手札循环 |
| 11 | 感恩节 | 主城套装循环 |
| 12 | 圣诞节 | 斗士皮肤循环 |
| — | 备用：泼水节 / 摘果节 / 篝火节 | — |

## 典型使用场景

- **"帮我想 2027 科技节的新方向"** → 从 `knowledge/03_科技节.md` 排除历年已用方向，推荐 3-5 个候选题材
- **"包装 2026 10 月万圣节，亡灵节方向"** → 按 `10_万圣节.md` 范式产出传说+超凡双档 + 手札 + BP 全套美需
- **"蒸汽朋克能套哪几个节日"** → 扫 12 份节日 MD 的"已用方向"章节，推荐最适配的 2-3 个档期

## 相关 skill

这个 skill 只管美需包装，下游链路交给别的 skill：

- `p2-translation-style` — 中英风格基准
- `p2-translation-automatic` — 18 语翻译扩散
- `p2-unite-gift-pack` — 行军表情/特效/联动/头像框礼包端到端配置
- `p2-unite-gift-config` — 上述礼包的表级配置规范

## 维护者

liusiyi@happyfactory.com
