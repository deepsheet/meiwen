# 文本转 HTML API 技术文档

## 概述

深表美文提供文本转 HTML API 服务，可将普通文本转换为具有丰富视觉效果的精美 HTML 页面。本 API 采用 IP 白名单机制进行访问控制，目前仅允许公司内部系统调用。

---

## API 端点

**接口地址：** `POST /api/text-to-html`

**完整 URL 示例：** `http://localhost:5000/api/text-to-html`

---

## 访问控制

### IP 白名单机制

API 采用多层验证机制，只有以下来源的请求会被接受：

#### 1. 允许的 IP 地址
- `127.0.0.1`（本地 IPv4）
- `::1`（本地 IPv6）
- `localhost`

#### 2. 允许的域名
- `deepsheet.net`
- `chaojibiaoge.com`

#### 3. 反向代理支持
API 支持通过以下 HTTP 头识别真实客户端 IP：
- `X-Forwarded-For`
- `X-Real-IP`

如果请求来自未授权的 IP 或域名，将返回 **403 Forbidden** 错误。

---

## 请求参数

### 请求头

```
Content-Type: application/json
```

### 请求体（JSON 格式）

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `content` | string | ✅ 是 | - | 要转换的文本内容 |
| `title` | string | ❌ 否 | AI 生成 | 文章标题（如不提供,AI 会自动生成） |
| `content_strategy` | string | ❌ 否 | `strict` | **扩写模式**，控制 AI 如何处理原文：<br>- `strict`（严格遵循原文，一字不改）<br>- `interpret`（解读优化，可调整表达逻辑）<br>- `expand`（扩写丰富，可补充背景和案例） |
| `extra_requirements` | string | ❌ 否 | 空 | **额外需求**，用自然语言描述格式化要求，例如：<br>- "使用蓝色主题"<br>- "添加表格展示数据"<br>- "使用卡片布局，添加 emoji" |
| `response_type` | string | ❌ 否 | `html` | 响应类型，可选值：<br>- `html`（返回 HTML 代码，默认）<br>- `url`（返回网页访问 URL） |

### 请求示例

#### 基础用法（最小化请求）

```json
{
  "content": "这是一段测试文本。\n\nAI 技术正在改变我们的生活方式。"
}
```

#### 完整用法

```json
{
  "content": "这是一篇关于人工智能的文章。\n\n人工智能（AI）是计算机科学的一个分支，它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。",
  "title": "人工智能的未来发展",
  "content_strategy": "strict",
  "extra_requirements": "请使用蓝色主题，添加一些科技感的元素"
}
```

#### 返回 URL 模式

如果不希望直接返回 HTML 代码，而是希望获得一个可以访问的网页链接，可以使用 `response_type: "url"`：

```json
{
  "content": "这是一篇关于人工智能的文章。\n\n人工智能正在改变世界...",
  "title": "人工智能的未来发展",
  "response_type": "url"
}
```

**响应示例：**

```json
{
  "status": "success",
  "message": "HTML generated and saved successfully",
  "url": "/p/abcdefgh",
  "full_url": "http://localhost:5000/p/abcdefgh",
  "article_id": "abcdefgh",
  "title": "人工智能的未来发展"
}
```

**使用场景：**
- ✅ 需要在多个地方分享同一篇文章
- ✅ 希望文章可以被搜索引擎索引
- ✅ 需要永久链接供用户访问
- ✅ 不想在响应中传输大量 HTML 数据

---

## 🎨 扩写模式详解

### 1. strict（严格模式）

**特点：**
- 一字不差地保持原文 100% 完整
- 仅修正错别字、语法错误
- 不添加任何新内容

**适用场景：**
- 正式文档、法律文件
- 新闻报道、官方公告
- 需要保持原文准确性的内容

**示例：**
```json
{
  "content": "人工智能是计算机科学的一个分支...",
  "content_strategy": "strict"
}
```

### 2. interpret（解读优化）

**特点：**
- 可以调整段落顺序、优化表达逻辑
- 可以添加必要的过渡句、解释性文字
- 保持核心内容不变，提升可读性

**适用场景：**
- 技术文档、教程
- 内容逻辑需要重组
- 需要提升阅读体验的内容

**示例：**
```json
{
  "content": "AI技术...机器学习...深度学习...",
  "content_strategy": "interpret"
}
```

### 3. expand（扩写丰富）

**特点：**
- 可以补充背景信息、案例、数据支撑
- 可以对专业术语进行解释说明
- 可以添加相关的扩展内容

**适用场景：**
- 营销文案、推广文章
- 科普文章、知识普及
- 需要丰富内容的场景

**示例：**
```json
{
  "content": "Python是一种编程语言...",
  "content_strategy": "expand"
}
```

---

## 💡 额外需求详解

`extra_requirements` 参数允许你用自然语言描述想要的格式化效果。

### 常用格式化要求

#### 颜色主题
```json
{
  "extra_requirements": "使用蓝色主题"
}
```
支持的颜色：红色、蓝色、绿色、紫色、橙色、粉色等

