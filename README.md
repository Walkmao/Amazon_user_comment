# Amazon-User-Comment

本文档旨在爬取美国亚马逊官网的用户评论，以做用户体验数据分析，但近期因美国官网已被墙故而需要翻墙才能访问，请知悉。

-------------------------

**1.代码及文件配置说明**：

- Amazon.py：网页爬取和页面缓存（download）
- Amazon_review.py：页面解析和数据输出（analysis）
- Id.xlsx：储存亚马逊产品的唯一编号ASIN码，实现自动输入
- newUA.txt：储存cookie和IP池，实现随机变换IP反爬虫
