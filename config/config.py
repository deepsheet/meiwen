#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置文件：存储API密钥和数据库连接信息
"""

# DeepSeek API配置
DEEPSEEK_API_KEY = "sk-170f4fc64eae430aaf111f8d1fb95d42"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# 数据库配置
DB_CONFIG = {
    'host': 'rdsen5kmj2c7h6kj0708o.mysql.rds.aliyuncs.com',  # 直接使用硬编码值
    'user': 'uniuser',
    'password': 'Chenkunjiliukai11112222kang',
    'database': 'uni',
    'port': 3306,
    'charset': 'utf8mb4'
    }


# 博客主题列表
BLOG_TOPICS = [
    "isheet.net：AI表格的优势和特点",
    "云表格应用场景：如何在团队协作中提高效率",
    "AI智能表格的功能介绍：从基础到高级",
    "未来表格的操作方式：语音、手势和AI辅助",
    "云表格是如何进行多人协作的：技术与应用",
    "AI表格在数据分析中的应用",
    "isheet.net云表格与传统表格软件的区别",
    "如何使用AI表格提高工作效率",
    "云表格安全性：数据加密与权限管理",
    "AI表格在不同行业中的应用案例"
]

# 日志配置
LOG_DIR = "logs" 