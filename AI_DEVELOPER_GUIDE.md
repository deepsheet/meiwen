# AI 开发者指南 - 深表美文技术文档

> **本文档专为 AI 编程智能体设计**，提供完整的技术架构、开发规范和项目结构说明，帮助新的 AI IDE 快速理解和开发本项目。

---

## 📋 目录

1. [项目概述](#项目概述)
2. [技术架构](#技术架构)
3. [核心模块说明](#核心模块说明)
4. [API 接口规范](#api-接口规范)
5. [数据流与处理流程](#数据流与处理流程)
6. [开发规范](#开发规范)
7. [常见问题与解决方案](#常见问题与解决方案)
8. [扩展指南](#扩展指南)

---

## 项目概述

### 产品定位

**深表美文**是一个基于 AI 的文章美化和 HTML 格式化系统，将普通文本转换为视觉精美的 HTML 页面。

### 核心价值

- ✨ **一键美化**：普通文本 → 精美页面，零设计成本
- 🤖 **AI 驱动**：智能理解内容，自动匹配最佳排版风格
- 🔗 **永久链接**：每篇文章生成独立短 URL，随时分享
- 📱 **完美适配**：手机、平板、电脑全设备响应式

### 主要功能

1. **HTML 格式化服务**：将文本转换为精美 HTML 页面
2. **三款美化模式**：严格原文 / 解读优化 / 扩写丰富
3. **AI 自动标题**：智能分析内容生成标题
4. **多模型支持**：DeepSeek、Qwen 等模型灵活切换
5. **长文章处理**：流式输出技术支持万字长文

---

## 技术架构

### 整体架构图

```
用户浏览器
    ↓
Flask Web Server (src/web_server.py)
    ↓
LLM Client (src/llm_client.py) ←→ DeepSeek/Qwen API
    ↓
HTML Formatter (src/html_formatter.py)
    ↓
File Storage (static/userfiles/)
    ↓
Article ID Mapping (static/article_ids/)
```

### 技术栈

| 层级 | 技术选型 | 说明 |
|------|---------|------|
| **后端框架** | Flask | Python Web 框架 |
| **AI 模型** | DeepSeek、Qwen | 大语言模型 API |
| **统一接口** | LLMClient | 封装多模型调用 |
| **数据库** | MySQL（可选） | 博客生成功能使用 |
| **前端** | 纯 HTML + 内联 CSS | 离线优先，无外部依赖 |
| **部署** | Shell 脚本 + crontab | 自动化运维 |

### 项目结构

```
isheetmarketing/
│
├── README.md                 # 📖 产品总体介绍（面向用户）
├── AI_DEVELOPER_GUIDE.md     # 🤖 AI 开发者技术文档（本文件）
├── app.py                    # 🚀 Flask 应用入口
├── requirements.txt          # 📋 Python 依赖列表
│
├── src/                      # 【源代码】核心业务逻辑
│   ├── web_server.py         # Web 服务器主程序（路由、API）
│   ├── llm_client.py         # 统一的 LLM 客户端（多模型支持）
│   ├── html_formatter.py     # HTML 格式化服务
│   ├── segmented_formatter.py # 分段式 HTML 格式化器（长文章）
│   ├── blog_generator.py     # 博客生成器
│   ├── db_manager.py         # 数据库管理器
│   └── logger.py             # 日志系统
│
├── config/                   # 【配置】配置文件
│   └── config.py             # API 密钥、数据库配置、模型选择
│
├── static/                   # 【静态资源】
│   ├── index.html            # 首页
│   ├── formatter.html        # HTML 格式化服务页面
│   ├── css/                  # 样式文件
│   ├── js/                   # JavaScript 文件
│   ├── userfiles/            # 生成的文章 HTML 文件
│   └── article_ids/          # 文章 ID 映射文件（JSON）
│
├── docs/                     # 【文档】详细说明文档
│   ├── BEAUTY_MODE_GUIDE.md           # 美化模式指南
│   ├── CONTENT_STRATEGY_GUIDE.md      # 内容策略指南
│   ├── EXTRA_REQUIREMENTS_GUIDE.md    # 额外要求指南
│   ├── LONG_ARTICLE_HANDLING.md       # 长文章处理说明
│   ├── MULTI_MODEL_QUICKSTART.md      # 多模型快速开始
│   ├── MULTI_MODEL_SUPPORT.md         # 多模型详细文档
│   ├── MULTI_MODEL_COMPLETION_SUMMARY.md # 多模型完成总结
│   ├── DOCUMENTATION_INDEX.md         # 文档索引
│   ├── QUICK_REFERENCE.md             # 快速参考手册
│   └── QUICK_START_TUTORIAL.md        # 快速入门教程
│
├── debug/                    # 【测试调试】所有测试代码
│   ├── test_*.py             # 各种测试脚本
│   ├── switch_model.py       # 模型切换工具
│   └── *.html                # 临时 HTML 文件
│
└── logs/                     # 【日志】运行日志
    └── *.log                 # 日志文件
```

---

## 核心模块说明

### 1. Web Server (`src/web_server.py`)

**职责**：处理 HTTP 请求、路由分发、API 端点

**关键路由**：

| 路由 | 方法 | 功能 | 说明 |
|------|------|------|------|
| `/` | GET | 首页 | 返回 `static/index.html` |
| `/html-formatter` | GET | 格式化页面 | 返回 `static/formatter.html` |
| `/api/format-html` | POST | 格式化 API | 接收文本，返回美化后的 HTML 链接 |
| `/p/<article_id>` | GET | 文章访问 | 根据 ID 返回生成的 HTML 文件 |
| `/blog/generate` | POST | 博客生成 | AI 自动生成博客文章 |

**核心函数**：

```python
@app.route('/api/format-html', methods=['POST'])
def format_html_api():
    """
    HTML 格式化 API 端点
    
    请求体:
    {
        "content": "文章内容...",
        "title": "文章标题（可选）",
        "beauty_mode": "strict",  // strict | interpret | expand
        "extra_requirements": "自定义要求（可选）"
    }
    
    响应:
    {
        "status": "success",
        "access_url": "/p/abc12345",
        "article_id": "abc12345"
    }
    """
```

### 2. LLM Client (`src/llm_client.py`)

**职责**：统一的大语言模型客户端，支持多模型切换

**核心类**：`LLMClient`

**主要方法**：

```python
class LLMClient:
    def __init__(self, model_name=None):
        """
        初始化 LLM 客户端
        
        Args:
            model_name: 模型名称（deepseek | qwen），默认使用 config.CURRENT_MODEL
        """
    
    def generate_blog(self, topic):
        """
        生成博客文章
        
        Args:
            topic: 博客主题
            
        Returns:
            tuple: (title, content)
        """
    
    def generate_title(self, content):
        """
        根据内容生成标题
        
        Args:
            content: 文章内容
            
        Returns:
            str: 生成的标题
        """
    
    def format_article(self, content, title=None, 
                      beauty_mode="strict", 
                      extra_requirements=None):
        """
        格式化文章为 HTML
        
        Args:
            content: 文章内容
            title: 文章标题（可选）
            beauty_mode: 美化模式（strict | interpret | expand）
            extra_requirements: 额外要求（可选）
            
        Returns:
            str: 格式化后的 HTML
        """
```

**支持的模型**：

| 模型 | 配置前缀 | 特点 |
|------|---------|------|
| DeepSeek | `DEEPSEEK_*` | 响应快，适合快速任务 |
| Qwen | `QWEN_*` | 上下文大，适合长文处理 |

**切换模型**：

```python
# 方式 1：修改配置文件
# config/config.py
CURRENT_MODEL = "deepseek"  # 或 "qwen"

# 方式 2：代码中指定
client = LLMClient(model_name="qwen")
```

### 3. HTML Formatter (`src/html_formatter.py`)

**职责**：将文本内容格式化为精美的 HTML 页面

**核心类**：`HTMLFormatter`

**主要方法**：

```python
class HTMLFormatter:
    def __init__(self, base_url="", model_name=None):
        """
        初始化 HTML 格式化器
        
        Args:
            base_url: 基础 URL（用于生成访问链接）
            model_name: 使用的 LLM 模型名称
        """
    
    def format_article(self, content, title=None, 
                      beauty_mode="strict", 
                      extra_requirements=None):
        """
        格式化文章
        
        Args:
            content: 文章内容
            title: 文章标题（可选）
            beauty_mode: 美化模式
            extra_requirements: 额外要求
            
        Returns:
            str: 完整的 HTML 文档
        """
    
    def save_to_file(self, html_content, title):
        """
        保存 HTML 到文件并生成访问链接
        
        Args:
            html_content: HTML 内容
            title: 文章标题
            
        Returns:
            dict: {"article_id": "...", "access_url": "/p/..."}
        """
```

**美化特性**：

- ✅ 渐变色主题（紫色系 #667eea → #764ba2）
- ✅ 圆角卡片设计（16-24px 圆角）
- ✅ 柔和阴影效果
- ✅ Emoji 图标点缀
- ✅ 彩色圆形数字编号
- ✅ 高亮背景和文字效果
- ✅ 引用块样式
- ✅ 响应式布局

### 4. Segmented Formatter (`src/segmented_formatter.py`)

**职责**：处理超长文章的分段格式化

**核心类**：`SegmentedFormatter`

**工作原理**：

1. 将长文章按段落分割
2. 逐段调用 LLM 进行格式化
3. 合并所有片段为完整 HTML

**适用场景**：

- 文章长度 > 5000 字
- 避免单次 API 调用超时
- 提高长文章处理成功率

### 5. Blog Generator (`src/blog_generator.py`)

**职责**：AI 自动生成博客文章

**核心类**：`BlogGenerator`

**主要方法**：

```python
class BlogGenerator:
    def __init__(self, model_name=None):
        """
        初始化博客生成器
        
        Args:
            model_name: 使用的 LLM 模型名称
        """
    
    def generate_and_save_blog(self, topic=None):
        """
        生成并保存博客文章
        
        Args:
            topic: 博客主题（可选，不填则随机生成）
            
        Returns:
            dict: {"title": "...", "content": "...", "url": "..."}
        """
```

### 6. 配置文件 (`config/config.py`)

**关键配置项**：

```python
# ==================== DeepSeek API 配置 ====================
DEEPSEEK_API_KEY = "your-deepseek-api-key-here"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# ==================== Qwen API 配置 ====================
QWEN_API_KEY = "your-qwen-api-key-here"
QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
QWEN_MODEL = "qwen3-30b-a3b-instruct-2507"

# ==================== 当前使用的模型 ====================
# 👇 关键：切换这个变量即可更换模型（deepseek 或 qwen）
CURRENT_MODEL = "qwen"

# ==================== 数据库配置（可选）====================
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = "password"
DB_NAME = "isheetmarketing"

# ==================== 服务器配置 ====================
SERVER_PORT = 8009
STATIC_FOLDER = "static"
USERFILES_FOLDER = "static/userfiles"
ARTICLE_IDS_FOLDER = "static/article_ids"
```

---

## API 接口规范

### 1. HTML 格式化 API

**端点**：`POST /api/format-html`

**请求体**：

```json
{
  "content": "文章内容...",
  "title": "文章标题（可选，不填则 AI 自动生成）",
  "beauty_mode": "strict",  // 可选：strict | interpret | expand，默认 strict
  "extra_requirements": "使用蓝色系配色"  // 可选，自定义要求
}
```

**响应**：

```json
{
  "status": "success",
  "access_url": "/p/abc12345",
  "article_id": "abc12345"
}
```

**错误响应**：

```json
{
  "status": "error",
  "message": "错误描述信息"
}
```

**示例代码**：

```python
import requests

response = requests.post(
    "http://localhost:8009/api/format-html",
    json={
        "content": "这是文章内容...",
        "title": "文章标题",
        "beauty_mode": "interpret"
    }
)

result = response.json()
print(f"访问链接：http://localhost:8009{result['access_url']}")
```

### 2. 文章访问 API

**端点**：`GET /p/<article_id>`

**响应**：返回完整的 HTML 文档

**示例**：

```bash
curl http://localhost:8009/p/abc12345
```

### 3. 博客生成 API

**端点**：`POST /blog/generate`

**请求体**：

```json
{
  "topic": "AI 表格"  // 可选，不填则随机生成主题
}
```

**响应**：

```json
{
  "status": "success",
  "title": "生成的标题",
  "content": "生成的内容...",
  "url": "/p/xyz67890"
}
```

---

## 数据流与处理流程

### HTML 格式化流程

```
1. 用户提交文本
   ↓
2. Web Server 接收请求 (/api/format-html)
   ↓
3. 解析参数（content, title, beauty_mode, extra_requirements）
   ↓
4. 如果没有标题，调用 LLMClient.generate_title() 生成标题
   ↓
5. 调用 LLMClient.format_article() 格式化文章
   ↓
6. LLMClient 根据 beauty_mode 生成不同的提示词
   ↓
7. 调用对应的 LLM API（DeepSeek 或 Qwen）
   ↓
8. 接收 LLM 返回的 HTML 内容
   ↓
9. HTMLFormatter 添加底部标识和必要元素
   ↓
10. 保存到文件（static/userfiles/）
   ↓
11. 生成文章 ID 映射（static/article_ids/）
   ↓
12. 返回访问链接给前端
```

### 美化模式处理差异

| 模式 | 提示词特点 | 适用场景 |
|------|-----------|---------|
| **strict** | 一字不差，仅修正错误 | 正式文档、法律文件 |
| **interpret** | 可调整逻辑、添加过渡句 | 技术文档、内容优化 |
| **expand** | 可补充背景、案例、解释 | 营销文案、科普文章 |

### 文章 ID 生成机制

1. **生成唯一 ID**：8 位随机字母组合（如 `abc12345`）
2. **检查冲突**：确保 ID 未被使用
3. **保存映射**：在 `static/article_ids/{id}.json` 中记录
   ```json
   {
     "article_id": "abc12345",
     "filename": "文章标题_1775092466.html",
     "created_at": "2026-04-04 10:30:00",
     "title": "文章标题"
   }
   ```
4. **访问时查找**：根据 ID 找到对应文件名并返回

---

## 开发规范

### 1. 代码组织规范

**必须遵守**：

- ✅ 源代码放在 `src/` 目录
- ✅ 测试代码放在 `debug/` 目录
- ✅ 文档放在 `docs/` 目录
- ✅ 配置文件放在 `config/` 目录
- ❌ **禁止**在根目录创建新文件（除非是必要的入口文件）

**文件命名**：

- Python 文件：小写字母 + 下划线（如 `html_formatter.py`）
- 文档文件：大写字母 + 下划线 + `.md`（如 `BEAUTY_MODE_GUIDE.md`）
- 测试文件：`test_` 前缀（如 `test_multi_model.py`）

### 2. 代码风格规范

**Python 代码**：

```python
# ✅ 推荐：清晰的函数签名和类型提示
def format_article(
    self, 
    content: str, 
    title: str = None,
    beauty_mode: str = "strict",
    extra_requirements: str = None
) -> str:
    """
    格式化文章为 HTML
    
    Args:
        content: 文章内容
        title: 文章标题（可选）
        beauty_mode: 美化模式（strict | interpret | expand）
        extra_requirements: 额外要求（可选）
        
    Returns:
        str: 格式化后的 HTML
    """
    # 实现代码...
```

**注释规范**：

- 所有公共函数必须有 docstring
- 复杂逻辑需要行内注释说明
- 使用中文注释（团队内部项目）

### 3. API 设计规范

**RESTful 原则**：

- 使用名词作为资源名（如 `/api/format-html`）
- 使用 HTTP 方法表示操作（GET/POST/PUT/DELETE）
- 返回 JSON 格式响应
- 统一的错误响应格式

**响应格式**：

```python
# 成功响应
{
    "status": "success",
    "data": {...}  # 具体数据
}

# 错误响应
{
    "status": "error",
    "message": "错误描述"
}
```

### 4. 文档编写规范

**新增功能时必须**：

1. 在 `docs/` 目录创建对应的指南文档
2. 更新 `README.md` 中的相关章节
3. 在 `AI_DEVELOPER_GUIDE.md` 中添加技术说明
4. 更新 `docs/DOCUMENTATION_INDEX.md` 索引

**文档结构**：

```markdown
# 功能名称

## 功能概述
简要说明功能用途

## 使用方法
详细的使用步骤和示例

## 技术实现
核心代码逻辑说明

## 注意事项
使用时需要注意的点

## 修改记录
- 修改时间：YYYY-MM-DD
- 修改内容：...
- 影响范围：...
```

### 5. 测试规范

**测试文件位置**：`debug/` 目录

**测试文件命名**：`test_<功能名>.py`

**测试内容**：

- 单元测试：测试单个函数/方法
- 集成测试：测试多个模块协作
- 端到端测试：测试完整业务流程

**运行测试**：

```bash
python debug/test_xxx.py
```

---

## 常见问题与解决方案

### Q1: 如何添加新的 LLM 模型？

**A**: 按照以下步骤操作：

1. **在 `config/config.py` 中添加配置**：

```python
# 新模型配置
NEWMODEL_API_KEY = "your-api-key"
NEWMODEL_API_URL = "https://..."
NEWMODEL_MODEL = "model-name"
```

2. **在 `src/llm_client.py` 中添加模型支持**：

```python
elif self.model_name.lower() == 'newmodel':
    self.api_key = NEWMODEL_API_KEY
    self.api_url = NEWMODEL_API_URL
    self.model = NEWMODEL_MODEL
```

3. **更新 `CURRENT_MODEL` 配置**：

```python
CURRENT_MODEL = "newmodel"
```

4. **创建测试脚本**：`debug/test_newmodel.py`

5. **编写文档**：`docs/NEWMODEL_SUPPORT.md`

### Q2: 如何处理 API 超时问题？

**A**: 

1. **检查网络**：确保能够访问 LLM API 端点
2. **增加超时时间**：在 `llm_client.py` 中调整 `timeout` 参数
3. **使用流式输出**：对于长文章，自动切换到流式模式
4. **查看日志**：`tail -f logs/server.log` 了解详细错误

### Q3: 文章 ID 冲突怎么办？

**A**: 

系统已内置冲突检测机制：

```python
# 生成唯一 ID
while True:
    article_id = ''.join(random.choices(string.ascii_lowercase, k=8))
    if not os.path.exists(f"{ARTICLE_IDS_FOLDER}/{article_id}.json"):
        break
```

理论上不会出现冲突，但如果发生：

1. 检查 `static/article_ids/` 目录
2. 手动删除冲突的 ID 文件
3. 重新生成文章

### Q4: 如何自定义 HTML 样式？

**A**: 

1. **修改 `html_formatter.py` 中的模板**：

```python
# 找到 HTML 模板部分
html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        /* 在这里修改 CSS */
    </style>
</head>
<body>
    ...
</body>
</html>
"""
```

2. **保持内联样式**：确保所有样式都是内联的，以保持离线可用性

3. **测试兼容性**：在不同浏览器和设备上测试

### Q5: 长文章处理失败怎么办？

**A**: 

1. **检查文章长度**：如果 > 10000 字，考虑分段处理
2. **使用 SegmentedFormatter**：

```python
from src.segmented_formatter import SegmentedFormatter

formatter = SegmentedFormatter(model_name="qwen")
html = formatter.format_long_article(content, title)
```

3. **增加超时时间**：流式模式默认 300 秒，可适当增加
4. **检查 API 额度**：确保账户有足够的 token 余额

---

## 扩展指南

### 1. 添加新的美化模式

**步骤**：

1. **在 `config/config.py` 中定义新模式**（可选）

2. **在 `src/llm_client.py` 中添加模式处理逻辑**：

```python
def _create_format_prompt(self, content, title, beauty_mode, extra_requirements):
    if beauty_mode == "new_mode":
        prompt = f"""
        你是专业的内容美化专家。
        
        【新模式规则】
        - 规则 1...
        - 规则 2...
        
        【原文内容】
        {content}
        """
    # ... 其他模式
```

3. **在前端添加 UI 选项**：`static/formatter.html`

```html
<label class="mode-option">
    <input type="radio" name="beautyMode" value="new_mode">
    <span class="mode-icon">🆕</span>
    <span class="mode-name">新模式</span>
    <span class="mode-desc">模式描述</span>
</label>
```

4. **更新文档**：`docs/NEW_MODE_GUIDE.md`

### 2. 添加新的 API 端点

**步骤**：

1. **在 `src/web_server.py` 中添加路由**：

```python
@app.route('/api/new-endpoint', methods=['POST'])
def new_endpoint():
    """
    新功能 API
    
    请求体:
    {
        "param1": "value1",
        "param2": "value2"
    }
    """
    try:
        data = request.get_json()
        # 处理逻辑...
        
        return jsonify({
            "status": "success",
            "data": result
        })
    except Exception as e:
        logger.error(f"Error in new_endpoint: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
```

2. **实现业务逻辑**：在相应的模块中实现功能

3. **编写测试**：`debug/test_new_endpoint.py`

4. **更新文档**：在 `AI_DEVELOPER_GUIDE.md` 的 API 章节添加说明

### 3. 集成新的前端框架

**当前架构**：纯 HTML + 内联 CSS（离线优先）

**如果需要现代化前端**：

1. **保持向后兼容**：保留现有的 HTML 页面
2. **创建新版本**：`static/v2/` 目录
3. **使用现代框架**：React/Vue + Vite
4. **API 保持不变**：继续使用现有的 RESTful API
5. **渐进式迁移**：逐步将功能迁移到新前端

### 4. 添加缓存机制

**目的**：提高性能，减少 API 调用

**方案**：

1. **使用 Redis**：

```python
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_result(key):
    result = redis_client.get(key)
    if result:
        return json.loads(result)
    return None

def cache_result(key, value, ttl=3600):
    redis_client.setex(key, ttl, json.dumps(value))
```

2. **缓存键设计**：`format:{content_hash}:{beauty_mode}`

3. **缓存策略**：相同内容 + 相同模式 → 直接返回缓存结果

### 5. 添加用户系统

**当前状态**：无用户系统，所有文章公开访问

**如果需要用户系统**：

1. **数据库设计**：

```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE articles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    article_id VARCHAR(8) UNIQUE NOT NULL,
    title VARCHAR(255),
    is_public BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

2. **认证中间件**：

```python
from functools import wraps
from flask import session, redirect

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function
```

3. **权限控制**：私有文章只有作者可访问

---

## 附录

### A. 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `PORT` | 服务器端口 | 8009 |
| `FLASK_ENV` | Flask 环境 | development |
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | - |
| `QWEN_API_KEY` | Qwen API 密钥 | - |

### B. 常用命令

```bash
# 启动服务
python src/web_server.py

# 查看日志
tail -f logs/server.log

# 切换模型
python debug/switch_model.py deepseek
python debug/switch_model.py qwen

# 运行测试
python debug/test_multi_model.py

# 安装依赖
pip install -r requirements.txt
```

### C. 性能优化建议

1. **启用 Gzip 压缩**：

```python
from flask_compress import Compress
Compress(app)
```

2. **使用 Gunicorn**：

```bash
gunicorn -w 4 -b 0.0.0.0:8009 src.web_server:app
```

3. **添加 CDN**：如果有外部资源（字体、图片）

4. **数据库连接池**：如果使用 MySQL

5. **异步任务**：对于耗时操作，使用 Celery

### D. 安全注意事项

1. **API 密钥保护**：不要将 `config.py` 提交到版本控制
2. **输入验证**：对所有用户输入进行验证和清理
3. **速率限制**：防止 API 滥用
4. **HTTPS**：生产环境必须使用 HTTPS
5. **CORS**：根据需要配置跨域策略

---

## 更新记录

| 日期 | 版本 | 更新内容 |
|------|------|---------|
| 2026-04-04 | 1.0 | 初始版本，完整技术文档 |

---

**维护者**：深表 AI 工作室  
**最后更新**：2026 年 4 月 4 日

**🤖 提示**：本文档专为 AI 编程智能体设计，如需人类可读的产品介绍，请参阅 [README.md](../README.md)
