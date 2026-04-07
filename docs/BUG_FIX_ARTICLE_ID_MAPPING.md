# Bug 修复 - article_id 映射问题

## 📅 修复日期
2026-04-06

## 🐛 问题描述

### 现象
调用 API 时返回了 `article_id`，但访问 `/p/{article_id}` 时报错"文章不存在"。

**测试步骤：**
1. 调用 API：`POST http://127.0.0.1:8009/api/text-to-html`
2. API 返回：`{"article_id": "firvdihh", ...}`
3. 访问链接：`http://localhost:8009/p/firvdihh`
4. 报错：`{"message": "文章不存在", "status": "error"}`

### 根本原因

原代码逻辑存在问题：

```python
# 原代码（有问题）
if response_type == 'url':
    # 只有 URL 模式才保存文件和创建映射
    save_article_mapping(article_id, relative_filepath)
    return jsonify({...})
else:
    # HTML 模式不保存文件，但返回了 article_id
    return jsonify({
        "article_id": article_id,  # ❌ 返回了 ID，但没有保存文件
        "html": formatted_html
    })
```

**问题分析：**
- 当 `response_type` 为 `'html'`（默认值）时，代码返回了 `article_id`
- 但**没有保存 HTML 文件**到 `userdata/userfiles/`
- 也**没有创建文章 ID 映射**文件到 `userdata/article_ids/`
- 导致访问 `/p/{article_id}` 时找不到对应的文件

---

## ✅ 修复方案

### 核心改进

**无论哪种响应模式，都保存文件并创建映射。**

```python
# 修复后的代码
# 🔴 无论哪种模式，都保存文件并创建映射，确保 article_id 有效
project_root = os.path.dirname(app.root_path)
userfiles_dir = os.path.join(project_root, 'userdata', 'userfiles')
if not os.path.exists(userfiles_dir):
    os.makedirs(userfiles_dir)

# 生成智能文件名
filename = generate_smart_filename(title, article_id)
filepath = os.path.join(userfiles_dir, filename)

# 保存格式化后的 HTML
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(formatted_html)

# 保存文章 ID 映射
relative_filepath = f"userdata/userfiles/{filename}"
save_article_mapping(article_id, relative_filepath)

# 生成访问 URL
access_url = f"/p/{article_id}"
full_url = f"{protocol}://{host}{access_url}"

# 根据 response_type 返回不同的响应
if response_type == 'url':
    # URL 模式：只返回 URL
    return jsonify({
        "url": access_url,
        "full_url": full_url,
        "article_id": article_id,
        ...
    })
else:
    # HTML 模式：返回 HTML + URL
    return jsonify({
        "html": formatted_html,
        "url": access_url,      # ✅ 新增：也返回 URL
        "full_url": full_url,   # ✅ 新增：也返回完整 URL
        "article_id": article_id,
        ...
    })
```

### 改进点

1. **统一文件保存逻辑**
   - 移除了条件判断，所有模式都保存文件
   - 确保 `article_id` 始终有效

2. **HTML 模式也返回 URL**
   - 即使选择 HTML 模式，也提供访问链接
   - 增加灵活性，调用者可以选择使用 HTML 或 URL

3. **保证数据一致性**
   - 返回的 `article_id` 一定对应有效的文件
   - 访问 `/p/{article_id}` 一定能成功

---

## 📊 修复前后对比

### 修复前

| 响应模式 | 保存文件 | 创建映射 | 返回 article_id | /p/{id} 可访问 |
|---------|---------|---------|----------------|---------------|
| `html` | ❌ | ❌ | ✅ | ❌ |
| `url` | ✅ | ✅ | ✅ | ✅ |

**问题：** HTML 模式返回了无效的 article_id

### 修复后

| 响应模式 | 保存文件 | 创建映射 | 返回 article_id | 返回 URL | /p/{id} 可访问 |
|---------|---------|---------|----------------|---------|---------------|
| `html` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `url` | ✅ | ✅ | ✅ | ✅ | ✅ |

**改进：** 两种模式都能保证 article_id 有效，且 HTML 模式额外提供 URL

