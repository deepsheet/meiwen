"""
文本转 HTML API - Python 调用示例集合

这些示例展示了如何使用 Python 调用 /api/text-to-html 接口
"""

import requests
import json


# ==================== 基础示例 ====================

def example_basic():
    """基础用法：最简单的调用方式（返回 URL）"""
    print("=" * 60)
    print("示例 1: 基础用法 - 返回 URL")
    print("=" * 60)
    
    url = "http://localhost:8009/api/text-to-html"
    
    payload = {
        "content": "这是一段测试文本。\n\nAI 技术正在改变我们的生活。",
        "response_type": "url"  # 返回 URL 而不是 HTML
    }
    
    response = requests.post(url, json=payload, timeout=60)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 成功!")
        print(f"文章 ID: {result['article_id']}")
        print(f"标题: {result['title']}")
        print(f"访问 URL: {result['url']}")
        print(f"完整 URL: {result['full_url']}")
        print(f"💡 提示: 可以立即访问 {result['full_url']} 查看页面")
    else:
        print(f"❌ 失败: {response.json()}")


def example_return_url():
    """显式指定返回 URL 模式"""
    print("\n" + "=" * 60)
    print("示例 2: 显式指定 URL 模式")
    print("=" * 60)
    
    url = "http://localhost:8009/api/text-to-html"
    
    payload = {
        "content": "这是一段测试文本。\n\nAI 技术正在改变我们的生活。",
        "title": "测试 URL 模式",
        "response_type": "url"  # 关键参数：返回 URL 而不是 HTML
    }
    
    response = requests.post(url, json=payload, timeout=60)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 成功!")
        print(f"文章 ID: {result['article_id']}")
        print(f"标题: {result['title']}")
        print(f"访问 URL: {result['url']}")
        print(f"完整 URL: {result['full_url']}")
        print(f"💡 提示: 可以立即访问 {result['full_url']} 查看页面")
        
        # 注意：此模式下不返回 HTML 代码
        if 'html' not in result:
            print(f"ℹ️  此模式不返回 HTML 代码，只返回 URL")
    else:
        print(f"❌ 失败: {response.json()}")


def example_with_title():
    """指定标题（返回 URL）"""
    print("\n" + "=" * 60)
    print("示例 3: 指定标题")
    print("=" * 60)
    
    url = "http://localhost:5000/api/text-to-html"
    
    payload = {
        "content": "深度学习是机器学习的一个子领域...",
        "title": "深度学习入门指南",
        "response_type": "url"
    }
    
    response = requests.post(url, json=payload, timeout=60)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 成功! 标题: {result['title']}")
        print(f"🔗 访问链接: {result['full_url']}")


# ==================== 高级示例 ====================

def example_with_strategy():
    """使用不同的扩写模式"""
    print("\n" + "=" * 60)
    print("示例 4: 扩写模式对比")
    print("=" * 60)
    
    url = "http://localhost:5000/api/text-to-html"
    
    content = "人工智能是计算机科学的一个分支。它研究如何使计算机能够模拟人类的智能行为。"
    
    # 1. 严格模式
    print("\n【4.1】严格模式（strict）- 保持原文不变")
    payload_strict = {
        "content": content,
        "title": "AI 简介",
        "content_strategy": "strict",  # 严格模式
        "response_type": "url"
    }
    
    response = requests.post(url, json=payload_strict, timeout=60)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 成功 - {result['full_url']}")
    
    # 2. 解读优化模式
    print("\n【4.2】解读优化（interpret）- 优化表达逻辑")
    payload_interpret = {
        "content": content,
        "title": "AI 简介",
        "content_strategy": "interpret",  # 解读模式
        "response_type": "url"
    }
    
    response = requests.post(url, json=payload_interpret, timeout=60)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 成功 - {result['full_url']}")
    
    # 3. 扩写丰富模式
    print("\n【4.3】扩写丰富（expand）- 补充背景案例")
    payload_expand = {
        "content": content,
        "title": "AI 简介",
        "content_strategy": "expand",  # 扩写模式
        "response_type": "url"
    }
    
    response = requests.post(url, json=payload_expand, timeout=60)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 成功 - {result['full_url']}")


