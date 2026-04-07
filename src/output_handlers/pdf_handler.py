#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PDF Output Handler
Handles converting HTML to PDF and saving it.
"""

import os
import re
from xhtml2pdf import pisa
from src.output_handlers.base_handler import OutputHandler
from src.logger import logger


class PdfOutputHandler(OutputHandler):
    """Handler for PDF output format."""
    
    def __init__(self, app_root, save_mapping_func):
        self.app_root = app_root
        self.save_mapping_func = save_mapping_func
    
    def _clean_css_for_pdf(self, html_content):
        """
        清理 HTML 中 xhtml2pdf 不支持的 CSS3 特性（如 @keyframes, transform 等）
        """
        # 移除 @keyframes 块（处理多行情况）
        html_content = re.sub(r'@keyframes\s+[\w-]+\s*\{.*?\}', '', html_content, flags=re.DOTALL)
        # 移除 @media 查询（xhtml2pdf 支持有限，且容易引发解析错误）
        html_content = re.sub(r'@media\s+[\w\s()]+\s*\{.*?\}', '', html_content, flags=re.DOTALL)
        # 移除 animation 属性
        html_content = re.sub(r'animation\s*:[^;]*;', '', html_content)
        html_content = re.sub(r'-webkit-animation\s*:[^;]*;', '', html_content)
        # 移除 transform 属性 (xhtml2pdf 支持有限，容易报错)
        html_content = re.sub(r'transform\s*:[^;]*;', '', html_content)
        html_content = re.sub(r'-webkit-transform\s*:[^;]*;', '', html_content)
        # 移除 transition
        html_content = re.sub(r'transition\s*:[^;]*;', '', html_content)
        return html_content

    def handle(self, content, title, article_id, filename=None):
        """
        Convert HTML content to PDF and save it.
        """
        try:
            userfiles_dir = os.path.join(self.app_root, 'userdata', 'userfiles')
            if not os.path.exists(userfiles_dir):
                os.makedirs(userfiles_dir)
            
            # Generate filename
            if not filename:
                from src.web_server import generate_smart_filename
                base_name = generate_smart_filename(title, article_id).replace('.html', '')
                filename = f"{base_name}.pdf"
            else:
                filename = filename.replace('.html', '.pdf')
            
            filepath = os.path.join(userfiles_dir, filename)
            
            # 预处理 HTML：清理不兼容的 CSS
            cleaned_content = self._clean_css_for_pdf(content)
            
            # 转换 HTML 为 PDF
            with open(filepath, "w+b") as result_file:
                pisa_status = pisa.CreatePDF(cleaned_content, dest=result_file)
            
            if pisa_status.err:
                logger.error("xhtml2pdf 转换过程中出现错误")
                raise Exception("PDF generation failed due to content errors")
            
            logger.info(f"PDF file saved: {filepath}")
            
            relative_filepath = f"userdata/userfiles/{filename}"
            self.save_mapping_func(article_id, relative_filepath)
            
            access_url = f"/p/{article_id}"
            download_url = f"/api/download-pdf/{article_id}"
            
            return {
                "status": "success",
                "access_url": access_url,
                "download_url": download_url,
                "output_format": "pdf"
            }
        except Exception as e:
            logger.error(f"PdfOutputHandler failed: {str(e)}")
            raise
