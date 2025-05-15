#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试DeepSeek API连接和调用
"""

import sys
import os
import json

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.deepseek_client import DeepSeekClient
from src.logger import logger

def main():
    """
    主函数
    """
    logger.info("开始测试DeepSeek API连接")
    
    try:
        # 创建DeepSeek客户端
        client = DeepSeekClient()
        
        # 简单测试 - 仅生成一个短内容
        short_prompt = {
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位专业的助手。"
                },
                {
                    "role": "user",
                    "content": "请用一句话描述什么是isheet.net云表格。"
                }
            ],
            "model": "deepseek-chat",
            "max_tokens": 100
        }
        
        logger.info("发送测试请求到DeepSeek API...")
        response = client._call_api(short_prompt)
        
        logger.info("收到API响应:")
        logger.info(json.dumps(response, ensure_ascii=False, indent=2))
        
        # 解析响应
        content = client._parse_response(response)
        logger.info(f"解析的内容: {content}")
        
        logger.info("DeepSeek API测试成功!")
        return 0
    except Exception as e:
        logger.error(f"测试DeepSeek API失败: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 