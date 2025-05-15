#!/bin/bash

# 确保日志目录存在
mkdir -p logs

# 安装项目依赖
echo "安装项目依赖..."
pip install -r requirements.txt

# 提示用户配置信息
echo "请编辑 config/config.py 文件，填入以下信息:"
echo "1. DeepSeek API密钥"
echo "2. 数据库连接信息"

echo "安装完成。可以通过以下命令启动服务:"
echo "./start.sh" 