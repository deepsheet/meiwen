#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
快速测试脚本：仅测试数据库插入功能，不调用DeepSeek API
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.db_manager import DatabaseManager
from src.logger import logger

def main():
    """
    主函数
    """
    logger.info("开始快速测试数据库插入功能")
    
    try:
        # 创建测试数据
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        test_title = f"测试标题 - {now}"
        test_content = f"这是一个测试内容，生成于 {now}。\n\n这只是一个简单的测试，用于验证数据库插入功能是否正常工作。"
        
        logger.info(f"创建测试数据 - 标题: {test_title}")
        
        # 插入数据库
        db_manager = DatabaseManager()
        success = db_manager.insert_blog(test_title, test_content)
        db_manager.disconnect()
        
        if success:
            logger.info("数据库插入测试成功")
            return 0
        else:
            logger.error("数据库插入测试失败")
            return 1
    except Exception as e:
        logger.error(f"测试过程中发生异常: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 