#### 布局方式
```json
{
  "extra_requirements": "使用卡片布局展示内容"
}
```
支持的布局：卡片、列表、表格、引用块、网格等

#### 视觉元素
```json
{
  "extra_requirements": "添加 emoji 图标，使用渐变色背景"
}
```
支持的元素：emoji、图标、分隔线、装饰元素等

#### 强调方式
```json
{
  "extra_requirements": "重点内容用高亮背景，关键数据加粗显示"
}
```
支持的强调：加粗、高亮、背景色、边框等

### 组合使用示例

```json
{
  "content": "产品特点：高性能、易使用、安全可靠",
  "extra_requirements": "使用绿色主题，用卡片展示每个特点，添加对应的 emoji 图标"
}
```

```json
{
  "content": "销售数据：华东 50万，华南 30万，华北 20万",
  "extra_requirements": "使用表格展示数据，紫色渐变主题，突出显示最高值"
}
```

```json
{
  "content": "步骤一：注册账号\n步骤二：完善资料\n步骤三：开始使用",
  "extra_requirements": "使用编号列表，每个步骤用卡片展示，添加箭头图标连接"
}
```

---

## 响应格式

### 成功响应（HTTP 200）

#### 模式 1: 返回 HTML 代码（默认）

当 `response_type` 为 `"html"` 或未指定时：

```json
{
  "status": "success",
  "message": "HTML generated successfully",
  "html": "<!DOCTYPE html>\n<html lang=\"zh-CN\">\n<head>\n    <meta charset=\"UTF-8\">\n    ...",
  "article_id": "abcdefgh",
  "title": "人工智能的未来发展"
}
```

**响应字段说明：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `status` | string | 状态码，`success` 表示成功 |
| `message` | string | 响应消息 |
| `html` | string | 生成的完整 HTML 代码（包含完整的 HTML 文档结构） |
| `article_id` | string | 文章唯一标识符（8 位小写字母） |
| `title` | string | 文章标题（如果请求中未提供，则为 AI 生成的标题） |

#### 模式 2: 返回网页 URL

当 `response_type` 为 `"url"` 时：

```json
{
  "status": "success",
  "message": "HTML generated and saved successfully",
  "url": "/p/abcdefgh",
  "full_url": "http://localhost:5000/p/abcdefgh",
  "article_id": "abcdefgh",
  "title": "人工智能的未来发展"
}
```

**响应字段说明：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `status` | string | 状态码，`success` 表示成功 |
| `message` | string | 响应消息 |
| `url` | string | 文章的相对访问路径 |
| `full_url` | string | 文章的完整访问 URL |
| `article_id` | string | 文章唯一标识符（8 位小写字母） |
| `title` | string | 文章标题 |

### 错误响应

#### 400 Bad Request - 缺少必要参数

```json
{
  "status": "error",
  "message": "Content is required"
}
```

#### 403 Forbidden - IP 未授权

```json
{
  "status": "error",
  "message": "Access denied: Your IP is not authorized to use this API"
}
```

#### 500 Internal Server Error - 服务器错误

```json
{
  "status": "error",
  "message": "Failed to generate HTML: [错误详情]"
}
```

---

## 使用示例

### Python 示例

```python
import requests
import json

# API 端点
url = "http://localhost:5000/api/text-to-html"

# 请求数据
payload = {
    "content": """人工智能正在改变世界
    
随着技术的进步，人工智能已经深入到我们生活的方方面面。从智能手机到自动驾驶汽车，AI 技术正在重塑我们的生活方式。

未来展望：
1. 更智能的个人助手
2. 医疗诊断的革新
3. 教育个性化
4. 工业自动化""",
    "title": "人工智能改变生活",
    "content_strategy": "strict"
}

# 发送请求
response = requests.post(url, json=payload)

# 检查响应
if response.status_code == 200:
    result = response.json()
    if result["status"] == "success":
        html_content = result["html"]
        article_id = result["article_id"]
        
        # 保存 HTML 文件
        with open(f"article_{article_id}.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"✅ HTML 生成成功！文章 ID: {article_id}")
        print(f"📄 HTML 长度: {len(html_content)} 字符")
    else:
        print(f"❌ 生成失败: {result['message']}")
else:
    print(f"❌ 请求失败，状态码: {response.status_code}")
    print(response.json())
```

### JavaScript/Node.js 示例

```javascript
const fetch = require('node-fetch');

async function textToHtml() {
    const url = 'http://localhost:5000/api/text-to-html';
    
    const payload = {
        content: `人工智能正在改变世界

随着技术的进步，人工智能已经深入到我们生活的方方面面。`,
        title: '人工智能改变生活',
        content_strategy: 'strict'
    };
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            console.log('✅ HTML 生成成功！');
            console.log('文章 ID:', result.article_id);
            console.log('HTML 长度:', result.html.length);
            
            // 可以在这里保存 HTML 或进行其他处理
            return result.html;
        } else {
            console.error('❌ 生成失败:', result.message);
        }
    } catch (error) {
        console.error('❌ 请求异常:', error.message);
    }
}

textToHtml();
```

