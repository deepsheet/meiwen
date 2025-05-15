#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DeepSeek API客户端：负责与DeepSeek API进行交互生成博客内容
"""

import sys
import os
import json
import requests
import random
import re

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.config import DEEPSEEK_API_KEY, DEEPSEEK_API_URL, BLOG_TOPICS
from src.logger import logger

class DeepSeekClient:
    """
    DeepSeek API客户端类
    """
    def __init__(self):
        """
        初始化DeepSeek API客户端
        """
        self.api_key = DEEPSEEK_API_KEY
        self.api_url = DEEPSEEK_API_URL
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def generate_blog(self, topic=None):
        """
        生成博客内容和标题
        
        @param {str} topic - 可选的博客主题，如果不提供则随机选择一个
        @return {tuple} - (标题, 内容)元组
        """
        if not topic:
            topic = random.choice(BLOG_TOPICS)
        
        logger.info(f"开始生成博客，主题：{topic}")
        
        try:
            prompt = self._create_prompt(topic)
            response = self._call_api(prompt)
            blog_content = self._parse_response(response)
            
            # 提取标题和内容
            title, content = self._extract_title_and_content(blog_content)
            
            # 检查内容是否包含可能导致SQL插入失败的字符
            clean_title = self._sanitize_content(title)
            clean_content = self._sanitize_content(content)
            
            logger.info(f"博客生成成功，标题：{clean_title}，内容长度：{len(clean_content)}字符")
            return clean_title, clean_content
        except Exception as e:
            logger.error(f"博客生成失败：{str(e)}")
            return None, None
    
    def _create_prompt(self, topic):
        """
        创建用于生成博客的提示
        
        @param {str} topic - 博客主题
        @return {str} - 格式化的提示文本
        """
        return {
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位专业的技术博客作者，擅长撰写关于云计算、AI和协作工具的文章。请生成一篇原创、信息丰富且吸引人的博客文章。"
                },
                {
                    "role": "user",
                    "content": f"""请为isheet.net网站编写一篇原创博客文章，主题是"{topic}"。
要求：
1. 文章长度在800-1200字之间
2. 包含一个吸引人的标题，标题前使用'# '标记
3. 内容包含适当的小标题和段落
4. 提供实用的信息和相关案例
5. 使用专业但易懂的语言
6. 避免使用特殊字符，特别是引号、反斜杠等可能导致SQL插入错误的字符
7. 确保内容是中文的
8. 结尾鼓励读者尝试或了解isheet.net的服务"""
                }
            ],
            "model": "deepseek-chat",  # 根据实际可用模型调整
            "temperature": 0.7,
            "max_tokens": 2000
        }
    
    def _call_api(self, prompt):
        """
        调用DeepSeek API
        
        @param {dict} prompt - API请求的提示信息
        @return {dict} - API响应
        """
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=prompt,
                timeout=120  # 增加超时时间到120秒
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"DeepSeek API请求失败：{str(e)}")
            raise
    
    def _parse_response(self, response):
        """
        解析API响应获取生成的内容
        
        @param {dict} response - API响应
        @return {str} - 解析后的内容
        """
        try:
            # 请根据实际的DeepSeek API响应格式调整
            return response["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            logger.error(f"解析API响应失败：{str(e)}")
            logger.error(f"API响应：{json.dumps(response, ensure_ascii=False)}")
            raise
    
    def _extract_title_and_content(self, full_text):
        """
        从生成的文本中提取标题和内容
        
        @param {str} full_text - 生成的完整文本
        @return {tuple} - (标题, 内容)元组
        """
        # 查找以'# '开头的标题
        title_match = re.search(r'# (.+?)[\n\r]', full_text)
        
        if title_match:
            title = title_match.group(1).strip()
            # 从内容中移除标题行
            content = re.sub(r'# .+?[\n\r]', '', full_text, count=1).strip()
        else:
            # 如果没有找到标题格式，使用全文的第一行作为标题
            lines = full_text.split('\n')
            title = lines[0].strip().replace('#', '').strip()
            content = '\n'.join(lines[1:]).strip()
            
            # 如果第一行内容太长，可能不是标题，创建一个默认标题
            if len(title) > 50:
                title = "iSheet.net云表格技术博客"
                content = full_text
        
        return title, content
    
    def _sanitize_content(self, content):
        """
        清理内容中可能导致SQL插入失败的字符
        
        @param {str} content - 原始内容
        @return {str} - 清理后的内容
        """
        if not content:
            return ""
            
        # 替换单引号、双引号和反斜杠，以避免SQL注入问题
        sanitized = content.replace("'", "''").replace("\\", "\\\\")
        
        # 删除其他可能导致问题的特殊字符
        # 根据实际需要增加更多替换规则
        
        return sanitized
    
    def retry_with_sanitized_content(self, original_title, original_content):
        """
        当插入失败时，尝试重新清理内容或生成新内容
        
        @param {str} original_title - 原始标题
        @param {str} original_content - 原始内容
        @return {tuple} - (清理后的标题, 清理后的内容)元组
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