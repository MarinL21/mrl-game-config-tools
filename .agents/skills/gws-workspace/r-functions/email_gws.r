# ============================================================
# email_gws.r — 业务逻辑：发送各游戏周报邮件
# 依赖：email_gws_fn.r（函数定义）
# ============================================================
source(file.path(dirname(sys.frame(1)$ofile), "email_gws_fn.r"))

day <- Sys.Date()

flog.info(paste0("=", paste(rep("=", 50), collapse = ""), "="))
flog.info("开始发送邮件（gws 命令行方案）")
flog.info(paste0("=", paste(rep("=", 50), collapse = ""), "="))

# ============================================================
# 发送 K1 周报
# ============================================================
# flog.info("--- 发送 K1 周报 ---")

# k1_to <- c(
#   'xuzizhan@nibirutech.com', 'zhangjinge@nibirutech.com',
#   'songweihua@nibirutech.com', 'cuilinxu@nibirutech.com',
#   'jinan@nibirutech.com', 'shengying@nibirutech.com',
#   'wanghaizhu@nibirutech.com', 'lijinyuan@nibirutech.com',
#   'zhuhao@nibirutech.com', 'xuefeng@nibirutech.com',
#   'zouhanling@nibirutech.com', 'jiangzhenyu@nibirutech.com',
#   'luodengfeng@nibirutech.com'
# )

# k1_conclude <- read_conclude_text(
#   paste0("/Users/duansiyi/Desktop/result/k1_conclude_text_", day, ".txt"), "K1"
# )
# k1_share_link <- paste0("https://bi-docs.tap4fun.com/%E6%95%B0%E6%8D%AE%E5%88%86%E6%9E%90%E6%8A%A5%E5%91%8A/%E5%8D%8A%E5%B9%B4%E5%91%A8%E6%AF%94%E5%91%A8%E6%8A%A5/K1%E5%91%A8%E6%8A%A5_", day, ".html")
# k1_body <- paste0(
#   "<strong>您好，</strong><br><br>",
#   "本期周报可以通过以下链接在线查看，也可以下载附件到本地进行查看。<br><br>",
#   "周报链接：<a href='", k1_share_link, "'>K1周报在线浏览链接-", day, "</a><br><br>",
#   "<strong>本次报告结论如下：</strong><br><br>",
#   gsub("\n", "<br>", k1_conclude)
# )
# send_email_gws(
#   from        = "duansiyi@nibirutech.com",
#   to          = k1_to,
#   subject     = paste0("【市场数据邮件K1】-", day),
#   body_text   = k1_body,
#   attachments = paste0("/Users/duansiyi/Desktop/result/K1周报_", day, ".html")
# )

# # ============================================================
# # 发送 P2 周报
# # ============================================================
# flog.info("--- 发送 P2 周报 ---")

# p2_to <- c(
#   'xuzizhan@nibirutech.com', 'wanghaizhu@nibirutech.com',
#   'yaoyuanchao@nibirutech.com', 'songweihua@nibirutech.com',
#   'zouhanling@nibirutech.com', 'zhangjinge@nibirutech.com',
#   'cuilinxu@nibirutech.com', 'guoyifeng@nibirutech.com',
#   'jinan@nibirutech.com', 'shengying@nibirutech.com'
# )

# p2_conclude <- read_conclude_text(
#   paste0("/Users/duansiyi/Desktop/result/p2_conclude_text_", day, ".txt"), "P2"
# )
# p2_share_link <- paste0("https://bi-docs.tap4fun.com/%E6%95%B0%E6%8D%AE%E5%88%86%E6%9E%90%E6%8A%A5%E5%91%8A/%E5%8D%8A%E5%B9%B4%E5%91%A8%E6%AF%94%E5%91%A8%E6%8A%A5/P2%E5%91%A8%E6%8A%A5_", day, ".html")
# p2_body <- paste0(
#   "<strong>您好，</strong><br><br>",
#   "本期周报可以通过以下链接在线查看，也可以下载附件到本地进行查看。<br><br>",
#   "周报链接：<a href='", p2_share_link, "'>P2周报在线浏览链接-", day, "</a><br><br>",
#   "<strong>本次报告结论如下：</strong><br><br>",
#   gsub("\n", "<br>", p2_conclude)
# )
# send_email_gws(
#   from        = "duansiyi@nibirutech.com",
#   to          = p2_to,
#   subject     = paste0("【市场数据邮件P2】-", day),
#   body_text   = p2_body,
#   attachments = paste0("/Users/duansiyi/Desktop/result/P2周报_", day, ".html")
# )

