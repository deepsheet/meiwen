#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Web服务器模块：提供HTTP接口，处理博客生成请求
"""

import sys
import os
import time
import uuid
import random
import string
import re
from flask import Flask, jsonify, send_from_directory, request, render_template_string, redirect, render_template

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.blog_generator import BlogGenerator
from src.html_formatter import HTMLFormatter
from src.llm_client import LLMClient
from src.logger import logger
from src.i18n import get_language_from_request, get_translation, create_language_response
from src.output_handlers.url_handler import UrlOutputHandler
from src.output_handlers.pdf_handler import PdfOutputHandler
import redis
from config.config import REDIS_CONFIG, CURRENT_MODEL, DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES

from flask_cors import CORS

try:
    import requests
    from bs4 import BeautifulSoup
    HAS_CRAWLER_DEPS = True
except ImportError:
    HAS_CRAWLER_DEPS = False
    logger.warning("未安装爬虫依赖包，URL 爬取功能不可用。请运行: pip install requests beautifulsoup4")


def generate_article_id(length=8):
    """
    生成 8 位随机小写字母的文章 ID
    
    @return {str} - 文章 ID
    """
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))


def save_article_mapping(article_id, filepath):
    """
    保存文章 ID 到文件路径的映射
    
    @param {str} article_id - 文章 ID
    @param {str} filepath - 文件相对路径（如 userdata/userfiles/xxx.html）
    """
    # app.root_path 是 src 目录，需要向上一级到项目根目录
    project_root = os.path.dirname(app.root_path)
    article_ids_dir = os.path.join(project_root, 'userdata', 'article_ids')
    if not os.path.exists(article_ids_dir):
        os.makedirs(article_ids_dir)


def crawl_url_content(url):
    """
    爬取 URL 内容并提取文本
    
    @param {str} url - 要爬取的 URL
    @return {dict} - 包含 status, content, title, message 的字典
    """
    if not HAS_CRAWLER_DEPS:
        return {
            'status': 'error',
            'message': '服务器未安装爬虫依赖包，无法爬取 URL 内容。请联系管理员安装 requests 和 beautifulsoup4。'
        }
    
    try:
        logger.info(f"开始爬取 URL: {url}")
        
        # 设置请求头，模拟浏览器访问
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
        }
        
        # 发送 HTTP 请求，超时 10 秒
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        response.raise_for_status()  # 如果状态码不是 200，抛出异常
        
        # 检测编码
        response.encoding = response.apparent_encoding
        
        # 解析 HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 移除不需要的元素
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            element.decompose()
        
        # 提取标题
        title = ''
        if soup.title:
            title = soup.title.string.strip()
        
        # 提取正文内容（尝试多个选择器）
        content = ''
        
        # 尝试常见的文章内容容器
        article_containers = [
            soup.find('article'),
            soup.find('main'),
            soup.find(id=re.compile(r'(content|article|post|main)', re.I)),
            soup.find(class_=re.compile(r'(content|article|post|main)', re.I)),
        ]
        
        # 找到最合适的容器
        best_container = None
        for container in article_containers:
            if container and len(container.get_text(strip=True)) > 100:
                best_container = container
                break
        
        if best_container:
            # 从容器中提取段落
            paragraphs = best_container.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
            content = '\n\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
        else:
            # 如果没有找到合适的容器，提取所有段落
            paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
            content = '\n\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
        
        # 清理多余空白
        content = re.sub(r'\n{3,}', '\n\n', content).strip()
        
        if not content or len(content) < 50:
            return {
                'status': 'error',
                'message': f'无法从 URL 中提取有效内容。该页面可能没有足够的文本内容，或者使用了 JavaScript 动态加载内容。'
            }
        
        logger.info(f"成功爬取 URL，标题: {title}, 内容长度: {len(content)}")
        
        return {
            'status': 'success',
            'content': content,
            'title': title,
            'message': '成功爬取 URL 内容'
        }
        
    except requests.exceptions.Timeout:
        return {
            'status': 'error',
            'message': f'爬取 URL 超时。该网站响应过慢，请稍后重试或手动复制内容。'
        }
    except requests.exceptions.ConnectionError:
        return {
            'status': 'error',
            'message': f'无法连接到该 URL。请检查链接是否正确，或网站是否可访问。'
        }
    except requests.exceptions.HTTPError as e:
        return {
            'status': 'error',
            'message': f'HTTP 错误: {e.response.status_code}。该页面可能不存在或需要权限访问。'
        }
    except Exception as e:
        error_msg = str(e)
        logger.error(f"爬取 URL 失败: {error_msg}")
        return {
            'status': 'error',
            'message': f'爬取 URL 失败: {error_msg}'
        }


def save_article_mapping(article_id, filepath):
    """
    保存文章 ID 到文件路径的映射
    
    @param {str} article_id - 文章 ID
    @param {str} filepath - 文件相对路径（如 userdata/userfiles/xxx.html）
    """
    # app.root_path 是 src 目录，需要向上一级到项目根目录
    project_root = os.path.dirname(app.root_path)
    article_ids_dir = os.path.join(project_root, 'userdata', 'article_ids')
    if not os.path.exists(article_ids_dir):
        os.makedirs(article_ids_dir)
        logger.info(f"创建目录：{article_ids_dir}")
    
    # 创建 .txt 文件，内容为文件路径
    mapping_file = os.path.join(article_ids_dir, f"{article_id}.txt")
    with open(mapping_file, 'w', encoding='utf-8') as f:
        f.write(filepath)
    
    logger.info(f"保存文章映射：{article_id} -> {filepath}")


def get_article_path_by_id(article_id):
    """
    根据文章 ID 获取文件路径
    
    @param {str} article_id - 文章 ID
    @return {str|None} - 文件路径，如果不存在则返回 None
    """
    # app.root_path 是 src 目录，需要向上一级到项目根目录
    project_root = os.path.dirname(app.root_path)
    mapping_file = os.path.join(project_root, 'userdata', 'article_ids', f"{article_id}.txt")
    if os.path.exists(mapping_file):
        with open(mapping_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return None

def get_redis_client():
    """
    获取 Redis 客户端连接
    
    @return {redis.Redis} - Redis 客户端实例
    """
    try:
        client = redis.Redis(
            host=REDIS_CONFIG['host'],
            port=REDIS_CONFIG['port'],
            password=REDIS_CONFIG['password'],
            decode_responses=True,
            socket_timeout=2,  # 连接超时 2 秒
            socket_connect_timeout=2  # 连接建立超时 2 秒
        )
        # 测试连接
        client.ping()
        logger.info("Redis 连接成功")
        return client
    except Exception as e:
        logger.warning(f"Redis 连接失败：{str(e)}")
        return None


def increment_pv(key='isheetpv'):
    """
    增加 PV 计数（总 PV 和每日 PV）
    
    @param {str} key - Redis 键名
    @return {dict} - 当前的 PV 值（总计和今日）
    """
    try:
        r = get_redis_client()
        if r:
            # 增加总 PV
            total_pv = r.incr('isheetpv')
            if REDIS_CONFIG.get('expire', 0) > 0:
                r.expire('isheetpv', REDIS_CONFIG['expire'])
            
            # 获取今日日期作为键
            today = time.strftime('%Y-%m-%d')
            daily_key = f'isheetpv:{today}'
            
            # 增加今日 PV
            daily_pv = r.incr(daily_key)
            # 设置过期时间为明天凌晨 +30 天
            expire_time = REDIS_CONFIG.get('expire', 3600 * 24 * 30)
            r.expire(daily_key, expire_time)
            
            logger.info(f"PV 增加成功 - 总计：{total_pv}, 今日：{daily_pv}")
            return {
                'total': total_pv,
                'daily': daily_pv,
                'date': today
            }
        else:
            # Redis 不可用，返回 0
            logger.debug("Redis 连接失败，PV 显示为 0")
            return {
                'total': 0,
                'daily': 0,
                'date': time.strftime('%Y-%m-%d')
            }
    except Exception as e:
        logger.error(f"增加 PV 失败：{str(e)}")
        return {'total': 0, 'daily': 0, 'date': time.strftime('%Y-%m-%d')}


def get_pv(key='isheetpv'):
    """
    获取 PV 计数（总计、今日和昨日）
    
    @param {str} key - Redis 键名
    @return {dict} - 当前的 PV 值（总计、今日和昨日）
    """
    try:
        r = get_redis_client()
        if r:
            # 获取总 PV
            total_pv = r.get('isheetpv')
            
            # 获取今日 PV
            today = time.strftime('%Y-%m-%d')
            daily_key = f'isheetpv:{today}'
            daily_pv = r.get(daily_key)
            
            # 获取昨日 PV
            yesterday = time.strftime('%Y-%m-%d', time.localtime(time.time() - 86400))
            yesterday_key = f'isheetpv:{yesterday}'
            yesterday_pv = r.get(yesterday_key)
            
            return {
                'total': int(total_pv) if total_pv else 0,
                'daily': int(daily_pv) if daily_pv else 0,
                'yesterday': int(yesterday_pv) if yesterday_pv else 0,
                'date': today
            }
        else:
            # Redis 不可用，返回 0
            logger.debug("Redis 连接失败，PV 显示为 0")
            return {
                'total': 0,
                'daily': 0,
                'yesterday': 0,
                'date': time.strftime('%Y-%m-%d')
            }
    except Exception as e:
        logger.error(f"获取 PV 失败：{str(e)}")
        return {'total': 0, 'daily': 0, 'yesterday': 0, 'date': time.strftime('%Y-%m-%d')}


def get_daily_pv_history(days=7):
    """
    获取历史每日 PV 数据
    
    @param {int} days - 获取最近多少天的数据
    @return {list} - 每日 PV 数据列表
    """
    try:
        r = get_redis_client()
        if not r:
            return []
        
        history = []
        for i in range(days):
            # 计算日期
            date = time.strftime('%Y-%m-%d', time.localtime(time.time() - i * 86400))
            daily_key = f'isheetpv:{date}'
            pv = r.get(daily_key)
            
            history.append({
                'date': date,
                'pv': int(pv) if pv else 0
            })
        
        # 按日期正序排列
        history.reverse()
        return history
    except Exception as e:
        logger.error(f"获取历史 PV 失败：{str(e)}")
        return []


app = Flask(__name__, static_folder='static', template_folder='templates')

CORS(app, resources={r"/api/*": {"origins": "*", "allow_headers": "*"}})

@app.route('/')
def index():
    """
    返回状态页面
    
    @return {Response} - HTML 页面
    """
    lang = get_language_from_request()
    response = render_template('index.html', lang=lang, t=lambda key: get_translation(key, lang))
    return create_language_response(response, lang)

@app.route('/generate-blog', methods=['GET'])
def generate_blog():
    """
    生成博客的 API 端点
    
    @return {dict} - API 响应
    """
    try:
        logger.info("收到博客生成请求")
        logger.info("开始处理博客生成任务")
        
        generator = BlogGenerator()
        success = generator.generate_and_save_blog()
        generator.close()
        
        if success:
            logger.info("博客生成任务已完成")
            # 查询刚刚插入的博客信息
            blog_info = get_latest_blog()
            return jsonify({
                "status": "success",
                "message": "博客生成成功",
                "title": blog_info.get('title', '未知'),
                "publish_time": blog_info.get('publish_time', '未知')
            })
        else:
            logger.error("博客生成任务失败")
            return jsonify({
                "status": "error",
                "message": "博客生成失败"
            })
    except Exception as e:
        error_msg = str(e)
        logger.error(f"博客生成任务异常：{error_msg}")
        return jsonify({
            "status": "error",
            "message": f"博客生成异常：{error_msg}"
        }), 500

def get_latest_blog():
    """
    获取最新插入的博客信息
    
    @return {dict} - 包含标题和发布时间的字典
    """
    import pymysql
    from config.config import DB_CONFIG
    
    try:
        conn = pymysql.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            charset=DB_CONFIG["charset"]
        )
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 查询最新的博客
        sql = "SELECT title, sys_addtime FROM oa_discussion WHERE project_id = 'blog' ORDER BY sys_addtime DESC LIMIT 1"
        cursor.execute(sql)
        result = cursor.fetchone()
        
        if result:
            return {
                'title': result['title'],
                'publish_time': result['sys_addtime'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(result['sys_addtime'], 'strftime') else result['sys_addtime']
            }
        else:
            return {}
    except Exception as e:
        logger.error(f"查询最新博客失败：{str(e)}")
        return {}
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/health', methods=['GET'])
def health_check():
    """
    健康检查接口
    
    @return {dict} - 服务状态信息
    """
    return jsonify({
        "status": "healthy",
        "service": "isheet-marketing-blog-generator",
        "time": time.strftime("%Y-%m-%d %H:%M:%S")
    })


@app.route('/api/pv', methods=['GET'])
def get_pv_api():
    """
    获取 PV 统计数据的 API 接口（总计、今日和昨日）
    
    @return {dict} - PV 数据
    """
    try:
        pv_data = get_pv('isheetpv')
        return jsonify({
            "status": "success",
            "total": pv_data['total'],
            "daily": pv_data['daily'],
            "yesterday": pv_data['yesterday'],
            "date": pv_data['date'],
            "key": "isheetpv"
        })
    except Exception as e:
        logger.error(f"获取 PV 数据失败：{str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/pv/history', methods=['GET'])
def get_pv_history_api():
    """
    获取历史 PV 统计数据的 API 接口
    
    @return {dict} - 历史 PV 数据列表
    """
    try:
        days = request.args.get('days', 7, type=int)  # 默认获取 7 天
        history = get_daily_pv_history(days)
        return jsonify({
            "status": "success",
            "days": days,
            "history": history
        })
    except Exception as e:
        logger.error(f"获取历史 PV 数据失败：{str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/html-formatter', methods=['GET'])
def html_formatter_page():
    """
    返回 HTML 格式化服务的页面
    
    @return {Response} - HTML 页面
    """
    lang = get_language_from_request()
    response = render_template('formatter.html', lang=lang, t=lambda key: get_translation(key, lang))
    return create_language_response(response, lang)


@app.route('/p/<article_id>', methods=['GET'])
def serve_article(article_id):
    """
    根据文章 ID 提供文章访问
    
    @param {str} article_id - 8 位文章 ID
    @return {Response|File} - 文章 HTML 文件或 404
    """
    increment_pv('isheetpv')     # 增加 PV 计数

    # 获取文章实际路径
    article_path = get_article_path_by_id(article_id)
    
    if not article_path:
        return jsonify({
            "status": "error",
            "message": "文章不存在"
        }), 404
    
    # 从相对路径提取文件名
    filename = os.path.basename(article_path)
    
    # 将相对路径转换为绝对路径
    # article_path 格式："userdata/userfiles/xxx.html"
    if article_path.startswith('userdata/'):
        # 移除 'userdata/' 前缀，得到相对于 userdata 文件夹的路径
        relative_path = article_path[9:]  # 移除 'userdata/'
        # app.root_path 是 src 目录，需要向上一级到项目根目录
        project_root = os.path.dirname(app.root_path)
        directory = os.path.join(project_root, 'userdata', os.path.dirname(relative_path))
    elif article_path.startswith('static/'):
        # 移除 'static/' 前缀，得到相对于 static 文件夹的路径
        relative_path = article_path[7:]  # 移除 'static/'
        directory = os.path.join(app.static_folder, os.path.dirname(relative_path))
    else:
        # 如果不是以 static/或 userdata/开头，直接使用 dirname
        directory = os.path.dirname(article_path)
    
    # 返回文件
    logger.info(f"访问文章：{article_id} -> {directory}/{filename}")
    return send_from_directory(
        directory,
        filename,
        mimetype='text/html; charset=utf-8'
    )


@app.route('/api/download-html/<article_id>', methods=['GET'])
def download_html_api(article_id):
    """
    根据文章 ID 下载 HTML 文件
    
    @param {str} article_id - 8 位文章 ID
    @return {Response} - HTML 文件下载
    """
    try:
        # 获取文章实际路径
        article_path = get_article_path_by_id(article_id)
        
        if not article_path:
            return jsonify({
                "status": "error",
                "message": "文章不存在"
            }), 404
        
        # 从相对路径提取文件名
        filename = os.path.basename(article_path)
        
        # 将相对路径转换为绝对路径
        if article_path.startswith('userdata/'):
            # 移除 'userdata/' 前缀，得到相对于 userdata 文件夹的路径
            relative_path = article_path[9:]  # 移除 'userdata/'
            # app.root_path 是 src 目录，需要向上一级到项目根目录
            project_root = os.path.dirname(app.root_path)
            filepath = os.path.join(project_root, article_path)
        elif article_path.startswith('static/'):
            # 移除 'static/' 前缀，得到相对于 static 文件夹的路径
            relative_path = article_path[7:]  # 移除 'static/'
            filepath = os.path.join(app.static_folder, relative_path)
        else:
            # 如果不是以 static/或 userdata/开头，直接使用路径
            filepath = article_path
        
        # 检查文件是否存在
        if not os.path.exists(filepath):
            return jsonify({
                "status": "error",
                "message": "文件不存在"
            }), 404
        
        logger.info(f"下载文章：{article_id} -> {filepath}")
        
        # 返回文件作为附件下载
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='text/html; charset=utf-8'
        )
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"下载 HTML 文件异常：{error_msg}")
        return jsonify({
            "status": "error",
            "message": f"下载失败：{error_msg}"
        }), 500


@app.route('/', methods=['GET'])
def landing_page():
    """
    返回美美文宣传首页
    
    @return {Response} - HTML 页面
    """
    # 重定向到 html-formatter 页面（因为首页功能已集成到 formatter.html）

    return redirect('/html-formatter')


@app.route('/favicon.ico', methods=['GET'])
def favicon():
    """
    提供网站 favicon 图标
    
    @return {Response} - favicon.ico 文件或 404
    """
    # favicon.ico 在项目根目录
    return send_from_directory(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )


@app.route('/beauty_html', methods=['GET'])
def beauty_html_page():
    """
    返回深表美文宣传页（美化 HTML 展示页）
    
    @return {Response} - HTML 页面
    """
    increment_pv('isheetpv')     # 增加 PV 计数

    from flask import send_from_directory
    return send_from_directory(
        app.static_folder,
        'index.html',
        mimetype='text/html; charset=utf-8'
    )


@app.route('/isheetmarketing', methods=['GET'])
def isheetmarketing_page():
    """
    返回 isheetmarketing 宣传页
    
    @return {Response} - HTML 页面
    """
    increment_pv('isheetpv')     # 增加 PV 计数
    return render_template('isheetmarketing.html')


@app.route('/pagelist', methods=['GET'])
def pagelist_page():
    """
    返回页面列表页
    
    @return {Response} - HTML 页面
    """
    increment_pv('isheetpv')     # 增加 PV 计数
    return render_template('pagelist.html')


def generate_landing_page_html():
    """生成首页 HTML 内容"""
    articles = get_latest_articles(20)
    featured_articles = articles[:5]
    all_articles = articles
    
    # 生成精选案例 HTML
    featured_html = ''
    for article in featured_articles:
        summary_escaped = article['summary'].replace('"', '&quot;')
        featured_html += f'''
        <div class="article-card">
            <h3 class="article-title">{article['title']}</h3>
            <p class="article-summary">{summary_escaped}</p>
            <a href="{article['url']}" class="article-link" target="_blank">阅读全文 →</a>
        </div>
        '''
    
    # 生成全部案例列表 HTML
    list_html = ''
    for article in all_articles:
        list_html += f'''
            <div class="list-item">
                <a href="{article['url']}" target="_blank">📄 {article['title']}</a>
            </div>
        '''
    
    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>深表美文·文字美化器 - 把你的文字一键变成可分享的精美页面</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
            line-height: 1.6;
            color: #333;
            overflow-x: hidden;
        }
        
        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .hero {
            min-height: 100vh;
            background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #4facfe);
            background-size: 400% 400%;
            animation: gradient 15s ease infinite;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            color: white;
            padding: 20px;
            position: relative;
            overflow: hidden;
        }
        
        .hero::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.2);
        }
        
        .hero-content {
            position: relative;
            z-index: 1;
            max-width: 900px;
        }
        
        .logo {
            font-size: 6em;
            font-weight: 700;
            margin-bottom: 20px;
            text-shadow: 0 4px 20px rgba(0,0,0,0.3);
            animation: float 3s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-20px); }
        }
        
        .slogan {
            font-size: 2em;
            margin-bottom: 30px;
            font-weight: 300;
            text-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }
        
        .cta-button {
            display: inline-block;
            padding: 18px 50px;
            background: white;
            color: #667eea;
            text-decoration: none;
            border-radius: 50px;
            font-size: 1.3em;
            font-weight: 600;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            transition: all 0.3s;
            margin: 10px;
        }
        
        .cta-button:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.4);
        }
        
        .cta-button.secondary {
            background: transparent;
            border: 3px solid white;
            color: white;
        }
        
        section {
            padding: 80px 20px;
        }
        
        .section-title {
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 60px;
            color: #667eea;
            position: relative;
        }
        
        .section-title::after {
            content: '';
            position: absolute;
            bottom: -15px;
            left: 50%;
            transform: translateX(-50%);
            width: 100px;
            height: 4px;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 2px;
        }
        
        .features {
            background: #f8f9fa;
        }
        
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 40px;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .feature-card {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            transition: all 0.3s;
            text-align: center;
        }
        
        .feature-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.2);
        }
        
        .feature-icon {
            font-size: 4em;
            margin-bottom: 20px;
        }
        
        .feature-title {
            font-size: 1.5em;
            color: #667eea;
            margin-bottom: 15px;
        }
        
        .feature-desc {
            color: #666;
            line-height: 1.8;
        }
        
        .showcase {
            background: white;
        }
        
        .article-card {
            background: #f8f9fa;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 3px 15px rgba(0,0,0,0.1);
            transition: all 0.3s;
        }
        
        .article-card:hover {
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            transform: translateY(-5px);
        }
        
        .article-title {
            font-size: 1.8em;
            color: #667eea;
            margin-bottom: 15px;
        }
        
        .article-summary {
            color: #666;
            line-height: 1.8;
            margin-bottom: 20px;
        }
        
        .article-link {
            display: inline-block;
            color: #4facfe;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .article-link:hover {
            color: #667eea;
            padding-left: 10px;
        }
        
        .article-list-section {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }
        
        .article-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .list-item {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            transition: all 0.3s;
        }
        
        .list-item:hover {
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            transform: translateY(-3px);
        }
        
        .list-item a {
            color: #667eea;
            text-decoration: none;
            font-size: 1.2em;
            font-weight: 600;
            display: block;
        }
        
        .list-item a:hover {
            color: #764ba2;
        }
        
        footer {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 40px 20px;
        }
        
        .footer-content {
            max-width: 800px;
            margin: 0 auto;
        }
        
        .team-name {
            font-size: 1.5em;
            margin-bottom: 10px;
        }
        
        .copyright {
            opacity: 0.8;
            font-size: 0.9em;
        }
        
        @media (max-width: 768px) {
            .logo {
                font-size: 3em;
            }
            .slogan {
                font-size: 1.3em;
            }
            .section-title {
                font-size: 1.8em;
            }
            .article-list {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="hero">
        <div class="hero-content">
            <div class="logo">✨ 深表美文</div>
            <div class="slogan">把你的文字一键变成可分享的精美页面</div>
            <a href="/html-formatter" class="cta-button">🎨 开始美化</a>
            <a href="#showcase" class="cta-button secondary">📖 查看案例</a>
        </div>
    </div>
    
    <section class="features">
        <h2 class="section-title">核心特性</h2>
        <div class="feature-grid">
            <div class="feature-card">
                <div class="feature-icon">🤖</div>
                <h3 class="feature-title">AI 智能排版</h3>
                <p class="feature-desc">基于先进 AI 技术，自动理解文字内容，智能匹配最佳排版风格，让每段文字都独具魅力。</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🎨</div>
                <h3 class="feature-title">精美设计</h3>
                <p class="feature-desc">渐变色主题、圆角卡片、柔和阴影，每一个细节都经过精心设计，呈现专业级视觉效果。</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">⚡</div>
                <h3 class="feature-title">快速生成</h3>
                <p class="feature-desc">只需几秒钟，普通文本瞬间变身精美 HTML 页面，高效便捷，立即可用。</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📱</div>
                <h3 class="feature-title">完全响应式</h3>
                <p class="feature-desc">完美适配各种设备，无论是手机、平板还是电脑，都能获得最佳浏览体验。</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🔗</div>
                <h3 class="feature-title">永久链接</h3>
                <p class="feature-desc">每篇美化的文章都生成独立 URL，随时分享，永久访问，传播无障碍。</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">💾</div>
                <h3 class="feature-title">离线可用</h3>
                <p class="feature-desc">所有样式内联，无需外部资源，断网环境也能完美显示，真正随时随地使用。</p>
            </div>
        </div>
    </section>
    
    <section class="showcase" id="showcase">
        <h2 class="section-title">精选案例</h2>''' + featured_html + '''
    </section>
    
    <section class="article-list-section">
        <h2 class="section-title">全部案例</h2>
        <div class="article-list">''' + list_html + '''
        </div>
    </section>
    
    <section style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center; padding: 100px 20px;">
        <h2 style="font-size: 2.5em; margin-bottom: 20px;">准备好让您的文字焕然一新了吗？</h2>
        <p style="font-size: 1.3em; margin-bottom: 40px; opacity: 0.9;">立即体验 AI 驱动的文字美化服务</p>
        <a href="/html-formatter" class="cta-button" style="background: white; color: #667eea;">🎨 免费开始使用</a>
    </section>
    
    <footer>
        <div class="footer-content">
            <div class="team-name">深表 AI 工作室</div>
            <p style="margin: 15px 0; font-size: 1.1em;">用 AI 技术，让内容创作更美好</p>
            <div class="copyright">
                &copy; 2026 深表美文·文字美化器<br>
                Powered by AI Technology
            </div>
        </div>
    </footer>
</body>
</html>'''

def get_latest_articles(limit=20):
    """
    获取最新的文章列表
    
    @param {int} limit - 返回的文章数量
    @return {list} - 文章信息列表
    """
    # app.root_path 是 src 目录，需要向上一级到项目根目录
    project_root = os.path.dirname(app.root_path)
    userfiles_dir = os.path.join(project_root, 'userdata', 'userfiles')
    
    if not os.path.exists(userfiles_dir):
        return []
    
    # 获取所有 HTML 文件，按修改时间排序
    files = []
    for filename in os.listdir(userfiles_dir):
        if filename.endswith('.html') and not filename.startswith('.'):
            filepath = os.path.join(userfiles_dir, filename)
            mtime = os.path.getmtime(filepath)
            files.append({
                'filename': filename,
                'filepath': filepath,
                'mtime': mtime
            })
    
    # 按修改时间倒序排列
    files.sort(key=lambda x: x['mtime'], reverse=True)
    
    # 提取文章信息
    articles = []
    for file in files[:limit]:
        # 从文件名提取标题（去除时间戳）
        title_parts = file['filename'].rsplit('_', 1)
        if len(title_parts) == 2 and title_parts[1].replace('.html', '').isdigit():
            title = title_parts[0]
        else:
            title = file['filename'].replace('.html', '')
        
        # 查找对应的文章 ID
        article_id = None
        # app.root_path 是 src 目录，需要向上一级到项目根目录
        project_root = os.path.dirname(app.root_path)
        article_ids_dir = os.path.join(project_root, 'userdata', 'article_ids')
        if os.path.exists(article_ids_dir):
            for id_file in os.listdir(article_ids_dir):
                if id_file.endswith('.txt'):
                    id_path = os.path.join(article_ids_dir, id_file)
                    try:
                        with open(id_path, 'r', encoding='utf-8') as f:
                            if f.read().strip() == f"userdata/userfiles/{file['filename']}":
                                article_id = id_file.replace('.txt', '')
                                break
                    except:
                        pass
        
        # 如果没有找到文章 ID，使用旧格式 URL
        if article_id:
            url = f'/p/{article_id}'
        else:
            url = f'/userdata/userfiles/{file["filename"]}'
        
        # 读取文件开头内容作为摘要
        try:
            with open(file['filepath'], 'r', encoding='utf-8') as f:
                content = f.read(500)  # 读取前 500 字符
                # 提取 <p>标签内容
                import re
                paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', content, re.DOTALL)
                summary = ''.join(paragraphs[:2])[:300] + '...' if paragraphs else '点击查看精彩内容'
                # 去除 HTML 标签
                summary = re.sub(r'<[^>]+>', '', summary)
        except:
            summary = '点击查看精彩内容'
        
        articles.append({
            'title': title,
            'url': f'/p/{file["article_id"]}',  # 使用新的短 URL 格式
            'summary': summary,
            'time': file['mtime']
        })
    
    return articles


def get_latest_pages(limit=50):
    """
    获取最新创建的网页列表（用于 pagelist 页面）
    
    @param {int} limit - 返回的页面数量
    @return {list} - 页面信息列表，包含 title, url, create_time
    """
    # app.root_path 是 src 目录，需要向上一级到项目根目录
    project_root = os.path.dirname(app.root_path)
    userfiles_dir = os.path.join(project_root, 'userdata', 'userfiles')
    
    if not os.path.exists(userfiles_dir):
        return []
    
    # 获取所有 HTML 文件，按创建时间排序
    files = []
    for filename in os.listdir(userfiles_dir):
        if filename.endswith('.html') and not filename.startswith('.'):
            filepath = os.path.join(userfiles_dir, filename)
            # 使用创建时间（ctime）或修改时间（mtime）
            ctime = os.path.getctime(filepath)
            mtime = os.path.getmtime(filepath)
            # 使用较早的时间作为创建时间
            create_time = min(ctime, mtime)
            
            files.append({
                'filename': filename,
                'filepath': filepath,
                'create_time': create_time
            })
    
    # 按创建时间倒序排列（最新的在前）
    files.sort(key=lambda x: x['create_time'], reverse=True)
    
    # 提取页面信息
    pages = []
    for file in files[:limit]:
        # 从文件名提取标题
        filename_without_ext = file['filename'].replace('.html', '')
        
        # 尝试从文件名中提取有意义的标题（去除文件ID和时间戳）
        # 新格式：文件ID_中文标题.html
        parts = filename_without_ext.split('_', 1)
        if len(parts) == 2 and len(parts[0]) == 8 and parts[0].islower() and parts[0].isalpha():
            # 这是新格式，第二部分是标题
            title = parts[1]
        else:
            # 旧格式或其他格式，直接使用文件名
            title = filename_without_ext
        
        # 查找对应的文章 ID
        article_id = None
        project_root = os.path.dirname(app.root_path)
        article_ids_dir = os.path.join(project_root, 'userdata', 'article_ids')
        if os.path.exists(article_ids_dir):
            for id_file in os.listdir(article_ids_dir):
                if id_file.endswith('.txt'):
                    id_path = os.path.join(article_ids_dir, id_file)
                    try:
                        with open(id_path, 'r', encoding='utf-8') as f:
                            if f.read().strip() == f"userdata/userfiles/{file['filename']}":
                                article_id = id_file.replace('.txt', '')
                                break
                    except:
                        pass
        
        # 生成访问 URL
        if article_id:
            url = f'/p/{article_id}'
        else:
            url = f'/userdata/userfiles/{file["filename"]}'
        
        # 格式化创建时间
        create_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file['create_time']))
        
        pages.append({
            'title': title,
            'url': url,
            'create_time': create_time_str,
            'timestamp': file['create_time']
        })
    
    return pages


def generate_landing_page():
    """生成宣传首页的 HTML"""
    articles = get_latest_articles(20)
    featured_articles = articles[:5]
    all_articles = articles
    
    # 生成精选案例 HTML
    featured_html = ''
    for article in featured_articles:
        summary_escaped = article['summary'].replace('"', '&quot;')
        featured_html += f'''
        <div class="article-card">
            <h3 class="article-title">{article['title']}</h3>
            <p class="article-summary">{summary_escaped}</p>
            <a href="{article['url']}" class="article-link" target="_blank">阅读全文 →</a>
        </div>
        '''
    
    # 生成全部案例列表 HTML
    list_html = ''
    for article in all_articles:
        list_html += f'''
            <div class="list-item">
                <a href="{article['url']}" target="_blank">📄 {article['title']}</a>
            </div>
        '''
    
    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>深表美文·文字美化器 - 把你的文字一键变成可分享的精美页面</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
            line-height: 1.6;
            color: #333;
            overflow-x: hidden;
        }
        
        /* 渐变背景动画 */
        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        /* Hero Section */
        .hero {
            min-height: 100vh;
            background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #4facfe);
            background-size: 400% 400%;
            animation: gradient 15s ease infinite;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            color: white;
            padding: 20px;
            position: relative;
            overflow: hidden;
        }
        
        .hero::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.2);
        }
        
        .hero-content {
            position: relative;
            z-index: 1;
            max-width: 900px;
        }
        
        .logo {
            font-size: 6em;
            font-weight: 700;
            margin-bottom: 20px;
            text-shadow: 0 4px 20px rgba(0,0,0,0.3);
            animation: float 3s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-20px); }
        }
        
        .slogan {
            font-size: 2em;
            margin-bottom: 30px;
            font-weight: 300;
            text-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }
        
        .cta-button {
            display: inline-block;
            padding: 18px 50px;
            background: white;
            color: #667eea;
            text-decoration: none;
            border-radius: 50px;
            font-size: 1.3em;
            font-weight: 600;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            transition: all 0.3s;
            margin: 10px;
        }
        
        .cta-button:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.4);
        }
        
        .cta-button.secondary {
            background: transparent;
            border: 3px solid white;
            color: white;
        }
        
        /* Section Styles */
        section {
            padding: 80px 20px;
        }
        
        .section-title {
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 60px;
            color: #667eea;
            position: relative;
        }
        
        .section-title::after {
            content: '';
            position: absolute;
            bottom: -15px;
            left: 50%;
            transform: translateX(-50%);
            width: 100px;
            height: 4px;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 2px;
        }
        
        /* Features */
        .features {
            background: #f8f9fa;
        }
        
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 40px;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .feature-card {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            transition: all 0.3s;
            text-align: center;
        }
        
        .feature-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.2);
        }
        
        .feature-icon {
            font-size: 4em;
            margin-bottom: 20px;
        }
        
        .feature-title {
            font-size: 1.5em;
            color: #667eea;
            margin-bottom: 15px;
        }
        
        .feature-desc {
            color: #666;
            line-height: 1.8;
        }
        
        /* Showcase */
        .showcase {
            background: white;
        }
        
        .article-card {
            background: #f8f9fa;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 3px 15px rgba(0,0,0,0.1);
            transition: all 0.3s;
        }
        
        .article-card:hover {
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            transform: translateY(-5px);
        }
        
        .article-title {
            font-size: 1.8em;
            color: #667eea;
            margin-bottom: 15px;
        }
        
        .article-summary {
            color: #666;
            line-height: 1.8;
            margin-bottom: 20px;
        }
        
        .article-link {
            display: inline-block;
            color: #4facfe;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .article-link:hover {
            color: #667eea;
            padding-left: 10px;
        }
        
        /* Article List */
        .article-list-section {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }
        
        .article-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .list-item {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            transition: all 0.3s;
        }
        
        .list-item:hover {
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            transform: translateY(-3px);
        }
        
        .list-item a {
            color: #667eea;
            text-decoration: none;
            font-size: 1.2em;
            font-weight: 600;
            display: block;
        }
        
        .list-item a:hover {
            color: #764ba2;
        }
        
        /* Footer */
        footer {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 40px 20px;
        }
        
        .footer-content {
            max-width: 800px;
            margin: 0 auto;
        }
        
        .team-name {
            font-size: 1.5em;
            margin-bottom: 10px;
        }
        
        .copyright {
            opacity: 0.8;
            font-size: 0.9em;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .logo {
                font-size: 3em;
            }
            .slogan {
                font-size: 1.3em;
            }
            .section-title {
                font-size: 1.8em;
            }
            .article-list {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <!-- Hero Section -->
    <div class="hero">
        <div class="hero-content">
            <div class="logo">✨ 深表美文</div>
            <div class="slogan">把你的文字一键变成可分享的精美页面</div>
            <a href="/html-formatter" class="cta-button">🎨 开始美化</a>
            <a href="#showcase" class="cta-button secondary">📖 查看案例</a>
        </div>
    </div>
    
    <!-- Features Section -->
    <section class="features">
        <h2 class="section-title">核心特性</h2>
        <div class="feature-grid">
            <div class="feature-card">
                <div class="feature-icon">🤖</div>
                <h3 class="feature-title">AI 智能排版</h3>
                <p class="feature-desc">基于先进 AI 技术，自动理解文字内容，智能匹配最佳排版风格，让每段文字都独具魅力。</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🎨</div>
                <h3 class="feature-title">精美设计</h3>
                <p class="feature-desc">渐变色主题、圆角卡片、柔和阴影，每一个细节都经过精心设计，呈现专业级视觉效果。</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">⚡</div>
                <h3 class="feature-title">快速生成</h3>
                <p class="feature-desc">只需几秒钟，普通文本瞬间变身精美 HTML 页面，高效便捷，立即可用。</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📱</div>
                <h3 class="feature-title">完全响应式</h3>
                <p class="feature-desc">完美适配各种设备，无论是手机、平板还是电脑，都能获得最佳浏览体验。</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🔗</div>
                <h3 class="feature-title">永久链接</h3>
                <p class="feature-desc">每段美化的文字都生成独立 URL，随时分享，永久访问，传播无障碍。</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">💾</div>
                <h3 class="feature-title">离线可用</h3>
                <p class="feature-desc">所有样式内联，无需外部资源，断网环境也能完美显示，真正随时随地使用。</p>
            </div>
        </div>
    </section>
    
    <!-- Showcase Section -->
    <section class="showcase" id="showcase">
        <h2 class="section-title">精选案例</h2>''' + featured_html + '''
    </section>
    
    <section class="article-list-section">
        <h2 class="section-title">全部案例</h2>
        <div class="article-list">''' + list_html + '''
        </div>
    </section>
    
    <section style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center; padding: 100px 20px;">
        <h2 style="font-size: 2.5em; margin-bottom: 20px;">准备好让您的文字焕然一新了吗？</h2>
        <p style="font-size: 1.3em; margin-bottom: 40px; opacity: 0.9;">立即体验 AI 驱动的文字美化服务</p>
        <a href="/html-formatter" class="cta-button" style="background: white; color: #667eea;">🎨 免费开始使用</a>
    </section>
    
    <footer>
        <div class="footer-content">
            <div class="team-name">坤极 AI 工作室</div>
            <p style="margin: 15px 0; font-size: 1.1em;">用 AI 技术，让内容创作更美好</p>
            <div class="copyright">
                &copy; 2026 深表美文·文字美化器<br>
                Powered by AI Technology
            </div>
        </div>
    </footer>
</body>
</html>'''

@app.route('/api/format-html', methods=['POST'])
def format_html_api():
    """
    HTML 格式化 API 端点
    
    @return {dict} - API 响应，包含生成文件的访问 URL
    """
    lang = get_language_from_request()
    
    try:
        data = request.get_json()
        content = data.get('content', '')
        is_url = data.get('is_url', False)  # 标记是否为 URL
        title = data.get('title', '').strip()  # 获取标题，去除首尾空格
        content_strategy = data.get('content_strategy', 'strict')  # 获取内容策略，默认为 strict
        style = data.get('style', 'auto')  # 获取样式风格，默认为 auto
        extra_requirements = data.get('extra_requirements', '')  # 获取额外要求，默认为空
        
        if not content:
            return jsonify({
                "status": "error",
                "message": get_translation('error_content_required', lang)
            }), 400
        
        # 如果是 URL，先爬取内容
        if is_url:
            logger.info(f"检测到 URL，开始爬取: {content}")
            crawl_result = crawl_url_content(content)
            
            if crawl_result['status'] == 'error':
                return jsonify({
                    "status": "error",
                    "message": crawl_result['message']
                }), 400
            
            # 使用爬取的内容
            content = crawl_result['content']
            
            # 如果用户没有提供标题，使用爬取的标题
            if not title and crawl_result.get('title'):
                title = crawl_result['title']
                logger.info(f"使用爬取的标题: {title}")
            
            logger.info(f"URL 爬取成功，内容长度: {len(content)}")
        
        logger.info(f"收到 HTML 格式化请求，标题：{title if title else '(空，需要自动生成)'}，策略：{content_strategy}，样式：{style}，额外要求：{extra_requirements if extra_requirements else '(无)'}")
        
        # 如果标题为空，调用 AI 自动生成标题
        if not title:
            logger.info("标题为空，正在调用 AI 生成标题...")
            ai_title = generate_title_by_ai(content)
            logger.info(f"AI 生成的标题：{ai_title}")
            # 使用 AI 生成的标题作为主标题
            title = ai_title
        
        # 🔴 动态获取域名：从请求中获取协议、主机和端口
        protocol = request.scheme  # http 或 https
        host = request.host  # 例如：localhost:8080 或 www.example.com
        base_url = f"{protocol}://{host}/beauty_html"
        logger.info(f"动态域名：{base_url}")
        
        # 生成文章 ID（需要在格式化前生成，以便嵌入到 HTML 中）
        article_id = generate_article_id()
        
        # 调用 HTML 格式化服务（使用配置文件中的模型）
        formatter = HTMLFormatter(base_url=base_url, model_name=CURRENT_MODEL, language=lang)
        formatted_html = formatter.format_article(content, title, content_strategy=content_strategy, style=style, extra_requirements=extra_requirements, include_download_button=True, article_id=article_id)
        
        # 获取项目根目录
        project_root = os.path.dirname(app.root_path)
        
        # 根据输出格式选择处理器
        output_format = data.get('output_format', 'url')
        
        if output_format == 'pdf':
            handler = PdfOutputHandler(project_root, save_article_mapping)
            result = handler.handle(formatted_html, title, article_id)
        else:
            handler = UrlOutputHandler(project_root, save_article_mapping)
            result = handler.handle(formatted_html, title, article_id)
        
        return jsonify({
            "status": "success",
            "message": get_translation('success_format_complete', lang),
            "access_url": result['access_url'],
            "full_url": f"http://localhost:{os.environ.get('PORT', 8080)}{result['access_url']}",
            "download_url": result.get('download_url'),
            "output_format": result['output_format'],
            "article_id": article_id
        })
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"HTML 格式化异常：{error_msg}")
        return jsonify({
            "status": "error",
            "message": get_translation('error_format_failed', lang) + f": {error_msg}"
        }), 500


def generate_title_by_ai(content):
    """
    使用先进 AI 技术根据文章内容自动生成标题
    
    @param {str} content - 文章内容
    @return {str} - 生成的标题
    """
    try:
        # 🔴 使用统一的 LLM 客户端生成标题
        lang = get_language_from_request()
        llm_client = LLMClient(model_name=CURRENT_MODEL, language=lang)
        generated_title = llm_client.generate_title(content)
        
        logger.info(f"AI 成功生成标题：{generated_title}")
        return generated_title
        
    except Exception as e:
        logger.error(f"AI 生成标题失败：{str(e)}")
        # 如果 AI 生成失败，从内容中提取前 20 个字作为标题
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


def generate_smart_filename(title, article_id=None):
    """
    根据文章标题生成智能文件名
    规则：
    1. 只保留英文字母、数字和汉字
    2. 去除所有空格和特殊字符
    3. 限制长度，避免过长
    4. 如果有 article_id，格式为：文件ID_中文标题.html
    
    @param {str} title - 文章标题
    @param {str} article_id - 文章 ID（可选）
    @return {str} - 智能文件名（包含 .html 扩展名）
    """
    import re
    
    logger.info(f"原始标题：{title}")
    
    # 如果标题为空或只有空格，使用默认名称
    if not title or not title.strip():
        logger.warning("标题为空，使用默认名称")
        title = 'untitled'
    
    # 只保留英文字母、数字和汉字，去除所有其他字符（包括空格）
    # 允许的字符：字母 (a-zA-Z)、数字 (0-9)、汉字 (\u4e00-\u9fff)
    cleaned_title = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '', title)
    
    logger.info(f"清理后标题：{cleaned_title}")
    
    # 如果清理后为空，使用默认名称
    if not cleaned_title:
        logger.warning("清理后标题为空，使用默认名称")
        cleaned_title = 'untitled'
    
    # 限制长度（最多 50 个字符，避免文件名过长）
    if len(cleaned_title) > 50:
        cleaned_title = cleaned_title[:50]
        logger.info(f"截断后标题：{cleaned_title}")
    
    # 生成文件名
    if article_id:
        # 新格式：文件ID_中文标题.html
        filename = f"{article_id}_{cleaned_title}.html"
    else:
        # 旧格式：标题_时间戳.html（向后兼容）
        import time
        timestamp = int(time.time())
        filename = f"{cleaned_title}_{timestamp}.html"
    
    logger.info(f"生成智能文件名：{filename}")
    return filename


@app.route('/api/set-language', methods=['POST'])
def set_language():
    """
    设置用户语言偏好
    
    @return {dict} - API 响应
    """
    data = request.get_json()
    lang = data.get('language', DEFAULT_LANGUAGE)
    
    if lang not in SUPPORTED_LANGUAGES:
        return jsonify({
            "status": "error",
            "message": get_translation('error_unsupported_language', lang)
        }), 400
    
    response = jsonify({
        "status": "success",
        "message": get_translation('success_language_updated', lang),
        "language": lang
    })
    
    return create_language_response(response, lang)


@app.route('/api/latest-pages', methods=['GET'])
def get_latest_pages_api():
    """
    获取最新创建的网页列表 API
    
    @return {dict} - 包含最新50个网页的列表
    """
    try:
        limit = request.args.get('limit', 50, type=int)  # 默认获取 50 个
        pages = get_latest_pages(limit)
        return jsonify({
            "status": "success",
            "count": len(pages),
            "pages": pages
        })
    except Exception as e:
        logger.error(f"获取最新页面列表失败：{str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/download-pdf/<article_id>', methods=['GET'])
def download_pdf_api(article_id):
    """
    根据文章 ID 下载 PDF 文件
    
    @param {str} article_id - 8 位文章 ID
    @return {Response} - PDF 文件下载
    """
    try:
        from flask import send_file
        
        # 获取文章实际路径
        article_path = get_article_path_by_id(article_id)
        
        if not article_path:
            return jsonify({
                "status": "error",
                "message": "文件不存在"
            }), 404
        
        # 检查是否为 PDF 文件
        if not article_path.endswith('.pdf'):
            return jsonify({
                "status": "error",
                "message": "该文章不是 PDF 格式"
            }), 400
        
        # 将相对路径转换为绝对路径
        project_root = os.path.dirname(app.root_path)
        filepath = os.path.join(project_root, article_path)
        
        # 检查文件是否存在
        if not os.path.exists(filepath):
            return jsonify({
                "status": "error",
                "message": "文件不存在"
            }), 404
        
        logger.info(f"下载 PDF：{article_id} -> {filepath}")
        
        # 返回文件作为附件下载
        return send_file(
            filepath,
            as_attachment=True,
            download_name=os.path.basename(filepath),
            mimetype='application/pdf'
        )
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"下载 PDF 文件异常：{error_msg}")
        return jsonify({
            "status": "error",
            "message": f"下载失败：{error_msg}"
        }), 500


def check_allowed_ip():
    """
    检查调用者的 IP 是否在白名单中
    
    @return {bool} - 是否允许访问
    """
    # 允许的 IP 和域名
    allowed_ips = ['127.0.0.1', 'localhost', '::1']
    allowed_domains = ['deepsheet.net', 'chaojibiaoge.com']
    
    # 获取客户端 IP
    client_ip = request.remote_addr
    
    # 检查是否在允许的 IP 列表中
    if client_ip in allowed_ips:
        logger.info(f"IP 验证通过：{client_ip}")
        return True
    
    # 检查 Host 头是否在允许的域名中
    host = request.headers.get('Host', '')
    for domain in allowed_domains:
        if domain in host:
            logger.info(f"域名验证通过：{host}")
            return True
    
    # 检查 X-Forwarded-For 或 X-Real-IP（用于反向代理场景）
    forwarded_for = request.headers.get('X-Forwarded-For', '')
    real_ip = request.headers.get('X-Real-IP', '')
    
    if forwarded_for:
        # X-Forwarded-For 可能包含多个 IP，取第一个
        first_ip = forwarded_for.split(',')[0].strip()
        if first_ip in allowed_ips:
            logger.info(f"X-Forwarded-For 验证通过：{first_ip}")
            return True
    
    if real_ip and real_ip in allowed_ips:
        logger.info(f"X-Real-IP 验证通过：{real_ip}")
        return True
    
    logger.warning(f"IP 验证失败：{client_ip}, Host: {host}")
    return False


@app.route('/api/text-to-html', methods=['POST', 'OPTIONS'])  # ← 必须包含 OPTIONS
def text_to_html_api():
    """
    文本转 HTML API（第三方工具调用接口）
    输入一段文本，返回生成的 HTML 代码或网页 URL
    
    @return {dict} - 包含 HTML 代码或 URL 的响应
    """
    # 首先检查 IP 白名单
    # if not check_allowed_ip():
    #     logger.warning("未授权的访问尝试")
    #     return jsonify({
    #         "status": "error",
    #         "message": "Access denied: Your IP is not authorized to use this API"
    #     }), 403
    
# 如果是 OPTIONS 预检请求，直接返回成功
    if request.method == 'OPTIONS':
        resp = jsonify({"status": "ok"})
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return resp
            
    lang = get_language_from_request()
    
    try:
        data = request.get_json()
        content = data.get('content', '').strip()
        title = data.get('title', '').strip()
        content_strategy = data.get('content_strategy', 'strict')
        extra_requirements = data.get('extra_requirements', '')
        response_type = data.get('response_type', 'html')  # 'html' 或 'url'
        
        if not content:
            return jsonify({
                "status": "error",
                "message": "Content is required"
            }), 400
        
        # 验证 response_type 参数
        if response_type not in ['html', 'url']:
            return jsonify({
                "status": "error",
                "message": "Invalid response_type. Must be 'html' or 'url'"
            }), 400
        
        logger.info(f"收到文本转 HTML 请求，标题：{title if title else '(空)'}, 策略：{content_strategy}, 响应类型：{response_type}")
        
        # 如果标题为空，调用 AI 自动生成标题
        if not title:
            logger.info("标题为空，正在调用 AI 生成标题...")
            ai_title = generate_title_by_ai(content)
            logger.info(f"AI 生成的标题：{ai_title}")
            title = ai_title
        
        # 🔴 动态获取域名：从请求中获取协议、主机和端口
        protocol = request.scheme  # http 或 https
        host = request.host  # 例如：localhost:8080 或 www.example.com
        base_url = f"{protocol}://{host}/beauty_html"
        logger.info(f"动态域名：{base_url}")
        
        # 生成文章 ID
        article_id = generate_article_id()
        
        # 调用 HTML 格式化服务
        formatter = HTMLFormatter(base_url=base_url, model_name=CURRENT_MODEL, language=lang)
        formatted_html = formatter.format_article(
            content, 
            title, 
            content_strategy=content_strategy, 
            extra_requirements=extra_requirements,
            include_download_button=False,  # API 返回不需要下载按钮
            article_id=article_id
        )
        
        logger.info(f"HTML 生成成功，长度：{len(formatted_html)}")
        
        # 🔴 无论哪种模式，都保存文件并创建映射，确保数据完整性
        # 创建 userfiles 目录（如果不存在）
        project_root = os.path.dirname(app.root_path)
        userfiles_dir = os.path.join(project_root, 'userdata', 'userfiles')
        if not os.path.exists(userfiles_dir):
            os.makedirs(userfiles_dir)
            logger.info(f"创建目录：{userfiles_dir}")
        
        # 生成智能文件名
        filename = generate_smart_filename(title, article_id)
        filepath = os.path.join(userfiles_dir, filename)
        
        # 保存格式化后的 HTML
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(formatted_html)
        
        logger.info(f"HTML 文件已保存：{filepath}")
        
        # 保存文章 ID 映射
        relative_filepath = f"userdata/userfiles/{filename}"
        save_article_mapping(article_id, relative_filepath)
        
        # 生成访问 URL
        access_url = f"/p/{article_id}"
        full_url = f"{protocol}://{host}{access_url}"
        
        logger.info(f"生成访问 URL：{full_url}")
        
        # 根据 response_type 返回不同的响应
        if response_type == 'url':
            # URL 模式：返回 URL 和 article_id，方便后续访问
            return jsonify({
                "status": "success",
                "message": "HTML generated and saved successfully",
                "url": access_url,
                "full_url": full_url,
                "article_id": article_id,
                "title": title
            })
        else:
            # HTML 模式：只返回 HTML 内容，不暴露 article_id
            return jsonify({
                "status": "success",
                "message": "HTML generated successfully",
                "html": formatted_html
            })
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"文本转 HTML 异常：{error_msg}")
        return jsonify({
            "status": "error",
            "message": f"Failed to generate HTML: {error_msg}"
        }), 500

def run_server(host='0.0.0.0', port=5000):
    """
    启动Web服务器
    
    @param {str} host - 主机地址
    @param {int} port - 端口号
    """
    logger.info(f"启动Web服务器，监听 {host}:{port}")
    app.run(host=host, port=port, debug=True)

if __name__ == "__main__":
    run_server() 