# 额外要求开关功能说明

## 功能概述

将"额外要求"从常显输入框改为可折叠的开关设计，默认隐藏，用户点击按钮后才显示输入框。

---

## 优化目标

### Before（改进前）
- ❌ 页面元素过多，视觉负担重
- ❌ 所有选项同时展示，信息密度高
- ❌ "开始美化"按钮可能被挤到第二屏

### After（改进后）
- ✅ 默认隐藏非核心选项
- ✅ 页面更简洁，聚焦主要内容
- ✅ 按钮稳定在第一屏可见
- ✅ 按需展开，交互更优雅

---

## 界面设计

### 默认状态

```
┌─────────────────────────────────────┐
│ 📝 文章内容                         │
│ [大文本输入框]                      │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 🏷️ 文章标题（可选）                │
│ [单行输入框]                        │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 🎨 美化模式                         │
│ ○ 🔒 严格原文  ○ 📝 解读优化        │
│ ○ ✨ 扩写丰富                       │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 📋 添加额外要求                     │
│ [虚线边框按钮，浅灰色背景]          │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│        🎨 开始美化                  │
└─────────────────────────────────────┘
```

### 展开状态（点击后）

```
┌─────────────────────────────────────┐
│ 📋 收起额外要求                     │
│ [按钮变为紫色渐变，带图标]          │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 📋 额外要求（可选）                 │
│ [多行文本输入框]                    │
│ 例如：使用蓝色系配色...             │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│        🎨 开始美化                  │
└─────────────────────────────────────┘
```

---

## 交互设计

### 按钮状态

#### 1. **默认状态** - 诱导点击
- 文案："📋 添加额外要求"
- 样式：浅灰渐变背景 + 虚线边框
- 位置：美化模式下方，开始美化按钮上方

#### 2. **悬停状态** - 视觉反馈
- 背景色加深
- 边框颜色加深
- 轻微上移效果

#### 3. **激活状态** - 已展开
- 文案："📋 收起额外要求"
- 样式：紫色渐变背景 + 实线边框
- 输入框带滑入动画

### 动画效果

**slideDown 动画：**
```css
@keyframes slideDown {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
```

- 时长：0.3s
- 缓动：ease-out
- 效果：从上向下滑入，同时淡入

---

## 用户体验优势

### 1. **渐进式披露**
- 默认只展示核心功能
- 高级选项按需展开
- 降低初学者的认知负担

### 2. **视觉减负**
- 减少页面上的视觉元素
- 让"开始美化"按钮更显眼
- 提高页面的可读性

### 3. **操作流畅**
- 一键展开/收起
- 展开后自动聚焦到输入框
- 动画过渡自然流畅

### 4. **空间优化**
- 默认节省约 120px 高度
- 确保核心按钮在第一屏
- 移动端体验更好

---

## 技术实现

### HTML 结构

```html
<div class="form-group">
    <!-- 开关按钮 -->
    <button type="button" id="toggleExtraBtn" class="toggle-btn" onclick="toggleExtraRequirements()">
        📋 添加额外要求
    </button>
    
    <!-- 可折叠容器 -->
    <div id="extraRequirementsContainer" class="extra-requirements-container" style="display: none;">
        <label for="extraRequirements">额外要求（可选）</label>
        <textarea id="extraRequirements" placeholder="..." rows="3"></textarea>
    </div>
</div>
```

### JavaScript 逻辑

```javascript
function toggleExtraRequirements() {
    const container = document.getElementById('extraRequirementsContainer');
    const toggleBtn = document.getElementById('toggleBtn');
    
    if (container.style.display === 'none') {
        // 显示
        container.style.display = 'block';
        toggleBtn.innerHTML = '📋 收起额外要求';
        toggleBtn.classList.add('active');
        
        // 自动聚焦
        setTimeout(() => {
            document.getElementById('extraRequirements').focus();
        }, 100);
    } else {
        // 隐藏
        container.style.display = 'none';
        toggleBtn.innerHTML = '📋 添加额外要求';
        toggleBtn.classList.remove('active');
    }
}
```

### CSS 样式

**开关按钮：**
```css
.toggle-btn {
    width: 100%;
    padding: 12px;
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    color: #495057;
    border: 2px dashed #ced4da;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s;
}
```

