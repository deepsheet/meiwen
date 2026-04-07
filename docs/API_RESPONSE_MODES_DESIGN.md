# API 响应模式设计说明

## 📅 更新日期
2026-04-06

## 🎯 设计理念

文本转 HTML API 提供两种响应模式，每种模式有不同的使用场景和返回内容：

| 模式 | 适用场景 | 返回内容 | article_id |
|------|---------|---------|-----------|
| **HTML 模式** | 需要直接获取 HTML 代码进行后续处理 | 只返回 HTML | ❌ 不返回 |
| **URL 模式** | 需要分享链接或永久访问 | 返回 URL + article_id | ✅ 返回 |

---

## 📊 两种模式对比

### 1. HTML 模式（默认）

**特点：**
- ✅ 直接返回完整的 HTML 代码
- ❌ 不返回 `article_id`、`url`、`full_url`
- 🔒 隐藏内部实现细节
- 💾 后台仍会保存文件和创建映射（确保数据完整性）

**响应示例：**
```json
{
  "status": "success",
  "message": "HTML generated successfully",
  "html": "<!DOCTYPE html>..."
}
```

**适用场景：**
- 需要在自己的系统中嵌入 HTML
- 需要对 HTML 进行二次处理
- 不需要分享链接
- 关注隐私，不想暴露文章 ID

**调用示例：**
```python
import requests

response = requests.post(
    "http://localhost:8009/api/text-to-html",
    json={
        "content": "测试内容",
        "title": "测试文章"
        # 不指定 response_type，默认为 "html"
    }
)

result = response.json()
html_code = result["html"]  # 直接使用 HTML 代码

# 可以保存到本地文件
with open("article.html", "w", encoding="utf-8") as f:
    f.write(html_code)
```

---

### 2. URL 模式

**特点：**
- ✅ 返回可访问的网页链接
- ✅ 返回 `article_id`，方便后续管理
- 🔗 适合分享和永久访问
- 💾 保存文件和创建映射

**响应示例：**
```json
{
  "status": "success",
  "message": "HTML generated and saved successfully",
  "url": "/p/abcdefgh",
  "full_url": "http://localhost:8009/p/abcdefgh",
  "article_id": "abcdefgh",
  "title": "测试文章"
}
```

**适用场景：**
- 需要分享文章链接
- 需要永久访问地址
- 需要通过 article_id 管理文章
- 希望文章可以被搜索引擎索引

**调用示例：**
```python
import requests

response = requests.post(
    "http://localhost:8009/api/text-to-html",
    json={
        "content": "测试内容",
        "title": "测试文章",
        "response_type": "url"  # 关键参数
    }
)

result = response.json()
url = result["full_url"]           # 访问链接
article_id = result["article_id"]  # 文章 ID

print(f"文章已生成，访问链接: {url}")
print(f"文章 ID: {article_id}")

# 可以直接分享这个链接
# http://localhost:8009/p/abcdefgh
```

---

## 🔍 为什么这样设计？

### 问题背景

之前的实现存在以下问题：

**方案 A：HTML 模式也返回 article_id**
```json
{
  "html": "...",
  "article_id": "abcdefgh",  // ❌ 问题
  "url": "/p/abcdefgh"
}
```

**存在的问题：**
1. **信息泄露** - 暴露了内部的文章 ID 系统
2. **职责不清** - HTML 模式的目的是获取代码，不是获取链接
3. **混淆用户** - 用户可能误以为必须使用 article_id
4. **安全隐患** - article_id 可能被滥用

**方案 B：HTML 模式不保存文件**
```python
if response_type == 'html':
    return {"html": "..."}  # ❌ 不保存文件
```

**存在的问题：**
1. **数据丢失** - 生成的 HTML 没有持久化
2. **无法追溯** - 无法通过任何方式找回这篇文章
3. **统计缺失** - 无法统计这篇文章的访问量
4. **不一致** - 同样的内容，不同模式处理方式不同

---

### 最终方案：结合两者优点

**核心原则：**
1. ✅ **所有模式都保存文件** - 确保数据完整性和可追溯性
2. ✅ **只有 URL 模式返回 article_id** - 明确区分使用场景
3. ✅ **HTML 模式保持简洁** - 只返回需要的内容

