---
name: iap-leichong-sync
description: IAP累充表同步工具 - 从累充规划表读取K列数据，通过iap_template映射config_id，最终写入iap_config的A_ARR_iap_status字段。触发场景：累充表同步、iap_status替换、累充配置更新、iap配置同步、礼包状态更新、累充替换、拓荒节、复活节累充。
---

# IAP 累充表同步工具

将累充规划表中的 K 列内容同步到 iap_config 的 `A_ARR_iap_status` 字段。

## 触发条件

当用户提到以下关键词时自动激活：
- 累充表同步 / 累充替换 / 累充配置
- iap_status 替换 / iap 配置同步
- 提到具体活动页签名（如"27拓荒节"、"26复活节"）+ 替换/同步

## AI 执行指引

### 1. 确认参数

向用户确认以下信息（如用户已提供则跳过）：

| 参数 | 说明 | 示例 |
|------|------|------|
| **页签名**（必填） | 累充表中的活动页签 | `27拓荒节`、`26复活节` |
| **ID 列表**（可选） | 要同步的 2013xxxx ID | `2013510034,2013510035` |

如果用户没有指定页签名，**必须询问**。

### 2. 执行脚本

脚本位于：`.agents/skills/iap-leichong-sync/scripts/sync_leichong.py`

```bash
# 同步指定 ID
python -X utf8 .agents/skills/iap-leichong-sync/scripts/sync_leichong.py --tab "页签名" --ids ID1,ID2,ID3

# 同步整个页签的所有 2013xxxx ID
python -X utf8 .agents/skills/iap-leichong-sync/scripts/sync_leichong.py --tab "页签名"

# 仅预览不写入（安全检查）
python -X utf8 .agents/skills/iap-leichong-sync/scripts/sync_leichong.py --tab "页签名" --dry-run
```

**重要**：必须使用 `python -X utf8` 运行以避免 Windows 中文乱码。使用 `working_directory` 参数设置工作目录为项目根目录。

### 3. 汇报结果

执行完成后，向用户汇报：
- 找到了多少条记录
- 每条记录的 ID 映射关系（2013xxxx → config_id → iap_config 行号）
- 实际更新了多少个单元格
- 提醒用户可以去 iap_config 表核对

## 三张表关系

| 简称 | Spreadsheet ID | 用途 |
|------|---------------|------|
| 累充表 | `1RFAyBfpG3-8rm3ugNn3NHFdeDg8Erha0VttGzokIy6E` | 源数据，A列=2013xxxx ID，K列=要写入的数据 |
| iap_template | `1sJzacpa0CBp1B8LQX1TboSBOA4T80_t8lH8eEzqHLbY` | 映射表，`A_INT_id` → `A_INT_config_id`，页签=`iap_template_QA` |
| iap_config | `1yS_BehT_Rfcc3sXjDPsSaQRcjPh8YepucYTnUQDpEMc` | 目标表，通过 `A_INT_id`(=config_id) 定位行，写入 `A_ARR_iap_status`(L列)，页签=`iap_config_QA` |

## 数据流

```
累充表(A列: 2013xxxx ID, K列: 数据)
        ↓ 用 2013xxxx ID 匹配
iap_template_QA(A_INT_id → A_INT_config_id)
        ↓ 用 config_id 匹配
iap_config_QA(A_INT_id) → 写入 A_ARR_iap_status(L列)
```

## Google Sheets 认证

使用 `gws auth export --unmasked` 获取凭据，通过 Google Sheets API v4 操作。脚本内部已封装认证逻辑，无需额外配置。

## 注意事项

- 累充表的 K 列对应第 11 列（index 10），列头可能不是标准列名
- iap_config 的 `A_ARR_iap_status` 通过表头动态定位，不硬编码列号
- 写入使用 `RAW` 模式，保持 JSON 字符串原样
- 批量写入使用 `batchUpdate` API 一次完成
- 已存在且内容相同的单元格会显示 `[SAME]` 并跳过写入