**激活状态：**
```css
.toggle-btn.active {
    background: linear-gradient(135deg, #e0e7ff 0%, #f3e8ff 100%);
    border-color: #667eea;
    color: #667eea;
}
```

**容器动画：**
```css
.extra-requirements-container {
    margin-top: 15px;
    animation: slideDown 0.3s ease-out;
}
```

---

## 数据传递

### 前端发送

```javascript
// 即使输入框隐藏，仍然会获取值（可能为空）
const extraRequirements = document.getElementById('extraRequirements').value.trim();

// 发送到后端
fetch('/api/format-html', {
    method: 'POST',
    body: JSON.stringify({
        content: content,
        extra_requirements: extraRequirements  // 空字符串也表示无额外要求
    })
});
```

### 后端处理

```python
# 后端接收逻辑不变
extra_requirements = data.get('extra_requirements', '')

# 如果为空字符串，AI 不会收到额外要求指令
if extra_requirements and extra_requirements.strip():
    # 插入到提示词中
    extra_requirements_text = f"""
🔴 **用户的额外要求（必须严格遵守）**：
{extra_requirements}
"""
```

---

## 无障碍优化

### 键盘支持

- ✅ Tab 键可以聚焦到开关按钮
- ✅ Enter 或 Space 可以触发切换
- ✅ 展开后自动聚焦到输入框

### 屏幕阅读器

- ✅ 按钮文案清晰描述功能
- ✅ 状态变化时更新按钮文字
- ✅ 可以考虑添加 aria-expanded 属性

### 鼠标用户

- ✅ 明显的按钮样式
- ✅ 悬停时有视觉反馈
- ✅ 点击响应迅速

---

## 响应式设计

### 桌面端（>768px）

- 按钮宽度 100%，与上方表单对齐
- 三列美化模式横向排列
- 整体布局紧凑

### 移动端（≤768px）

- 按钮触控友好（高度 48px+）
- 美化模式单列排列
- 卡片内边距进一步缩小

---

## 性能优化

### 渲染性能

- ✅ 使用 CSS transform 而非 height 动画
- ✅ display: none 完全移除 DOM 渲染
- ✅ animation 使用 GPU 加速

### 代码性能

- ✅ 简单的 DOM 操作
- ✅ 无第三方依赖
- ✅ 事件处理函数复用

---

## 测试要点

### 功能测试

1. **开关切换**
   - ✅ 点击展开输入框
   - ✅ 再次点击收起
   - ✅ 按钮文字正确切换

2. **数据提交**
   - ✅ 展开并填写内容能正常提交
   - ✅ 未展开时提交（空值）也能正常工作
   - ✅ 展开后不填写直接提交也正常

3. **焦点管理**
   - ✅ 展开后自动聚焦到输入框
   - ✅ 可以用键盘操作

### 兼容性测试

- ✅ Chrome / Edge
- ✅ Firefox
- ✅ Safari
- ✅ 微信内置浏览器
- ✅ 移动端浏览器

---

## 数据分析建议

### 追踪指标

1. **点击率**
   - 多少用户会点击展开额外要求
   - 点击后有多少用户实际填写内容

2. **转化率**
   - 使用额外要求的用户 vs 不使用的用户
   - 对最终生成结果满意度的影响

3. **交互路径**
   - 用户通常在哪个阶段展开
   - 展开后平均停留时间

---

## 后续优化方向

### 可能的改进

1. **智能推荐**
   - 根据选择的模式推荐额外要求模板
   - 提供快捷选项（一键应用预设）

2. **记忆功能**
   - 记住用户上次使用的额外要求
   - 下次打开页面时自动填充

3. **折叠动画**
   - 添加收起时的向上滑动动画
   - 更流畅的过渡效果

4. **快捷键支持**
   - Alt+E 快速展开/收起
   - ESC 收起输入框

### 不建议的改动

❌ 移除开关，恢复常显  
❌ 默认展开  
❌ 过度复杂的动画效果  

---

## 修改记录

- **修改时间**: 2026-04-03
- **修改内容**: 将额外要求从常显改为可折叠开关
- **影响范围**: 
  - `static/formatter.html` - 添加开关按钮和折叠容器
  - `static/css/formater.css` - 添加开关样式和动画
  - `static/js/formatter.js` - 添加切换函数
- **兼容性**: 完全向后兼容，功能逻辑不变
- **性能影响**: 几乎为零，仅增加少量 CSS 和 JS
