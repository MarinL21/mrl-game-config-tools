# p2-translation-automatic

游戏本地化翻译全流程工具。

## 核心能力

从 **UX截图** 或 **原始文本** 出发，完成完整的本地化翻译流程：

1. **文本提取** — 从 UX 截图识别或直接接收中文原文
2. **Key 查重** — 检查新 Key 是否与现有 46000+ 条记录冲突
3. **术语对齐** — 规范库 + 在线检索，确保术语一致性
4. **翻译记忆** — 复用 40000+ 条已有翻译
5. **18 语言翻译** — cn → en → fr → de → po → zh → id → th → sp → ru → tr → vi → it → pl → ar → jp → kr → cns
6. **写入暂存区** — 自动写入 Google Sheet「AI翻译暂存」页签
7. **用户 Review → 提交** — 勾选确认后一键提交到目标页签

## 前置依赖

| 依赖 | 说明 |
|------|------|
| Python 3 | `google-api-python-client`, `google-auth` |
| gws CLI | 已认证（`gws auth login`），用于获取 OAuth 凭据 |
| Google Sheet | 需有编辑权限 |
| Apps Script | 已部署 `localization_tool.gs`（见 [setup-apps-script.md](setup-apps-script.md)） |

## 安装

```bash
npx skills add git@git.tap4fun.com:skills/p2-translation-automatic.git --skill 'p2-translation-automatic'
```

## 工具脚本

| 脚本 | 功能 |
|------|------|
| `glossary_lookup.py` | 术语规范库查询/添加 |
| `analyze_term.py` | 术语翻译频率分析 |
| `search_terms.py` | 术语在线检索（直连 Google Sheet） |
| `check_duplicates.py` | Key 重复检测 |
| `lookup_tm.py` | 翻译记忆查询 |
| `scan_all_keys.py` | 刷新 Key 索引 |
| `build_translation_memory.py` | 刷新翻译记忆库 |
| `fix_dropdown.py` | 修复暂存区下拉菜单 |

## 触发场景

游戏多语言配置、本地化翻译表、i18n 配置、UI 文本提取、多语言扩散翻译、LC_Key 生成、翻译存入表格、UX 截图翻译。
