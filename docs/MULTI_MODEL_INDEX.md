# 多模型支持 - 文档索引

## 📚 文档导航

本文档索引帮助你快速找到多模型支持相关的文档和工具。

---

## 🚀 快速开始

### 我想...

#### 立即使用多模型功能
👉 **[快速开始指南](MULTI_MODEL_QUICKSTART.md)** - 30 秒上手

#### 查看当前使用的模型
```bash
python debug/switch_model.py
```

#### 切换模型
```bash
# 切换到 DeepSeek
python debug/switch_model.py deepseek

# 切换到 Qwen
python debug/switch_model.py qwen
```

#### 测试模型是否正常
```bash
python debug/test_multi_model.py
```

---

## 📖 完整文档

### 入门级

1. **[快速开始指南](MULTI_MODEL_QUICKSTART.md)** ⭐ 推荐首先阅读
   - 适合人群：新手用户
   - 阅读时间：5 分钟
   - 内容：快速上手、常用命令、简单示例

2. **[README.md](../README.md)** - 项目总览
   - 适合人群：所有人
   - 阅读时间：10 分钟
   - 内容：项目简介、安装配置、基本使用

### 进阶级

3. **[多模型支持详细文档](MULTI_MODEL_SUPPORT.md)**
   - 适合人群：开发者、高级用户
   - 阅读时间：20 分钟
   - 内容：完整功能说明、使用示例、故障排查、扩展指南

4. **[完成总结](MULTI_MODEL_COMPLETION_SUMMARY.md)**
   - 适合人群：项目管理者、技术负责人
   - 阅读时间：15 分钟
   - 内容：工作总结、统计数据、使用场景

### 专家级

5. **[重构报告](MULTI_MODEL_REFACTORING_REPORT.md)**
   - 适合人群：架构师、核心开发者
   - 阅读时间：30 分钟
   - 内容：技术实现、架构设计、性能对比、扩展方案

---

## 🛠️ 工具脚本

### 命令行工具

| 脚本 | 用途 | 使用示例 |
|------|------|---------|
| `debug/switch_model.py` | 切换模型 | `python debug/switch_model.py qwen` |
| `debug/test_multi_model.py` | 测试模型 | `python debug/test_multi_model.py` |

### 详细说明

#### 1. switch_model.py - 模型切换工具

**功能**:
- 查看当前模型
- 一键切换模型
- 验证配置是否生效

**使用示例**:
```bash
# 查看当前模型
python debug/switch_model.py

# 切换到 DeepSeek
python debug/switch_model.py deepseek

# 切换到 Qwen
python debug/switch_model.py qwen
```

#### 2. test_multi_model.py - 多模型测试

**功能**:
- 测试 DeepSeek 和 Qwen 初始化
- 测试标题生成功能
- 输出详细测试报告

**使用示例**:
```bash
python debug/test_multi_model.py
```

**预期输出**:
```
✅ deepseek 客户端初始化成功
✅ 生成的标题：xxx

✅ qwen 客户端初始化成功
✅ 生成的标题：xxx

🎉 所有模型测试通过！
```

---

## 💻 源代码文件

### 核心文件

| 文件 | 作用 | 行数 |
|------|------|------|
| `src/llm_client.py` | 统一的 LLM 客户端（核心） | 525 |
| `config/config.py` | 模型配置文件 | ~70 |
| `src/blog_generator.py` | 博客生成器（已适配） | 117 |
| `src/html_formatter.py` | HTML 格式化器（已适配） | ~1465 |
| `src/segmented_formatter.py` | 分段格式化器（已适配） | ~539 |
| `src/web_server.py` | Web 服务器（已适配） | ~1525 |

### 代码示例

#### 使用 LLMClient

```python
from src.llm_client import LLMClient

# 使用默认模型
client = LLMClient()

# 使用指定模型
client = LLMClient(model_name="deepseek")

# 生成博客
title, content = client.generate_blog(topic="AI 表格")

# 生成标题
title = client.generate_title(content)

# 格式化文章
html = client.format_article(content, title)
```

