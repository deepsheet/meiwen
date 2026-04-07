# API 参数说明 - 扩写模式与额外需求

## 📅 更新日期
2026-04-06

## 🎯 核心参数说明

文本转 HTML API 提供两个关键参数来控制 AI 如何处理和美化内容：

1. **`content_strategy`** - 扩写模式（控制AI如何处理原文）
2. **`extra_requirements`** - 额外需求（用自然语言描述格式化要求）

---

## 🎨 扩写模式（content_strategy）

### 三种模式对比

| 模式 | 值 | 特点 | 适用场景 |
|------|-----|------|---------|
| **严格模式** | `strict` | 一字不改，保持100%原文 | 正式文档、法律文件、新闻报道 |
| **解读优化** | `interpret` | 可调整逻辑、优化表达 | 技术文档、教程、需要提升可读性 |
| **扩写丰富** | `expand` | 可补充背景、案例、解释 | 营销文案、科普文章、知识普及 |

### 使用示例

#### 1. 严格模式（strict）

```python
import requests

response = requests.post(
    "http://localhost:5000/api/text-to-html",
    json={
        "content": "人工智能是计算机科学的一个分支。它研究如何使计算机能够模拟人类的智能行为。",
        "content_strategy": "strict"  # 严格保持原文
    }
)
```

**效果：**
- ✅ 完全保留原文内容
- ✅ 仅修正错别字和语法错误
- ✅ 不添加任何新内容
- ✅ 适合需要准确性的场景

#### 2. 解读优化（interpret）

```python
response = requests.post(
    "http://localhost:5000/api/text-to-html",
    json={
        "content": "AI技术...机器学习...深度学习...",
        "content_strategy": "interpret"  # 解读优化
    }
)
```

**效果：**
- ✅ 可以调整段落顺序
- ✅ 可以优化表达逻辑
- ✅ 可以添加过渡句
- ✅ 保持核心内容不变

#### 3. 扩写丰富（expand）

```python
response = requests.post(
    "http://localhost:5000/api/text-to-html",
    json={
        "content": "Python是一种编程语言...",
        "content_strategy": "expand"  # 扩写丰富
    }
)
```

**效果：**
- ✅ 可以补充背景信息
- ✅ 可以添加案例和数据
- ✅ 可以解释专业术语
- ✅ 内容丰富度大幅提升

---

## 💡 额外需求（extra_requirements）

### 什么是额外需求？

`extra_requirements` 允许你用**自然语言**描述想要的格式化效果，AI 会理解并应用这些要求。

### 常用格式化要求

#### 1. 颜色主题

```python
{
    "extra_requirements": "使用蓝色主题"
}
```

支持的颜色：
- 红色、蓝色、绿色、紫色
- 橙色、粉色、青色、黄色
- 渐变色组合

#### 2. 布局方式

```python
{
    "extra_requirements": "使用卡片布局展示内容"
}
```

支持的布局：
- 卡片布局
- 列表展示
- 表格呈现
- 引用块
- 网格布局

#### 3. 视觉元素

```python
{
    "extra_requirements": "添加 emoji 图标，使用渐变色背景"
}
```

支持的元素：
- Emoji 图标（🎯✨💡等）
- 装饰性图标
- 分隔线
- 背景渐变
- 阴影效果

#### 4. 强调方式

```python
{
    "extra_requirements": "重点内容用高亮背景，关键数据加粗显示"
}
```

支持的强调：
- 文字加粗
- 背景高亮
- 边框强调
- 颜色突出
- 字体大小

### 组合使用示例

#### 示例 1: 产品展示

```python
response = requests.post(
    "http://localhost:5000/api/text-to-html",
    json={
        "content": "产品特点：高性能、易使用、安全可靠",
        "extra_requirements": "使用绿色主题，用卡片展示每个特点，添加对应的 emoji 图标"
    }
)
```

**预期效果：**
- 🎨 绿色主题配色
- 📦 三个卡片分别展示三个特点
- ✨ 每个卡片配有相关 emoji

#### 示例 2: 数据报告