def example_with_requirements():
    """添加额外格式化需求"""
    print("\n" + "=" * 60)
    print("示例 5: 额外需求示例")
    print("=" * 60)
    
    url = "http://localhost:5000/api/text-to-html"
    
    # 示例 1: 颜色主题
    print("\n【5.1】指定颜色主题")
    payload1 = {
        "content": "产品特点：高性能、易使用、安全可靠",
        "title": "产品特性",
        "extra_requirements": "使用绿色主题，用卡片展示每个特点",
        "response_type": "url"
    }
    
    response = requests.post(url, json=payload1, timeout=60)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 成功 - {result['full_url']}")
    
    # 示例 2: 表格展示
    print("\n【5.2】表格展示数据")
    payload2 = {
        "content": "销售数据：\n华东地区\t50万\t增长40%\n华南地区\t30万\t增长32%\n华北地区\t20万\t增长28%",
        "title": "销售报告",
        "extra_requirements": "使用表格展示数据，紫色渐变主题，突出显示最高值",
        "response_type": "url"
    }
    
    response = requests.post(url, json=payload2, timeout=60)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 成功 - {result['full_url']}")
    
    # 示例 3: 视觉元素
    print("\n【5.3】添加视觉元素")
    payload3 = {
        "content": "步骤一：注册账号\n步骤二：完善资料\n步骤三：开始使用",
        "title": "使用指南",
        "extra_requirements": "使用编号列表，每个步骤用卡片展示，添加 emoji 图标",
        "response_type": "url"
    }
    
    response = requests.post(url, json=payload3, timeout=60)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 成功 - {result['full_url']}")


# ==================== 实际应用场景 ====================

def example_blog_post():
    """博客文章美化（返回 URL）"""
    print("\n" + "=" * 60)
    print("示例 6: 博客文章美化")
    print("=" * 60)
    
    url = "http://localhost:5000/api/text-to-html"
    
    blog_content = """
    # Python 编程最佳实践
    
    ## 代码规范
    
    良好的代码规范可以提高代码可读性和可维护性。
    
    ### 命名规范
    - 变量名使用小写字母和下划线
    - 类名使用驼峰命名法
    - 常量使用大写字母
    
    ### 注释规范
    - 为复杂逻辑添加注释
    - 使用文档字符串说明函数功能
    - 避免无意义的注释
    
    ## 性能优化
    
    1. 使用合适的数据结构
    2. 避免不必要的循环
    3. 利用缓存机制
    
    ## 总结
    
    遵循最佳实践可以写出更高质量的代码。
    """
    
    payload = {
        "content": blog_content,
        "title": "Python 编程最佳实践",
        "content_strategy": "interpret",
        "response_type": "url"
    }
    
    response = requests.post(url, json=payload, timeout=60)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 博客文章生成成功")
        print(f"🔗 访问链接: {result['full_url']}")
        print(f"📄 文章 ID: {result['article_id']}")


def example_product_doc():
    """产品文档生成（返回 URL）"""
    print("\n" + "=" * 60)
    print("示例 7: 产品文档")
    print("=" * 60)
    
    url = "http://localhost:5000/api/text-to-html"
    
    product_info = """
    产品名称：智能办公助手 v2.0
    
    核心功能：
    • 智能日程管理
    • 会议纪要自动生成
    • 任务分配与跟踪
    • 数据分析报告
    
    技术规格：
    - 支持平台：Windows, Mac, Linux
    - 语言支持：中文、英文、日文
    - 数据存储：云端加密存储
    - API 接口：RESTful API
    
    价格方案：
    基础版：免费
    专业版：¥99/月
    企业版：定制报价
    """
    
    payload = {
        "content": product_info,
        "title": "智能办公助手产品文档",
        "extra_requirements": "使用蓝色商务风格，用表格展示技术规格",
        "response_type": "url"
    }
    
    response = requests.post(url, json=payload, timeout=60)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 产品文档生成成功")
        print(f"🔗 访问链接: {result['full_url']}")
        print(f"📄 文章 ID: {result['article_id']}")


