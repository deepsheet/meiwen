# 多语言支持使用说明

## 概述

深表美文系统现已支持完整的中英文多语言功能,包括:
- ✅ 前端页面界面翻译
- ✅ API 响应消息多语言
- ✅ LLM 提示词多语言
- ✅ 智能语言检测与持久化存储

## 功能特性

### 1. 语言检测优先级

系统按照以下优先级检测用户语言偏好:

1. **用户手动选择** - 通过首页右上角的语言切换器选择
2. **Cookie 存储** - 读取之前设置的 `language_preference` Cookie
3. **浏览器语言** - 检测浏览器的 `Accept-Language` 头部
4. **配置默认值** - 使用 `config.py` 中配置的 `DEFAULT_LANGUAGE`

### 2. 语言存储机制

- **Cookie**: `language_preference`,过期时间 365 天,用于后端读取
- **localStorage**: `userLanguage`,用于前端 UI 状态同步
- **自动同步**: 前后端语言设置自动保持一致

### 3. 支持的语言

目前支持:
- `zh` - 中文 (默认)
- `en` - 英文

未来可轻松扩展更多语言。

## 使用方法

### 前端页面切换语言

在首页或格式化页面的右上角,点击语言切换按钮:
- 点击 "中文" 切换到中文界面
- 点击 "English" 切换到英文界面

切换后:
1. 语言偏好保存到 localStorage
2. 调用后端 API 设置 Cookie
3. 页面自动刷新应用新语言

### 后端 API 设置语言

如果需要编程方式设置语言,可以调用:

```javascript
fetch('/api/set-language', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({language: 'en'})  // 'zh' 或 'en'
})
.then(response => response.json())
.then(data => {
    console.log('Language set:', data.language);
    window.location.reload();  // 刷新页面
});
```

### LLM 提示词自动适配

当用户选择不同语言时:
- 博客生成提示词自动使用对应语言
- 标题生成提示词自动使用对应语言  
- 文章格式化提示词自动使用对应语言
- 内容处理策略说明自动使用对应语言

这确保了 AI 生成的内容与用户选择的语言一致。

## 技术实现

### 文件结构

```
isheetmarketing/
├── config/
│   ├── config.py          # 添加 DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES
│   └── i18n.py            # 翻译字典和 LLM 提示词模板 (新建)
├── src/
│   ├── i18n.py            # 语言工具模块 (新建)
│   ├── llm_client.py      # 支持多语言提示词
│   ├── html_formatter.py  # 支持 language 参数
│   └── web_server.py      # 路由支持多语言
└── src/templates/
    ├── index.html         # 多语言首页
    └── formatter.html     # 多语言格式化页面
```

### 核心模块

#### 1. config/i18n.py

包含完整的翻译字典和 LLM 提示词模板:

```python
TRANSLATIONS = {
    'zh': {...},  # 中文翻译
    'en': {...}   # 英文翻译
}

LLM_PROMPTS = {
    'zh': {...},  # 中文提示词
    'en': {...}   # 英文提示词
}
```

#### 2. src/i18n.py

提供语言检测和翻译功能:

```python
# 从请求中获取语言偏好
lang = get_language_from_request()

# 获取翻译文本
text = get_translation('slogan', lang)

# 获取 LLM 提示词
prompt = get_llm_prompt('format_system', lang)

# 为响应设置语言 Cookie
response = create_language_response(response, lang)
```

#### 3. 模板文件

使用 Jinja2 模板语法:

```html
<title>{{ t('page_title') }}</title>
<h1>{{ t('brand_name') }}</h1>
<button>{{ t('btn_start_beautify') }}</button>
```

### 扩展现有功能

如需添加新功能的多语言支持:

1. **在 config/i18n.py 中添加翻译键**:
```python
TRANSLATIONS = {
    'zh': {
        'new_feature_title': '新功能标题',
        ...
    },
    'en': {
        'new_feature_title': 'New Feature Title',
        ...
    }
}
```

2. **在模板中使用**:
```html
<h2>{{ t('new_feature_title') }}</h2>
```

3. **在 API 响应中使用**:
```python
from src.i18n import get_translation

lang = get_language_from_request()
return jsonify({
    "message": get_translation('success_message', lang)
})
```

## 注意事项

### 1. 向后兼容

- 未设置语言偏好时,系统使用配置的默认语言 (中文)
- 现有功能不受影响,只是增加了多语言支持

### 2. 性能优化

- 翻译字典在模块加载时一次性读入内存
- 避免重复文件 I/O 操作

### 3. SEO 友好

- 每个页面都有正确的 `<html lang="{{ lang }}">` 属性
- 可为不同语言版本添加 hreflang 标签 (可选)

### 4. 扩展性

添加新语言只需:
1. 在 `config/config.py` 的 `SUPPORTED_LANGUAGES` 中添加语言代码
2. 在 `config/i18n.py` 中添加对应的翻译和提示词
3. 在前端添加语言切换按钮

例如添加日语支持:
```python
# config/config.py
SUPPORTED_LANGUAGES = ['zh', 'en', 'ja']

# config/i18n.py
TRANSLATIONS = {
    'zh': {...},
    'en': {...},
    'ja': {
        'page_title': '深表美文·テキスト美化ツール',
        ...
    }
}
```

## 测试验证

运行测试脚本验证多语言功能:

```bash
python debug/test_multilang.py
```

测试内容包括:
- ✅ 翻译字典完整性检查
- ✅ LLM 提示词完整性检查
- ✅ i18n 模块功能测试

## 常见问题

### Q: 为什么刷新页面后语言又变回中文了?

A: 请检查:
1. 浏览器是否禁用了 Cookie
2. localStorage 是否正常保存
3. 查看浏览器控制台是否有错误信息

### Q: API 返回的消息还是中文怎么办?

A: 确保:
1. Cookie 已正确设置 (`language_preference`)
2. 请求时携带了正确的 Cookie
3. 后端路由使用了 `get_language_from_request()`

### Q: 如何调试语言检测问题?

A: 可以在后端添加日志:
```python
from src.logger import logger

lang = get_language_from_request()
logger.info(f"Detected language: {lang}")
logger.info(f"Cookie: {request.cookies.get('language_preference')}")
logger.info(f"Accept-Language: {request.headers.get('Accept-Language')}")
```

## 总结

多语言功能已完全集成到系统中,用户可以:
- 🌐 在首页一键切换语言
- 💾 语言偏好持久化保存
- 🤖 AI 生成内容与选择语言一致
- 📱 所有页面都支持多语言显示

系统具备良好的扩展性,未来可以轻松添加更多语言支持。
