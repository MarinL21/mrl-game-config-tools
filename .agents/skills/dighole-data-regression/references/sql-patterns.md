# 挖孔数据回归 SQL 查询模板

所有 SQL 基于 P2 游戏（game_cd=1041），TRINO 环境。
使用 `v1041.ods_user_xxx` 表，**无需 game_cd 条件**。

占位符说明：
- `{START_DATE}` / `{END_DATE}` — 活动日期（partition_date 用，UTC+8）
- `{UTC_START_TS}` / `{UTC_END_TS}` — 活动开始/结束的 Unix 时间戳（UTC）
- `{ACTIVITY_ID}` — 活动 ID（如 21127575）
- `{TASK_IDS}` — 任务 ID 列表（从配置表读取）
- `{IAP_IDS}` — 礼包 ID 列表（从配置表读取）
- `{FIRST_TASK_ID}` — 第一个任务 ID（用于确定活动服务器）

---

## 1. 活动服活跃人数

**不能用全服活跃**，必须先获取活动开放的服务器列表。

```sql
WITH activity_servers AS (
    SELECT DISTINCT server_id
    FROM v1041.ods_user_task
    WHERE task_id = '{FIRST_TASK_ID}'
      AND attribute1 LIKE '%{ACTIVITY_ID}%'
      AND status = 1
)
SELECT
    COUNT(DISTINCT l.user_id) AS active_users,
    COUNT(DISTINCT s.server_id) AS server_count
FROM v1041.ods_user_login l
JOIN activity_servers s ON l.server_id = s.server_id
WHERE l.partition_date BETWEEN '{START_DATE}' AND '{END_DATE}'
```

---

## 2. 触达人数

control_id 格式注意大小写：`UiActivityMain.ActivityItem_{ACTIVITY_ID}`

```sql
SELECT COUNT(DISTINCT user_id) AS touch_users
FROM v1041.ods_user_click
WHERE partition_date BETWEEN '{START_DATE}' AND '{END_DATE}'
  AND control_id = 'UiActivityMain.ActivityItem_{ACTIVITY_ID}'
```

如果活动有多个 activity_id，用 IN：
```sql
  AND control_id IN (
      'UiActivityMain.ActivityItem_{ACTIVITY_ID_1}',
      'UiActivityMain.ActivityItem_{ACTIVITY_ID_2}'
  )
```

---

## 3. 关卡通关数据

使用 `ods_user_task` 表，**不是 ods_user_event**。

### 3.1 各关卡通关人数

```sql
SELECT
    task_id,
    COUNT(DISTINCT user_id) AS clear_users
FROM v1041.ods_user_task
WHERE partition_date BETWEEN '{START_DATE}' AND '{END_DATE}'
  AND task_id IN ({TASK_IDS})
  AND attribute1 LIKE '%{ACTIVITY_ID}%'
  AND status = 1
GROUP BY task_id
ORDER BY task_id
```

### 3.2 玩家最高完成关卡

```sql
SELECT
    user_id,
    MAX(task_id) AS max_task_id
FROM v1041.ods_user_task
WHERE partition_date BETWEEN '{START_DATE}' AND '{END_DATE}'
  AND task_id IN ({TASK_IDS})
  AND attribute1 LIKE '%{ACTIVITY_ID}%'
  AND status = 1
GROUP BY user_id
```

---

## 4. 付费数据

### 4.1 整体付费（按 UTC timestamps 过滤）

```sql
SELECT
    COUNT(DISTINCT user_id) AS pay_users,
    SUM(pay_price) AS total_revenue,
    SUM(pay_price) / COUNT(DISTINCT user_id) AS arppu
FROM v1041.ods_user_order
WHERE partition_date BETWEEN '{START_DATE_MINUS1}' AND '{END_DATE}'
  AND iap_id IN ({IAP_IDS})
  AND timestamps >= {UTC_START_TS}
  AND timestamps < {UTC_END_TS}
```

> `partition_date` 比 UTC 日期多扩 1 天（因 partition_date 是 UTC+8），确保不遗漏。

### 4.2 按 IAP 分类统计

```sql
SELECT
    iap_id,
    pay_price,
    COUNT(DISTINCT user_id) AS buyers,
    COUNT(*) AS purchases,
    SUM(pay_price) AS revenue
FROM v1041.ods_user_order
WHERE partition_date BETWEEN '{START_DATE_MINUS1}' AND '{END_DATE}'
  AND iap_id IN ({IAP_IDS})
  AND timestamps >= {UTC_START_TS}
  AND timestamps < {UTC_END_TS}
GROUP BY iap_id, pay_price
ORDER BY iap_id
```

