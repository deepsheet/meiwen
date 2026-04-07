# 内容处理策略使用说明

## 设计思路

### 为什么这样设计？

在早期的实现中，提示词采用固定的"一字不差"原则。但这带来一个问题：无论用户输入什么内容，AI 都只能严格遵循原文，无法根据实际场景灵活处理。

**现在的架构优势：**

1. **灵活性**：根据不同场景选择合适的策略
   - 正式文档 → `strict`（严格模式）
   - 内容优化 → `interpret`（解读模式）
   - 内容丰富 → `expand`（扩写模式）

2. **清晰的职责分离**
   - System prompt：定义通用角色和设计原则
   - User prompt：指定具体的内容处理策略

3. **向后兼容**：默认使用 `strict` 策略，老代码不受影响

4. **可扩展性**：未来可以轻松添加更多策略（如"翻译"、"摘要"等）

`llm_client.py` 中的 `format_article` 方法现在支持三种内容处理策略，可以根据不同场景选择合适的处理方式。

## 三种策略

### 1. strict（严格遵循原文）- **默认选项**

**特点：**
- ✅ 一字不差地保持原文 100% 完整
- ✅ 仅修正错别字、语法错误、标点符号错误
- ✅ 可以使用表格、列表等可视化形式呈现
- ❌ 绝对禁止添加任何原文没有的内容

**适用场景：**
- 正式文档格式化
- 法律文件、合同
- 新闻报道
- 用户明确要求保持原文不变的情况

**使用示例：**
```python
from src.llm_client import LLMClient

client = LLMClient()

# 方式 1：不传参数，默认使用 strict
html = client.format_article(content, title="文章标题")

# 方式 2：明确指定 strict 策略
html = client.format_article(content, title="文章标题", content_strategy="strict")
```

---

### 2. interpret（允许解读但不创造）

**特点：**
- ✅ 保持原文核心信息、数据、观点完整
- ✅ 可以调整段落顺序、优化表达逻辑
- ✅ 可以添加必要的过渡句、解释性文字
- ✅ 可以修正错别字、语法错误
- ❌ 禁止创造原文没有的新信息、新观点、新数据
- ❌ 禁止添加冗长的引言、结语、总结等画蛇添足的内容

**适用场景：**
- 技术文档优化
- 内容逻辑重组
- 增加可读性但不改变原意
- 需要让内容更流畅易懂

**使用示例：**
```python
from src.llm_client import LLMClient

client = LLMClient()

# 指定 interpret 策略
html = client.format_article(content, title="文章标题", content_strategy="interpret")
```

---

### 3. expand（允许合理扩写）

**特点：**
- ✅ 保持原文核心信息、数据、观点完整
- ✅ 可以补充背景信息、案例、数据支撑
- ✅ 可以对专业术语、复杂概念进行解释说明
- ✅ 可以调整段落顺序、添加小标题、优化逻辑流程
- ✅ 可以修正错别字、语法错误
- ❌ 禁止改变原文的核心观点和立场
- ❌ 禁止添加与原文主题无关的冗余内容

**适用场景：**
- 内容营销文章
- 科普文章
- 需要丰富内容的短文
- 需要增加背景说明的专业内容

**使用示例：**
```python
from src.llm_client import LLMClient

client = LLMClient()

# 指定 expand 策略
html = client.format_article(content, title="文章标题", content_strategy="expand")
```

---

## 策略对比表

| 特性 | strict | interpret | expand |
|------|--------|-----------|--------|
| 保持核心内容 | ✅ | ✅ | ✅ |
| 修正错误 | ✅ | ✅ | ✅ |
| 调整段落顺序 | ❌ | ✅ | ✅ |
| 添加过渡句 | ❌ | ✅ | ✅ |
| 补充背景信息 | ❌ | ❌ | ✅ |
| 添加案例/数据 | ❌ | ❌ | ✅ |
| 添加小标题 | ❌ | ✅ | ✅ |
| 解释专业术语 | ❌ | 有限度 | ✅ |

---

## 完整示例代码

```python
from src.llm_client import LLMClient

# 初始化客户端
client = LLMClient(model="deepseek-chat")

# 示例文章内容
content = """
千万人

这是一个简短的内容示例。
"""

title = "文章标题"

# 使用默认策略（strict）
html_strict = client.format_article(content, title=title)

# 使用解读策略（interpret）
html_interpret = client.format_article(content, title=title, content_strategy="interpret")

# 使用扩写策略（expand）
html_expand = client.format_article(content, title=title, content_strategy="expand")

# 保存结果
with open("strict.html", "w", encoding="utf-8") as f:
    f.write(html_strict)

with open("interpret.html", "w", encoding="utf-8") as f:
    f.write(html_interpret)

with open("expand.html", "w", encoding="utf-8") as f:
    f.write(html_expand)
```

---

## 注意事项

1. **默认策略是 `strict`**，确保向后兼容，不会影响现有代码
2. **策略参数是可选的**，如果不传则使用默认的严格模式
3. **所有策略都禁止**添加"内容完整性确认"等画蛇添足的文字
4. **所有策略都必须**包含底部标识"powered by 深表美文"
5. 选择策略时应根据实际业务需求和用户期望来决定

---

## 修改记录

- **修改时间**: 2026-04-03
- **修改内容**: 将固定的内容处理原则改为可选择的策略选项
- **影响范围**: `llm_client.py` 的 `format_article` 和 `_create_format_prompt` 方法
- **兼容性**: 完全向后兼容，默认行为与之前一致
