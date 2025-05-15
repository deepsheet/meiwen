#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
应用入口文件：启动Web服务器，提供API接口
"""

import os
import sys
from src.web_server import run_server
from src.logger import logger

def main():
    """
    主函数：应用程序入口点
    @returns {int} - 返回状态码，0表示成功，1表示失败
    """
    try:
        print("调试：进入main函数")  # 添加调试打印
        # 默认端口为8080，可通过环境变量覆盖
        port = int(os.environ.get('PORT', 8080))
        host = os.environ.get('HOST', '0.0.0.0')
        
        logger.info(f"启动isheet.net自动化营销工具服务")
        run_server(host=host, port=port)
        return 0
    except Exception as e:
        logger.error(f"服务启动失败: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 