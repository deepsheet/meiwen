#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试脚本：直接触发博客生成逻辑，用于测试和调试
"""

import sys
from src.blog_generator import BlogGenerator
from src.logger import logger

def main():
    """
    测试主函数
    """
    logger.info("开始测试博客生成")
    
    try:
        generator = BlogGenerator()
        success = generator.generate_and_save_blog()
        generator.close()
        
        if success:
            logger.info("测试成功")
            return 0
        else:
            logger.error("测试失败")
            return 1
    except Exception as e:
        logger.error(f"测试过程中发生异常: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 