# # ============================================================
# # 发送 KOW 周报
# # ============================================================
# flog.info("--- 发送 KOW 周报 ---")

# kow_to <- c(
#   'xuzizhan@nibirutech.com', 'zhongyan@nibirutech.com',
#   'songweihua@nibirutech.com', 'zhangjinge@nibirutech.com',
#   'cheyaodong@nibirutech.com', 'wanghaizhu@nibirutech.com',
#   'chenfenglong@nibirutech.com', 'guoyifeng@nibirutech.com',
#   'cuilinxu@nibirutech.com', 'Linxiaoxiao@nibirutech.com',
#   'jinan@nibirutech.com', 'shengying@nibirutech.com',
#   'zhenglongfei@nibirutech.com'
# )

# kow_conclude <- read_conclude_text(
#   paste0("/Users/duansiyi/Desktop/result/kow_conclude_text_", day, ".txt"), "KOW"
# )
# kow_share_link <- paste0("https://bi-docs.tap4fun.com/%E6%95%B0%E6%8D%AE%E5%88%86%E6%9E%90%E6%8A%A5%E5%91%8A/%E5%8D%8A%E5%B9%B4%E5%91%A8%E6%AF%94%E5%91%A8%E6%8A%A5/KOW%E5%91%A8%E6%8A%A5_", day, ".html")
# kow_body <- paste0(
#   "<strong>您好，</strong><br><br>",
#   "本期周报可以通过以下链接在线查看，也可以下载附件到本地进行查看。<br><br>",
#   "周报链接：<a href='", kow_share_link, "'>KOW周报在线浏览链接-", day, "</a><br><br>",
#   "<strong>本次报告结论如下：</strong><br><br>",
#   gsub("\n", "<br>", kow_conclude)
# )
# send_email_gws(
#   from        = "duansiyi@nibirutech.com",
#   to          = kow_to,
#   subject     = paste0("【市场数据邮件KOW】-", day),
#   body_text   = kow_body,
#   attachments = paste0("/Users/duansiyi/Desktop/result/KOW周报_", day, ".html")
# )

# # ============================================================
# # 发送 K1D23 周报
# # ============================================================
# flog.info("--- 发送 K1D23 周报 ---")

# k1d23_to <- c(
#   'xuzizhan@nibirutech.com', 'fengqiwu@nibirutech.com',
#   'lizhen@nibirutech.com', 'zhangjinge@nibirutech.com',
#   'songweihua@nibirutech.com', 'luoweiran@nibirutech.com',
#   'getian@nibirutech.com', 'jinan@nibirutech.com',
#   'shengying@nibirutech.com', 'zhangzhiquan@nibirutech.com',
#   'zhenglongfei@nibirutech.com', 'guoyifeng@nibirutech.com'
# )

# k1d23_conclude <- read_conclude_text(
#   paste0("/Users/duansiyi/Desktop/result/k1d23_conclude_text_", day, ".txt"), "K1D23"
# )
# k1d23_share_link <- paste0("https://bi-docs.tap4fun.com/%E6%95%B0%E6%8D%AE%E5%88%86%E6%9E%90%E6%8A%A5%E5%91%8A/%E5%8D%8A%E5%B9%B4%E5%91%A8%E6%AF%94%E5%91%A8%E6%8A%A5/K1D23%E5%91%A8%E6%8A%A5_", day, ".html")
# k1d23_body <- paste0(
#   "<strong>您好，</strong><br><br>",
#   "本期周报可以通过以下链接在线查看，也可以下载附件到本地进行查看。<br><br>",
#   "周报链接：<a href='", k1d23_share_link, "'>K1D23周报在线浏览链接-", day, "</a><br><br>",
#   "<strong>本次报告结论如下：</strong><br><br>",
#   gsub("\n", "<br>", k1d23_conclude)
# )
# send_email_gws(
#   from        = "duansiyi@nibirutech.com",
#   to          = k1d23_to,
#   subject     = paste0("【市场数据邮件K1D23】-", day),
#   body_text   = k1d23_body,
#   attachments = paste0("/Users/duansiyi/Desktop/result/K1D23周报_", day, ".html")
# )

# flog.info(paste0("=", paste(rep("=", 50), collapse = ""), "="))
# flog.info("所有邮件发送完成")
# flog.info(paste0("=", paste(rep("=", 50), collapse = ""), "="))
