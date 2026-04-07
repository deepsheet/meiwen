#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PDF Output Handler
Handles converting HTML to PDF and saving it.
"""

import os
import asyncio
from playwright.async_api import async_playwright
from src.output_handlers.base_handler import OutputHandler
from src.logger import logger


class PdfOutputHandler(OutputHandler):
    """Handler for PDF output format using Playwright."""
    
    def __init__(self, app_root, save_mapping_func):
        self.app_root = app_root
        self.save_mapping_func = save_mapping_func
    
    def _html_to_pdf_sync(self, html_content, output_path):
        """
        使用 Playwright 将 HTML 转换为 PDF（同步包装器）
        """
        async def convert():
            async with async_playwright() as p:
                # 启动浏览器
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # 设置内容
                await page.set_content(html_content, wait_until='networkidle')
                
                # 生成 PDF
                await page.pdf(
                    path=output_path,
                    format='A4',
                    print_background=True,  # 打印背景色和图片
                    margin={
                        'top': '20mm',
                        'right': '20mm',
                        'bottom': '20mm',
                        'left': '20mm'
                    }
                )
                
                await browser.close()
        
        # 运行异步函数
        asyncio.run(convert())

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
            
            # 使用 Playwright 将 HTML 转换为 PDF
            logger.info("开始使用 Playwright 生成 PDF...")
            self._html_to_pdf_sync(content, filepath)
            
            # 检查文件是否真的生成了内容
            file_size = os.path.getsize(filepath)
            if file_size == 0:
                logger.error("PDF 文件生成失败：文件大小为 0")
                raise Exception("PDF file is empty")
            
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