def example_data_report():
    """数据报告美化（返回 URL）"""
    print("\n" + "=" * 60)
    print("示例 8: 数据报告")
    print("=" * 60)
    
    url = "http://localhost:5000/api/text-to-html"
    
    report = """
    2026年第一季度销售报告
    
    总体业绩：
    销售额：¥1,250,000（同比增长 35%）
    订单数：3,580（同比增长 28%）
    客户满意度：92%
    
    区域表现：
    华东地区：¥520,000（增长 40%）
    华南地区：¥380,000（增长 32%）
    华北地区：¥350,000（增长 28%）
    
    产品线分析：
    产品 A：占比 45%，增长 38%
    产品 B：占比 35%，增长 30%
    产品 C：占比 20%，增长 35%
    
    下季度目标：
    1. 销售额突破 ¥150万
    2. 新客户增长 20%
    3. 推出 2 款新产品
    """
    
    payload = {
        "content": report,
        "title": "2026 Q1 销售报告",
        "content_strategy": "strict",
        "extra_requirements": "使用表格展示数据，紫色渐变主题",
        "response_type": "url"
    }
    
    response = requests.post(url, json=payload, timeout=60)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 数据报告生成成功")
        print(f"🔗 访问链接: {result['full_url']}")
        print(f"📄 文章 ID: {result['article_id']}")


# ==================== 错误处理示例 ====================

def example_error_handling():
    """完整的错误处理"""
    print("\n" + "=" * 60)
    print("示例 9: 错误处理")
    print("=" * 60)
    
    url = "http://localhost:5000/api/text-to-html"
    
    # 测试缺少必要参数
    payload = {
        "title": "只有标题，没有内容"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 400:
            print("✅ 正确捕获 400 错误")
            print(f"错误信息: {response.json()['message']}")
        elif response.status_code == 403:
            print("❌ IP 未授权")
            print(f"错误信息: {response.json()['message']}")
        elif response.status_code == 500:
            print("❌ 服务器错误")
            print(f"错误信息: {response.json()['message']}")
        else:
            print(f"⚠️ 未知状态码: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败，请检查服务是否启动")
    except Exception as e:
        print(f"❌ 未知错误: {str(e)}")


# ==================== 批量处理示例 ====================

def example_batch_processing():
    """批量处理多个文本（返回 URL）"""
    print("\n" + "=" * 60)
    print("示例 10: 批量处理")
    print("=" * 60)
    
    url = "http://localhost:5000/api/text-to-html"
    
    articles = [
        {"title": "文章一", "content": "这是第一篇文章的内容...", "response_type": "url"},
        {"title": "文章二", "content": "这是第二篇文章的内容...", "response_type": "url"},
        {"title": "文章三", "content": "这是第三篇文章的内容...", "response_type": "url"},
    ]
    
    success_count = 0
    fail_count = 0
    urls = []
    
    for i, article in enumerate(articles, 1):
        try:
            response = requests.post(url, json=article, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                urls.append(result['full_url'])
                success_count += 1
                print(f"✅ 文章 {i} 处理成功")
                print(f"   🔗 {result['full_url']}")
            else:
                fail_count += 1
                print(f"❌ 文章 {i} 处理失败")
                
        except Exception as e:
            fail_count += 1
            print(f"❌ 文章 {i} 异常: {str(e)}")
    
    print(f"\n批量处理完成: 成功 {success_count}, 失败 {fail_count}")
    if urls:
        print(f"\n生成的所有链接:")
        for i, url in enumerate(urls, 1):
            print(f"{i}. {url}")


# ==================== 主函数 ====================

if __name__ == "__main__":
    print("\n🚀 开始运行示例...\n")
    
    # 运行所有示例
    example_basic()
    example_return_url()  # 新增：返回 URL 模式
    example_with_title()
    example_with_strategy()
    example_with_requirements()
    example_blog_post()
    example_product_doc()
    example_data_report()
    example_error_handling()
    example_batch_processing()
    
    print("\n✨ 所有示例运行完成!\n")