```python
response = requests.post(
    "http://localhost:5000/api/text-to-html",
    json={
        "content": "销售数据：\n华东地区\t50万\t增长40%\n华南地区\t30万\t增长32%",
        "extra_requirements": "使用表格展示数据，紫色渐变主题，突出显示最高值"
    }
)
```

**预期效果：**
- 📊 标准表格展示
- 💜 紫色渐变主题
- 🔥 最高值特殊标记

#### 示例 3: 使用指南

```python
response = requests.post(
    "http://localhost:5000/api/text-to-html",
    json={
        "content": "步骤一：注册账号\n步骤二：完善资料\n步骤三：开始使用",
        "extra_requirements": "使用编号列表，每个步骤用卡片展示，添加箭头图标连接"
    }
)
```

**预期效果：**
- 🔢 编号列表
- 📦 步骤卡片
- ➡️ 箭头连接符

---

## 🎯 最佳实践

### 1. 根据内容类型选择扩写模式

```python
# 正式文档 → strict
{"content_strategy": "strict"}

# 技术教程 → interpret  
{"content_strategy": "interpret"}

# 营销文案 → expand
{"content_strategy": "expand"}
```

### 2. 额外需求要具体明确

❌ **不好的写法：**
```python
{"extra_requirements": "好看一点"}  # 太模糊
```

✅ **好的写法：**
```python
{"extra_requirements": "使用蓝色主题，用卡片布局，添加 emoji 图标"}  # 具体明确
```

### 3. 组合使用效果更佳

```python
{
    "content": "AI技术正在改变世界...",
    "content_strategy": "expand",  # 扩写丰富内容
    "extra_requirements": "使用科技蓝主题，添加相关案例，用卡片展示应用场景"  # 具体格式化要求
}
```

---

## 📊 实际应用场景

### 场景 1: 博客文章

```python
{
    "content": "Python编程技巧...",
    "title": "Python编程最佳实践",
    "content_strategy": "interpret",  # 解读优化，提升可读性
    "extra_requirements": "使用代码块样式，重点内容高亮，添加提示框"
}
```

### 场景 2: 产品文档

```python
{
    "content": "产品功能介绍...",
    "title": "智能办公助手",
    "content_strategy": "strict",  # 严格保持产品描述准确性
    "extra_requirements": "使用蓝色商务风格，用表格展示技术参数，添加功能图标"
}
```

### 场景 3: 营销文案

```python
{
    "content": "我们的服务优势...",
    "title": "为什么选择我们",
    "content_strategy": "expand",  # 扩写丰富，增加说服力
    "extra_requirements": "使用橙色活力主题，用卡片展示优势，添加客户评价区块"
}
```

### 场景 4: 数据报告

```python
{
    "content": "季度销售数据...",
    "title": "Q1 销售报告",
    "content_strategy": "strict",  # 严格保持数据准确性
    "extra_requirements": "使用表格展示数据，紫色渐变主题，添加趋势图表说明"
}
```

---

## 🔍 常见问题

### Q1: 三种扩写模式有什么区别？

**A:** 
- `strict`: 一字不改，最安全
- `interpret`: 优化表达，提升可读性
- `expand`: 丰富内容，增加信息量

### Q2: extra_requirements 支持哪些描述方式？

**A:** 可以用自然语言描述任何格式化需求，AI 会尽量理解并实现。建议描述具体的：
- 颜色主题
- 布局方式
- 视觉元素
- 强调方法

### Q3: 可以同时使用扩写模式和额外需求吗？

**A:** 当然可以！这两个参数是独立的，可以自由组合：

```python
{
    "content_strategy": "expand",  # 扩写内容
    "extra_requirements": "使用蓝色主题"  # 蓝色样式
}
```

### Q4: 如果不指定这些参数会怎样？

**A:** 
- `content_strategy` 默认为 `strict`（严格模式）
- `extra_requirements` 默认为空（AI 自动决定样式）

---

## 📚 相关文档

- 📖 [完整 API 文档](TEXT_TO_HTML_API.md) - 详细的技术规范
- 🚀 [快速开始指南](TEXT_TO_HTML_QUICKSTART.md) - 5分钟上手
- 💡 [使用示例](../examples/text_to_html_examples.py) - 10个实用示例

---

**掌握这两个参数，让你的文本转 HTML 更加灵活强大！** ✨
