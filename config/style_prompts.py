"""
样式风格提示词配置
包含16种风格的专用提示词（中文和英文版本）
"""

# 通用可读性保障要求（中文）
READABILITY_REQUIREMENT_ZH = """
【重要：可读性保障】
- 确保文字与背景有足够的对比度（至少4.5:1）
- 避免浅色文字配浅色背景，或深色文字配深色背景
- 所有正文文字必须清晰可读，字号不小于1em
- 测试配色方案在不同设备上的可读性
"""

# 通用可读性保障要求（英文）
READABILITY_REQUIREMENT_EN = """
【Important: Readability Guarantee】
- Ensure sufficient contrast between text and background (at least 4.5:1)
- Avoid light text on light backgrounds or dark text on dark backgrounds
- All body text must be clearly readable, font size not less than 1em
- Test color schemes for readability on different devices
"""

# 中文样式风格提示词
STYLE_PROMPTS_ZH = {
    "auto": """请根据文章内容自动判断最适合的视觉风格，并应用该风格的HTML和CSS设计。
考虑因素包括：
- 文章主题和 tone
- 目标受众
- 内容类型（技术、生活、商业等）
选择最能提升阅读体验的风格。

【重要：可读性保障】
- 确保文字与背景有足够的对比度（至少4.5:1）
- 避免浅色文字配浅色背景，或深色文字配深色背景
- 所有正文文字必须清晰可读，字号不小于1em
- 测试配色方案在不同设备上的可读性""",

    "default": """请将文章内容格式化为美观的HTML页面，遵循以下设计规范：

【整体布局】
- 使用响应式设计，最大宽度900px，居中显示
- 添加适当的内边距和外边距
- 确保移动端友好

【标题设计】
- 主标题使用渐变色或醒目颜色
- 字体大小2.2-2.8em，加粗
- 居中对齐，添加适当间距

【段落样式】
- 每个段落用独立的<p>标签包裹
- 行高1.7-1.9，字号1.1-1.2em
- 添加左侧装饰条或背景色块
- 段间距18-25px

【视觉元素】
- 为关键信息添加高亮样式（背景色或边框）
- 适当使用emoji图标增强可读性
- 引用内容使用特殊样式（引用框或大引号）

【底部标识】
- 添加优雅的底部卡片
- 使用渐变背景
- 包含"✨ powered by 深表美文"文字
- 添加悬停动画效果

【色彩方案】
- 主色调：蓝紫色系 (#667eea, #764ba2)
- 辅助色：温暖色系
- 背景：浅灰或白色渐变
- 文字：深灰色系保证可读性

【交互效果】
- 卡片悬停时轻微上浮
- 按钮有缩放和阴影变化
- 平滑过渡动画（0.3-0.5s）

【重要：可读性保障】
- 确保文字与背景有足够的对比度（至少4.5:1）
- 避免浅色文字配浅色背景，或深色文字配深色背景
- 所有正文文字必须清晰可读，字号不小于1em
- 测试配色方案在不同设备上的可读性

请生成完整的HTML文档，包含<head>和<body>，所有CSS使用内联<style>标签。""",

    "minimalist": """请使用极简主义风格格式化文章：

【核心特征】
- 极致的简洁和留白
- 纯黑白灰配色
- 无多余装饰元素
- 专注于内容本身

【色彩方案】
- 背景：纯白 (#ffffff) 或极浅灰 (#fafafa)
- 主文字：深灰 (#333333)
- 次要文字：中灰 (#666666)
- 强调色：单一accent色（如黑色或深蓝）
- 避免使用彩色和渐变

【排版设计】
- 超大留白（padding/margin 60-100px）
- 单栏布局，最大宽度700-800px
- 标题字重300-400（轻量）
- 正文字重400，行高1.8-2.0
- 字号层次分明但不夸张

【元素简化】
- 不使用卡片边框和阴影
- 不使用装饰性图标
- 分隔线使用细线（1px）或省略
- 引用使用简单的左侧竖线
- 避免任何花哨效果

【交互极简】
- 悬停效果微妙或无
- 无动画或极简单淡入
- 按钮使用纯文本或极简边框
- 聚焦于内容阅读体验

【重要：可读性保障】
- 确保文字与背景有足够的对比度（至少4.5:1）
- 避免浅色文字配浅色背景，或深色文字配深色背景
- 所有正文文字必须清晰可读，字号不小于1em
- 测试配色方案在不同设备上的可读性

生成完整HTML，体现少即是多的设计理念。""",

    "neon_glass": """请使用霓虹玻璃态设计风格格式化文章：

【核心特征】
- 深色背景 (#0a0e27) 配合动态渐变光晕
- 毛玻璃效果卡片 (backdrop-filter: blur(20px))
- 霓虹发光边框和文字
- 粒子动画背景效果

【色彩方案】
- 主色：紫蓝渐变 (#667eea → #764ba2 → #f093fb)
- 强调色：霓虹粉 (#f5576c)
- 文字：白色带发光效果
- 半透明背景 rgba(255,255,255,0.05-0.15)

【卡片设计】
- 圆角24px，半透明背景
- 悬停时上浮10px并放大
- 流光扫过动画效果
- 添加彩色标签徽章

【特效】
- 标题使用渐变文字+光晕
- 背景添加浮动粒子（JavaScript生成）
- 卡片角落添加装饰性光效
- 平滑的3D变换效果

【重要：可读性保障】
- 确保文字与背景有足够的对比度（至少4.5:1）
- 避免浅色文字配浅色背景，或深色文字配深色背景
- 所有正文文字必须清晰可读，字号不小于1em
- 测试配色方案在不同设备上的可读性

生成完整HTML，所有样式内联，包含粒子动画脚本。""",

    "magazine_gradient": """请使用杂志渐变风格格式化文章：

【核心特征】
- 温暖渐变背景 (橙色→粉色 #ffecd2 → #fcb69f)
- 浮动几何装饰图形
- 杂志式卡片布局
- 大号编号和水印

【色彩方案】
- 背景：温暖渐变 (#ffecd2 → #fcb69f)
- 卡片：纯白背景 + 顶部彩色条
- 强调色：珊瑚红 (#ff6b6b)、青绿 (#4ecdc4)
- 文字：深灰 (#2d3436)

【卡片设计】
- 圆角30px，白色背景
- 右上角大号半透明编号 (01, 02, 03...)
- 顶部8px彩色渐变条
- 悬停时旋转-1度并上浮

【排版特色】
- Issue Badge 标签
- 下划线装饰标题
- 大型引用框（紫色渐变背景）
- 荧光笔高亮效果

【重要：可读性保障】
- 确保文字与背景有足够的对比度（至少4.5:1）
- 避免浅色文字配浅色背景，或深色文字配深色背景
- 所有正文文字必须清晰可读，字号不小于1em
- 测试配色方案在不同设备上的可读性

生成完整HTML，包含浮动背景动画。""",

    "cyberpunk_neon": """请使用赛博朋克霓虹风格格式化文章：

【核心特征】
- 深色科技背景 (#0f0f23)
- 网格线背景图案
- CRT扫描线效果
- 霓虹发光文字和边框

【色彩方案】
- 主色：青色霓虹 (#00ffff)
- 辅色：品红霓虹 (#ff00ff)
- 警告色：绿色终端 (#00ff00)
- 背景：深蓝黑 (#0f0f23)

【HUD卡片设计】
- 切角多边形边框 (clip-path)
- 四角装饰标记
- 青色发光边框
- 悬停时边框变彩虹渐变

【特效】
- 标题故障艺术效果 (glitch animation)
- 数据流装饰文字（垂直排列）
- 终端风格引用框（等宽字体）
- 霓虹按钮带光晕

【字体】
- 标题：大写、字母间距加宽
- 数据流：Courier New 等宽字体
- 科技感、未来感

【重要：可读性保障】
- 确保文字与背景有足够的对比度（至少4.5:1）
- 避免浅色文字配浅色背景，或深色文字配深色背景
- 所有正文文字必须清晰可读，字号不小于1em
- 测试配色方案在不同设备上的可读性

生成完整HTML，包含网格背景和扫描线效果。""",

    "minimalist_timeline": """请使用极简主义时间线风格格式化文章：

【核心特征】
- 黑白极简配色
- 中央时间线布局
- 大量留白
- 优雅排版

【色彩方案】
- 背景：浅灰渐变 (#fafafa → #f0f0f0)
- 主色：纯黑 (#1a1a1a)
- 辅色：中灰 (#666)
- 卡片：纯白背景

【时间线设计】
- 中央垂直线（渐变透明度）
- 左右交替卡片布局
- 圆形节点标记（黑色+白边）
- 移动端改为单侧布局

【卡片样式】
- 简洁白色卡片
- 微妙阴影 (0 10px 40px rgba(0,0,0,0.05))
- 悬停时上浮10px
- 无多余装饰

【排版】
- 超大标题（字重300）
- 细线分隔符
- 大型引用区块（黑色背景）
- 下划线强调文字

【重要：可读性保障】
- 确保文字与背景有足够的对比度（至少4.5:1）
- 避免浅色文字配浅色背景，或深色文字配深色背景
- 所有正文文字必须清晰可读，字号不小于1em
- 测试配色方案在不同设备上的可读性

生成完整HTML，注重留白和呼吸感。""",

    "gradient_glass": """请使用渐变玻璃态风格格式化文章：

【核心特征】
- 紫色渐变背景 (#667eea → #764ba2)
- 流体动画背景
- 玻璃态卡片 (glassmorphism)
- 3D标题效果

【色彩方案】
- 背景：紫蓝到紫粉渐变
- 卡片：rgba(255,255,255,0.15) + backdrop-filter
- 强调：白色文字带阴影
- 徽章：半透明白色

【玻璃态卡片】
- backdrop-filter: blur(20px)
- 半透明边框 rgba(255,255,255,0.3)
- 径向渐变光晕效果
- 悬停时放大+上浮

【特效】
- 标题3D浮动动画（rotateX/Y）
- 背景流体运动（15s循环）
- 图标脉冲动画
- 渐变按钮光泽扫过

【布局】
- 响应式网格（auto-fit）
- 大型中心引用框
- 徽章标签系统

【重要：可读性保障】
- 确保文字与背景有足够的对比度（至少4.5:1）
- 避免浅色文字配浅色背景，或深色文字配深色背景
- 所有正文文字必须清晰可读，字号不小于1em
- 测试配色方案在不同设备上的可读性

生成完整HTML，包含流体背景动画。""",

    "bold_waves": """请使用大胆波浪风格格式化文章：

【核心特征】
- 鲜艳红色背景 (#ff6b6b)
- SVG波浪动画背景
- 大胆的白色卡片
- 强烈的视觉对比

【色彩方案】
- 背景：活力红 (#ff6b6b)
- 卡片：纯白 (rgba(255,255,255,0.95))
- 强调：红色文字 (#ff6b6b)
- 文字：深灰 (#333)

【波浪背景】
- 多层SVG波浪（3层）
- 不同透明度和速度
- 持续水平移动动画
- 营造流动感

【卡片设计】
- 圆角20px
- 右上角三角形装饰
- 悬停时右移20px+放大
- 强阴影效果

【排版】
- 超粗标题（字重900）
- 白色分隔线
- 大型白色引用框
- 红色下划线强调

【重要：可读性保障】
- 确保文字与背景有足够的对比度（至少4.5:1）
- 避免浅色文字配浅色背景，或深色文字配深色背景
- 所有正文文字必须清晰可读，字号不小于1em
- 测试配色方案在不同设备上的可读性

生成完整HTML，包含SVG波浪动画。""",

    "space_cosmic": """请使用太空宇宙风格格式化文章：

【核心特征】
- 深空背景 (#1a1a2e)
- 闪烁星星动画
- 轨道环旋转动画
- 宇宙渐变卡片

【色彩方案】
- 背景：深空蓝 (#1a1a2e → #090a0f)
- 主色：紫蓝渐变 (#667eea → #764ba2)
- 强调：粉色 (#f093fb)
- 星星：白色闪烁

【星空背景】
- JavaScript生成100颗星星
- 随机位置和闪烁延迟
- 3秒闪烁周期
- 营造深邃感

【轨道动画】
- 中央圆形轨道环
- 🦞 emoji沿轨道旋转
- 20秒完整旋转
- counter-rotate保持正向

【卡片设计】
- conic-gradient旋转光晕
- 圆形图标容器（渐变背景）
- 悬停时显示完整光晕
- 太空科技感

【重要：可读性保障】
- 确保文字与背景有足够的对比度（至少4.5:1）
- 避免浅色文字配浅色背景，或深色文字配深色背景
- 所有正文文字必须清晰可读，字号不小于1em
- 测试配色方案在不同设备上的可读性

生成完整HTML，包含星空生成脚本和轨道动画。""",

    "swiss_grid": """请使用瑞士网格风格格式化文章：

【核心特征】
- 不对称布局
- 12列网格系统
- 粗体排版
- 黑白对比强烈

【色彩方案】
- 背景：浅灰 (#f8f9fa)
- 主色：深灰蓝 (#2c3e50)
- 卡片：纯白
- 文字：深灰 (#2c3e50, #555)

【网格布局】
- 12列网格系统
- 不对称头部（1:2比例）
- 大小组合卡片（7:5, 5:7, 12）
- 左侧5px黑色装饰条

【排版特色】
- 年份徽章（黑色方块）
- 超粗标题（字重900）
- 双实线分隔符
- 负字间距标题

【卡片交互】
- 悬停时装饰条变宽（5px→10px）
- 上浮8px
- 阴影加深
- 简洁专业

【重要：可读性保障】
- 确保文字与背景有足够的对比度（至少4.5:1）
- 避免浅色文字配浅色背景，或深色文字配深色背景
- 所有正文文字必须清晰可读，字号不小于1em
- 测试配色方案在不同设备上的可读性

生成完整HTML，采用严格的网格系统。""",

    "handdrawn_notes": """请使用手绘便签风格格式化文章：

【核心特征】
- 温暖渐变背景
- 便签纸卡片
- 胶带固定效果
- 轻微旋转角度

【色彩方案】
- 背景： peach渐变 (#ffecd2 → #fcb69f)
- 卡片：纯白便签
- 强调：橙色 (#e17055)
- 文字：深灰 (#2d3436)

【便签设计】
- 小圆角（5px）
- 顶部胶带圆圈（伪元素）
- 交替旋转角度（±2deg）
- 悬停时回正+放大

【胶带效果】
- 40px圆形胶带
- 半透明黑色
- 内阴影模拟立体感
- 固定在卡片顶部

【排版】
- 手绘风格下划线
- 荧光笔高亮（黄色）
- 居中大号引用框
- 倾斜贴纸按钮

【重要：可读性保障】
- 确保文字与背景有足够的对比度（至少4.5:1）
- 避免浅色文字配浅色背景，或深色文字配深色背景
- 所有正文文字必须清晰可读，字号不小于1em
- 测试配色方案在不同设备上的可读性

生成完整HTML，营造温馨手账感。""",

    "dark_luxury": """请使用暗黑奢华风格格式化文章：

【核心特征】
- 纯黑背景 (#0a0a0a)
- 动态渐变背景（低透明度）
- 超大字体标题
- 分屏面板布局

【色彩方案】
- 背景：纯黑 (#0a0a0a)
- 渐变：多彩但透明度15%
- 文字：纯白 + 灰色
- 强调：白色发光

【动态背景】
- 四色渐变（橙、粉、蓝、青）
- 400%背景尺寸
- 15秒位置循环
- 营造奢华动感

【分屏面板】
- 无边框分隔
- 右侧大号水印数字
- 悬停时背景微亮
- 简洁高级

【排版】
- 超大标题（8em，clamp）
- 文字发光动画
- 全宽引用区域
- 极简底部按钮

【重要：可读性保障】
- 确保文字与背景有足够的对比度（至少4.5:1）
- 避免浅色文字配浅色背景，或深色文字配深色背景
- 所有正文文字必须清晰可读，字号不小于1em
- 测试配色方案在不同设备上的可读性

生成完整HTML，强调奢华感和空间感。""",

    "pastel_soft": """请使用柔和粉彩风格格式化文章：

【核心特征】
- 柔和渐变背景（青→粉）
- 圆角卡片（30px）
- 圆形emoji容器
- 温和配色

【色彩方案】
- 背景：#a8edea → #fed6e3
- 主色：紫色 (#6c5ce7)
- 卡片：纯白
- 强调：渐变青粉

【圆角设计】
- 卡片圆角30px
- emoji圆形容器（渐变背景）
- 引用框左侧紫色边框
- 药丸形按钮

【卡片特效】
- 悬停时旋转2度+上浮
- 渐变背景淡入
- 柔和阴影
- 流畅动画

【排版】
- 轻量标题（字重300）
- 渐变分隔线
- 左侧边框引用
- 柔和高亮背景

【重要：可读性保障】
- 确保文字与背景有足够的对比度（至少4.5:1）
- 避免浅色文字配浅色背景，或深色文字配深色背景
- 所有正文文字必须清晰可读，字号不小于1em
- 测试配色方案在不同设备上的可读性

生成完整HTML，营造温柔舒适感。""",

    "brutalist_bold": """请使用粗野主义风格格式化文章：

【核心特征】
- 纯黑白对比
- 粗黑边框（4-5px）
- 硬阴影（无模糊）
- 原始直接的设计

【色彩方案】
- 背景：纯白 (#fff)
- 边框/阴影：纯黑 (#000)
- 文字：纯黑
- 无渐变、无圆角

【粗野卡片】
- 4px黑色边框
- 8px硬阴影（offset 8px 8px）
- 左上角黑色编号徽章
- 悬停时位移-4px，阴影变大

【头部设计】
- 双层边框效果
- 伪元素创建偏移背景
- 全大写标题
- 强烈视觉冲击

【交互】
- 悬停时卡片位移
- 阴影从8px增至12px
- 按钮反色效果
- 直接、粗暴

【重要：可读性保障】
- 确保文字与背景有足够的对比度（至少4.5:1）
- 避免浅色文字配浅色背景，或深色文字配深色背景
- 所有正文文字必须清晰可读，字号不小于1em
- 测试配色方案在不同设备上的可读性

生成完整HTML，体现粗野主义美学。""",

    "kawaii_bubbles": """请使用可爱气泡风格格式化文章：

【核心特征】
- 粉色渐变背景
- 气泡状卡片
- 心跳动画
- 超可爱设计

【色彩方案】
- 背景：#ff9a9e → #fecfef
- 主色：粉红 (#fd79a8)
- 卡片：纯白
- 强调：黄橙渐变

【气泡卡片】
- 大圆角（30px）
- 底部小圆点装饰（伪元素）
- 粉色阴影
- 悬停时弹跳放大

【爱心元素】
- 标题下方心跳emoji
- 1.5秒心跳动画
- 引用框顶部爱心
- 粉色系贯穿

【排版】
- 阴影文字效果
- 圆润高亮背景
- 可爱语气（～符号）
- 双层阴影按钮

【重要：可读性保障】
- 确保文字与背景有足够的对比度（至少4.5:1）
- 避免浅色文字配浅色背景，或深色文字配深色背景
- 所有正文文字必须清晰可读，字号不小于1em
- 测试配色方案在不同设备上的可读性

生成完整HTML，充满少女心和可爱感。""",

    "newspaper_classic": """请使用报纸排版风格格式化文章：

【核心特征】
- 经典报纸布局
- 双栏分栏（column-count）
- Georgia衬线字体
- 双线分隔符

【色彩方案】
- 背景：浅灰 (#f5f5f5)
- 卡片：纯白
- 文字：黑色/深灰
- 引用：黑底白字

【报纸头部】
- 日期标签（大写）
- Georgia字体标题
- 斜体副标题
- 双线底部分隔

【分栏布局】
- column-count: 2
- column-gap: 50px
- column-rule分隔线
- 跨栏引用框

【卡片样式】
- 细边框（1px #ddd）
- 底部边框标题
- 两端对齐文本
- 黄色高亮标记

【排版】
- 衬线字体（Georgia）
- 传统报纸感
- 专业严肃
- 引用框黑底白字

【重要：可读性保障】
- 确保文字与背景有足够的对比度（至少4.5:1）
- 避免浅色文字配浅色背景，或深色文字配深色背景
- 所有正文文字必须清晰可读，字号不小于1em
- 测试配色方案在不同设备上的可读性

生成完整HTML，重现经典报纸阅读体验。""",

    "geometric_modern": """请使用几何现代风格格式化文章：

【核心特征】
- 深蓝背景 (#0f3460)
- 浮动几何图形
- 渐变图标容器
- 现代简洁

【色彩方案】
- 背景：深蓝 (#0f3460)
- 强调：红 (#e94560)、绿 (#16c79a)、黄 (#f9a826)
- 卡片：半透明白
- 文字：浅灰白

【几何背景】
- 菱形、三角形、六边形
- 10%透明度
- 20秒浮动旋转动画
- 三个图形不同延迟

【卡片设计】
- 顶部渐变条（悬停展开）
- 圆角图标容器（渐变背景）
- 半透明背景+模糊
- 悬停时上浮+变亮

【排版】
- 渐变标题文字
- 渐变分隔线
- 左侧边框引用
- 渐变按钮

【重要：可读性保障】
- 确保文字与背景有足够的对比度（至少4.5:1）
- 避免浅色文字配浅色背景，或深色文字配深色背景
- 所有正文文字必须清晰可读，字号不小于1em
- 测试配色方案在不同设备上的可读性

生成完整HTML，包含几何图形动画。"""
}

