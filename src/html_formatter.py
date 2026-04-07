#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HTML 格式化服务：将纯文本或简单 HTML 转换为具有丰富视觉效果的 HTML 文章
可独立使用，也可为博客生成器提供格式增强服务
"""

import sys
import os
import re
import requests
from config.config import CURRENT_MODEL
from src.llm_client import LLMClient
from src.logger import logger


class HTMLFormatter:
    """
    HTML 格式化服务类
    """
    
    # 页面底部标识的固定模板（公共变量）
    FOOTER_TEMPLATE = '''
    <!-- 页面底部标识 - 深表美文 -->
    <div style="text-align: center; margin-top: 60px; padding: 30px 0; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 16px;width: 100%;">
      <a href="{base_url}" target="_blank" style="text-decoration: none; color: #667eea; font-size: 16px; font-weight: 600; display: inline-flex; align-items: center; gap: 8px; transition: all 0.3s ease;" onmouseover="this.style.color='#764ba2'; this.style.transform='scale(1.05)'" onmouseout="this.style.color='#667eea'; this.style.transform='scale(1)'">
        🎨 <span>深表美文-文本转美页</span>
      </a>
    </div>
    '''
    
    def __init__(self, base_url=None, model_name=None, language=None):
        """
        初始化 HTML 格式化服务
        
        @param {str} base_url - 可选的域名配置，用于生成底部标识链接
        @param {str} model_name - 可选的模型名称，如果不提供则使用配置文件中的设置
        @param {str} language - 可选的语言代码，如果不提供则自动检测
        """
        # 🔴 动态域名支持：优先使用传入的参数，否则使用默认值
        self.base_url = base_url if base_url else "http://localhost:8009/beauty_html"
        # 🔴 使用统一的 LLM 客户端
        self.model_name = model_name if model_name else CURRENT_MODEL
        self.language = language
        self.llm_client = LLMClient(model_name=self.model_name, language=language)
        logger.info(f"HTMLFormatter 初始化完成，使用模型：{self.model_name}，语言：{language}")
    
    def get_footer_html(self, base_url=None):
        """
        获取页面底部标识 HTML
        
        @param {str} base_url - 网站首页链接，如果为 None 则使用默认值
        @return {str} - 底部标识 HTML
        """
        if base_url is None:
            base_url = self.base_url
        return self.FOOTER_TEMPLATE.format(base_url=base_url)
    
    def format_article(self, content, title=None, content_strategy="strict", style="auto", extra_requirements=None, include_download_button=False, article_id=None):
        """
        将文章内容转换为具有丰富视觉效果的 HTML
        
        @param {str} content - 文章内容（纯文本或简单 HTML）
        @param {str} title - 可选的文章标题
        @param {str} content_strategy - 内容处理策略："strict"(严格遵循原文), "interpret"(允许解读), "expand"(允许扩写)
        @param {str} style - 样式风格："auto"(自动匹配), "default"(默认风格), 或其他15种风格
        @param {str} extra_requirements - 额外的格式化要求
        @param {bool} include_download_button - 是否包含下载按钮（默认为 False）
        @param {str} article_id - 文章 ID（用于 SEO 结构化数据）
        @return {str} - 包含丰富格式的完整 HTML
        """
        try:
            logger.info(f"开始格式化文章，策略：{content_strategy}，样式：{style}，额外要求：{extra_requirements if extra_requirements else '(无)'}...")
            
            # 使用 LLMClient 进行文章格式化（已包含模板渲染）
            logger.info("使用 LLMClient 进行文章格式化...")
            formatted_html = self.llm_client.format_article(
                content, 
                title, 
                base_url=self.base_url, 
                content_strategy=content_strategy,
                style=style,
                extra_requirements=extra_requirements,
                article_id=article_id
            )
            
            # 🔴 如果需要包含下载按钮，则在底部标识前添加下载按钮
            if include_download_button:
                formatted_html = self._add_download_button_to_html(formatted_html)
            
            logger.info(f"文章格式化完成，HTML 长度：{len(formatted_html)}")
            return formatted_html
            
        except Exception as e:
            logger.error(f"文章格式化失败：{str(e)}")
            # 如果格式化失败，返回基础 HTML
            return self._create_fallback_html(content, title)
    
    def _call_api(self, prompt, use_stream=False):
        """
        调用 DeepSeek API
        
        @param {dict} prompt - API 请求的提示信息
        @param {bool} use_stream - 是否使用流式输出（处理超长内容）
        @return {dict|str} - API 响应（非流式）或完整内容（流式）
        """
        try:
            if use_stream:
                logger.info("使用流式输出模式处理长文章...")
                return self._call_api_stream(prompt)
            else:
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json=prompt,
                    timeout=180  # 增加超时时间到 180 秒
                )
                response.raise_for_status()
                return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"DeepSeek API 请求失败：{str(e)}")
            raise
    
    def _call_api_stream(self, prompt):
        """
        使用流式输出调用 DeepSeek API，适合处理超长内容
        
        @param {dict} prompt - API 请求的提示信息
        @return {str} - 完整的内容
        """
        try:
            # 启用流式输出
            prompt["stream"] = True
            # 注意：流式输出时不设置 max_tokens，让 AI 自然输出完成
            # max_tokens 在流式模式下可能导致截断，所以移除这个限制
            if "max_tokens" in prompt:
                del prompt["max_tokens"]
            
            logger.info("开始流式接收数据... (无 max_tokens 限制)")
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=prompt,
                timeout=600,  # 流式输出需要更长的超时时间（10 分钟）
                stream=True
            )
            response.raise_for_status()
            
            # 收集所有流式片段
            full_content = []
            chunk_count = 0
            error_count = 0  # 记录 JSON 解析错误次数
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data = line_str[6:]  # 移除 'data: ' 前缀
                        if data == '[DONE]':
                            break
                        try:
                            import json
                            chunk = json.loads(data)
                            content = chunk["choices"][0].get("delta", {}).get("content", "")
                            if content:
                                full_content.append(content)
                                chunk_count += 1
                                # 每接收 100 个片段记录一次日志
                                if chunk_count % 100 == 0:
                                    current_length = sum(len(c) for c in full_content)
                                    logger.info(f"已接收 {chunk_count} 个片段，当前长度：{current_length}")
                        except json.JSONDecodeError as e:
                            # JSON 解析失败时，尝试直接提取 content 字段
                            error_count += 1
                            logger.warning(f"JSON 解析失败 (第{error_count}次)，尝试备用方案... data: {data[:100]}...")
                            try:
                                # 备用方案：使用正则表达式提取 content
                                import re
                                match = re.search(r'"content":"([^"]*(?:\\"[^"]*)*)"', data)
                                if match:
                                    content = match.group(1).replace('\\"', '"')
                                    full_content.append(content)
                                    chunk_count += 1
                            except Exception as extract_error:
                                logger.error(f"备用方案也失败：{str(extract_error)}")
                                # 如果两种方法都失败，记录错误但继续处理后续内容
                                continue
            
            # 合并所有片段
            final_content = ''.join(full_content)
            logger.info(f"流式接收完成，共 {chunk_count} 个片段，总长度：{len(final_content)}")
            return final_content
            
        except Exception as e:
            logger.error(f"流式输出失败：{str(e)}")
            # 如果已经接收了部分内容，尝试返回已接收的内容
            if 'full_content' in locals() and full_content:
                partial_content = ''.join(full_content)
                logger.warning(f"返回已接收的部分内容，长度：{len(partial_content)}")
                return partial_content
            raise
    
    def _parse_response(self, response):
        """
        解析 API 响应获取格式化后的 HTML
        
        @param {dict|str} response - API 响应（非流式）或完整内容（流式）
        @return {str} - 解析后的 HTML 内容
        """
        try:
            # 如果是流式输出，response 直接是字符串
            if isinstance(response, str):
                content = response
            else:
                # 非流式输出，从 JSON 中提取
                content = response["choices"][0]["message"]["content"]
            
            # 清理可能的 markdown 代码块标记
            content = re.sub(r'^```html\s*', '', content)
            content = re.sub(r'```$', '', content)
            content = content.strip()
            
            # 检查 HTML 是否完整
            if not self._is_html_complete(content):
                logger.warning(f"检测到 HTML 不完整，尝试修复...")
                content = self._fix_incomplete_html(content)
            
            return content
        except (KeyError, IndexError) as e:
            logger.error(f"解析 API 响应失败：{str(e)}")
            logger.error(f"API 响应：{response}")
            raise
    
    def _add_download_button_to_html(self, html):
        """
        在 HTML 中添加下载按钮（直接插入到 body 开头）
        
        @param {str} html - HTML 内容
        @return {str} - 包含下载按钮的 HTML
        """
        import re
        
        # 查找 <body> 标签的位置
        body_match = re.search(r'<body[^>]*>', html, re.IGNORECASE)
        
        if not body_match:
            logger.warning("未找到 <body> 标签，无法添加下载按钮")
            return html
        
        body_end_pos = body_match.end()
        
        # 创建下载按钮 HTML（使用 CSS hover 代替 inline events 避免闪烁）
        download_button_html = '''
    <!-- 下载按钮 -->
    <style>
        #downloadBtn {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            background: rgba(102, 126, 234, 0.8);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            backdrop-filter: blur(10px);
        }
        #downloadBtn:hover {
            background: rgba(102, 126, 234, 1);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }
    </style>
    <button id="downloadBtn" onclick="downloadCurrentPage()" title="下载本网页到本地">
        📥 下载
    </button>
    
    <script>
        function downloadCurrentPage() {
            // 移除下载按钮元素及其样式
            const downloadBtn = document.getElementById('downloadBtn');
            if (downloadBtn) {
                downloadBtn.remove();
                // 移除相关的 style 标签
                const styles = document.querySelectorAll('style');
                styles.forEach(style => {
                    if (style.textContent.includes('#downloadBtn')) {
                        style.remove();
                    }
                });
            }
            
            // 创建一个 Blob 对象（使用移除按钮后的 HTML）
            const blob = new Blob([document.documentElement.outerHTML], { type: 'text/html;charset=utf-8' });
            
            // 创建下载链接
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            
            // 生成文件名（使用页面标题）
            const title = document.title || 'page';
            const filename = title.replace(/[^\\w\u4e00-\u9fff]/g, '_') + '.html';
            a.download = filename;
            
            // 触发下载
            document.body.appendChild(a);
            a.click();
            
            // 清理
            setTimeout(() => {
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }, 100);
        }
    </script>
'''
        
        # 在 <body> 标签后立即插入下载按钮
        result = html[:body_end_pos] + '\n' + download_button_html + html[body_end_pos:]
        
        logger.info("已添加下载按钮到 HTML（body 开头）")
        return result
    
    def _cleanup_duplicate_footers(self, html):
        """
        清理重复的底部标识，保留最后一个正确的版本
        
        @param {str} html - 包含重复底部标识的 HTML
        @return {str} - 清理后的 HTML
        """
        logger.info("开始清理重复的底部标识...")
        
        # 🔴 策略：找到最后一个底部标识，保留它及其后面的闭合标签
        footer_marker = '深表美文-文本转美页面'
        
        # 找到所有底部标识的位置
        footer_positions = []
        start = 0
        while True:
            pos = html.find(footer_marker, start)
            if pos == -1:
                break
            footer_positions.append(pos)
            start = pos + 1
        
        if len(footer_positions) == 1:
            logger.info("✅ 只有一个底部标识，无需清理")
            # 但仍然需要检查是否有重复的闭合标签
            return self._fix_footer_closing_tags(html)
        
        logger.warning(f"检测到 {len(footer_positions)} 个重复的底部标识")
        
        # 保留最后一个底部标识
        last_footer_pos = footer_positions[-1]
        
        # 从最后一个底部标识开始，找到</body>和</html>
        remaining_html = html[last_footer_pos:]
        body_match = re.search(r'</body>', remaining_html, re.IGNORECASE)
        html_match = re.search(r'</html>', remaining_html, re.IGNORECASE)
        
        if body_match and html_match:
            # 🔴 正确策略：
            # 1. 找到第一个底部标识的位置
            first_footer_pos = footer_positions[0]
            
            # 2. 找到最后一个底部标识及其闭合标签在原始 html 中的结束位置
            last_footer_pos = footer_positions[-1]
            remaining_html = html[last_footer_pos:]
            html_match = re.search(r'</html>', remaining_html, re.IGNORECASE)
            if not html_match:
                return self._fix_footer_closing_tags(html)
            
            end_pos_in_original = last_footer_pos + html_match.end()
            
            # 3. 截取从开头到第一个底部标识之前的内容
            result = html[:first_footer_pos]
            
            # 4. 添加最后一个底部标识及其闭合标签
            last_footer_section = html[last_footer_pos:end_pos_in_original]
            result += last_footer_section.strip()
            
            logger.info(f"✅ 已保留最后一个底部标识，移除了{len(footer_positions) - 1}个重复的")
            logger.info(f"清理前长度：{len(html)}, 清理后长度：{len(result)}")
            return result.strip()
        else:
            logger.warning("最后一个底部标识后缺少闭合标签，尝试其他方案...")
            # 如果最后一个底部标识不完整，使用第一个完整的
            return self._fix_footer_closing_tags(html)
    
    def _fix_footer_closing_tags(self, html):
        """
        修复底部标识后的重复闭合标签
        
        @param {str} html - HTML 内容
        @return {str} - 修复后的 HTML
        """
        import re
        
        # 检查是否已经有底部标识
        if '深表美文-文本转美页面' not in html:
            return html
        
        # 找到底部标识的位置
        footer_pos = html.find('深表美文-文本转美页面')
        if footer_pos == -1:
            return html
        
        # 从底部标识后查找</body>和</html>
        remaining = html[footer_pos:]
        
        # 使用正则找到第一个完整的</body></html>结构
        match = re.search(r'</body>\s*</html>', remaining, re.IGNORECASE)
        if match:
            # 保留到第一个正确的闭合位置
            end_pos = footer_pos + match.end()
            result = html[:end_pos].strip()
            
            # 检查后面是否还有重复的标签
            remaining_after = html[end_pos:].strip()
            if remaining_after:
                # 移除重复的闭合标签
                cleanup = re.sub(r'^\s*</(?:div|body|html)>\s*', '', remaining_after, flags=re.IGNORECASE)
                if cleanup.strip():
                    logger.warning(f"发现无法清理的尾部内容：{cleanup[:50]}...")
            
            logger.info("✅ 已清理底部标识后的重复闭合标签")
            return result
        else:
            # 如果没有找到完整的闭合，手动添加
            logger.warning("未找到完整的闭合标签，手动添加...")
            # 找到最后一个>符号
            last_tag_pos = html.rfind('>')
            if last_tag_pos > footer_pos:
                return html[:last_tag_pos + 1].strip() + '\n</body>\n</html>'
            else:
                return html + '\n</body>\n</html>'
    
    def _detect_incomplete_css_property(self, html):
        """
        检测 HTML 中是否有未完成的 CSS 属性
        
        @param {str} html - HTML 内容
        @return {tuple} - (是否不完整，最后不完整的位置，属性名)
        """
        import re
        
        # 🔴 改进：匹配 style="..." 或 style='...'，包括未闭合的情况
        # 先找到所有 style= 的位置
        style_matches = re.finditer(r'style\s*=\s*["\']?', html)
        
        for style_match in style_matches:
            start_pos = style_match.end()
            
            # 找到这个 style 属性的结束位置（下一个>之前或引号结束）
            remaining = html[start_pos:]
            
            # 尝试找到结束引号或标签结束
            end_quote_match = re.search(r'["\'][^>]*?>', remaining)
            if end_quote_match:
                # 有引号的情况
                style_content = remaining[:end_quote_match.start()]
            else:
                # 可能未闭合，找最近的>
                tag_end = remaining.find('>')
                if tag_end != -1:
                    style_content = remaining[:tag_end]
                else:
                    style_content = remaining
            
            # 检查是否有未完成的属性（以冒号结尾或冒号后没有分号/结束引号）
            if style_content.rstrip().endswith(':'):
                # CSS 属性以冒号结尾，说明值缺失
                prop_match = re.search(r'([\w-]+)\s*:\s*$', style_content)
                if prop_match:
                    prop_name = prop_match.group(1)
                    logger.warning(f"检测到未完成的 CSS 属性：{prop_name}")
                    return (True, start_pos, prop_name)
            
            # 检查属性值被截断的情况（有冒号但没有分号或结束）
            lines = style_content.split(';')
            if lines and lines[-1].strip() and ':' in lines[-1]:
                last_prop = lines[-1].strip()
                if not last_prop.endswith('"') and ':' in last_prop:
                    # 可能是属性值被截断
                    prop_match = re.search(r'([\w-]+)\s*:\s*([^;]*)$', last_prop)
                    if prop_match:
                        prop_name = prop_match.group(1)
                        prop_value = prop_match.group(2)
                        # 如果值很短或不完整（如只有几个字符）
                        if len(prop_value) < 3 and not prop_value.replace(' ', '').isdigit():
                            logger.warning(f"检测到可能被截断的 CSS 属性：{prop_name}: {prop_value}")
                            return (True, start_pos, prop_name)
        
        return (False, -1, None)
    
    def _fix_incomplete_css_properties(self, html):
        """
        修复未完成的 CSS 属性
        
        @param {str} html - HTML 内容
        @return {str} - 修复后的 HTML
        """
        import re
        
        is_incomplete, pos, prop_name = self._detect_incomplete_css_property(html)
        
        if not is_incomplete:
            return html
        
        logger.warning(f"尝试修复未完成的 CSS 属性：{prop_name}")
        
        # 根据属性名提供默认值
        default_values = {
            'border-radius': '50%',
            'color': '#333',
            'background': 'white',
            'margin': '0',
            'padding': '10px',
            'font-size': '1rem',
            'width': '100%',
            'height': 'auto',
        }
        
        # 🔴 简单策略：直接在 HTML 中查找并替换未完成的 CSS 属性
        # 匹配模式：属性名：后面没有值（以 > 或"结尾，或者在字符串末尾）
        for prop, default_value in default_values.items():
            # 模式 1: 属性后直接是引号或>或字符串结束
            pattern1 = rf'{prop}\s*:\s*(?:["\'>]|$)'
            matches = list(re.finditer(pattern1, html))
            for match in matches:
                start = match.start()
                end = match.end()
                matched_text = match.group(0)
                
                # 检查是否在 style 属性内
                before = html[:start]
                if 'style=' in before[-100:]:
                    # 在 style 内，根据情况修复
                    if matched_text.endswith('"') or matched_text.endswith("'"):
                        # 替换为完整的属性和值
                        replacement = f'{prop}: {default_value}'
                        html = html[:start] + replacement + html[end-1:]  # -1 是因为要保留引号
                        logger.info(f"✅ 已修复 CSS 属性：{prop}: {default_value}")
                        break
                    elif matched_text.endswith('>'):
                        # 特殊情况：属性后直接是>
                        replacement = f'{prop}: {default_value}>'
                        html = html[:start] + replacement + html[end:]
                        logger.info(f"✅ 已修复 CSS 属性：{prop}: {default_value}")
                        break
                    elif end == len(html):
                        # 在字符串末尾，添加值和引号
                        replacement = f'{prop}: {default_value}"'
                        html = html[:start] + replacement
                        logger.info(f"✅ 已修复 CSS 属性：{prop}: {default_value}")
                        break
        
        logger.info("✅ 已尝试修复未完成的 CSS 属性")
        return html
    
    def _create_fallback_html(self, content, title=None):
        """
        当格式化失败时，创建基础的 HTML
        
        @param {str} content - 原始内容
        @param {str} title - 标题
        @return {str} - 基础 HTML
        """
        logger.warning("使用基础 HTML 模板作为备选方案")
        
        # 简单的样式增强
        styled_content = content.replace('\n\n', '</p><p style="margin-bottom: 20px; line-height: 1.8;">')
        styled_content = styled_content.replace('# ', '<h1 style="color: #667eea; font-size: 32px; margin-bottom: 20px;">').replace('</h1>', '</h1>')
        
        title_html = f'<h1 style="color: #667eea; font-size: 32px; margin-bottom: 20px;">{title}</h1>' if title else ''
        
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title or '文章'}</title>
    <link rel="icon" href="/favicon.ico" type="image/x-icon">
</head>
<body style="font-family: PingFang SC, Microsoft YaHei, SimHei, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); min-height: 100vh;">
    <article style="background: white; border-radius: 20px; padding: 40px; box-shadow: 0 10px 40px rgba(0,0,0,0.1);">
        {title_html}
        <div style="line-height: 1.8; color: #333;">
            <p style="margin-bottom: 20px; line-height: 1.8;">{styled_content}</p>
        </div>
    </article>
</body>
</html>"""
        """
        检测内容是否为表格数据（制表符分隔的多列）
        
        @param {str} content - 内容
        @return {bool} - 如果是表格数据返回 True
        """
        lines = content.strip().split('\n')
        if len(lines) < 2:
            return False
        
        # 检查是否有多行包含制表符
        tab_lines = [line for line in lines if '\t' in line]
        if len(tab_lines) >= 2:
            return True
        
        return False
    
    def _is_table_content(self, content):
        """
        检测内容是否为表格数据（制表符分隔的多列）
        
        @param {str} content - 内容
        @return {bool} - 如果是表格数据返回 True
        """
        lines = content.strip().split('\n')
        if len(lines) < 2:
            return False
        
        # 检查是否有多行包含制表符
        tab_lines = [line for line in lines if '\t' in line]
        if len(tab_lines) >= 2:
            return True
        
        return False
    
    def _fix_table_html(self, html, original_content):
        """
        修复未使用<table>标签的表格 HTML
        当 AI 未能正确生成 table 时，直接使用我们的模板生成完整的 HTML
        
        @param {str} html - AI 生成的 HTML（使用了错误的 div 布局）
        @param {str} original_content - 原始表格内容
        @return {str} - 修复后的完整 HTML
        """
        logger.info("正在将表格数据转换为标准<table>标签...")
        
        # 解析原始表格内容
        lines = original_content.strip().split('\n')
        rows = []
        for line in lines:
            cells = line.split('\t')
            rows.append(cells)
        
        if not rows or len(rows) < 2:
            return html
        
        # 生成完整的 HTML（不依赖 AI 的内容）
        complete_html = self._generate_complete_table_html(rows, title=None)
        
        return complete_html
        
        # 解析原始表格内容
        lines = original_content.strip().split('\n')
        rows = []
        for line in lines:
            cells = line.split('\t')
            rows.append(cells)
        
        if not rows or len(rows) < 2:
            return html
        
        # 生成标准 table HTML
        table_html = self._generate_table_html(rows)
        
        # 替换原有表格区域（简单策略：在主要内容区域插入 table）
        # 找到第一个<main>或主要内容 div，插入 table
        if '<main>' in html:
            # 提取 main 标签内的第一个 section 或 div
            import re
            # 简单方法：直接在 main 标签后插入
            html = html.replace('<main>', f'<main>\n{table_html}', 1)
        else:
            # 如果没有 main 标签，找主要内容容器
            html = html.replace('</head>', f'</head>\n<body>\n{table_html}')
        
        return html
    
    def _generate_table_html(self, rows):
        """
        根据行列数据生成标准 table HTML
        
        @param {list} rows - 二维列表 [[cell1, cell2, ...], ...]
        @return {str} - table HTML
        """
        if not rows:
            return ""
        
        # 表头（第一行）
        header_cells = ''.join([f'<th style="padding: 15px; text-align: left; color: white; font-weight: 600;">{cell}</th>' for cell in rows[0]])
        header_row = f'<tr style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">{header_cells}</tr>'
        header = f'<thead>{header_row}</thead>'
        
        # 表体（其余行）
        body_rows = []
        for i, row in enumerate(rows[1:], 1):
            bg_color = '#f8f9fa' if i % 2 == 0 else 'white'
            cells = ''.join([f'<td style="padding: 12px 15px; border-bottom: 1px solid #e0e0e0;">{cell}</td>' for cell in row])
            body_rows.append(f'<tr style="background-color: {bg_color};">{cells}</tr>')
        
        body = f'<tbody>{"".join(body_rows)}</tbody>'
        
        # 完整表格（带响应式容器）
        table = f'''<div style="overflow-x: auto; margin: 30px 0;">
            <table style="width: 100%; border-collapse: collapse; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-radius: 12px; overflow: hidden;">
                {header}
                {body}
            </table>
        </div>'''
        
        return table
    
    def _generate_complete_table_html(self, rows, title=None):
        """
        生成完整的 HTML 文档，包含美观的页面布局和表格展示
        
        @param {list} rows - 二维列表 [[cell1, cell2, ...], ...]
        @param {str} title - 可选的标题
        @return {str} - 完整的 HTML 文档
        """
        # 使用第一行第一列作为标题（如果没有提供标题）
        if title is None and rows and rows[0]:
            title = rows[0][0].replace(':', '').replace('：', '')
        
        # 生成表格 HTML
        table_html = self._generate_table_html(rows)
        
        # 构建完整的 HTML 文档
        complete_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title or '表格数据'}</title>
    <link rel="icon" href="/favicon.ico" type="image/x-icon">
