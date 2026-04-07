# HTML 美化服务 - 快速参考卡

## 🚀 一分钟启动服务

```bash
# 进入项目目录
cd /Users/chenkunji/Documents/cursor/isheetmarketing

# 启动服务
./start_formatter.sh
```

## 🌐 访问地址

**Web 界面**: http://localhost:8080/html-formatter  
**API 端点**: http://localhost:8080/api/format-html  
**健康检查**: http://localhost:8080/health

## 📝 使用流程（3 步）

1. **输入内容** → 在网页文本框粘贴文章
2. **点击美化** → 点击"🎨 开始美化"按钮
3. **获取链接** → 复制链接分享给他人

## 🔧 API 调用示例

### cURL
```bash
curl -X POST http://localhost:8080/api/format-html \
  -H "Content-Type: application/json" \
  -d '{
    "title": "我的文章",
    "content": "这里是文章内容..."
  }'
```

### Python
```python
import requests

response = requests.post(
    "http://localhost:8080/api/format-html",
    json={
        "title": "文章标题",
        "content": "文章内容..."
    }
)

result = response.json()
print(result["full_url"])
```

### JavaScript
```javascript
fetch('http://localhost:8080/api/format-html', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        title: '文章标题',
        content: '文章内容...'
    })
})
.then(r => r.json())
.then(data => console.log(data.full_url));
```

## 🎨 美化效果

✅ 渐变色主题（紫色系）  
✅ 圆角卡片设计  
✅ Emoji 图标点缀  
✅ 响应式布局  
✅ 全内联样式  

## 📁 重要文件

| 文件 | 用途 |
|------|------|
| `static/formatter.html` | Web 界面 |
| `src/html_formatter.py` | 格式化核心 |
| `src/web_server.py` | Web 服务 |
| `app.py` | 应用入口 |

## 🧪 测试命令

```bash
# 功能测试
python test_html_formatter_service.py

# 示例演示
python examples_html_formatter.py
```

## ⚙️ 配置修改

**端口**: `export PORT=8080`  
**API 密钥**: 编辑 `config/config.py`

## 🛠️ 故障排查

```bash
# 查看日志
tail -f logs/server.log

# 检查端口
lsof -i :8080

# 重装依赖
pip install -r requirements.txt
```

## 📖 完整文档

- 快速教程：[QUICK_START_TUTORIAL.md](QUICK_START_TUTORIAL.md)
- 使用指南：[HTML_FORMATTER_USAGE.md](HTML_FORMATTER_USAGE.md)
- 服务文档：[HTML_FORMATTER_SERVICE.md](HTML_FORMATTER_SERVICE.md)
- 项目总结：[HTML_FORMATTER_SUMMARY.md](HTML_FORMATTER_SUMMARY.md)

---

**需要帮助？** 查看完整文档或检查日志文件。
