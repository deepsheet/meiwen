#!/bin/bash

# 设置环境变量
export PORT=8009
export FLASK_ENV=development
export FLASK_DEBUG=1

# 确保日志目录存在
mkdir -p logs

# 先关闭已存在的服务
echo "正在检查并关闭已存在的服务..."
pkill -f "python3 app.py"
sleep 2  # 等待进程完全关闭

# 启动服务
echo "启动isheet.net自动化营销工具..."
echo "正在启动服务，详细日志请查看 logs/server.log ..."
python3 app.py > logs/server.log 2>&1 &

# 等待服务启动
sleep 3

# 检查服务是否成功启动
if curl -s http://localhost:${PORT}/health > /dev/null; then
    echo "服务启动成功！"
    echo "服务运行在 http://localhost:${PORT}"
    
    # 自动打开网页
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open "http://localhost:${PORT}"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open "http://localhost:${PORT}"
    fi
else
    echo "服务启动失败，请检查日志文件 logs/server.log"
    echo "最后 10 行日志："
    tail -n 10 logs/server.log
fi

echo ""
echo "可以通过以下命令检查服务状态："
echo "curl http://localhost:${PORT}/health"

# 提示如何设置定时任务
# echo "要设置定时任务，请运行以下命令："
# echo "crontab -e"
# echo "并添加以下内容："
# cat crontab_config.txt 