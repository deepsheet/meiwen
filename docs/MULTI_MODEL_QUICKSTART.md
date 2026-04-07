# 多模型支持 - 快速开始指南

## 🚀 30 秒快速上手

### 1️⃣ 查看当前模型

```bash
python debug/switch_model.py
```

输出示例：
```
当前使用模型：qwen
```

### 2️⃣ 切换模型（二选一）

**方法 A: 使用命令行工具**
```bash
# 切换到 DeepSeek
python debug/switch_model.py deepseek

# 切换到 Qwen
python debug/switch_model.py qwen
```

**方法 B: 手动修改配置文件**
```python
# config/config.py
CURRENT_MODEL = "deepseek"  # 或 "qwen"
```

### 3️⃣ 重启服务

```bash
python app.py
```

## 💡 核心概念

### 统一接口

所有 AI 功能通过 `LLMClient` 统一调用：

```python
from src.llm_client import LLMClient

# 自动使用 CURRENT_MODEL 配置的模型
client = LLMClient()

# 或手动指定
client = LLMClient(model_name="deepseek")
```

### 可用模型

- **DeepSeek** (`deepseek`) - 深度求索，快速响应
- **Qwen** (`qwen`) - 通义千问，擅长长文本

## 📋 完整使用示例

### 生成博客文章

```python
from src.blog_generator import BlogGenerator

# 使用配置的默认模型
generator = BlogGenerator()
success = generator.generate_and_save_blog()

# 或指定模型
generator = BlogGenerator(model_name="qwen")
success = generator.generate_and_save_blog()
```

### HTML 格式化

```python
from src.html_formatter import HTMLFormatter

# 使用默认模型
formatter = HTMLFormatter()
html = formatter.format_article(content, title)

# 使用指定模型
formatter = HTMLFormatter(model_name="deepseek")
html = formatter.format_article(content, title)
```

### Web 服务

Web 服务会自动读取配置：

```python
# 无需手动指定，自动使用 CURRENT_MODEL
# web_server.py 已处理
```

## 🧪 测试验证

运行测试脚本验证一切正常：

```bash
python debug/test_multi_model.py
```

预期输出：
```
✅ deepseek 客户端初始化成功
✅ 生成的标题：xxx

✅ qwen 客户端初始化成功
✅ 生成的标题：xxx

🎉 所有模型测试通过！
```

## ⚙️ 配置文件说明

在 `config/config.py` 中：

```python
# DeepSeek 配置
DEEPSEEK_API_KEY = "sk-xxx"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# Qwen 配置
QWEN_API_KEY = "sk-xxx"
QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
QWEN_MODEL = "qwen3-30b-a3b-instruct-2507"

# 👇 关键：切换这个变量即可更换模型
CURRENT_MODEL = "qwen"  # 可选值：deepseek, qwen
```

## 🔍 故障排查

### 问题：切换模型后不生效

**解决方案**：
1. 检查 `CURRENT_MODEL` 是否修改正确
2. 重启 Python 进程或 Web 服务
3. 清除缓存：`find . -name "*.pyc" -delete`

### 问题：API 调用失败

**解决方案**：
1. 检查 API Key 是否正确
2. 检查网络连接
3. 查看日志：`cat logs/*.log`

## 📖 进阶阅读

- [完整使用文档](MULTI_MODEL_SUPPORT.md) - 详细功能说明
- [重构报告](MULTI_MODEL_REFACTORING_REPORT.md) - 技术实现细节
- [扩展新模型](MULTI_MODEL_SUPPORT.md#扩展新模型) - 添加更多模型

## 🎯 最佳实践

1. **开发环境**: 使用 Qwen（免费额度充足）
2. **生产环境**: 根据成本和性能选择
3. **长文本处理**: 优先 Qwen
4. **快速响应**: 优先 DeepSeek

---

**提示**: 修改配置后记得重启服务！🔄