### 返回 URL 模式示例（Python）

```python
import requests

# API 端点
url = "http://localhost:5000/api/text-to-html"

# 请求数据 - 使用 response_type: "url"
payload = {
    "content": """人工智能正在改变世界

随着技术的进步，人工智能已经深入到我们生活的方方面面。从智能手机到自动驾驶汽车，AI 技术正在重塑我们的生活方式。

未来展望：
1. 更智能的个人助手
2. 医疗诊断的革新
3. 教育个性化
4. 工业自动化""",
    "title": "人工智能改变生活",
    "response_type": "url"  # 关键参数：返回 URL 而不是 HTML
}

# 发送请求
response = requests.post(url, json=payload)

# 检查响应
if response.status_code == 200:
    result = response.json()
    if result["status"] == "success":
        article_url = result["full_url"]
        article_id = result["article_id"]
        
        print(f"✅ 网页生成成功！")
        print(f"🔗 访问链接: {article_url}")
        print(f"📄 文章 ID: {article_id}")
        
        # 可以直接分享这个链接
        # 或者在浏览器中打开
        import webbrowser
        webbrowser.open(article_url)
    else:
        print(f"❌ 生成失败: {result['message']}")
else:
    print(f"❌ 请求失败，状态码: {response.status_code}")
    print(response.json())
```

### cURL 示例

```bash
curl -X POST http://localhost:5000/api/text-to-html \
  -H "Content-Type: application/json" \
  -d '{
    "content": "这是一段测试文本。\n\nAI 技术正在改变我们的生活。",
    "title": "测试文章",
    "content_strategy": "strict"
  }'
```

---

## 高级功能

### 1. 内容处理策略

#### strict（严格模式）
- 完全遵循原文内容
- 不进行任何内容修改或扩展
- 适合需要保持原文准确性的场景

#### interpret（解读模式）
- 允许对原文进行适度解读
- 可能会调整表达方式以提升可读性
- 适合博客、文章等场景

#### expand（扩写模式）
- 允许在原文基础上进行合理扩写
- 会补充相关背景和细节
- 适合需要丰富内容的场景

### 2. 额外格式化要求

可以通过 `extra_requirements` 参数指定特殊的格式化需求：

```json
{
  "content": "...",
  "extra_requirements": "请使用绿色主题，突出显示关键数据，添加对比表格"
}
```

支持的格式化特性包括：
- 自定义颜色主题
- 表格展示
- 卡片布局
- 引用块
- 列表样式
- Emoji 图标
- 渐变背景

### 3. 自动标题生成

如果不提供 `title` 参数，API 会使用 AI 自动分析内容并生成合适的标题：

```json
{
  "content": "人工智能的发展历程..."
  // 不提供 title，AI 会自动生成
}
```

---

## 性能说明

- **响应时间：** 通常在 3-10 秒之间（取决于文本长度和 AI 处理速度）
- **文本长度限制：** 建议单次请求不超过 10,000 字
- **并发限制：** 无硬性限制，但建议合理控制并发请求数

---

## 注意事项

1. **IP 白名单：** 确保您的服务器 IP 在白名单中，否则会返回 403 错误
2. **HTTPS 推荐：** 生产环境建议使用 HTTPS 协议
3. **错误处理：** 请妥善处理各种错误情况，特别是网络超时和服务器错误
4. **HTML 完整性：** 返回的 HTML 是完整的文档，包含 `<html>`、`<head>`、`<body>` 等标签
5. **编码格式：** 所有文本均使用 UTF-8 编码
6. **底部标识：** 生成的 HTML 页面底部会包含"深表美文-文本转美页"的品牌标识

---

## 常见问题

### Q1: 为什么返回 403 错误？
A: 您的 IP 地址不在白名单中。请联系管理员将您的 IP 添加到允许列表中。

### Q2: 如何获取文章的唯一链接？
A: API 返回的 `article_id` 可用于构建访问链接：`http://your-domain/p/{article_id}`

### Q3: 生成的 HTML 可以离线使用吗？
A: 是的，所有样式都是内联的，无需外部资源，可以完全离线使用。

### Q4: 支持哪些语言？
A: 支持中文、英文等多种语言，API 会自动检测文本语言并应用相应的排版规则。

### Q5: 如何处理长文本？
A: 对于超过 5000 字的长文本，建议使用分段处理或联系技术支持获取优化方案。

---

## 技术支持

如有问题或需要添加 IP 白名单，请联系：
- 邮箱：support@deepsheet.net
- 网站：https://deepsheet.net

---

## 版本历史

- **v1.0.0** (2026-04-06)
  - 初始版本发布
  - 支持基本的文本转 HTML 功能
  - 实现 IP 白名单访问控制

---

**最后更新：** 2026-04-06  
**文档版本：** v1.0.0
