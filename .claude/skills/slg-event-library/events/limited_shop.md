---
event_type: 限时折扣商店 / 刷新摊位
description: 伪随机折扣商品 + 钻石刷新，本质是折扣礼包的随机化
---

# Lucky Stall / Limited Shop 限时折扣摊位

## 机制总览

```
商店入口 → 随机出现 N 个折扣商品 → 玩家买单 / 跳过 → 钻石刷新重新抽
          (折扣强度随机，偶尔出超值单)
```

## 代表案例

| 游戏 | 活动名 | 视频 |
|---|---|---|
| ROK | **Lucky Stall** | [详解](https://www.youtube.com/watch?v=Z3OEHFnoNuk) / [Maximize](https://www.youtube.com/watch?v=8FZ2B9BOpjI) |
| Last War | Easter Shop | [拆解](https://www.youtube.com/watch?v=QwFci9pvGHw) |
| KoA | Lunar Shop + Lucky Shot | [详解](https://www.youtube.com/watch?v=2CPQ4YVQ9rQ) |
| Whiteout | Emporium of Enigma | [实玩](https://www.youtube.com/watch?v=SKx9bKbgcZA) |

## 设计要点

1. **伪随机折扣 ≠ 纯抽奖** — 本质是刷新式折扣，付费门槛低
2. **刷新钻石的设计** — 刷新成本 ≈ 1 次小额充值，勾人二次付费
3. **节日包装强适配** — 节日商店换皮肤都能用

## P2 落地映射

- 对应表：**1168**（限时商店）+ 刷新机制
- 改造方向：P2 现有商店是固定商品，可以改成"节日期间刷新式折扣"
