# API 更新说明 - 支持返回 URL 模式

## 📅 更新日期
2026-04-06

## 🎯 更新内容

### 新增功能：`response_type` 参数

文本转 HTML API 现在支持两种响应模式：

1. **HTML 模式（默认）**：直接返回完整的 HTML 代码
2. **URL 模式**：保存 HTML 文件并返回可访问的网页链接

---

## 🔧 使用方法

### 参数说明

在请求中添加 `response_type` 参数：

```json
{
  "content": "你的文本内容...",
  "response_type": "html"  // 或 "url"
}
```

**可选值：**
- `"html"`（默认）：返回 HTML 代码
- `"url"`：返回网页访问链接

---

## 📊 响应格式对比

### 模式 1: 返回 HTML 代码（默认）

**请求：**
```json
{
  "content": "测试内容",
  "response_type": "html"
}
```

**响应：**
```json
{
  "status": "success",
  "message": "HTML generated successfully",
  "html": "<!DOCTYPE html>...",
  "article_id": "abcdefgh",
  "title": "文章标题"
}
```

**适用场景：**
- ✅ 需要直接在代码中处理 HTML
- ✅ 需要嵌入到其他页面中
- ✅ 需要自定义保存方式
- ✅ 不需要永久链接

---

### 模式 2: 返回网页 URL

**请求：**
```json
{
  "content": "测试内容",
  "response_type": "url"
}
```

**响应：**
```json
{
  "status": "success",
  "message": "HTML generated and saved successfully",
  "url": "/p/abcdefgh",
  "full_url": "http://localhost:5000/p/abcdefgh",
  "article_id": "abcdefgh",
  "title": "文章标题"
}
```

**适用场景：**
- ✅ 需要分享链接给他人
- ✅ 需要永久访问地址
- ✅ 希望文章可被搜索引擎索引
- ✅ 不想在 API 响应中传输大量数据
- ✅ 需要统计页面访问量

---

## 💡 使用示例

### Python 示例

#### 获取 HTML 代码
```python
import requests

response = requests.post(
    "http://localhost:5000/api/text-to-html",
    json={
        "content": "你的文本内容...",
        "response_type": "html"  # 或不传，默认为 html
    }
)

if response.status_code == 200:
    html = response.json()["html"]
    # 直接使用 HTML 代码
```

#### 获取网页链接
```python
import requests

response = requests.post(
    "http://localhost:5000/api/text-to-html",
    json={
        "content": "你的文本内容...",
        "response_type": "url"  # 关键参数
    }
)

if response.status_code == 200:
    result = response.json()
    url = result["full_url"]
    print(f"访问链接: {url}")
    
    # 可以直接打开浏览器
    import webbrowser
    webbrowser.open(url)
```

---

## 🔄 向后兼容性

✅ **完全向后兼容**

- 如果不指定 `response_type`，默认行为与之前相同（返回 HTML 代码）
- 现有代码无需修改即可继续工作
- 新功能为可选参数，不影响已有功能

---

## 📝 技术实现

### 核心改动

1. **新增参数验证**
   - 验证 `response_type` 的值必须为 `"html"` 或 `"url"`
   - 无效值返回 400 错误

2. **URL 模式处理流程**
   ```
   生成 HTML → 保存到文件 → 创建文章映射 → 生成访问 URL → 返回 URL
   ```

3. **文件保存位置**
   - 路径：`userdata/userfiles/{article_id}_{title}.html`
   - 自动创建目录（如不存在）
   - 使用智能文件名生成规则

4. **URL 生成规则**
   - 相对路径：`/p/{article_id}`
   - 完整 URL：`{protocol}://{host}/p/{article_id}`
   - 动态获取协议和主机名

---

## 🧪 测试覆盖

### 新增测试用例

1. ✅ 返回 URL 模式测试
2. ✅ 无效的 response_type 参数测试
3. ✅ URL 模式文件保存验证
4. ✅ URL 可访问性验证

### 运行测试

```bash
python debug/test_text_to_html_api.py
```

---

## 📚 相关文档更新

以下文档已同步更新：

1. ✅ [TEXT_TO_HTML_API.md](TEXT_TO_HTML_API.md) - 完整 API 文档
2. ✅ [TEXT_TO_HTML_QUICKSTART.md](TEXT_TO_HTML_QUICKSTART.md) - 快速开始指南
3. ✅ [test_text_to_html_api.py](../debug/test_text_to_html_api.py) - 测试脚本
4. ✅ [text_to_html_examples.py](../examples/text_to_html_examples.py) - 使用示例

---

## 🎯 最佳实践建议

### 何时使用 HTML 模式？

- 需要在代码中直接处理 HTML 内容
- 需要将 HTML 嵌入到邮件、消息或其他系统中
- 需要自定义文件命名和存储位置
- 响应速度要求高（URL 模式需要额外保存文件）

### 何时使用 URL 模式？

- 需要分享链接给用户
- 需要永久访问地址
- 希望利用现有的 `/p/{article_id}` 访问机制
- 需要统计页面访问量（PV）
- 响应数据量敏感（URL 比 HTML 小得多）

---

## ⚠️ 注意事项

1. **存储空间**
   - URL 模式会在服务器保存 HTML 文件
   - 文件保存在 `userdata/userfiles/` 目录
   - 注意磁盘空间管理

2. **文件清理**
   - 目前不会自动清理旧文件
   - 建议定期清理不需要的文件
   - 可以基于 `article_id` 进行清理

3. **URL 有效期**
   - 生成的 URL 永久有效（除非手动删除文件）
   - 可以通过 `/p/{article_id}` 随时访问

4. **性能考虑**
   - URL 模式比 HTML 模式多一步文件保存操作
   - 通常增加 0.1-0.5 秒的处理时间
   - 对于大批量处理，建议使用 HTML 模式

---

## 🔮 未来规划

可能的后续优化：

1. 添加文件自动清理机制
2. 支持自定义 URL 过期时间
3. 添加 URL 访问统计
4. 支持批量生成 URL
5. 提供文件管理 API

---

## 📞 问题反馈

如有问题或建议，请联系：
- 📧 support@deepsheet.net
- 🌐 https://deepsheet.net

---

**更新完成！** ✨

API 现已支持灵活的响应模式，可以根据实际需求选择最合适的方式。
