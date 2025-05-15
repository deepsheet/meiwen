# iSheet.net 自动化营销工具

这是一个自动化营销工具，每天定时为isheet.net网站生成博客文章并插入到数据库中。

## 功能特点

- 每天凌晨5点自动生成博客文章
- 使用DeepSeek AI生成原创内容
- 自动将内容插入到数据库
- 处理内容清理，避免SQL注入问题
- 日志记录系统，每天生成一个日志文件
- RESTful API接口，支持手动触发博客生成

## 目录结构

```
.
├── app.py                # 应用入口文件
├── config/               # 配置文件目录
│   └── config.py         # 配置文件
├── crontab_config.txt    # Crontab定时任务配置
├── logs/                 # 日志目录
├── README.md             # 项目说明文档
├── requirements.txt      # 项目依赖
└── src/                  # 源代码目录
    ├── blog_generator.py # 博客生成器主模块
    ├── db_manager.py     # 数据库管理模块
    ├── deepseek_client.py# DeepSeek API客户端
    ├── logger.py         # 日志模块
    └── web_server.py     # Web服务器模块
```

## 安装配置

1. 安装依赖：

```bash
pip install -r requirements.txt
```

2. 配置DeepSeek API密钥和数据库连接信息：

编辑 `config/config.py` 文件，填入以下信息：
- DeepSeek API密钥
- 数据库连接信息（主机、端口、用户名、密码、数据库名）

3. 设置定时任务：

```bash
# 编辑crontab
crontab -e

# 添加以下内容（或使用crontab_config.txt文件）
0 5 * * * curl -s http://localhost:5000/generate-blog > /dev/null 2>&1
```

## 启动服务

```bash
python app.py
```

服务将在默认端口5000上启动。

## API接口

- `/generate-blog` - 触发博客生成任务
- `/health` - 健康检查接口

示例：

```bash
# 手动触发博客生成
curl http://localhost:5000/generate-blog

# 健康检查
curl http://localhost:5000/health
```

## 日志查看

日志文件存储在 `logs` 目录下，每天一个日志文件，命名格式为 `YYYY-MM-DD.log`。 