# English style prompts
STYLE_PROMPTS_EN = {
    "auto": """Please automatically determine the most suitable visual style based on the article content and apply that style's HTML and CSS design.
Consider factors including:
- Article theme and tone
- Target audience
- Content type (technical, lifestyle, business, etc.)
Choose the style that best enhances the reading experience.

【Important: Readability Guarantee】
- Ensure sufficient contrast between text and background (at least 4.5:1)
- Avoid light text on light backgrounds or dark text on dark backgrounds
- All body text must be clearly readable, font size not less than 1em
- Test color schemes for readability on different devices""",

    "default": """Please format the article content into a beautiful HTML page, following these design specifications:

【Overall Layout】
- Use responsive design, max-width 900px, centered
- Add appropriate padding and margins
- Ensure mobile-friendly

【Title Design】
- Main title uses gradient or eye-catching colors
- Font size 2.2-2.8em, bold
- Center aligned with appropriate spacing

【Paragraph Style】
- Each paragraph wrapped in independent <p> tag
- Line height 1.7-1.9, font size 1.1-1.2em
- Add left decorative bar or background color block
- Paragraph spacing 18-25px

【Visual Elements】
- Add highlight styles for key information (background color or border)
- Appropriately use emoji icons to enhance readability
- Use special styles for quotes (quote box or large quotation marks)

【Footer Badge】
- Add elegant footer card
- Use gradient background
- Include "✨ powered by 深表美文" text
- Add hover animation effects

【Color Scheme】
- Primary: Blue-purple tones (#667eea, #764ba2)
- Secondary: Warm tones
- Background: Light gray or white gradient
- Text: Dark gray for readability

【Interactive Effects】
- Cards slightly float on hover
- Buttons have scale and shadow changes
- Smooth transition animations (0.3-0.5s)

Please generate complete HTML document with <head> and <body>, all CSS using inline <style> tags.""",

    "minimalist": """Please format the article using Minimalist style:

【Core Features】
- Ultimate simplicity and whitespace
- Pure black-white-gray color scheme
- No excessive decorative elements
- Focus on content itself

【Color Scheme】
- Background: Pure white (#ffffff) or very light gray (#fafafa)
- Primary text: Dark gray (#333333)
- Secondary text: Medium gray (#666666)
- Accent: Single accent color (black or dark blue)
- Avoid colors and gradients

【Typography Design】
- Large whitespace (padding/margin 60-100px)
- Single column layout, max-width 700-800px
- Title font-weight 300-400 (light)
- Body font-weight 400, line-height 1.8-2.0
- Clear hierarchy but not exaggerated

【Element Simplification】
- No card borders or shadows
- No decorative icons
- Dividers use thin lines (1px) or omit
- Quotes use simple left vertical line
- Avoid any fancy effects

【Minimal Interaction】
- Subtle or no hover effects
- No animations or very simple fade-in
- Buttons use plain text or minimal borders
- Focus on content reading experience

【Important: Readability Guarantee】
- Ensure sufficient contrast between text and background (at least 4.5:1)
- Avoid light text on light backgrounds or dark text on dark backgrounds
- All body text must be clearly readable, font size not less than 1em
- Test color schemes for readability on different devices

Generate complete HTML, embodying the 'less is more' design philosophy.""",

    "neon_glass": """Please format the article using Neon Glassmorphism design style:

【Core Features】
- Dark background (#0a0e27) with dynamic gradient halos
- Frosted glass effect cards (backdrop-filter: blur(20px))
- Neon glowing borders and text
- Particle animation background

【Color Scheme】
- Primary: Purple-blue gradient (#667eea → #764ba2 → #f093fb)
- Accent: Neon pink (#f5576c)
- Text: White with glow effect
- Semi-transparent backgrounds rgba(255,255,255,0.05-0.15)

【Card Design】
- Border radius 24px, semi-transparent background
- Float up 10px and scale on hover
- Flowing light sweep animation
- Add colorful badge tags

【Effects】
- Title uses gradient text + glow
- Background adds floating particles (JavaScript generated)
- Decorative light effects on card corners
- Smooth 3D transform effects

Generate complete HTML with all styles inline, including particle animation script.""",

    "magazine_gradient": """Please format the article using Magazine Gradient style:

【Core Features】
- Warm gradient background (orange→pink #ffecd2 → #fcb69f)
- Floating geometric decorative shapes
- Magazine-style card layout
- Large numbering and watermarks

【Color Scheme】
- Background: Warm gradient (#ffecd2 → #fcb69f)
- Cards: Pure white background + top colored stripe
- Accent: Coral red (#ff6b6b), Teal (#4ecdc4)
- Text: Dark gray (#2d3436)

【Card Design】
- Border radius 30px, white background
- Large semi-transparent numbering in top-right (01, 02, 03...)
- Top 8px colored gradient stripe
- Rotate -1 degree and float up on hover

【Typography Features】
- Issue Badge labels
- Underline decorated titles
- Large quote box (purple gradient background)
- Highlighter pen effect

Generate complete HTML with floating background animations.""",

    "cyberpunk_neon": """Please format the article using Cyberpunk Neon style:

【Core Features】
- Dark tech background (#0f0f23)
- Grid line background pattern
- CRT scanline effect
- Neon glowing text and borders

【Color Scheme】
- Primary: Cyan neon (#00ffff)
- Secondary: Magenta neon (#ff00ff)
- Warning: Green terminal (#00ff00)
- Background: Deep blue-black (#0f0f23)

【HUD Card Design】
- Clipped polygon borders (clip-path)
- Four corner decorative markers
- Cyan glowing borders
- Rainbow gradient border on hover

【Effects】
- Title glitch art effect (glitch animation)
- Data stream decorative text (vertical layout)
- Terminal-style quote box (monospace font)
- Neon buttons with glow

【Typography】
- Titles: Uppercase, wide letter spacing
- Data streams: Courier New monospace
- Tech feel, futuristic

Generate complete HTML with grid background and scanline effects.""",

    "minimalist_timeline": """Please format the article using Minimalist Timeline style:

【Core Features】
- Black and white minimalist color scheme
- Central timeline layout
- Abundant whitespace
- Elegant typography

【Color Scheme】
- Background: Light gray gradient (#fafafa → #f0f0f0)
- Primary: Pure black (#1a1a1a)
- Secondary: Medium gray (#666)
- Cards: Pure white background

【Timeline Design】
- Central vertical line (gradient opacity)
- Alternating left-right card layout
- Circular node markers (black + white border)
- Single-side layout on mobile

【Card Style】
- Clean white cards
- Subtle shadows (0 10px 40px rgba(0,0,0,0.05))
- Float up 10px on hover
- No excessive decorations

【Typography】
- Ultra-large titles (font-weight 300)
- Thin line dividers
- Large quote blocks (black background)
- Underlined emphasis text

Generate complete HTML, emphasizing whitespace and breathing room.""",

    "gradient_glass": """Please format the article using Gradient Glassmorphism style:

【Core Features】
- Purple gradient background (#667eea → #764ba2)
- Fluid animation background
- Glassmorphism cards
- 3D title effects

【Color Scheme】
- Background: Purple-blue to purple-pink gradient
- Cards: rgba(255,255,255,0.15) + backdrop-filter
- Accent: White text with shadows
- Badges: Semi-transparent white

【Glassmorphism Cards】
- backdrop-filter: blur(20px)
- Semi-transparent borders rgba(255,255,255,0.3)
- Radial gradient halo effects
- Scale up + float on hover

【Effects】
- Title 3D floating animation (rotateX/Y)
- Background fluid motion (15s cycle)
- Icon pulse animation
- Gradient button gloss sweep

【Layout】
- Responsive grid (auto-fit)
- Large central quote box
- Badge tag system

Generate complete HTML with fluid background animation.""",

    "bold_waves": """Please format the article using Bold Waves style:

【Core Features】
- Vibrant red background (#ff6b6b)
- SVG wave animation background
- Bold white cards
- Strong visual contrast

【Color Scheme】
- Background: Energetic red (#ff6b6b)
- Cards: Pure white (rgba(255,255,255,0.95))
- Accent: Red text (#ff6b6b)
- Text: Dark gray (#333)

【Wave Background】
- Multi-layer SVG waves (3 layers)
- Different opacity and speed
- Continuous horizontal movement animation
- Create flowing sensation

【Card Design】
- Border radius 20px
- Triangular decoration in top-right
- Move right 20px + scale on hover
- Strong shadow effects

【Typography】
- Ultra-bold titles (font-weight 900)
- White divider lines
- Large white quote boxes
- Red underlined emphasis

Generate complete HTML with SVG wave animations.""",

    "space_cosmic": """Please format the article using Space Cosmic style:

【Core Features】
- Deep space background (#1a1a2e)
- Twinkling star animations
- Orbit ring rotation animation
- Cosmic gradient cards

【Color Scheme】
- Background: Deep space blue (#1a1a2e → #090a0f)
- Primary: Purple-blue gradient (#667eea → #764ba2)
- Accent: Pink (#f093fb)
- Stars: White twinkling

【Starfield Background】
- JavaScript generates 100 stars
- Random positions and twinkle delays
- 3-second twinkle cycle
- Create depth sensation

【Orbit Animation】
- Central circular orbit ring
- 🦞 emoji rotates along orbit
- 20-second full rotation
- counter-rotate to keep upright

【Card Design】
- conic-gradient rotating glow
- Circular icon containers (gradient background)
- Show full glow on hover
- Space tech feel

Generate complete HTML with star generation script and orbit animation.""",

    "swiss_grid": """Please format the article using Swiss Grid style:

【Core Features】
- Asymmetric layout
- 12-column grid system
- Bold typography
- Strong black-white contrast

【Color Scheme】
- Background: Light gray (#f8f9fa)
- Primary: Dark gray-blue (#2c3e50)
- Cards: Pure white
- Text: Dark gray (#2c3e50, #555)

【Grid Layout】
- 12-column grid system
- Asymmetric header (1:2 ratio)
- Combined size cards (7:5, 5:7, 12)
- Left 5px black decorative stripe

【Typography Features】
- Year badges (black squares)
- Ultra-bold titles (font-weight 900)
- Double solid line dividers
- Negative letter-spacing titles

【Card Interaction】
- Decorative stripe widens on hover (5px→10px)
- Float up 8px
- Shadow deepens
- Clean and professional

Generate complete HTML using strict grid system.""",

    "handdrawn_notes": """Please format the article using Hand-drawn Notes style:

【Core Features】
- Warm gradient background
- Sticky note cards
- Tape attachment effects
- Slight rotation angles

【Color Scheme】
- Background: peach gradient (#ffecd2 → #fcb69f)
- Cards: Pure white notes
- Accent: Orange (#e17055)
- Text: Dark gray (#2d3436)

【Note Design】
- Small border radius (5px)
- Top tape circle (pseudo-element)
- Alternating rotation angles (±2deg)
- Return to normal + scale on hover

【Tape Effect】
- 40px circular tape
- Semi-transparent black
- Inner shadow for 3D effect
- Fixed at card top

【Typography】
- Hand-drawn style underlines
- Highlighter pen highlights (yellow)
- Centered large quote box
- Tilted sticker buttons

Generate complete HTML, creating warm journal feel.""",

    "dark_luxury": """Please format the article using Dark Luxury style:

【Core Features】
- Pure black background (#0a0a0a)
- Dynamic gradient background (low opacity)
- Ultra-large font titles
- Split-screen panel layout

【Color Scheme】
- Background: Pure black (#0a0a0a)
- Gradient: Multi-color but 15% opacity
- Text: Pure white + gray
- Accent: White glow

【Dynamic Background】
- Four-color gradient (orange, pink, blue, cyan)
- 400% background size
- 15-second position cycle
- Create luxurious dynamics

【Split Panels】
- Borderless separation
- Large watermark numbers on right
- Background brightens on hover
- Simple and premium

【Typography】
- Ultra-large titles (8em, clamp)
- Text glow animation
- Full-width quote areas
- Minimal footer buttons

Generate complete HTML, emphasizing luxury and spatial sense.""",

    "pastel_soft": """Please format the article using Pastel Soft style:

【Core Features】
- Soft gradient background (cyan→pink)
- Rounded cards (30px)
- Circular emoji containers
- Gentle color scheme

【Color Scheme】
- Background: #a8edea → #fed6e3
- Primary: Purple (#6c5ce7)
- Cards: Pure white
- Accent: Gradient cyan-pink

【Rounded Design】
- Card border radius 30px
- Emoji circular containers (gradient background)
- Quote box left purple border
- Pill-shaped buttons

【Card Effects】
- Rotate 2 degrees + float on hover
- Gradient background fade-in
- Soft shadows
- Smooth animations

【Typography】
- Light titles (font-weight 300)
- Gradient dividers
- Left-border quotes
- Soft highlight backgrounds

Generate complete HTML, creating gentle comfortable feel.""",

    "brutalist_bold": """Please format the article using Brutalist Bold style:

【Core Features】
- Pure black-white contrast
- Thick black borders (4-5px)
- Hard shadows (no blur)
- Raw direct design

【Color Scheme】
- Background: Pure white (#fff)
- Borders/Shadows: Pure black (#000)
- Text: Pure black
- No gradients, no rounded corners

【Brutalist Cards】
- 4px black borders
- 8px hard shadows (offset 8px 8px)
- Black number badges in top-left
- Displace -4px on hover, shadow grows

【Header Design】
- Double border effect
- Pseudo-element creates offset background
- All-caps titles
- Strong visual impact

【Interaction】
- Cards displace on hover
- Shadows grow from 8px to 12px
- Button color inversion
- Direct, brutal

Generate complete HTML, embodying brutalist aesthetics.""",

    "kawaii_bubbles": """Please format the article using Kawaii Bubbles style:

【Core Features】
- Pink gradient background
- Bubble-like cards
- Heartbeat animation
- Super cute design

【Color Scheme】
- Background: #ff9a9e → #fecfef
- Primary: Pink (#fd79a8)
- Cards: Pure white
- Accent: Yellow-orange gradient

【Bubble Cards】
- Large border radius (30px)
- Bottom small dot decoration (pseudo-element)
- Pink shadows
- Bounce and scale on hover

【Heart Elements】
- Heartbeat emoji below title
- 1.5-second heartbeat animation
- Hearts on top of quote box
- Pink throughout

【Typography】
- Shadow text effects
- Rounded highlight backgrounds
- Cute tone (~ symbols)
- Double-shadow buttons

Generate complete HTML, full of girlish charm and cuteness.""",

    "newspaper_classic": """Please format the article using Newspaper Classic style:

【Core Features】
- Classic newspaper layout
- Two-column layout (column-count)
- Georgia serif fonts
- Double-line dividers

【Color Scheme】
- Background: Light gray (#f5f5f5)
- Cards: Pure white
- Text: Black/dark gray
- Quotes: Black background white text

【Newspaper Header】
- Date labels (uppercase)
- Georgia font titles
- Italic subtitles
- Double-line bottom divider

【Column Layout】
- column-count: 2
- column-gap: 50px
- column-rule divider line
- Cross-column quote boxes

【Card Style】
- Thin borders (1px #ddd)
- Bottom-border titles
- Justified text
- Yellow highlight markers

【Typography】
- Serif fonts (Georgia)
- Traditional newspaper feel
- Professional and serious
- Black background white text quotes

Generate complete HTML, recreating classic newspaper reading experience.""",

    "geometric_modern": """Please format the article using Geometric Modern style:

【Core Features】
- Dark blue background (#0f3460)
- Floating geometric shapes
- Gradient icon containers
- Modern and clean

【Color Scheme】
- Background: Dark blue (#0f3460)
- Accent: Red (#e94560), Green (#16c79a), Yellow (#f9a826)
- Cards: Semi-transparent white
- Text: Light gray-white

【Geometric Background】
- Diamonds, triangles, hexagons
- 10% opacity
- 20-second floating rotation animation
- Three shapes with different delays

【Card Design】
- Top gradient stripe (expands on hover)
- Rounded icon containers (gradient background)
- Semi-transparent background + blur
- Float up + brighten on hover

【Typography】
- Gradient title text
- Gradient dividers
- Left-border quotes
- Gradient buttons

Generate complete HTML with geometric shape animations."""
}


def get_style_prompt_zh(style_name):
    """获取中文样式风格提示词"""
    return STYLE_PROMPTS_ZH.get(style_name, STYLE_PROMPTS_ZH["default"])


def get_style_prompt_en(style_name):
    """获取英文样式风格提示词"""
    return STYLE_PROMPTS_EN.get(style_name, STYLE_PROMPTS_EN["default"])


def get_style_prompt(style_name, lang="zh"):
    """根据语言获取样式风格提示词"""
    if lang == "en":
        return get_style_prompt_en(style_name)
    else:
        return get_style_prompt_zh(style_name)
