#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Web服务器模块：提供HTTP接口，处理博客生成请求
"""

import sys
import os
import time
from flask import Flask, jsonify, send_from_directory

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.blog_generator import BlogGenerator
from src.logger import logger

app = Flask(__name__, static_folder='../static')

@app.route('/')
def index():
    """
    返回状态页面
    
    @return {Response} - HTML页面
    """
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/generate-blog', methods=['GET'])
def generate_blog():
    """
    生成博客的API端点
    
    @return {dict} - API响应
    """
    try:
        logger.info("收到博客生成请求")
        logger.info("开始处理博客生成任务")
        
        generator = BlogGenerator()
        success = generator.generate_and_save_blog()
        generator.close()
        
        if success:
            logger.info("博客生成任务已完成")
            return jsonify({
                "status": "success",
                "message": "博客生成成功"
            })
        else:
            logger.error("博客生成任务失败")
            return jsonify({
                "status": "error",
                "message": "博客生成失败"
            })
    except Exception as e:
        error_msg = str(e)
        logger.error(f"博客生成任务异常: {error_msg}")
        return jsonify({
            "status": "error",
            "message": f"博客生成异常: {error_msg}"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    健康检查接口
    
    @return {dict} - 服务状态信息
    """
    return jsonify({
        "status": "healthy",
        "service": "isheet-marketing-blog-generator",
        "time": time.strftime("%Y-%m-%d %H:%M:%S")
    })

def run_server(host='0.0.0.0', port=5000):
    """
    启动Web服务器
    
    @param {str} host - 主机地址
    @param {int} port - 端口号
    """
    logger.info(f"启动Web服务器，监听 {host}:{port}")
    app.run(host=host, port=port, debug=True)

if __name__ == "__main__":
    run_server() 