### 4.3 分 R 级付费

```sql
WITH user_pay AS (
    SELECT
        user_id,
        SUM(pay_price) AS total_pay
    FROM v1041.ods_user_order
    WHERE partition_date BETWEEN '{START_DATE_MINUS1}' AND '{END_DATE}'
      AND iap_id IN ({IAP_IDS})
      AND timestamps >= {UTC_START_TS}
      AND timestamps < {UTC_END_TS}
    GROUP BY user_id
)
SELECT
    CASE
        WHEN total_pay < 10 THEN '小R(<$10)'
        WHEN total_pay < 100 THEN '中R($10~$100)'
        WHEN total_pay < 500 THEN '大R($100~$500)'
        ELSE '超R($500+)'
    END AS r_level,
    COUNT(*) AS users,
    ROUND(SUM(total_pay), 2) AS total_revenue,
    ROUND(AVG(total_pay), 2) AS avg_pay,
    ROUND(SUM(total_pay) / (SELECT SUM(total_pay) FROM user_pay) * 100, 2) AS pct
FROM user_pay
GROUP BY 1
ORDER BY MIN(total_pay)
```

### 4.4 每日收入趋势（UTC 日期）

```sql
SELECT
    CAST(FROM_UNIXTIME(timestamps) AS DATE) AS utc_date,
    iap_id,
    SUM(pay_price) AS daily_revenue,
    COUNT(DISTINCT user_id) AS daily_buyers
FROM v1041.ods_user_order
WHERE partition_date BETWEEN '{START_DATE_MINUS1}' AND '{END_DATE}'
  AND iap_id IN ({IAP_IDS})
  AND timestamps >= {UTC_START_TS}
  AND timestamps < {UTC_END_TS}
GROUP BY 1, 2
ORDER BY 1, 2
```

> `FROM_UNIXTIME(timestamps)` 将 Unix 时间戳转为 UTC 日期。

---

## 5. 关卡完成与付费关联

分析完成特定里程碑关卡玩家的平均付费。

```sql
WITH user_pay AS (
    SELECT user_id, SUM(pay_price) AS total_pay
    FROM v1041.ods_user_order
    WHERE partition_date BETWEEN '{START_DATE_MINUS1}' AND '{END_DATE}'
      AND iap_id IN ({IAP_IDS})
      AND timestamps >= {UTC_START_TS}
      AND timestamps < {UTC_END_TS}
    GROUP BY user_id
),
user_max_task AS (
    SELECT user_id, MAX(task_id) AS max_task
    FROM v1041.ods_user_task
    WHERE partition_date BETWEEN '{START_DATE}' AND '{END_DATE}'
      AND task_id IN ({NORMAL_TASK_IDS})
      AND attribute1 LIKE '%{ACTIVITY_ID}%'
      AND status = 1
    GROUP BY user_id
)
SELECT
    CASE
        WHEN t.max_task >= {TASK_ID_100} THEN '完成100关'
        WHEN t.max_task >= {TASK_ID_60} THEN '完成60~99关'
        ELSE '未完成60关'
    END AS level_group,
    COUNT(DISTINCT t.user_id) AS users,
    ROUND(AVG(COALESCE(p.total_pay, 0)), 2) AS avg_pay,
    ROUND(SUM(COALESCE(p.total_pay, 0)), 2) AS total_pay
FROM user_max_task t
LEFT JOIN user_pay p ON t.user_id = p.user_id
GROUP BY 1
```

> 里程碑关卡（如60关、100关）的 task_id 从配置表读取后确定。

---

## 6. 成就礼包档位分析

```sql
SELECT
    iap_id,
    pay_price AS price,
    COUNT(DISTINCT user_id) AS buyers,
    COUNT(*) AS purchases,
    SUM(pay_price) AS revenue
FROM v1041.ods_user_order
WHERE partition_date BETWEEN '{START_DATE_MINUS1}' AND '{END_DATE}'
  AND iap_id IN ({ACHIEVEMENT_IAP_IDS})
  AND timestamps >= {UTC_START_TS}
  AND timestamps < {UTC_END_TS}
GROUP BY iap_id, pay_price
ORDER BY pay_price
```