</head>
<body style="margin: 0; padding: 20px; font-family: PingFang SC, Microsoft YaHei, SimHei, sans-serif; background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%); min-height: 100vh; box-sizing: border-box;">
    <div style="max-width: 1200px; margin: 0 auto;">
        
        <!-- 主标题 -->
        <div style="text-align: center; margin-bottom: 40px;">
            <h1 style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; color: transparent; font-size: 2.8rem; margin-bottom: 10px; display: inline-flex; align-items: center; gap: 15px;">
                📊 {title or '数据表格'}
            </h1>
            <p style="color: #666; font-size: 1.1rem; margin-top: 0;">数据清晰呈现，信息一目了然</p>
        </div>
        
        <!-- 引言卡片 -->
        <div style="background: linear-gradient(135deg, #e0e7ff 0%, #f3e8ff 100%); border-radius: 20px; padding: 25px 30px; margin-bottom: 40px; box-shadow: 0 10px 30px rgba(102, 126, 234, 0.1); border-left: 6px solid #667eea;">
            <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 10px;">
                <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 1.2rem;">💡</div>
                <h2 style="margin: 0; color: #4a5568; font-size: 1.3rem;">数据概览</h2>
            </div>
            <p style="margin: 0; color: #555; line-height: 1.8;">
                以下表格完整展示了所有数据记录。每一行都经过仔细核对，确保信息的准确性与完整性。
            </p>
        </div>
        
        <!-- 表格区域 -->
        {table_html}
        
        
    </div>
