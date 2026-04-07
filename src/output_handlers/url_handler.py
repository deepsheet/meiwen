#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
URL Output Handler
Handles saving HTML files and returning access URLs.
"""

import os
from src.output_handlers.base_handler import OutputHandler
from src.logger import logger


class UrlOutputHandler(OutputHandler):
    """Handler for URL (HTML) output format."""
    
    def __init__(self, app_root, save_mapping_func):
        self.app_root = app_root
        self.save_mapping_func = save_mapping_func
    
    def handle(self, content, title, article_id, filename=None):
        """
        Save HTML content and return access URL.
        """
        try:
            userfiles_dir = os.path.join(self.app_root, 'userdata', 'userfiles')
            if not os.path.exists(userfiles_dir):
                os.makedirs(userfiles_dir)
            
            # Use provided filename or generate one
            if not filename:
                from src.web_server import generate_smart_filename
                filename = generate_smart_filename(title, article_id)
            
            filepath = os.path.join(userfiles_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"HTML file saved: {filepath}")
            
            relative_filepath = f"userdata/userfiles/{filename}"
            self.save_mapping_func(article_id, relative_filepath)
            
            access_url = f"/p/{article_id}"
            
            return {
                "status": "success",
                "access_url": access_url,
                "output_format": "url"
            }
        except Exception as e:
            logger.error(f"UrlOutputHandler failed: {str(e)}")
            raise
