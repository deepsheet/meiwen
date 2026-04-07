#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LLM 客户端：统一的大语言模型调用接口，支持 DeepSeek、Qwen 等多个模型
"""

import sys
import os
import json
import requests
import random
import re

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.config import (
    DEEPSEEK_API_KEY, DEEPSEEK_API_URL, DEEPSEEK_MODEL,
    QWEN_API_KEY, QWEN_BASE_URL, QWEN_MODEL,
    CURRENT_MODEL, BLOG_TOPICS
)
from src.logger import logger
from src.i18n import get_llm_prompt, get_language_from_request


class LLMClient:
    """
    统一的大语言模型客户端类，支持多个模型提供商
    """
    
    def __init__(self, model_name=None, language=None):
        """
        初始化 LLM 客户端
        
        @param {str} model_name - 可选的模型名称，如果不提供则使用配置文件中的 CURRENT_MODEL
        @param {str} language - 可选的语言代码，如果不提供则从请求中自动检测
        """
        self.model_name = model_name if model_name else CURRENT_MODEL
        self.language = language if language else get_language_from_request()
        logger.info(f"初始化 LLM 客户端，使用模型：{self.model_name}，语言：{self.language}")
        
        # 根据模型名称配置 API 参数
        if self.model_name.lower() == 'deepseek':
            self.api_key = DEEPSEEK_API_KEY
            self.api_url = DEEPSEEK_API_URL
            self.model = DEEPSEEK_MODEL
        elif self.model_name.lower() == 'qwen':
            self.api_key = QWEN_API_KEY
            self.api_url = QWEN_BASE_URL
            self.model = QWEN_MODEL
        else:
            logger.error(f"不支持的模型：{self.model_name}")
            raise ValueError(f"不支持的模型：{self.model_name}")
        
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def generate_blog(self, topic=None):
        """
        生成博客内容和标题
        
        @param {str} topic - 可选的博客主题，如果不提供则随机选择一个
        @return {tuple} - (标题，内容) 元组
        """
        if not topic:
            topic = random.choice(BLOG_TOPICS)
        
        logger.info(f"开始生成博客，主题：{topic}，使用模型：{self.model_name}")
        
        try:
            prompt = self._create_blog_prompt(topic)
            response = self._call_api(prompt)
            blog_content = self._parse_response(response)
            
            # 提取标题和内容
            title, content = self._extract_title_and_content(blog_content)
            
            # 检查内容是否包含可能导致 SQL 插入失败的字符
            clean_title = self._sanitize_content(title)
            clean_content = self._sanitize_content(content)
            
            logger.info(f"博客生成成功，标题：{clean_title}，内容长度：{len(clean_content)}字符")
            return clean_title, clean_content
        except Exception as e:
            logger.error(f"博客生成失败：{str(e)}")
            return None, None
    
    def generate_title(self, content):
        """
        根据文章内容生成标题
        
        @param {str} content - 文章内容
        @return {str} - 生成的标题
        """
        logger.info(f"开始生成标题，使用模型：{self.model_name}")
        
        try:
            prompt = self._create_title_prompt(content)
            response = self._call_api(prompt)
            title = self._parse_response(response).strip()
            
            # 清理可能的 markdown 格式
            title = re.sub(r'^["\']|["\']$', '', title)
            title = re.sub(r'^#+\s*', '', title)
            
            logger.info(f"标题生成成功：{title}")
            return title
        except Exception as e:
            logger.error(f"标题生成失败：{str(e)}")
            # 如果生成失败，使用内容前 20 字作为标题
            if content:
                fallback_title = content[:20].replace('\n', ' ').strip()
                if fallback_title:
                    logger.info(f"使用内容前 20 字作为标题：{fallback_title}")
                    return fallback_title
            # 如果内容为空或提取失败，使用时间戳作为标题
            import time
            fallback_title = f"文章_{int(time.time())}"
            logger.info(f"使用时间戳作为标题：{fallback_title}")
            return fallback_title
    
    def format_article(self, content, title=None, base_url=None, content_strategy="strict", style="auto", extra_requirements=None, article_id=None):
        """
        格式化文章内容为精美的 HTML
        
        @param {str} content - 文章内容
        @param {str} title - 可选的文章标题
        @param {str} base_url - 可选的域名配置，用于底部标识链接
        @param {str} content_strategy - 内容处理策略："strict"(严格遵循原文), "interpret"(允许解读), "expand"(允许扩写)
        @param {str} style - 样式风格："auto"(自动匹配), "default"(默认风格), 或其他15种风格
        @param {str} extra_requirements - 额外的格式化要求
        @param {str} article_id - 文章 ID（用于 SEO 结构化数据）
        @return {str} - 格式化后的完整 HTML
        """
        logger.info(f"开始格式化文章，使用模型：{self.model_name}，策略：{content_strategy}，样式：{style}，额外要求：{extra_requirements if extra_requirements else '(无)'}")
        
        try:
            # 1. 调用 LLM 生成内容片段和 SEO 元数据
            prompt = self._create_format_prompt(content, title, content_strategy, style, extra_requirements)
            response = self._call_api(prompt, use_stream=True)
            llm_output = self._parse_response(response)
            
            # 2. 清理可能的代码块标记
            llm_output = self._clean_code_block_markers(llm_output)
            
            # 3. 解析 LLM 输出，提取内容和元数据
            content_html, seo_keywords, seo_description = self._parse_llm_output_with_metadata(llm_output)
            
            # 4. 生成页面标题
            page_title = title if title else self._generate_seo_title(content)
            
            # 5. 根据语言获取底部标识文本
            from src.i18n import get_translation
            powered_by = get_translation('powered_by', self.language)
            
            # 6. 加载模板并填充变量
            full_html = self._render_template(
                content_html=content_html,
                page_title=page_title,
                keywords=seo_keywords,
                description=seo_description,
                lang=self.language,
                powered_by=powered_by,
                article_id=article_id,
                publish_date=None,
                modify_date=None
            )
            
            logger.info(f"文章格式化完成，HTML 长度：{len(full_html)}")
            return full_html
        except Exception as e:
            logger.error(f"文章格式化失败：{str(e)}")
            return self._create_fallback_html(content, title)
    
    def _create_blog_prompt(self, topic):
        """
        创建用于生成博客的提示
        
        @param {str} topic - 博客主题
        @return {dict} - 格式化的提示文本
        """
        system_prompt = get_llm_prompt('blog_system', self.language)
        user_prompt_template = get_llm_prompt('blog_user', self.language)
        user_prompt = user_prompt_template.format(topic=topic)
        
        return {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "model": self.model,
            "temperature": 0.8,
            "max_tokens": 8000
        }
    
    def _create_title_prompt(self, content):
        """
        创建用于生成标题的提示
        
        @param {str} content - 文章内容
        @return {dict} - 格式化的提示文本
        """
        system_prompt = get_llm_prompt('title_system', self.language)
        user_prompt_template = get_llm_prompt('title_user', self.language)
        content_preview = content[:500] + "..." if len(content) > 500 else content
        user_prompt = user_prompt_template.format(content=content_preview)
        
        return {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "model": self.model,
            "temperature": 0.7,
            "max_tokens": 50
        }
    
    def _create_format_prompt(self, content, title=None, content_strategy="strict", style="auto", extra_requirements=None):
        """
        创建用于格式化文章的提示
        
        @param {str} content - 文章内容
        @param {str} title - 文章标题
        @param {str} content_strategy - 内容处理策略："strict"(严格遵循原文), "interpret"(允许解读), "expand"(允许扩写)
        @param {str} style - 样式风格："auto"(自动匹配), "default"(默认风格), 或其他15种风格
        @param {str} extra_requirements - 额外的格式化要求
        @return {dict} - 格式化的提示文本
        """
        # 根据样式风格获取对应的系统提示词
        if style and style != "auto":
            # 如果不是自动匹配，使用专用样式提示词
            from config.style_prompts import get_style_prompt
            system_prompt = get_style_prompt(style, self.language)
        else:
            # 自动匹配或空值，使用默认的格式化系统提示词
            system_prompt = get_llm_prompt('format_system', self.language)
        
        user_prompt_template = get_llm_prompt('format_user', self.language)
        
        # 构建额外要求的说明
        extra_requirements_text = self._build_extra_requirements_text(extra_requirements)
        
        # 根据策略生成对应的提示词
        strategy_text = self._get_strategy_text(content_strategy)
        
        title_info = f"文章标题：{title}\n\n" if title else ""
        
        user_prompt = user_prompt_template.format(
            content_length=len(content),
            line_count=content.count(chr(10)),
            strategy_text=strategy_text,
            extra_requirements_text=extra_requirements_text,
            title_info=title_info,
            content=content
        )

        return {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "model": self.model,
            "temperature": 0.7,
            "stream": True
        }
    
    def _get_strategy_text(self, strategy):
        """
        根据语言和策略获取对应的说明文本
        
        @param {str} strategy - 策略名称
        @return {str} - 策略说明文本
        """
        # 构建提示词键名：format_strategy_{strategy}_{language}
        prompt_key = f'format_strategy_{strategy}_{self.language}'
        return get_llm_prompt(prompt_key, self.language)
    
    def _build_extra_requirements_text(self, extra_requirements):
        """
        构建额外要求文本
        
        @param {str} extra_requirements - 额外要求
        @return {str} - 格式化后的额外要求文本
        """
        if not extra_requirements or not extra_requirements.strip():
            return ""
        
        template = get_llm_prompt('extra_requirements_template', self.language)
        return template.format(requirements=extra_requirements)
    
    def _call_api(self, prompt, use_stream=False):
        """
        调用 LLM API
        
        @param {dict} prompt - API 请求的提示信息
        @param {bool} use_stream - 是否使用流式输出
        @return {dict|str} - API 响应（非流式）或完整内容（流式）
        """
        try:
            if use_stream:
                logger.info("使用流式输出模式处理长内容...")
                return self._call_api_stream(prompt)
            else:
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json=prompt,
                    timeout=180
                )
                response.raise_for_status()
                return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"{self.model_name} API 请求失败：{str(e)}")
            raise
    
    def _call_api_stream(self, prompt):
        """
        使用流式输出调用 API，适合处理超长内容
        
        @param {dict} prompt - API 请求的提示信息
        @return {str} - 完整的内容
        """
        try:
            # 启用流式输出
            prompt["stream"] = True
            # 流式输出时不设置 max_tokens，让 AI 自然输出完成
            if "max_tokens" in prompt:
                del prompt["max_tokens"]
            
            logger.info("开始流式接收数据...")
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=prompt,
                timeout=600,
                stream=True
            )
            response.raise_for_status()
            
            # 收集所有流式片段
            full_content = []
            chunk_count = 0
            error_count = 0
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data = line_str[6:]
                        if data == '[DONE]':
                            break
                        try:
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
                            error_count += 1
                            logger.warning(f"JSON 解析失败 (第{error_count}次)，尝试备用方案...")
                            try:
                                match = re.search(r'"content":"([^"]*(?:\\"[^"]*)*)"', data)
                                if match:
                                    content = match.group(1).replace('\\"', '"')
                                    full_content.append(content)
                                    chunk_count += 1
                            except Exception as extract_error:
                                logger.error(f"备用方案也失败：{str(extract_error)}")
                                continue
            
            # 合并所有片段
            final_content = ''.join(full_content)
            logger.info(f"流式接收完成，共 {chunk_count} 个片段，总长度：{len(final_content)}")
            return final_content
            
        except Exception as e:
            logger.error(f"流式输出失败：{str(e)}")
            if 'full_content' in locals() and full_content:
                partial_content = ''.join(full_content)
                logger.warning(f"返回已接收的部分内容，长度：{len(partial_content)}")
                return partial_content
            raise
    
    def _parse_response(self, response):
        """
        解析 API 响应获取生成的内容
        
        @param {dict|str} response - API 响应（非流式）或完整内容（流式）
        @return {str} - 解析后的内容
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
            
            return content
        except (KeyError, IndexError) as e:
            logger.error(f"解析 API 响应失败：{str(e)}")
            logger.error(f"API 响应：{json.dumps(response, ensure_ascii=False)}")
            raise
    
    def _extract_title_and_content(self, full_text):
        """
        从生成的文本中提取标题和内容
        
        @param {str} full_text - 生成的完整文本
        @return {tuple} - (标题，内容) 元组
        """
        # 查找以'# '开头的标题
        title_match = re.search(r'# (.+?)[\n\r]', full_text)
        
        if title_match:
            title = title_match.group(1).strip()
            content = re.sub(r'# .+?[\n\r]', '', full_text, count=1).strip()
        else:
            # 如果没有找到标题格式，使用全文的第一行作为标题
            lines = full_text.split('\n')
            title = lines[0].strip().replace('#', '').strip()
            content = '\n'.join(lines[1:]).strip()
            
            # 如果第一行内容太长，可能不是标题，创建一个默认标题
            if len(title) > 50:
                title = "iSheet.net 云表格技术博客"
                content = full_text
        
        return title, content
    
    def _sanitize_content(self, content):
        """
        清理内容中可能导致 SQL 插入失败的字符
        
        @param {str} content - 原始内容
        @return {str} - 清理后的内容
        """
        if not content:
            return ""
        
        # 替换单引号、双引号和反斜杠，以避免 SQL 注入问题
        sanitized = content.replace("'", "''").replace("\\", "\\\\")
        
        return sanitized
    
    def retry_with_sanitized_content(self, original_title, original_content):
        """
        当插入失败时，尝试重新清理内容或生成新内容
        
        @param {str} original_title - 原始标题
        @param {str} original_content - 原始内容
        @return {tuple} - (清理后的标题，清理后的内容) 元组
        """
        logger.warning("尝试重新清理内容或生成新内容")
        
        # 首先尝试更严格的清理
        strict_title = self._strict_sanitize(original_title)
        strict_content = self._strict_sanitize(original_content)
        
        if strict_title and strict_content:
            return strict_title, strict_content
        
        # 如果清理无效，尝试生成新内容
        return self.generate_blog()
    
    def _strict_sanitize(self, content):
        """
        更严格的内容清理
        
        @param {str} content - 原始内容
        @return {str} - 严格清理后的内容
        """
        if not content:
            return None
        
        # 更严格的替换规则
        strict_sanitized = content
        problematic_chars = ["'", "\"", "\\", ";", "--", "/*", "*/", "%", "_"]
        
        for char in problematic_chars:
            if char == "'":
                strict_sanitized = strict_sanitized.replace(char, "''")
            elif char == "\\":
                strict_sanitized = strict_sanitized.replace(char, "\\\\")
            else:
                strict_sanitized = strict_sanitized.replace(char, " ")
        
        return strict_sanitized
    
    def _clean_code_block_markers(self, content):
        """
        清理 LLM 输出中的代码块标记
        
        @param {str} content - LLM 输出的内容
        @return {str} - 清理后的内容
        """
        # 移除 ```html 或 ``` 等代码块标记
        content = re.sub(r'^```html\s*', '', content, flags=re.MULTILINE)
        content = re.sub(r'^```\s*$', '', content, flags=re.MULTILINE)
        content = content.strip()
        return content
    
    def _parse_llm_output_with_metadata(self, llm_output):
        """
        解析 LLM 输出，提取 HTML 内容和 SEO 元数据
        
        期望 LLM 输出格式：
        ---METADATA_START---
        keywords: keyword1, keyword2, keyword3
        description: This is a description of the article.
        ---METADATA_END---
        <HTML content here>
        
        @param {str} llm_output - LLM 的完整输出
        @return {tuple} - (content_html, keywords, description)
        """
        try:
            # 尝试多种可能的元数据标记格式
            patterns = [
                # 标准格式
                r'---METADATA_START---\s*keywords:\s*(.+?)\s*description:\s*(.+?)\s*---METADATA_END---',
                # 没有空格的格式
                r'---METADATASTART---\s*keywords:\s*(.+?)\s*description:\s*(.+?)\s*---METADATAEND---',
                # 使用不同分隔符
                r'===METADATA_START===\s*keywords:\s*(.+?)\s*description:\s*(.+?)\s*===METADATA_END===',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, llm_output, re.DOTALL | re.IGNORECASE)
                if match:
                    keywords = match.group(1).strip()
                    description = match.group(2).strip()
                    # 提取元数据标记后的 HTML 内容
                    content_html = re.sub(pattern, '', llm_output, flags=re.DOTALL | re.IGNORECASE).strip()
                    logger.info(f"成功从 LLM 输出中提取元数据")
                    logger.info(f"Keywords: {keywords[:50]}...")
                    logger.info(f"Description: {description[:50]}...")
                    return content_html, keywords, description
            
            # 如果没有找到元数据标记，使用默认值
            logger.warning("未在 LLM 输出中找到元数据标记，使用默认算法生成")
            content_html = llm_output
            keywords = self._generate_keywords(llm_output)
            description = self._generate_description(llm_output)
            return content_html, keywords, description
        except Exception as e:
            logger.error(f"解析 LLM 元数据失败：{str(e)}，使用默认值")
            import traceback
            logger.error(traceback.format_exc())
            return llm_output, self._generate_keywords(llm_output), self._generate_description(llm_output)
    
    def _generate_seo_title(self, content, max_length=60):
        """
        从内容中生成 SEO 标题
        
        @param {str} content - 文章内容
        @param {int} max_length - 最大长度
        @return {str} - SEO 标题
        """
        # 尝试提取第一行作为标题
        lines = content.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) > 10:
                # 移除 Markdown 标题标记
                title = re.sub(r'^#+\s*', '', line)
                if len(title) <= max_length:
                    return title
                else:
                    return title[:max_length-3] + '...'
        
        # 如果没有合适的标题，使用内容前缀
        return content[:max_length-3].strip() + '...' if len(content) > max_length else content
    
    def _generate_keywords(self, content, max_keywords=5):
        """
        从内容中提取关键词
        
        @param {str} content - 文章内容
        @param {int} max_keywords - 最大关键词数量
        @return {str} - 逗号分隔的关键词
        """
        # 简单的关键词提取：提取出现频率较高的词
        # 这里使用简化版本，实际可以使用更复杂的 NLP 技术
        words = re.findall(r'[\u4e00-\u9fa5]{2,}|[a-zA-Z]{3,}', content)
        
        # 统计词频
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # 按频率排序，取前 max_keywords 个
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        keywords = [word for word, freq in sorted_words[:max_keywords]]
        
        return ', '.join(keywords) if keywords else '文章'
    
    def _generate_description(self, content, max_length=160):
        """
        从内容中生成描述
        
        @param {str} content - 文章内容
        @param {int} max_length - 最大长度
        @return {str} - 描述文本
        """
        # 提取第一段作为描述
        paragraphs = content.strip().split('\n\n')
        if paragraphs:
            description = paragraphs[0].strip()
            # 移除 Markdown 标记
            description = re.sub(r'#+\s*', '', description)
            description = re.sub(r'[*_`]', '', description)
            
            if len(description) > max_length:
                description = description[:max_length-3] + '...'
            return description
        
        return content[:max_length].strip()
    
    def _render_template(self, content_html, page_title, keywords, description, lang='zh-CN', powered_by='深表美文-文本转美页面', article_id=None, publish_date=None, modify_date=None):
        """
        将内容嵌入 HTML 模板
        
        @param {str} content_html - LLM 生成的内容 HTML
        @param {str} page_title - 页面标题
        @param {str} keywords - 关键词
        @param {str} description - 描述
        @param {str} lang - 语言代码
        @param {str} powered_by - 底部标识文本
        @param {str} article_id - 文章 ID（用于生成 URL）
        @param {str} publish_date - 发布日期
        @param {str} modify_date - 修改日期
        @return {str} - 完整的 HTML
        """
        try:
            # 读取模板文件
            template_path = os.path.join(os.path.dirname(__file__), 'templates', 'article.html')
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            
            # 如果未提供日期，使用当前时间
            from datetime import datetime
            if not publish_date:
                publish_date = datetime.now().strftime('%Y-%m-%d')
            if not modify_date:
                modify_date = datetime.now().strftime('%Y-%m-%d')
            
            # 如果未提供 article_id，使用默认值
            if not article_id:
                article_id = 'unknown'
            
            # 填充模板变量
            html = template.format(
                lang=lang,
                page_title=page_title,
                keywords=keywords,
                description=description,
                content=content_html,
                powered_by=powered_by,
                article_id=article_id,
                publish_date=publish_date,
                modify_date=modify_date
            )
            
            logger.info(f"模板渲染完成，HTML 长度：{len(html)}")
            return html
        except Exception as e:
            logger.error(f"模板渲染失败：{str(e)}，使用基础 HTML")
            import traceback
            logger.error(traceback.format_exc())
            return self._create_fallback_html_from_content(content_html, page_title)
    
    def _create_fallback_html_from_content(self, content_html, title=None):
        """
        当模板渲染失败时，创建基础的 HTML
        
        @param {str} content_html - 内容 HTML
        @param {str} title - 标题
        @return {str} - 基础 HTML
        """
        logger.warning("使用基础 HTML 模板作为备选方案")
        
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
            {content_html}
        </div>
    </article>
</body>
</html>"""
    
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


def main():
    """
    主函数 - 用于测试
    """
    # 测试不同模型
    models = ['deepseek', 'qwen']
    
    for model in models:
        logger.info(f"\n{'='*50}")
        logger.info(f"测试 {model.upper()} 模型")
        logger.info(f"{'='*50}\n")
        
        try:
            client = LLMClient(model_name=model)
            
            # 测试博客生成
            logger.info("测试博客生成...")
            title, content = client.generate_blog()
            if title and content:
                logger.info(f"博客生成成功 - 标题：{title}")
                logger.info(f"内容长度：{len(content)}字符")
            else:
                logger.error("博客生成失败")
            
            # 测试标题生成
            logger.info("\n测试标题生成...")
            test_content = "这是一段测试内容，用于验证标题生成功能。"
            generated_title = client.generate_title(test_content)
            logger.info(f"生成的标题：{generated_title}")
            
        except Exception as e:
            logger.error(f"{model} 模型测试失败：{str(e)}")


if __name__ == "__main__":
    main()