</body>
</html>"""
        
        return complete_html
    
    def _is_html_complete(self, html):
        """
        检查 HTML 是否完整（有完整的开始和结束标签）
            
        @param {str} html - HTML 内容
        @return {bool} - 是否完整
        """
        # 检查基本的闭合标签
        if not html.strip().endswith('</html>'):
            return False
        if not '</body>' in html:
            return False
            
        # 检查是否有未闭合的标签
        import re
        # 简单的检查：统计常见标签的开闭数量
        tags_to_check = ['div', 'p', 'h1', 'h2', 'h3', 'span', 'ul', 'li']
        for tag in tags_to_check:
            open_count = len(re.findall(rf'<{tag}(?:\s[^>]*)?>', html))
            close_count = len(re.findall(rf'</{tag}>', html))
            if open_count != close_count:
                logger.warning(f"标签不匹配：<{tag}> 开启{open_count}个，关闭{close_count}个")
                return False
            
        # 🔴 特别检查：表格必须完整闭合
        if '<table' in html.lower():
            table_open = len(re.findall(r'<table(?:\s[^>]*)?>', html))
            table_close = len(re.findall(r'</table>', html))
            tbody_open = len(re.findall(r'<tbody(?:\s[^>]*)?>', html))
            tbody_close = len(re.findall(r'</tbody>', html))
            thead_open = len(re.findall(r'<thead(?:\s[^>]*)?>', html))
            thead_close = len(re.findall(r'</thead>', html))
                
            if table_open != table_close:
                logger.warning(f"表格未闭合：<table> 开启{table_open}个，关闭{table_close}个")
                return False
            if tbody_open != tbody_close:
                logger.warning(f"表体未闭合：<tbody> 开启{tbody_open}个，关闭{tbody_close}个")
                return False
            if thead_open != thead_close:
                logger.warning(f"表头未闭合：<thead> 开启{thead_open}个，关闭{thead_close}个")
                return False
            
        return True
    
    def _fix_incomplete_html(self, html):
        """
        修复不完整的 HTML，添加缺失的闭合标签
        
        @param {str} html - 不完整的 HTML
        @return {str} - 修复后的 HTML
        """
        logger.info("正在修复不完整的 HTML...")
        
        # 🔴 特别处理：如果是表格未完成，手动闭合表格标签
        if '<table' in html.lower() and '</table>' not in html.lower():
            logger.warning("检测到表格未闭合，手动添加闭合标签...")
            # 移除末尾未完成的部分
            last_complete_tag_pos = html.rfind('>')
            if last_complete_tag_pos > 0 and last_complete_tag_pos < len(html) - 1:
                remaining = html[last_complete_tag_pos + 1:].strip()
                if remaining and not remaining.startswith('<'):
                    html = html[:last_complete_tag_pos + 1]
            
            # 手动闭合表格标签（从内到外）
            closing_tags = []
            if '</tr>' not in html[-100:]:  # 如果最后没有</tr>
                closing_tags.append('</tr>')
            if '</tbody>' not in html:
                closing_tags.append('</tbody>')
            if '</table>' not in html:
                closing_tags.append('</table>')
            
            if closing_tags:
                html += '\n' + '\n'.join(closing_tags)
                logger.info(f"已手动闭合表格标签：{closing_tags}")
        
        # 移除末尾未完成的部分
        # 找到最后一个完整的标签
        last_complete_tag_pos = html.rfind('>')
        if last_complete_tag_pos > 0 and last_complete_tag_pos < len(html) - 1:
            # 如果最后一个>后面还有内容，说明有未完成的标签
            remaining = html[last_complete_tag_pos + 1:].strip()
            if remaining and not remaining.startswith('<'):
                # 删除未完成的标签
                html = html[:last_complete_tag_pos + 1]
        
        # 检查是否已经有底部标识和闭合标签
        has_footer = '深表美文-文本转美页面' in html
        has_body_close = '</body>' in html
        has_html_close = '</html>' in html
        
        # 添加缺失的闭合标签和底部标识（只在确实缺失时才添加）
        closing_tags = []
        if not has_body_close:
            # 先添加底部标识（只有在没有的情况下）
            if not has_footer:
                footer_html = self.get_footer_html()
                closing_tags.append(footer_html)
            closing_tags.append('</body>')
        if not has_html_close:
            closing_tags.append('</html>')
        
        if closing_tags:
            html += '\n' + '\n'.join(closing_tags)
            logger.info(f"已添加缺失的闭合标签：{closing_tags}")
        else:
            logger.info("HTML 已包含所有必要的闭合标签，无需添加")
        
        return html
    
    def _continue_generation(self, incomplete_html, original_prompt, content, title=None):
        """
        智能续传机制：当 HTML 不完整时，请求 AI 继续生成
        
        @param {str} incomplete_html - 不完整的 HTML
        @param {dict} original_prompt - 原始的 prompt
        @param {str} content - 原始内容
        @param {str} title - 标题
        @return {str} - 续传后的完整 HTML
        """
        max_retries = 3  # 最多重试 3 次
        retry_count = 0
        current_html = incomplete_html
        
        while retry_count < max_retries:
            retry_count += 1
            logger.info(f"开始第 {retry_count} 次续传...")
            
            # 构建续传的 prompt
            continuation_prompt = self._create_continuation_prompt(
                current_html, content, title
            )
            
            try:
                # 调用 API 获取续传内容
                response = self._call_api(continuation_prompt, use_stream=True)
                continuation_content = self._parse_response(response)
                
                # 合并内容
                current_html = self._merge_continuation(current_html, continuation_content)
                
                # 检查是否已经完整
                if self._is_html_complete(current_html):
                    logger.info(f"续传成功！HTML 已完整，共尝试 {retry_count} 次")
                    break
                else:
                    logger.warning(f"第 {retry_count} 次续传后 HTML 仍不完整，继续...")
                    
            except Exception as e:
                logger.error(f"第 {retry_count} 次续传失败：{str(e)}")
                # 即使失败，也尝试修复并返回
                if retry_count == max_retries:
                    logger.warning("达到最大重试次数，尝试修复现有 HTML...")
                    current_html = self._fix_incomplete_html(current_html)
                    break
        
        return current_html
    
    def _create_continuation_prompt(self, incomplete_html, content, title=None):
        """
        创建续传的 prompt
        
        @param {str} incomplete_html - 已生成的不完整 HTML
        @param {str} content - 原始内容
        @param {str} title - 标题
        @return {dict} - 续传用的 prompt
        """
        # 🔴 智能识别中断点
        interruption_analysis = self._analyze_interruption_point(incomplete_html)
        
        # 提取已生成的最后部分（最后 1000 个字符，以便 AI 看到更多上下文）
        last_part = incomplete_html[-1000:] if len(incomplete_html) > 1000 else incomplete_html
        
        return {
            "messages": [
                {
                    "role": "system",
                    "content": """你是一位专业的 HTML 排版设计师。你的任务是继续生成被中断的 HTML 内容。
                    
