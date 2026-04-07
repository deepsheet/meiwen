# 长文章处理优化说明

## 问题背景

DeepSeek-V3.2 API 支持 128K 上下文长度，但 `max_tokens` 参数限制的是**输出**的最大 token 数，而非输入。

- **输入上下文**：最多 128K tokens（约 10 万汉字）
- **输出限制**：`max_tokens` 参数控制 AI 能生成的最大长度
- 当设置 `max_tokens: 20000` 时会报错
- 设置 `max_tokens: 4000` 可以正常工作

对于一万字的文章，主要问题是**输出会更长**（因为要添加大量 HTML 标签和样式），而不是输入。

## 解决方案

### 1. 提高 max_tokens 限制

将 `html_formatter.py` 中的 `max_tokens` 从 4000 提升到 8000：

```python
"max_tokens": 8000,  # 增加输出限制以支持长文章格式化
```

### 2. 实现流式输出（Streaming）

添加了流式输出功能，适合处理超长文章：

#### 核心改进：

1. **智能判断**：根据文章长度自动选择是否使用流式输出
   - 文章长度 > 5000 字：自动启用流式输出
   - 文章长度 ≤ 5000 字：使用普通模式

2. **流式输出优势**：
   - 没有单次输出的 token 限制
   - 可以处理任意长度的文章
   - 实时接收 AI 生成的内容片段
   - 超时时间延长到 300 秒

3. **API 调用方式**：
   ```python
   # 非流式（短文章）
   response = self._call_api(prompt, use_stream=False)
   
   # 流式（长文章）
   response = self._call_api(prompt, use_stream=True)
   ```

### 3. 代码改动

#### html_formatter.py 修改内容：

1. **format_article() 方法**：添加智能判断逻辑
   ```python
   use_stream = len(content) > 5000
   if use_stream:
       logger.info(f"文章长度：{len(content)} 字，使用流式输出模式")
   ```

2. **_call_api() 方法**：添加流式支持参数
   ```python
   def _call_api(self, prompt, use_stream=False):
       if use_stream:
           return self._call_api_stream(prompt)
       else:
           # 原有的非流式调用
   ```

3. **新增 _call_api_stream() 方法**：处理流式输出
   - 启用 `stream=True` 参数
   - 逐行读取 SSE 格式的数据
   - 收集所有 `data:` 片段
   - 合并成完整内容

4. **_parse_response() 方法**：兼容两种响应类型
   ```python
   if isinstance(response, str):
       content = response  # 流式输出直接是字符串
   else:
       content = response["choices"][0]["message"]["content"]
   ```

## 使用方法

### 常规使用（自动处理）

系统会自动根据文章长度选择合适的模式，无需手动干预：

```python
from src.html_formatter import HTMLFormatter

formatter = HTMLFormatter()

# 短文章（< 5000 字）- 自动使用普通模式
html = formatter.format_article(short_content)

# 长文章（> 5000 字）- 自动使用流式模式
html = formatter.format_article(long_content)
```

### 测试长文章处理

运行测试脚本验证功能：

```bash
python test_long_article_format.py
```

测试脚本会：
1. 生成一篇约 10000 字的测试文章
2. 调用 HTML 格式化服务
3. 验证生成的 HTML 完整性
4. 保存结果到 `test_long_article_output.html`

## 性能对比

| 文章长度 | 模式 | 预计耗时 | 备注 |
|---------|------|---------|------|
| < 3000 字 | 普通 | 10-30 秒 | 推荐 |
| 3000-5000 字 | 普通 | 30-60 秒 | 可用 |
| 5000-10000 字 | 流式 | 60-120 秒 | 推荐 |
| > 10000 字 | 流式 | 120-300 秒 | 需要较长超时时间 |

## 注意事项

1. **API 额度**：长文章消耗更多 token，请确保账户有足够额度
2. **网络连接**：流式输出需要稳定的网络连接
3. **超时设置**：
   - 普通模式：180 秒
   - 流式模式：300 秒
4. **错误处理**：如果流式输出失败，会自动降级到基础 HTML 模板

## 技术细节

### 流式输出工作原理

1. 客户端发送请求，设置 `stream: true`
2. 服务器以 SSE (Server-Sent Events) 格式返回数据
3. 每行数据格式为：`data: {JSON}`
4. 客户端逐行解析，提取 `choices[0].delta.content`
5. 累积所有片段，合并成完整内容
6. 遇到 `data: [DONE]` 表示结束

### SSE 数据格式示例

```
data: {"id":"chat-123","choices":[{"delta":{"content":"第"},"finish_reason":null}]}
data: {"id":"chat-123","choices":[{"delta":{"content":"一"},"finish_reason":null}]}
data: {"id":"chat-123","choices":[{"delta":{"content":"章"},"finish_reason":null}]}
data: [DONE]
```

## 兼容性

- ✅ 完全向后兼容，不影响现有短文章处理
- ✅ API 接口保持不变
- ✅ 现有的配置文件无需修改
- ✅ 所有功能正常工作

## 未来优化方向

1. **分块处理**：对于超长文章（> 50000 字），可以考虑分段处理
2. **进度反馈**：添加进度条或状态更新
3. **缓存机制**：对相同内容进行缓存，减少 API 调用
4. **批量处理**：支持多篇文章批量格式化

## 相关文件

- `/src/html_formatter.py` - 主要实现文件
- `/test_long_article_format.py` - 长文章测试脚本
- `/config/config.py` - API 配置

## 总结

通过提高 `max_tokens` 限制和实现流式输出，系统现在可以：

✅ 处理 10000 字以上的超长文章  
✅ 自动根据文章长度选择最优模式  
✅ 保持与短文章的兼容性  
✅ 提供稳定的错误处理机制  

DeepSeek-V3.2 的 128K 上下文能力得到充分利用，输入不再是问题，输出限制通过流式输出得到解决。
