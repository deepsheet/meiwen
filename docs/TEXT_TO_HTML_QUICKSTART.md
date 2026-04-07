# 文本转 HTML API - 快速开始指南

## 🚀 5 分钟快速上手

### 第一步：确认访问权限

确保您的服务器 IP 在白名单中：
- ✅ `127.0.0.1`（本地）
- ✅ `localhost`
- ✅ `deepsheet.net`
- ✅ `chaojibiaoge.com`

如果不在白名单中，请联系管理员添加。

---

### 第二步：发送第一个请求

使用 cURL 测试 API：

```bash
curl -X POST http://localhost:5000/api/text-to-html \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Hello World! 这是第一篇 AI 美化的文章。"
  }'
```

预期响应：
```json
{
  "status": "success",
  "message": "HTML generated successfully",
  "html": "<!DOCTYPE html>...",
  "article_id": "abcdefgh",
  "title": "Hello World"
}
```

---

### 第三步：在代码中使用

#### Python 示例（最简版）

```python
import requests

response = requests.post(
    "http://localhost:5000/api/text-to-html",
    json={"content": "你的文本内容"}
)

if response.status_code == 200:
    html = response.json()["html"]
    print(html)  # 或直接保存为 .html 文件
```

#### JavaScript 示例（最简版）

```javascript
fetch('http://localhost:5000/api/text-to-html', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({content: '你的文本内容'})
})
.then(res => res.json())
.then(data => console.log(data.html));
```

---

## 📋 常用场景示例

### 场景 1：博客文章美化

```python
import requests

content = """
# 人工智能的未来

人工智能正在快速发展，将深刻改变我们的生活。

## 主要趋势

1. **自动化** - 工作流程自动化
2. **个性化** - 定制化服务体验
3. **智能化** - 决策支持系统

未来已来，让我们拥抱 AI 时代！
"""

response = requests.post(
    "http://localhost:5000/api/text-to-html",
    json={
        "content": content,
        "title": "人工智能的未来",
        "content_strategy": "interpret"
    }
)

result = response.json()
with open("blog.html", "w", encoding="utf-8") as f:
    f.write(result["html"])

print(f"✅ 博客文章已生成: {result['article_id']}")
```

### 场景 2：产品说明文档

```python
import requests

product_doc = """
产品名称：智能办公助手 v2.0

核心功能：
• 智能日程管理
• 会议纪要自动生成
• 任务分配与跟踪
• 数据分析报告

技术特点：
- 基于最新 AI 技术
- 支持多语言
- 云端同步
- 数据安全加密

适用场景：
企业办公、团队协作、项目管理
"""

response = requests.post(
    "http://localhost:5000/api/text-to-html",
    json={
        "content": product_doc,
        "title": "智能办公助手产品说明",
        "extra_requirements": "使用绿色主题，突出产品特性"
    }
)

html = response.json()["html"]
# 保存或展示 HTML
```

### 场景 3：数据报告

```python
import requests

report = """
2026年第一季度销售报告

总体业绩：
销售额同比增长 35%
客户满意度达到 92%
新用户增长 50%

区域表现：
华东地区：增长 40%
华南地区：增长 32%
华北地区：增长 28%

关键成功因素：
1. 产品创新
2. 市场拓展
3. 客户服务优化

下季度目标：
继续保持增长势头，开拓新市场
"""

response = requests.post(
    "http://localhost:5000/api/text-to-html",
    json={
        "content": report,
        "title": "2026 Q1 销售报告",
        "content_strategy": "strict",
        "extra_requirements": "使用表格展示数据，蓝色商务风格"
    }
)

# 获取 HTML 并嵌入到邮件或网页中
html_content = response.json()["html"]
```

---

## ⚙️ 参数说明速查

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `content` | string | ✅ | - | 要转换的文本 |
| `title` | string | ❌ | AI 生成 | 文章标题 |
| `content_strategy` | string | ❌ | `strict` | **扩写模式**：<br>`strict`（严格）<br>`interpret`（解读）<br>`expand`（扩写） |
| `extra_requirements` | string | ❌ | 空 | **额外需求**：<br>用自然语言描述格式化要求 |
| `response_type` | string | ❌ | `html` | `html`（返回HTML代码）/`url`（返回网页链接） |

---

## 🎨 格式化技巧

### 让 AI 理解你的需求

在 `extra_requirements` 中可以使用自然语言描述：

```json
{
  "content": "...",
  "extra_requirements": "使用紫色渐变主题，添加 emoji 图标，重点内容用卡片展示"
}
```

支持的样式描述：
- 颜色主题：红色、蓝色、绿色、紫色等
- 布局方式：卡片、列表、表格、引用块
- 视觉元素：emoji、图标、分隔线
- 强调方式：加粗、高亮、背景色

---

## ❓ 常见问题

### Q: 返回 403 错误怎么办？
A: 您的 IP 不在白名单中。检查是否从 localhost 访问，或联系管理员添加 IP。

### Q: 生成的 HTML 如何使用？
A: 直接保存为 `.html` 文件即可在浏览器中打开，或嵌入到您的网站中。

### Q: 可以自定义样式吗？
A: 可以通过 `extra_requirements` 参数描述您想要的样式，AI 会自动应用。

### Q: 支持多长文本？
A: 建议单次不超过 10,000 字。更长文本可分段处理。

### Q: 响应时间多久？
A: 通常 3-10 秒，取决于文本长度和服务器负载。

---

## 🔗 相关资源

- 📖 [完整 API 文档](TEXT_TO_HTML_API.md)
- 🧪 [测试脚本](../debug/test_text_to_html_api.py)
- 💡 [使用示例](../debug/test_text_to_html_api.py)

---

## 📞 获取帮助

遇到问题？联系我们：
- 📧 support@deepsheet.net
- 🌐 https://deepsheet.net

---

**祝您使用愉快！** ✨
