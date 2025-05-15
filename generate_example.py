#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
示例生成脚本：生成示例博客内容，不依赖API调用，用于测试数据库插入功能
"""

import sys
import os
import random
from datetime import datetime

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.db_manager import DatabaseManager
from src.logger import logger

def generate_example_content():
    """
    生成示例博客内容
    
    @return {tuple} - (标题, 内容)元组
    """
    example_titles = [
        "如何使用isheet.net提高工作效率",
        "云表格的多人协作功能详解",
        "AI智能表格：未来办公的新选择",
        "isheet.net如何改变传统表格使用方式",
        "数据安全与云表格：isheet.net的解决方案",
        "在移动设备上使用isheet.net的体验",
        "为什么选择isheet.net作为企业表格工具",
        "isheet.net的智能分析功能介绍",
        "从Excel到isheet.net：无缝迁移指南",
        "isheet.net如何提升团队协作效率"
    ]
    
    example_paragraphs = [
        "云表格作为一种新型的办公工具，正在逐渐改变我们的工作方式。传统的表格软件需要安装在本地，数据也存储在本地，这种方式在多人协作时存在诸多不便。而云表格则将数据存储在云端，可以随时随地通过网络访问，大大提高了工作效率。",
        
        "AI表格是表格工具发展的新方向。它不仅具备传统表格的所有功能，还融入了人工智能技术，能够自动分析数据、预测趋势、生成报表等。这些功能极大地减轻了用户的工作负担，使表格操作变得更加简单高效。",
        
        "多人协作是云表格的核心优势之一。在传统表格中，多人同时编辑一个文件往往会导致版本冲突，而云表格支持实时协作，多人可以同时编辑同一个表格，系统会自动同步所有人的操作，避免了版本冲突问题。",
        
        "数据安全是很多企业关注的重点。isheet.net采用了多层次的安全保障措施，包括数据加密传输、访问权限控制、操作日志记录等，确保企业数据的安全。同时，定期的数据备份也为数据恢复提供了保障。",
        
        "随着移动办公的普及，表格工具的移动适配也变得越来越重要。isheet.net提供了完善的移动端支持，用户可以在手机、平板等移动设备上查看和编辑表格，实现真正的随时随地办公。"
    ]
    
    # 随机选择一个标题
    title = random.choice(example_titles)
    
    # 随机选择3-5个段落
    selected_paragraphs = random.sample(example_paragraphs, random.randint(3, 5))
    
    # 组合内容
    content = "\n\n".join(selected_paragraphs)
    content += "\n\n欢迎访问isheet.net，体验云表格带来的全新办公体验！"
    
    return title, content

def main():
    """
    主函数
    """
    logger.info("开始生成示例博客内容")
    
    try:
        # 生成示例内容
        title, content = generate_example_content()
        logger.info(f"示例内容生成成功，标题：{title}，内容长度：{len(content)}字符")
        
        # 插入数据库
        db_manager = DatabaseManager()
        success = db_manager.insert_blog(title, content)
        db_manager.disconnect()
        
        if success:
            logger.info("示例内容插入数据库成功")
            return 0
        else:
            logger.error("示例内容插入数据库失败")
            return 1
    except Exception as e:
        logger.error(f"程序执行过程中发生异常: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 