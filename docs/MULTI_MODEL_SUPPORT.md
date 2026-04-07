# 多模型支持功能说明

## 📋 概述

本项目现已支持多个大语言模型（LLM）的切换和使用，目前支持的模型包括：
- **DeepSeek** (深度求索)
- **Qwen** (通义千问)

## 🔧 配置方法

### 1. 修改配置文件

在 `config/config.py` 中配置和切换模型：

```python
# DeepSeek API 配置
DEEPSEEK_API_KEY = "your-deepseek-api-key"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# QWEN API 配置
QWEN_API_KEY = "your-qwen-api-key"
QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
QWEN_MODEL = "qwen3-30b-a3b-instruct-2507"

# 当前使用的模型选择（deepseek、qwen）
CURRENT_MODEL = "qwen"  # 修改此变量切换默认模型
```

### 2. 切换模型

只需修改 `CURRENT_MODEL` 变量的值：
- 使用 DeepSeek: `CURRENT_MODEL = "deepseek"`
- 使用 Qwen: `CURRENT_MODEL = "qwen"`

## 🏗️ 架构设计

### 统一接口层

所有 AI 模型的调用都通过统一的 `LLMClient` 类进行：

```python
from src.llm_client import LLMClient

# 使用默认模型（CURRENT_MODEL）
client = LLMClient()

# 或指定模型
client = LLMClient(model_name="deepseek")
client = LLMClient(model_name="qwen")
```

### 核心功能

`LLMClient` 提供以下统一方法：

1. **生成博客文章**
   ```python
   title, content = client.generate_blog(topic="AI 表格")
   ```

2. **生成标题**
   ```python
   title = client.generate_title(content)
   ```

3. **格式化文章为 HTML**
   ```python
   html = client.format_article(content, title)
   ```

## 📁 修改的文件

### 新增文件
- `src/llm_client.py` - 统一的 LLM 客户端（核心）

### 修改文件
- `config/config.py` - 添加模型配置和 CURRENT_MODEL 选项
- `src/blog_generator.py` - 使用 LLMClient 替代 DeepSeekClient
- `src/html_formatter.py` - 使用 LLMClient 进行格式化
- `src/segmented_formatter.py` - 使用 LLMClient 进行分段格式化
- `src/web_server.py` - 使用 LLMClient 生成标题和格式化

### 保留文件
- `src/deepseek_client.py` - 保留以兼容旧代码（建议迁移到 llm_client.py）

## 🧪 测试验证

运行测试脚本验证多模型支持：

```bash
cd /Users/chenkunji/Documents/cursor/isheetmarketing
python debug/test_multi_model.py
```

测试内容包括：
- ✅ 模型初始化
- ✅ 标题生成功能
- ✅ API 连接测试

## 💡 使用示例

### 示例 1：在代码中使用指定模型

```python
from src.blog_generator import BlogGenerator

# 使用 Qwen 模型生成博客
generator = BlogGenerator(model_name="qwen")
success = generator.generate_and_save_blog()

# 使用 DeepSeek 模型生成博客
generator = BlogGenerator(model_name="deepseek")
success = generator.generate_and_save_blog()
```

### 示例 2：HTML 格式化时使用不同模型

```python
from src.html_formatter import HTMLFormatter

# 使用 Qwen 格式化
formatter = HTMLFormatter(model_name="qwen")
html = formatter.format_article(content, title)

# 使用 DeepSeek 格式化
formatter = HTMLFormatter(model_name="deepseek")
html = formatter.format_article(content, title)
```

### 示例 3：Web 服务自动使用配置的模型

Web 服务会自动读取 `config.py` 中的 `CURRENT_MODEL` 配置：

```python
# web_server.py 中自动使用配置的模型
formatter = HTMLFormatter(base_url=base_url, model_name=CURRENT_MODEL)
```

## 🎯 扩展新模型

如需添加新模型（如 ChatGLM、Baichuan 等），只需：

### 1. 在 config.py 中添加配置

```python
# ChatGLM API 配置
CHATGLM_API_KEY = "your-chatglm-api-key"
CHATGLM_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
CHATGLM_MODEL = "glm-4"
```

### 2. 在 llm_client.py 中添加模型支持

```python
def __init__(self, model_name=None):
    self.model_name = model_name if model_name else CURRENT_MODEL
    
    if self.model_name.lower() == 'deepseek':
        # DeepSeek 配置
        ...
    elif self.model_name.lower() == 'qwen':
        # Qwen 配置
        ...
    elif self.model_name.lower() == 'chatglm':
        # ChatGLM 配置
        self.api_key = CHATGLM_API_KEY
        self.api_url = CHATGLM_API_URL
        self.model = CHATGLM_MODEL
    else:
        raise ValueError(f"不支持的模型：{self.model_name}")
```

### 3. 更新 CURRENT_MODEL 选项

```python
CURRENT_MODEL = "chatglm"  # 或其他新模型
```

## ⚠️ 注意事项

1. **API Key 管理**: 确保各模型的 API Key 配置正确且有效
2. **网络访问**: 确保能够访问对应模型的 API 端点
3. **超时设置**: 已统一设置为流式输出 600 秒，非流式 180 秒
4. **错误处理**: 所有 API 调用都有完善的异常处理和日志记录
5. **向后兼容**: 保留了原有的 `deepseek_client.py`，但建议迁移到新接口

## 📊 性能对比

不同模型的特点：

| 模型 | 优势 | 适用场景 |
|------|------|----------|
| DeepSeek | 中文理解好，生成速度快 | 博客生成、内容创作 |
| Qwen | 上下文长度大，逻辑性强 | 长文格式化、复杂任务 |

## 🔍 故障排查

### 问题 1：模型切换后不生效

**解决方案**：
1. 检查 `config.py` 中 `CURRENT_MODEL` 是否正确设置
2. 重启 Web 服务或 Python 进程
3. 清除 Python 缓存：`find . -name "*.pyc" -delete`

### 问题 2：API 调用失败

**解决方案**：
1. 检查 API Key 是否有效
2. 检查网络连接
3. 查看日志文件：`logs/*.log`
4. 运行测试脚本：`python debug/test_multi_model.py`

### 问题 3：模型响应格式不一致

**解决方案**：
- `LLMClient` 已内置格式化和清理逻辑
- 如果仍有问题，检查 `_parse_response` 方法的实现

## 📝 更新日志

- **2026-04-03**: 完成多模型支持重构
  - 新增统一的 LLMClient 类
  - 支持 DeepSeek 和 Qwen 两个模型
  - 所有子模块完成迁移
  - 添加测试脚本和文档

## 🤝 贡献指南

如需添加更多模型支持，请遵循以下模式：
1. 在 `config.py` 中添加配置
2. 在 `llm_client.py` 中实现模型适配
3. 更新本文档
4. 运行测试确保兼容性