🔴 **续传规则（最高优先级）**：
1. **精准接续**：从上文中断的地方直接继续，不要重复已生成的内容
2. **保持样式一致性**：使用相同的风格和配色
3. **🔴 特别重要：如果上文是未完成的表格（<tr>或<td>未闭合），必须立即继续生成表格剩余部分**
4. **必须确保所有标签完整闭合**：<table>, </table>, <tbody>, </tbody>
5. **🔴 绝对禁止**：在表格、卡片、章节等内容未完成前，不要添加底部标识和</body></html>
6. **CSS 属性完整性**：如果上文的 style 属性中 CSS 值未完成（如 border-radius: 后面没有值），必须先补全该值
7. **内容完整性**：继续生成原文剩余的所有内容，不能省略任何段落"""
                },
                {
                    "role": "user",
                    "content": f"""请继续生成以下被中断的 HTML 内容。

【中断点分析】
{interruption_analysis['analysis']}

【已生成的 HTML（最后部分）】
{last_part}

🔴 **续传要求（极其重要）**：
- ✅ **中断位置**：{interruption_analysis['position']}
- ✅ **当前状态**：{interruption_analysis['status']}
- ✅ **必须首先完成**：{interruption_analysis['must_complete_first']}
- ✅ **然后继续**：{interruption_analysis['then_continue']}
- ✅ **最后添加**：底部标识 + </body></html>（只有在所有内容完成后）