---

## 🔍 常见问题

### Q1: 如何切换模型？

**A**: 两种方法：

**方法 A** - 修改配置文件：
```python
# config/config.py
CURRENT_MODEL = "deepseek"
```

**方法 B** - 使用命令行工具：
```bash
python debug/switch_model.py deepseek
```

### Q2: 支持哪些模型？

**A**: 目前支持：
- **DeepSeek** (深度求索) - 快速响应
- **Qwen** (通义千问) - 擅长长文本

### Q3: 如何添加新模型？

**A**: 参考 [多模型支持详细文档](MULTI_MODEL_SUPPORT.md#扩展新模型)

### Q4: 切换模型后需要重启吗？

**A**: 是的，需要重启 Web 服务或 Python 进程。

### Q5: 哪个模型更好？

**A**: 各有优势：
- **DeepSeek**: 响应快，适合博客生成等快速任务
- **Qwen**: 上下文大，适合长文格式化等复杂任务

建议根据具体场景选择。

---

## 📊 性能对比

| 指标 | DeepSeek | Qwen |
|------|----------|------|
| 响应速度 | ⚡⚡⚡ 快 | ⚡⚡ 中等 |
| 中文质量 | ⭐⭐⭐⭐⭐ 优秀 | ⭐⭐⭐⭐⭐ 优秀 |
| 上下文长度 | 标准 | 大 |
| 适用场景 | 博客生成、快速响应 | 长文处理、复杂任务 |
| 成本 | 按 token 计费 | 按 token 计费 |

---

## 🎯 推荐阅读路径

### 对于普通用户

1. [快速开始指南](MULTI_MODEL_QUICKSTART.md) - 5 分钟
2. [README.md](../README.md) - 了解项目
3. 开始使用！✨

### 对于开发者

1. [快速开始指南](MULTI_MODEL_QUICKSTART.md) - 5 分钟
2. [多模型支持详细文档](MULTI_MODEL_SUPPORT.md) - 20 分钟
3. [源代码 - llm_client.py](../src/llm_client.py) - 深入理解
4. [重构报告](MULTI_MODEL_REFACTORING_REPORT.md) - 技术细节

### 对于架构师/技术负责人

1. [完成总结](MULTI_MODEL_COMPLETION_SUMMARY.md) - 15 分钟
2. [重构报告](MULTI_MODEL_REFACTORING_REPORT.md) - 30 分钟
3. [多模型支持详细文档](MULTI_MODEL_SUPPORT.md) - 扩展方案

---

## 🔗 相关链接

### 内部链接

- [项目主目录](../README.md)
- [文档总索引](DOCUMENTATION_INDEX.md)
- [快速开始教程](QUICK_START_TUTORIAL.md)

### 外部链接

- [DeepSeek 官方文档](https://platform.deepseek.com/)
- [Qwen 官方文档](https://help.aliyun.com/zh/dashscope/)

---

## 📝 更新日志

### 2026-04-03

- ✅ 创建多模型支持文档体系
- ✅ 新增 6 个文档文件
- ✅ 新增 2 个工具脚本
- ✅ 更新 README.md
- ✅ 完成所有代码重构

---

## 💡 提示

- 📌 **首次使用？** 从 [快速开始指南](MULTI_MODEL_QUICKSTART.md) 开始
- 🔧 **遇到问题？** 查看 [故障排查章节](MULTI_MODEL_SUPPORT.md#故障排查)
- 🎓 **想深入了解？** 阅读 [重构报告](MULTI_MODEL_REFACTORING_REPORT.md)
- 🚀 **想扩展功能？** 参考 [扩展新模型章节](MULTI_MODEL_SUPPORT.md#扩展新模型)

---

**最后更新**: 2026-04-03  
**维护者**: 深表 AI 工作室
