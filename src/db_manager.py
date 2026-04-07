#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据库管理模块：负责与数据库的交互，执行SQL插入操作
"""

import sys
import os
import pymysql
import string
import random
from datetime import datetime

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.config import DB_CONFIG
from src.logger import logger

class DatabaseManager:
    """
    数据库管理类
    """
    def __init__(self):
        """
        初始化数据库连接
        """
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """
        建立数据库连接
        
        @return {bool} - 连接是否成功
        """
        try:
            self.conn = pymysql.connect(
                host=DB_CONFIG["host"],
                port=DB_CONFIG["port"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"],
                database=DB_CONFIG["database"],
                charset=DB_CONFIG["charset"]
            )
            self.cursor = self.conn.cursor()
            logger.info("数据库连接成功")
            return True
        except Exception as e:
            logger.error(f"数据库连接失败: {str(e)}")
            return False
    
    def disconnect(self):
        """
        关闭数据库连接
        """
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("数据库连接已关闭")
    
    def insert_blog(self, title, content):
        """
        插入博客到数据库
        
        @param {str} title - 博客标题
        @param {str} content - 博客内容
        @return {bool} - 插入是否成功
        """
        if not self.conn or not self.cursor:
            if not self.connect():
                return False
        
        try:
            # 生成随机8位字符串作为ID
            blog_id = self._generate_random_id(8)
            
            # 生成当天当前时间前一小时内的随机时间
            current_hour = datetime.now().hour
            # 如果当前时间小于10点，则使用9点
            if current_hour < 10:
                hour = 9
            # 如果当前时间大于22点，则使用21点
            elif current_hour > 22:
                hour = 21
            # 否则使用当前时间前一小时
            else:
                hour = current_hour - 1
            
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            current_time = datetime.now().replace(hour=hour, minute=minute, second=second).strftime('%Y-%m-%d %H:%M:%S')
            
            # 执行SQL插入
            sql = """
            INSERT INTO oa_discussion(id, project_id, sys_addtime, sys_adduser, tags, title, content)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            self.cursor.execute(sql, (blog_id, 'blog', current_time, 'system', '博客', title, content))
            self.conn.commit()
            
            logger.info(f"博客插入成功，ID: {blog_id}, 标题: {title}")
            return True
        except Exception as e:
            logger.error(f"博客插入失败: {str(e)}")
            self.conn.rollback()
            return False
    
    def _generate_random_id(self, length):
        """
        生成指定长度的随机字符串
        
        @param {int} length - 字符串长度
        @return {str} - 随机字符串
        """
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length)) 