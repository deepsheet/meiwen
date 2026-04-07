#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
博客生成器主模块：负责协调DeepSeek API和数据库操作，实现博客的生成和保存
"""

import sys
import os
import time
from datetime import datetime

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.llm_client import LLMClient
from src.db_manager import DatabaseManager
from src.html_formatter import HTMLFormatter
from src.logger import logger

class BlogGenerator:
    """
    博客生成器类
    """
    def __init__(self, base_url=None, model_name=None):
        """
        初始化博客生成器
        
        @param {str} base_url - 可选的域名配置，用于 HTML 格式化时的底部标识链接
        @param {str} model_name - 可选的模型名称，如果不提供则使用配置文件中的设置
        """
        self.llm_client = LLMClient(model_name=model_name)
        self.db_manager = DatabaseManager()
        # 🔴 动态域名支持：传递域名给 HTMLFormatter
        self.html_formatter = HTMLFormatter(base_url=base_url)
    
    def generate_and_save_blog(self, format_html=True):
        """
        生成博客并保存到数据库
            
        @param {bool} format_html - 是否对文章进行 HTML 格式化增强
        @return {bool} - 操作是否成功
        """
        logger.info(f"开始执行博客生成任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        # 生成博客内容
        title, content = self.llm_client.generate_blog()
            
        if not title or not content:
            logger.error("博客内容生成失败，任务终止")
            return False
            
        logger.info(f"成功生成博客 - 标题：{title}")
            
        # 如果需要，对文章进行 HTML 格式化增强
        formatted_content = content
        # if format_html:
        #     logger.info("正在对文章进行 HTML 格式化增强...")
        #     try:
        #         formatted_content = self.html_formatter.format_article(content, title)
        #         logger.info("HTML 格式化完成")
        #     except Exception as e:
        #         logger.warning(f"HTML 格式化失败，使用原始内容：{str(e)}")
        #         formatted_content = content
            
        # 插入数据库
        success = self.db_manager.insert_blog(title, formatted_content)
            
        if not success:
            logger.warning("首次插入失败，尝试清理内容后重试")
            # 尝试清理内容后重新插入
            clean_title, clean_content = self.llm_client.retry_with_sanitized_content(title, formatted_content)
                
            if not clean_title or not clean_content:
                logger.error("内容清理失败，任务终止")
                return False
                
            # 重新尝试插入
            retry_success = self.db_manager.insert_blog(clean_title, clean_content)
                
            if not retry_success:
                logger.error("重试插入仍然失败，任务终止")
                return False
                
            logger.info("重试插入成功")
            return True
            
        logger.info("博客生成和保存任务完成")
        return True
    
    def close(self):
        """
        关闭资源连接
        """
        self.db_manager.disconnect()
        logger.info("资源连接已关闭")

def main():
    """
    主函数
    """
    try:
        generator = BlogGenerator()
        result = generator.generate_and_save_blog()
        generator.close()
        
        if result:
            logger.info("程序执行成功")
            return 0
        else:
            logger.error("程序执行失败")
            return 1
    except Exception as e:
        logger.error(f"程序执行过程中发生异常: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 