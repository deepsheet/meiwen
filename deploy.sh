#!/bin/bash

# 部署脚本
echo "开始部署项目..."

# 检查SSH密钥是否存在
if [ ! -f ~/.ssh/id_rsa ]; then
    echo "未找到SSH密钥，正在生成..."
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
    echo "请将以下公钥添加到服务器的 ~/.ssh/authorized_keys 文件中："
    cat ~/.ssh/id_rsa.pub
    exit 1
fi

# 测试SSH连接
echo "测试SSH连接..."
if ! ssh -o BatchMode=yes -o ConnectTimeout=5 root@121.40.238.36 echo "SSH连接成功" > /dev/null 2>&1; then
    echo "SSH连接失败，请确保："
    echo "1. 服务器IP地址正确"
    echo "2. SSH密钥已添加到服务器的 ~/.ssh/authorized_keys"
    echo "3. 服务器防火墙允许SSH连接"
    exit 1
fi

# 1. 创建远程目录
echo "创建远程目录..."
ssh root@121.40.238.36 "mkdir -p /alidata/www/isheetmarting"

# 2. 传输项目文件（排除不需要的文件和目录）
echo "传输项目文件..."
rsync -avz --exclude '.git' \
    --exclude '.vscode' \
    --exclude '.conda' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude 'logs/*' \
    --exclude 'test_*.py' \
    --exclude 'quick_test.py' \
    --exclude 'Miniconda3-latest-MacOSX-arm64.sh' \
    ./ root@121.40.238.36:/alidata/www/isheetmarting/

# 3. 在服务器上安装系统依赖
echo "安装系统依赖..."
ssh root@121.40.238.36 "apt-get update && \
    apt-get install -y python3-dev python3-pip python3-venv libssl-dev libffi-dev build-essential"

# 4. 在服务器上安装Python依赖
echo "安装项目依赖..."
ssh root@121.40.238.36 "cd /alidata/www/isheetmarting && \
    python3 -m pip install --upgrade pip && \
    python3 -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt"

# 5. 设置启动脚本权限
echo "设置脚本权限..."
ssh root@121.40.238.36 "cd /alidata/www/isheetmarting && \
    chmod +x start.sh"

echo "部署完成！" 