**优势：**
- 📦 **数据完整性** - 所有生成的内容都被保存
- 🔒 **安全性** - HTML 模式不暴露内部 ID
- 🎯 **职责清晰** - 每种模式有明确的用途
- 💡 **灵活性** - 用户可以根据需求选择模式

---

## 💡 使用建议

### 场景 1: 在自己的网站中展示

**推荐：HTML 模式**

```python
# 获取 HTML 代码
response = requests.post(api_url, json={
    "content": "文章内容",
    "response_type": "html"  # 或不传，默认就是 html
})

html = response.json()["html"]

# 嵌入到自己的页面中
page_template = f"""
<!DOCTYPE html>
<html>
<head><title>我的文章</title></head>
<body>
    {html}
</body>
</html>
"""

with open("my_page.html", "w", encoding="utf-8") as f:
    f.write(page_template)
```

**优点：**
- 完全控制页面样式
- 可以自定义布局
- 不依赖外部链接

---

### 场景 2: 分享给其他人阅读

**推荐：URL 模式**

```python
# 获取访问链接
response = requests.post(api_url, json={
    "content": "文章内容",
    "response_type": "url"
})

result = response.json()
share_url = result["full_url"]

# 分享链接
print(f"请阅读这篇文章: {share_url}")

# 或者发送到邮件、聊天工具等
send_email(to="user@example.com", body=f"查看文章: {share_url}")
```

**优点：**
- 一键分享
- 对方无需任何技术知识
- 可以统计访问量

---

### 场景 3: 批量生成并管理

**推荐：URL 模式**

```python
articles = [
    {"title": "文章1", "content": "内容1"},
    {"title": "文章2", "content": "内容2"},
    {"title": "文章3", "content": "内容3"},
]

article_ids = []

for article in articles:
    response = requests.post(api_url, json={
        **article,
        "response_type": "url"
    })
    
    result = response.json()
    article_ids.append(result["article_id"])
    print(f"✅ {article['title']}: {result['full_url']}")

# 保存 article_id 列表，方便后续管理
with open("article_ids.json", "w") as f:
    json.dump(article_ids, f)

# 后续可以通过 article_id 访问任意文章
for aid in article_ids:
    url = f"http://localhost:8009/p/{aid}"
    print(f"访问: {url}")
```

**优点：**
- 便于批量管理
- 可以通过 ID 追踪文章
- 支持后续操作（删除、更新等）

---

### 场景 4: 混合使用

**根据需求灵活选择：**

```python
# 场景 A: 需要立即展示 + 后续分享
response = requests.post(api_url, json={
    "content": "文章内容",
    "response_type": "html"  # 先获取 HTML 立即展示
})

html = response.json()["html"]
display_html(html)  # 立即显示

# 如果需要分享，再次调用获取 URL
response2 = requests.post(api_url, json={
    "content": "文章内容",
    "response_type": "url"
})
share_url = response2.json()["full_url"]
share_link(share_url)  # 分享链接
```

**注意：** 同样的内容会生成两个不同的 article_id，但内容相同。

---

## 🔐 安全性考虑

### HTML 模式的优势

1. **不暴露内部结构**
   - 用户不知道文章 ID 的存在
   - 无法猜测其他文章的 ID
   - 减少被爬取的风险

2. **防止滥用**
   - 用户无法通过遍历 ID 获取所有文章
   - 只能通过 API 重新生成

3. **简化接口**
   - 返回值少，降低带宽消耗
   - 响应更快

### URL 模式的安全措施

1. **随机 ID**
   - article_id 是 8 位随机小写字母
   - 难以暴力破解（26^8 ≈ 2000 亿种组合）

2. **IP 白名单**
   - 只有授权的 IP 可以调用 API
   - 防止未授权访问

3. **访问统计**
   - 可以监控异常访问
   - 及时发现可疑行为

---

## 📝 技术实现细节

### 文件保存逻辑

