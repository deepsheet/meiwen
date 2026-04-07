# API 响应模式 - 快速参考

## 🚀 快速开始

### HTML 模式（默认）

```python
import requests

response = requests.post(
    "http://localhost:8009/api/text-to-html",
    json={
        "content": "文章内容",
        "title": "文章标题"
        # 不传 response_type，默认为 "html"
    }
)

result = response.json()
html_code = result["html"]  # ✅ 获取 HTML 代码
```

**响应：**
```json
{
  "status": "success",
  "message": "HTML generated successfully",
  "html": "<!DOCTYPE html>..."
}
```

---

### URL 模式

```python
import requests

response = requests.post(
    "http://localhost:8009/api/text-to-html",
    json={
        "content": "文章内容",
        "title": "文章标题",
        "response_type": "url"  # ✅ 关键参数
    }
)

result = response.json()
share_url = result["full_url"]      # ✅ 获取分享链接
article_id = result["article_id"]   # ✅ 获取文章 ID
```

**响应：**
```json
{
  "status": "success",
  "message": "HTML generated and saved successfully",
  "url": "/p/abcdefgh",
  "full_url": "http://localhost:8009/p/abcdefgh",
  "article_id": "abcdefgh",
  "title": "文章标题"
}
```

---

## 📊 对比表

| 特性 | HTML 模式 | URL 模式 |
|------|----------|---------|
| **返回字段** | `html` | `url`, `full_url`, `article_id`, `title` |
| **后台保存** | ✅ 是 | ✅ 是 |
| **适用场景** | 获取代码、嵌入展示 | 分享链接、管理文章 |
| **隐私安全** | 🔒 高 | ⚠️ 中 |

---

## 💡 选择指南

**需要 HTML 代码？** → 使用 HTML 模式（默认）
- 在自己的网站中嵌入
- 需要自定义样式
- 注重隐私安全

**需要分享链接？** → 使用 URL 模式
- 分享给他人阅读
- 批量管理文章
- 需要统计访问量

---

## ⚙️ 其他参数

### 扩写模式（content_strategy）

```python
{
  "content_strategy": "strict"     # 严格模式（默认）
  "content_strategy": "interpret"  # 解读优化
  "content_strategy": "expand"     # 扩写丰富
}
```

### 额外需求（extra_requirements）

```python
{
  "extra_requirements": "使用蓝色主题，用卡片布局，添加 emoji"
}
```

---

## 🔍 完整示例

```python
import requests

# 示例 1: 简单调用
response = requests.post(
    "http://localhost:8009/api/text-to-html",
    json={"content": "测试内容"}
)
html = response.json()["html"]

# 示例 2: 指定所有参数
response = requests.post(
    "http://localhost:8009/api/text-to-html",
    json={
        "content": "文章内容",
        "title": "文章标题",
        "content_strategy": "expand",
        "extra_requirements": "使用绿色主题",
        "response_type": "url"
    }
)
result = response.json()
print(f"访问链接: {result['full_url']}")

# 示例 3: 错误处理
try:
    response = requests.post(
        "http://localhost:8009/api/text-to-html",
        json={"content": "测试"},
        timeout=60
    )
    
    if response.status_code == 200:
        result = response.json()
        print("成功!")
    else:
        print(f"失败: {response.json()}")
        
except Exception as e:
    print(f"异常: {e}")
```

---

## 📚 更多文档

- 📖 [完整 API 文档](TEXT_TO_HTML_API.md)
- 🎯 [最终设计方案](API_FINAL_DESIGN.md)
- 💡 [参数使用指南](API_PARAMETERS_GUIDE.md)
- 🚀 [快速开始教程](TEXT_TO_HTML_QUICKSTART.md)

---

**✨ 选择合适的模式，让 API 更好地服务于你的业务！**
