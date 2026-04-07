#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Output Handler Base Class
"""

from abc import ABC, abstractmethod


class OutputHandler(ABC):
    """Abstract base class for output handlers."""
    
    @abstractmethod
    def handle(self, content, title, article_id, **kwargs):
        """
        Handle the output generation.
        
        @param {str} content - The formatted HTML content.
        @param {str} title - The article title.
        @param {str} article_id - The unique article ID.
        @return {dict} - A dictionary containing status, access_url, and optional download_url.
        """
        pass