⚠️ **绝对禁止**：
- ❌ 不要重复已生成的内容
- ❌ 不要在中间添加底部标识
- ❌ 不要省略原文的任何内容
- ❌ 不要使用"..."或其他省略符号

请直接输出续传的 HTML 内容（不需要重复已生成的部分，直接从断点处继续）："""
                }
            ],
            "model": "deepseek-chat",
            "temperature": 0.7,
            "max_tokens": 25000,
            "stream": True
        }
    
    def _analyze_interruption_point(self, html):
        """
        智能识别 HTML 的中断点，帮助 AI 精准续传
        
        @param {str} html - 不完整的 HTML
        @return {dict} - 中断点分析报告
        """
        import re
        
        analysis = []
        position = "未知"
        status = "需要检查"
        must_complete_first = "无"
        then_continue = "生成剩余内容"
        
        # 🔴 检查 1: CSS 属性是否未完成
        is_css_incomplete, css_pos, prop_name = self._detect_incomplete_css_property(html)
        if is_css_incomplete:
            analysis.append(f"检测到 CSS 属性 '{prop_name}' 未完成，值缺失")
            position = f"style 属性中的 {prop_name} 处"
            status = "CSS 属性截断"
            must_complete_first = f"补全 {prop_name} 的值（如 border-radius: 50%）"
            then_continue = "继续完成当前元素的其他内容和后续所有內容"
            return {
                'analysis': '\n'.join(analysis),
                'position': position,
                'status': status,
                'must_complete_first': must_complete_first,
                'then_continue': then_continue
            }
        
        # 🔴 检查 2: 表格是否未完成
        if '<table' in html.lower():
            tr_open = len(re.findall(r'<tr(?:\s[^>]*)?>', html))
            tr_close = len(re.findall(r'</tr>', html))
            td_open = len(re.findall(r'<td(?:\s[^>]*)?>', html))
            td_close = len(re.findall(r'</td>', html))
            tbody_open = len(re.findall(r'<tbody(?:\s[^>]*)?>', html))
            tbody_close = len(re.findall(r'</tbody>', html))
            
            if tr_open > tr_close:
                analysis.append(f"表格行 <tr> 未闭合（开启{tr_open}个，关闭{tr_close}个）")
                position = "表格行 <tr> 内部"
                status = "表格行未闭合"
                must_complete_first = "完成当前<tr>行内的所有<td>单元格，并闭合</tr>"
                then_continue = "继续生成表格的剩余行，直到所有数据呈现完毕，然后闭合</tbody></table>"
            elif td_open > td_close:
                analysis.append(f"表格单元格 <td> 未闭合（开启{td_open}个，关闭{td_close}个）")
                position = "表格单元格 <td> 内部"
                status = "单元格未闭合"
                must_complete_first = "完成当前<td>的内容并闭合</td>"
                then_continue = "继续完成当前行的其他单元格，然后继续表格的剩余行"
            elif tbody_open > tbody_close:
                analysis.append(f"表体 <tbody> 未闭合")
                position = "表体 <tbody> 内部"
                status = "表体未闭合"
                must_complete_first = "继续生成表格数据行"
                then_continue = "生成完所有表格行后闭合</tbody></table>"
            
            if analysis:
                return {
                    'analysis': '\n'.join(analysis),
                    'position': position,
                    'status': status,
                    'must_complete_first': must_complete_first,
                    'then_continue': then_continue
                }
        
        # 🔴 检查 3: 普通 div 标签是否未完成
        last_tag_match = re.search(r'<([a-zA-Z0-9]+)(?:\s[^>]*)?$', html[-200:])
        if last_tag_match:
            tag_name = last_tag_match.group(1)
            if tag_name not in ['br', 'hr', 'img', 'input', 'meta', 'link']:  # 自闭合标签
                # 检查这个标签是否有对应的闭合标签
                remaining_html = html[last_tag_match.start():]
                closing_tag = f'</{tag_name}>'
                if closing_tag not in remaining_html:
                    analysis.append(f"标签 <{tag_name}> 可能未闭合")
                    position = f"<{tag_name}> 标签内部"
                    status = f"{tag_name} 标签未闭合"
                    must_complete_first = f"完成<{tag_name}>的内容并闭合</{tag_name}>"
                    then_continue = "继续生成后续内容"
                    return {
                        'analysis': '\n'.join(analysis),
                        'position': position,
                        'status': status,
                        'must_complete_first': must_complete_first,
                        'then_continue': then_continue
                    }
        
        # 🔴 检查 4: 是否有底部标识但缺少闭合标签
        if '深表美文-文本转美页面' in html:
            if '</body>' not in html or '</html>' not in html:
                analysis.append("已有底部标识但缺少</body>或</html>")
                position = "底部标识之后"
                status = "文档未闭合"
                must_complete_first = "添加</body>和</html>"
                then_continue = "无需更多内容"
                return {
                    'analysis': '\n'.join(analysis),
                    'position': position,
                    'status': status,
                    'must_complete_first': must_complete_first,
                    'then_continue': then_continue
                }
        
        # 默认情况
        if not analysis:
            analysis.append("未检测到明显的中断问题，可能需要生成更多内容")
            position = "文档末尾"
            status = "需要续传"
            must_complete_first = "检查是否还有原文内容未生成"
            then_continue = "继续生成直到包含原文所有内容并正确闭合所有标签"
        
        return {
            'analysis': '\n'.join(analysis),
            'position': position,
            'status': status,
            'must_complete_first': must_complete_first,
            'then_continue': then_continue
        }
    
    def _merge_continuation(self, existing_html, new_content):
        """
        合并续传内容
        
        @param {str} existing_html - 已存在的 HTML
        @param {str} new_content - 新生成的续传内容
        @return {str} - 合并后的 HTML
        """
        # 清理新内容的 markdown 标记
        new_content = re.sub(r'^```html\s*', '', new_content)
        new_content = re.sub(r'```$', '', new_content)
        new_content = new_content.strip()
        
        # 简单的合并策略：直接拼接
        merged = existing_html + "\n" + new_content
        
        logger.info(f"合并完成，总长度：{len(merged)}")
        return merged
    
    def _force_complete_table(self, html, original_content, title=None):
        """
        强制补全表格：当 AI 生成的行数不足时，直接使用原始数据生成完整表格
        
        @param {str} html - AI 生成的不完整 HTML
        @param {str} original_content - 原始表格内容
        @param {str} title - 标题
        @return {str} - 完整的表格 HTML
        """
        logger.warning("🔴 开始强制补全表格...")
        
        # 解析原始表格数据
        lines = original_content.strip().split('\n')
        if len(lines) < 2:
            logger.error("表格数据行数不足，无法补全")
            return html
        
        # 提取表头（第一行）
        headers = lines[0].split('\t')
        
        # 提取数据行（第 2 行到最后）
        data_rows = []
        for line in lines[1:]:
            cells = line.split('\t')
            data_rows.append(cells)
        
        logger.info(f"原始表格：{len(headers)}列，{len(data_rows)}行数据")
        
        # 生成完整的表格 HTML（使用我们的模板，不依赖 AI）
        complete_html = self._generate_complete_table_html_manual(headers, data_rows, title)
        
        logger.info("✅ 表格强制补全完成")
        return complete_html
    
    def _generate_complete_table_html_manual(self, headers, data_rows, title=None):
        """
        手动生成完整的表格 HTML（不依赖 AI）
        
        @param {list} headers - 表头列表
        @param {list} data_rows - 数据行（二维列表）
        @param {str} title - 标题
        @return {str} - 完整的 HTML 文档
        """
        # 使用第一个表头作为标题（如果没有提供标题）
        if title is None and headers:
            title = headers[0].replace(':', '').replace('：', '')
        
        # 生成表头 HTML
        header_cells = ''.join([f'<th style="padding: 15px; text-align: left; color: white; font-weight: 600;">{cell}</th>' for cell in headers])
        header_row = f'<tr style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">{header_cells}</tr>'
        
        # 生成数据行 HTML
        body_rows = []
        for i, row in enumerate(data_rows, 1):
            bg_color = '#f8f9fa' if i % 2 == 0 else 'white'
            cells = ''.join([f'<td style="padding: 12px 15px; border-bottom: 1px solid #e0e0e0;">{cell if cell else ""}</td>' for cell in row])
            body_rows.append(f'<tr style="background-color: {bg_color};">{cells}</tr>')
        
        table_body = ''.join(body_rows)
        
        # 构建完整的 HTML
        complete_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title or '表格数据'}</title>
    <link rel="icon" href="/favicon.ico" type="image/x-icon">
</head>
<body style="margin: 0; padding: 20px; font-family: PingFang SC, Microsoft YaHei, SimHei, sans-serif; background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%); min-height: 100vh; color: #333; line-height: 1.6;">
    <div style="max-width: 1200px; margin: 0 auto;">
        
        <!-- 主标题 -->
        <div style="text-align: center; margin-bottom: 40px;">
            <h1 style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; color: transparent; font-size: 2.8rem; margin-bottom: 10px; display: inline-flex; align-items: center; gap: 15px;">
                📊 {title or '数据表格'}
            </h1>
            <p style="color: #666; font-size: 1.1rem; margin-top: 0;">数据清晰呈现，信息一目了然</p>
        </div>
        
        <!-- 表格区域 -->
        <div style="overflow-x: auto; border-radius: 18px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);">
            <table style="width: 100%; border-collapse: collapse; min-width: 1000px; font-size: 0.95rem;">
                <thead>
                    {header_row}
                </thead>
                <tbody>
                    {table_body}
                </tbody>
            </table>
        </div>
        
        {self.get_footer_html()}
    </div>
</body>
</html>"""
        
        return complete_html


def main():
    """
    主函数 - 用于测试
    """
    # 测试示例
    formatter = HTMLFormatter()
    
    test_content = """# 这是一个测试标题

这是第一段内容。我们来看看格式化效果如何。

## 第二部分

这里是第二个章节的内容。"""
    
    result = formatter.format_article(test_content, "测试文章")
    print(result)


if __name__ == "__main__":
    main()