```python
# 无论哪种模式，都执行以下步骤：

# 1. 生成唯一的 article_id
article_id = generate_article_id()  # 例如: "abcdefgh"

# 2. 生成智能文件名
filename = generate_smart_filename(title, article_id)
# 例如: "abcdefgh_测试文章.html"

# 3. 保存 HTML 文件
filepath = os.path.join(userfiles_dir, filename)
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(formatted_html)

# 4. 创建文章 ID 映射
save_article_mapping(article_id, relative_filepath)
# 在 userdata/article_ids/abcdefgh.txt 中保存文件路径
```

### 响应返回逻辑

```python
if response_type == 'url':
    # URL 模式：返回完整信息
    return {
        "status": "success",
        "url": "/p/abcdefgh",
        "full_url": "http://localhost:8009/p/abcdefgh",
        "article_id": "abcdefgh",
        "title": "测试文章"
    }
else:
    # HTML 模式：只返回 HTML
    return {
        "status": "success",
        "html": "<!DOCTYPE html>..."
    }
```

---

## 🧪 测试验证

### 测试 HTML 模式

```python
import requests

response = requests.post(
    "http://localhost:8009/api/text-to-html",
    json={
        "content": "测试内容",
        "title": "测试文章"
    }
)

result = response.json()

# ✅ 应该包含
assert "html" in result
assert result["status"] == "success"

# ❌ 不应该包含
assert "article_id" not in result
assert "url" not in result
assert "full_url" not in result

print("✅ HTML 模式测试通过")
```

### 测试 URL 模式

```python
import requests

response = requests.post(
    "http://localhost:8009/api/text-to-html",
    json={
        "content": "测试内容",
        "title": "测试文章",
        "response_type": "url"
    }
)

result = response.json()

# ✅ 应该包含
assert "url" in result
assert "full_url" in result
assert "article_id" in result
assert result["status"] == "success"

# ❌ 不应该包含
assert "html" not in result

print("✅ URL 模式测试通过")
```

### 测试文件是否保存

```python
import os

# 检查文件是否存在
userfiles_dir = "userdata/userfiles"
files = os.listdir(userfiles_dir)

print(f"已保存的文件数量: {len(files)}")

# 检查映射文件是否存在
article_ids_dir = "userdata/article_ids"
mappings = os.listdir(article_ids_dir)

print(f"已创建的映射数量: {len(mappings)}")

# 验证映射文件内容
for mapping_file in mappings[:3]:  # 检查前 3 个
    with open(os.path.join(article_ids_dir, mapping_file), 'r') as f:
        filepath = f.read().strip()
        print(f"{mapping_file} -> {filepath}")
        
        # 验证文件确实存在
        if os.path.exists(filepath):
            print(f"  ✅ 文件存在")
        else:
            print(f"  ❌ 文件不存在")
```

---

## 📚 相关文档

- 📖 [完整 API 文档](TEXT_TO_HTML_API.md) - 详细的技术规范
- 🐛 [Bug 修复说明](BUG_FIX_ARTICLE_ID_MAPPING.md) - article_id 映射问题修复
- 💡 [参数指南](API_PARAMETERS_GUIDE.md) - 扩写模式和额外需求详解
- 🚀 [快速开始](TEXT_TO_HTML_QUICKSTART.md) - 5分钟上手

---

## ✨ 总结

### 设计原则

1. **数据完整性优先** - 所有模式都保存文件
2. **职责分离清晰** - HTML 模式给代码，URL 模式给链接
3. **安全考虑周全** - HTML 模式不暴露内部 ID
4. **用户体验友好** - 根据场景选择最合适的模式

### 选择建议

| 你的需求 | 推荐模式 | 原因 |
|---------|---------|------|
| 需要 HTML 代码 | HTML 模式 | 直接获取，无需解析 |
| 需要分享链接 | URL 模式 | 一键分享，方便访问 |
| 需要管理文章 | URL 模式 | 有 article_id 可追踪 |
| 注重隐私安全 | HTML 模式 | 不暴露内部结构 |
| 需要统计分析 | URL 模式 | 可以统计页面访问 |
| 嵌入式展示 | HTML 模式 | 完全控制样式 |

---

**🎯 选择合适的模式，让 API 更好地服务于你的业务场景！**
