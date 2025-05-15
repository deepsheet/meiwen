#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试博客生成功能
"""

import sys
import os

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.deepseek_client import DeepSeekClient
from src.logger import logger

def main():
    """
    主函数
    """
    logger.info("开始测试博客生成功能")
    
    try:
        # 创建DeepSeek客户端
        client = DeepSeekClient()
        
        # 生成博客内容
        logger.info("开始生成博客内容...")
        title, content = client.generate_blog()
        
        if title and content:
            # 保存到文件以便检查
            with open("test_blog_output.txt", "w", encoding="utf-8") as f:
                f.write(f"# {title}\n\n{content}")
            
            logger.info(f"博客生成成功，标题: {title}")
            logger.info(f"内容长度: {len(content)} 字符")
            logger.info(f"博客内容已保存到 test_blog_output.txt")
            logger.info(f"内容预览: {content[:100]}...")
            return 0
        else:
            logger.error("博客生成失败")
            return 1
    except Exception as e:
        logger.error(f"测试博客生成失败: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 