# 深表美文 - AI 文章美化系统

**转文本为漂亮页面，让文字自己说话**

🌐 **在线体验**: [p.isheet.net](http://p.isheet.net)

## 📖 产品简介

深表美文是一个基于 AI 的文章美化和 HTML 格式化系统。它能够将普通文本转换为视觉精美的 HTML 页面，支持 AI 自动生成标题、智能排版、响应式设计等功能。

### 核心价值

- ✨ **一键美化**：普通文本 → 精美页面，零设计成本
- 🤖 **AI 驱动**：智能理解内容，自动匹配最佳排版风格
- 🔗 **永久链接**：每篇文章生成独立短 URL，随时分享
- 📱 **完美适配**：手机、平板、电脑全设备响应式
- ⚡ **快速生成**：几秒钟完成格式化，高效便捷
- 💾 **离线可用**：所有样式内联，无需外部资源

## 🎯 应用场景

### 🔗 微信方案
将微信上的方案文字转换为精美网页链接，分享更专业，阅读体验更佳。

### 📊 数据报告
把枯燥的数据表格变成视觉化的精美报告，让信息更直观易懂。

### 📽️ 替代 PPT
大量文字内容不适合 PPT 时，转换为精美网页，更适合阅读和传播。

### 📋 文档资料
技术文档、产品说明、使用手册等，瞬间提升阅读体验。

### 💬 社交媒体
为朋友圈、微博、公众号创建吸睛的图文内容，传播力更强。

### 📝 博客文章
将博客草稿一键转换为精美页面，立即分享你的想法和见解。

## 🚀 快速开始

### 环境要求

- Python 3.8+
- DeepSeek API 密钥或 Qwen API 密钥
- MySQL 数据库（可选，用于博客生成）

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置 API 密钥

编辑 `config/config.py` 文件，设置你的 API 密钥和选择模型：

```python
# DeepSeek API 配置
DEEPSEEK_API_KEY = "your-deepseek-api-key-here"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# QWEN API 配置
QWEN_API_KEY = "your-qwen-api-key-here"
QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
QWEN_MODEL = "qwen3-30b-a3b-instruct-2507"

# 👇 关键：切换这个变量即可更换模型（deepseek 或 qwen）
CURRENT_MODEL = "qwen"
```

💡 **提示**：可以使用命令行工具快速切换模型：
```bash
# 查看当前模型
python debug/switch_model.py

# 切换到 DeepSeek
python debug/switch_model.py deepseek

# 切换到 Qwen
python debug/switch_model.py qwen
```

### 启动服务

```bash
# 方式 1：直接启动
python src/web_server.py

# 方式 2：使用启动脚本
./start.sh
```

服务默认运行在 `http://localhost:8009`

## 📁 项目结构

```
isheetmarketing/
├── README.md              # 项目说明文档（本文件）
├── requirements.txt       # Python 依赖列表
├── app.py                # Flask 应用入口
├── start.sh              # 启动脚本
│
├── src/                  # 源代码目录
│   ├── web_server.py     # Web 服务器主程序
│   ├── blog_generator.py # 博客生成器
│   ├── html_formatter.py # HTML 格式化服务
│   ├── llm_client.py     # 🆕统一的大语言模型客户端（支持多模型）
│   ├── segmented_formatter.py # 分段式 HTML 格式化器
│   ├── db_manager.py     # 数据库管理器
│   └── logger.py         # 日志系统
│
├── config/               # 配置文件目录
│   └── config.py         # API 密钥和数据库配置
│
├── static/               # 静态资源目录
│   ├── index.html        # 首页
│   ├── formatter.html    # HTML 格式化服务页面
│   ├── userfiles/        # 生成的文章文件
│   └── article_ids/      # 文章 ID 映射文件
│
├── docs/                 # 文档目录
│   ├── TEXT_TO_HTML_API.md          # 🆕文本转 HTML API 完整文档
│   ├── TEXT_TO_HTML_QUICKSTART.md   # 🆕文本转 HTML API 快速开始
│   ├── API_DEVELOPMENT_SUMMARY.md   # 🆕API 开发总结
│   ├── DELIVERY_CHECKLIST.md        # 🆕交付清单
│   ├── MULTI_MODEL_QUICKSTART.md    # 🆕多模型支持快速开始
│   ├── MULTI_MODEL_SUPPORT.md       # 🆕多模型支持详细文档
│   ├── MULTI_MODEL_REFACTORING_REPORT.md  # 🆕多模型重构报告
│   ├── PROJECT_COMPLETION.md      # 项目完成总结
│   ├── QUICK_START_TUTORIAL.md    # 快速入门教程
│   ├── QUICK_REFERENCE.md         # 快速参考手册
│   ├── DOCUMENTATION_INDEX.md     # 文档索引
│   └── LONG_ARTICLE_HANDLING.md   # 长文章处理说明
│
├── debug/                # 测试和调试文件目录
│   ├── test_text_to_html_api.py   # 🆕文本转 HTML API 测试脚本
│   ├── test_multi_model.py      # 🆕多模型支持测试脚本
│   ├── switch_model.py          # 🆕模型切换工具
│   ├── test_*.py         # 各种测试脚本
│   ├── check_*.py        # 检查脚本
│   ├── generate_*.py     # 生成示例脚本
│   ├── deploy_*.sh       # 部署脚本（可选）
│   └── *.html            # 临时 HTML 文件
│
├── examples/             # 🆕示例代码目录
│   └── text_to_html_examples.py  # 🆕文本转 HTML API 使用示例
│
└── logs/                 # 日志文件目录
    └── *.log             # 系统日志
```

## 🎨 核心功能

### 1. HTML 格式化服务

将普通文本转换为精美的 HTML 页面：

**API 端点**: `POST /api/format-html`

**请求示例**:
```javascript
{
  "content": "文章内容...",
  "title": "文章标题（可选，不填则 AI 自动生成）",
  "beauty_mode": "strict",  // strict | interpret | expand
  "extra_requirements": "使用蓝色系配色"  // 可选
}
```

**响应示例**:
```javascript
{
  "status": "success",
  "access_url": "/p/abc12345",
  "article_id": "abc12345"
}
```

### 2. 🆕 文本转 HTML API（第三方工具调用）

专为内部系统设计的 API 接口，输入文本直接返回 HTML 代码：

**API 端点**: `POST /api/text-to-html`

**访问控制**: IP 白名单机制（仅允许 localhost、deepsheet.net、chaojibiaoge.com）

**请求示例**:
```python
import requests

response = requests.post(
    "http://localhost:5000/api/text-to-html",
    json={
        "content": "你的文本内容...",
        "title": "可选标题",
        "content_strategy": "strict"
    }
)

if response.status_code == 200:
    html = response.json()["html"]
    # 直接使用 HTML 代码
```

**响应示例**:
```javascript
{
  "status": "success",
  "message": "HTML generated successfully",
  "html": "<!DOCTYPE html>\n<html>...</html>",
  "article_id": "abcdefgh",
  "title": "文章标题"
}
```

**详细文档**:
- 📖 [完整 API 文档](docs/TEXT_TO_HTML_API.md)
- 🚀 [快速开始指南](docs/TEXT_TO_HTML_QUICKSTART.md)
- 💡 [使用示例](examples/text_to_html_examples.py)

### 2. 文章访问

通过短 URL 访问美化后的文章：

**URL 格式**: `/p/{article_id}`

例如：`http://localhost:8009/p/abc12345`

### 3. 三款美化模式

#### 🔒 严格原文
- 一字不差地保持原文 100% 完整
- 仅修正错别字、语法错误
- 适用：正式文档、法律文件、新闻报道

#### 📝 解读优化
- 可以调整段落顺序、优化表达逻辑
- 可以添加必要的过渡句、解释性文字
- 适用：技术文档、内容逻辑重组

#### ✨ 扩写丰富
- 可以补充背景信息、案例、数据支撑
- 可以对专业术语进行解释说明
- 适用：营销文案、科普文章

### 4. AI 自动标题

当用户未提供标题时，系统会自动调用 AI 分析文章内容并生成标题：

- 使用配置的 LLM 模型（DeepSeek/Qwen）
- 标题长度控制在 30 字以内
- 准确概括文章核心内容

### 5. 智能文件名

根据标题自动生成友好的文件名：

- 只保留英文字母、数字和汉字
- 去除特殊字符和空格
- 添加时间戳确保唯一性

例如：`AI 云表格_1775092466.html`

### 6. 长文章处理

采用流式输出技术，支持万字长文：

- ≤ 5000 字：普通模式（快速）
- > 5000 字：流式模式（无输出限制）
- 自动判断，无需手动干预

## 🛠️ 开发指南

### 运行测试

所有测试文件都在 `debug/` 目录下：

```bash
# 测试 HTML 格式化
python debug/test_html_formatter.py

# 测试 AI 标题生成
python debug/test_ai_title_generation.py

# 测试长文章处理（需要 API 额度）
python debug/test_long_article_format.py
```

### 查看日志

```bash
# 实时查看日志
tail -f logs/server.log

# 查看最近的错误
grep ERROR logs/*.log | tail -20
```

### 部署到生产环境

1. 配置生产数据库信息到 `config/config.py`
2. 设置环境变量 `PORT=8009`
3. 使用 gunicorn 或其他 WSGI 服务器运行：
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8009 src.web_server:app
   ```

## 📚 文档导航

### 🎯 新手入门

- **[多模型快速开始](docs/MULTI_MODEL_QUICKSTART.md)** - 30 秒上手，了解如何切换模型
- **[快速参考手册](docs/QUICK_REFERENCE.md)** - 常用命令和 API 示例速查
- **[快速入门教程](docs/QUICK_START_TUTORIAL.md)** - 手把手教你如何使用服务

### 📖 功能详解

- **[文本转 HTML API 文档](docs/TEXT_TO_HTML_API.md)** - 🆕完整的 API 技术规范
- **[文本转 HTML 快速开始](docs/TEXT_TO_HTML_QUICKSTART.md)** - 🆕5分钟快速上手指南
- **[美化模式指南](docs/BEAUTY_MODE_GUIDE.md)** - 三款美化模式详细说明
- **[内容策略指南](docs/CONTENT_STRATEGY_GUIDE.md)** - 内容处理策略使用指南
- **[额外要求指南](docs/EXTRA_REQUIREMENTS_GUIDE.md)** - 如何添加自定义要求
- **[长文章处理说明](docs/LONG_ARTICLE_HANDLING.md)** - 万字长文技术支持

### 🛠️ 开发者文档

- **[多模型支持详细文档](docs/MULTI_MODEL_SUPPORT.md)** - 完整的多模型功能说明
- **[多模型完成总结](docs/MULTI_MODEL_COMPLETION_SUMMARY.md)** - 工作总结和使用场景
- **[文档索引](docs/DOCUMENTATION_INDEX.md)** - 所有文档的导航中心

## 🔧 技术栈

- **后端框架**: Flask
- **AI 模型**: DeepSeek、Qwen 等多个大语言模型
- **统一接口**: LLMClient（支持灵活切换）
- **数据库**: MySQL
- **前端**: 纯 HTML + 内联 CSS（离线优先）
- **部署**: Shell 脚本 + crontab

## 📊 性能指标

| 文章长度 | 处理模式 | 预计耗时 |
|---------|---------|---------|
| < 3000 字 | 普通 | 10-30 秒 |
| 3000-5000 字 | 普通 | 30-60 秒 |
| 5000-10000 字 | 流式 | 60-120 秒 |
| > 10000 字 | 流式 | 120-300 秒 |

## ⚠️ 注意事项

1. **API 额度**：长文章消耗更多 token，请确保账户有足够额度
2. **网络连接**：需要稳定的网络以调用 LLM API
3. **超时设置**：
   - 普通模式：180 秒
   - 流式模式：300 秒
4. **文件存储**：生成的文章保存在 `userdata/userfiles/` 目录

## 🤝 贡献指南

本项目主要用于内部使用，如需修改请参考以下规范：

1. 源代码放在 `src/` 目录
2. 测试代码放在 `debug/` 目录
3. 文档放在 `docs/` 目录
4. 遵循项目的代码规范和命名约定
5. 新功能需配套相应的文档说明

## 📄 许可证

内部项目，仅供内部使用。

---

**深表 AI 工作室** · 用 AI 技术，让内容创作更美好

*最后更新：2026 年 4 月 6 日*
