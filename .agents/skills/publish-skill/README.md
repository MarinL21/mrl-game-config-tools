# Publish Skill

这是一个用于 Cursor 的 Agent Skill，旨在引导用户将本地开发好的 Skill 规范化并上传到公司内部 Skills 平台。

## 功能特性

*   **完整性检查**: 自动检查 `SKILL.md`（支持根目录或子目录）、`README.md` 和关键字段（如 description）。
*   **SkillsMP 对齐**: 说明子目录技能与根目录的安装命令差异（SSH vs GitLab `/-/tree/...`）；可选 **`ignore`**，默认不写即上站。
*   **安全检查**: 扫描敏感文件（如 `.env`），防止意外提交。
*   **GitLab 引导**: 提供明确的步骤创建 Internal 类型的 GitLab 仓库。
*   **自动化推送**: 提供 Git 命令自动完成初始化和推送（多 `SKILL.md` 同仓一次推送即可）。

## 使用方法

当你在 Cursor 中输入以下关键词时触发：
*   "发布 skill"
*   "上传 skill"
*   "publish skill"

Agent 会按照预定义的流程一步步引导你完成发布。

## 维护者

*   齐梦瑶