---

## 🧪 测试验证

### 测试 1: HTML 模式（默认）

```python
import requests

response = requests.post(
    "http://127.0.0.1:8009/api/text-to-html",
    json={
        "content": "测试内容",
        "title": "测试文章"
        # 不指定 response_type，默认为 "html"
    }
)

result = response.json()
print(f"Article ID: {result['article_id']}")
print(f"URL: {result['full_url']}")

# ✅ 现在可以正常访问
# http://localhost:8009/p/{article_id}
```

**预期结果：**
- ✅ 返回 `article_id`
- ✅ 返回 `url` 和 `full_url`
- ✅ 访问 `/p/{article_id}` 成功

### 测试 2: URL 模式

```python
response = requests.post(
    "http://127.0.0.1:8009/api/text-to-html",
    json={
        "content": "测试内容",
        "response_type": "url"
    }
)

result = response.json()
print(f"Article ID: {result['article_id']}")
print(f"URL: {result['full_url']}")

# ✅ 可以正常访问
```

**预期结果：**
- ✅ 返回 `article_id`
- ✅ 返回 `url` 和 `full_url`
- ✅ 访问 `/p/{article_id}` 成功

---

## 📝 API 响应变化

### HTML 模式响应（修复后）

```json
{
  "status": "success",
  "message": "HTML generated successfully",
  "html": "<!DOCTYPE html>...",
  "url": "/p/abcdefgh",       // ✅ 新增
  "full_url": "http://localhost:8009/p/abcdefgh",  // ✅ 新增
  "article_id": "abcdefgh",
  "title": "文章标题"
}
```

**变化：**
- ✅ 新增 `url` 字段
- ✅ 新增 `full_url` 字段
- ✅ `article_id` 现在始终有效

### URL 模式响应（无变化）

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

## 💡 使用建议

### 1. 如果只需要 HTML 代码

```python
response = requests.post(url, json={
    "content": "文本内容",
    "response_type": "html"  # 或不传，默认就是 html
})

html = response.json()["html"]
# 如果需要，也可以使用返回的 URL
url = response.json()["full_url"]
```

### 2. 如果只需要访问链接

```python
response = requests.post(url, json={
    "content": "文本内容",
    "response_type": "url"
})

url = response.json()["full_url"]
# 直接分享或使用这个链接
```

### 3. 两者都需要

```python
response = requests.post(url, json={
    "content": "文本内容"
    # 默认返回 HTML + URL
})

result = response.json()
html = result["html"]      # HTML 代码
url = result["full_url"]   # 访问链接
article_id = result["article_id"]  # 文章 ID
```

---

## ⚠️ 注意事项

### 1. 存储空间

- 每次调用都会保存一个 HTML 文件
- 文件保存在 `userdata/userfiles/` 目录
- 建议定期清理不需要的文件

### 2. 文件命名

- 格式：`{article_id}_{title}.html`
- 例如：`firvdihh_测试文章.html`
- 自动处理特殊字符和空格

### 3. 访问统计

- 通过 `/p/{article_id}` 访问会计入 PV 统计
- 可以直接使用返回的 URL 进行分享

---

## 🔍 相关文件

- **核心代码：** [src/web_server.py](../src/web_server.py) - `text_to_html_api()` 函数
- **映射函数：** [src/web_server.py](../src/web_server.py) - `save_article_mapping()` 函数
- **访问路由：** [src/web_server.py](../src/web_server.py) - `serve_article()` 函数

---

## ✨ 总结

### 修复前的问题
- ❌ HTML 模式返回无效的 `article_id`
- ❌ 访问 `/p/{article_id}` 报错"文章不存在"
- ❌ 数据不一致，用户体验差

### 修复后的改进
- ✅ 所有模式都保存文件并创建映射
- ✅ `article_id` 始终有效
- ✅ HTML 模式额外提供 URL，更灵活
- ✅ 数据一致性好，用户体验佳

---

**问题已修复！** 🎉

现在无论使用哪种响应模式，返回的 `article_id` 都是有效的，可以通过 `/p/{article_id}` 正常访问生成的页面。
