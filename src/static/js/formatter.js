
let currentResultUrl = '';

/**
 * 初始化页面状态
 */
function initPageState() {
    // 从 localStorage 读取更多设置的状态
    const moreSettingsVisible = localStorage.getItem('moreSettingsVisible') === 'true';
    
    if (moreSettingsVisible) {
        const container = document.getElementById('moreSettingsContainer');
        const toggleBtn = document.getElementById('toggleMoreSettingsBtn');
        container.style.display = 'block';
        toggleBtn.innerHTML = '⚙️ 收起高级设置';
        toggleBtn.classList.add('active');
    }
    
    // 恢复扩写模式
    const savedBeautyMode = localStorage.getItem('beautyMode');
    if (savedBeautyMode) {
        const radioButtons = document.querySelectorAll('input[name="beautyMode"]');
        radioButtons.forEach(radio => {
            if (radio.value === savedBeautyMode) {
                radio.checked = true;
            }
        });
    }
    
    // 恢复样式风格
    const savedStyle = localStorage.getItem('selectedStyle');
    if (savedStyle) {
        document.getElementById('selectedStyle').value = savedStyle;
        const styleNameMap = {
            'auto': '自动匹配',
            'default': '默认排版',
            'minimalist': '极简主义',
            'neon_glass': '霓虹玻璃',
            'magazine_gradient': '杂志渐变',
            'cyberpunk_neon': '赛博朋克',
            'minimalist_timeline': '极简时间线',
            'gradient_glass': '渐变玻璃',
            'bold_waves': '粗犷波浪',
            'space_cosmic': '太空宇宙',
            'swiss_grid': '瑞士网格',
            'handdrawn_notes': '手绘笔记',
            'dark_luxury': '暗黑奢华',
            'pastel_soft': '柔和粉彩',
            'brutalist_bold': '粗野主义',
            'kawaii_bubbles': '可爱气泡',
            'newspaper_classic': '报纸排版',
            'geometric_modern': '几何现代'
        };
        // 简单的国际化处理，实际项目中应从后端获取
        const lang = document.documentElement.lang;
        if (lang === 'en') {
             // 这里可以补充英文映射，为了简洁暂时省略，或者统一用英文 key
        }
        document.getElementById('selectedStyleText').textContent = styleNameMap[savedStyle] || '自动匹配';
        
        // 更新下拉菜单的选中状态
        document.querySelectorAll('.style-option').forEach(option => {
            option.classList.remove('selected');
            if (option.dataset.style === savedStyle) {
                option.classList.add('selected');
            }
        });
    }
    
    // 恢复输出格式
    const savedOutputFormat = localStorage.getItem('outputFormat');
    if (savedOutputFormat) {
        const formatRadios = document.querySelectorAll('input[name="outputFormat"]');
        formatRadios.forEach(radio => {
            if (radio.value === savedOutputFormat) {
                radio.checked = true;
            }
        });
    }
}

// 页面加载时初始化状态
window.addEventListener('DOMContentLoaded', initPageState);

/**
 * 格式化 HTML
 */
async function formatHTML() {
    const titleInput = document.getElementById('title');
    const contentInput = document.getElementById('content');
    const extraRequirementsInput = document.getElementById('extraRequirements');
    const formatBtn = document.getElementById('formatBtn');
    const errorMessage = document.getElementById('errorMessage');
    const resultSection = document.getElementById('resultSection');
    const resultLink = document.getElementById('resultLink');
    
    // 验证输入
    if (!contentInput.value.trim()) {
        showError('请输入要美化的文章内容');
        return;
    }
    
    // 检测 URL 格式
    const inputValue = contentInput.value.trim();
    const urlValidation = validateUrlInput(inputValue);
    
    // 如果检测到 URL 相关问题，显示错误并返回
    if (urlValidation.hasError) {
        showError(urlValidation.message);
        return;
    }
    
    const isUrl = urlValidation.isUrl;
    
    // 获取选中的美化模式
    const selectedMode = document.querySelector('input[name="beautyMode"]:checked').value;
    
    // 获取样式风格
    const selectedStyle = document.getElementById('selectedStyle').value;
    
    // 获取额外要求
    const extraRequirements = extraRequirementsInput.value.trim();
    
    // 获取输出格式
    const outputFormat = document.querySelector('input[name="outputFormat"]:checked').value;
    
    // 清空之前的错误和结果
    hideError();
    resultSection.classList.remove('show');
    
    // 禁用按钮，显示加载状态
    formatBtn.disabled = true;
    formatBtn.innerHTML = '<span class="loading-spinner"></span>正在处理中...';
    
    try {
        const response = await fetch('/api/format-html', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title: titleInput.value.trim(),  // 可以为空
                content: inputValue,
                is_url: isUrl,  // 标记是否为 URL
                content_strategy: selectedMode,  // 传递美化模式参数
                style: selectedStyle,  // 传递样式风格参数
                extra_requirements: extraRequirements,  // 传递额外要求参数
                output_format: outputFormat  // 传递输出格式参数
            })
        });
        
        const data = await response.json();
        
        if (response.ok && data.status === 'success') {
            // 显示成功结果
            currentResultUrl = window.location.origin + data.access_url;
            resultLink.href = data.access_url;
            resultLink.textContent = currentResultUrl;
            
            // 根据输出格式显示不同的提示和操作
            const resultHint = document.getElementById('resultHint');
            const downloadBtn = document.getElementById('downloadBtn');
            const i18nHints = document.getElementById('i18nHints');
            
            if (data.output_format === 'pdf') {
                resultHint.textContent = i18nHints.dataset.pdfHint;
                downloadBtn.style.display = 'inline-block';
                downloadBtn.dataset.downloadUrl = data.download_url || data.access_url;
            } else {
                resultHint.textContent = i18nHints.dataset.urlHint;
                downloadBtn.style.display = 'none';
            }
            
            resultSection.classList.add('show');
            
            // 滚动到结果区域
            resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        } else {
            showError(data.message || '格式化失败，请稍后重试');
        }
    } catch (error) {
        showError(`请求失败：${error.message}`);
    } finally {
        // 恢复按钮状态
        formatBtn.disabled = false;
        formatBtn.innerHTML = '🎨 开始美化';
    }
}

/**
 * 复制链接
 */
function copyLink() {
    const linkText = currentResultUrl;
    navigator.clipboard.writeText(linkText).then(() => {
        const copyBtn = document.querySelector('.copy-btn');
        const originalText = copyBtn.textContent;
        copyBtn.textContent = '✅ 已复制！';
        setTimeout(() => {
            copyBtn.textContent = originalText;
        }, 2000);
    }).catch(err => {
        showError('复制失败，请手动复制');
    });
}

/**
 * 显示错误信息
 */
function showError(message) {
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.textContent = message;
    errorMessage.classList.add('show');
}

/**
 * 隐藏错误信息
 */
function hideError() {
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.classList.remove('show');
}

/**
 * 切换额外要求输入框的显示/隐藏
 */
function toggleExtraRequirements() {
    const container = document.getElementById('extraRequirementsContainer');
    const toggleBtn = document.getElementById('toggleExtraBtn');
    
    if (container.style.display === 'none') {
        // 显示输入框
        container.style.display = 'block';
        toggleBtn.innerHTML = '📋 收起额外要求';
        toggleBtn.classList.add('active');
        
        // 聚焦到输入框
        setTimeout(() => {
            document.getElementById('extraRequirements').focus();
        }, 100);
    } else {
        // 隐藏输入框
        container.style.display = 'none';
        toggleBtn.innerHTML = '📋 添加额外要求';
        toggleBtn.classList.remove('active');
    }
}

/**
 * 切换文章标题输入框的显示/隐藏
 */
function toggleArticleTitle() {
    const container = document.getElementById('articleTitleContainer');
    const toggleBtn = document.getElementById('toggleTitleBtn');
    
    if (container.style.display === 'none') {
        // 显示输入框
        container.style.display = 'block';
        toggleBtn.innerHTML = '🏷️ 收起文章标题';
        toggleBtn.classList.add('active');
        
        // 聚焦到输入框
        setTimeout(() => {
            document.getElementById('title').focus();
        }, 100);
    } else {
        // 隐藏输入框
        container.style.display = 'none';
        toggleBtn.innerHTML = '🏷️ 添加文章标题';
        toggleBtn.classList.remove('active');
    }
}

/**
 * 切换更多设置显示/隐藏
 */
function toggleMoreSettings() {
    const container = document.getElementById('moreSettingsContainer');
    const toggleBtn = document.getElementById('toggleMoreSettingsBtn');
    
    if (container.style.display === 'none') {
        // 显示进阶区
        container.style.display = 'block';
        toggleBtn.innerHTML = '⚙️ 收起设置';
        toggleBtn.classList.add('active');
        localStorage.setItem('moreSettingsVisible', 'true');
    } else {
        // 隐藏进阶区
        container.style.display = 'none';
        toggleBtn.innerHTML = '⚙️ 更多设置';
        toggleBtn.classList.remove('active');
        localStorage.setItem('moreSettingsVisible', 'false');
    }
}

// 支持 Ctrl+Enter 快速提交
document.getElementById('content').addEventListener('keydown', function(e) {
    if (e.ctrlKey && e.key === 'Enter') {
        formatHTML();
    }
});

// 为扩写模式的单选按钮添加事件监听器，保存选择状态
document.querySelectorAll('input[name="beautyMode"]').forEach(radio => {
    radio.addEventListener('change', function() {
        localStorage.setItem('beautyMode', this.value);
    });
});

/**
 * 插入预设文本到额外要求输入框
 */
function insertPreset(presetNumber) {
    const textarea = document.getElementById('extraRequirements');
    
    // 定义预设文本（根据当前语言）
    const currentLang = document.documentElement.lang || 'zh';
    
    let presets;
    if (currentLang === 'en') {
        presets = {
            1: 'Design unique styles for certain words to emphasize them',
            2: 'Use gradient backgrounds and rounded cards to highlight important paragraphs',
            3: 'Add eye-catching icons and animations next to key data',
            4: 'Use contrasting colors to highlight core viewpoints and conclusions'
        };
    } else {
        presets = {
            1: '可以为某些词或字设计独特的样式以表示强调',
            2: '使用渐变色背景和圆角卡片突出重要段落',
            3: '在关键数据旁添加醒目的图标和动画效果',
            4: '使用对比色高亮显示核心观点和结论'
        };
    }
    
    const presetText = presets[presetNumber];
    if (!presetText) return;
    
    // 获取当前文本
    const currentText = textarea.value;
    
    // 如果已有内容，添加换行符
    if (currentText.trim()) {
        textarea.value = currentText + '\n' + presetText;
    } else {
        textarea.value = presetText;
    }
    
    // 聚焦到输入框
    textarea.focus();
    
    // 滚动到底部
    textarea.scrollTop = textarea.scrollHeight;
}

/**
 * 验证 URL 输入
 * @param {string} input - 用户输入的内容
 * @returns {object} - { hasError: boolean, message: string, isUrl: boolean }
 */
function validateUrlInput(input) {
    // 1. 检查是否包含多个 URL（通过换行、空格或逗号分隔）
    // 使用正则表达式匹配 http/https 链接
    const urlRegex = /https?:\/\/[^\s,]+/g;
    const matches = input.match(urlRegex);
    
    if (matches && matches.length > 1) {
        return {
            hasError: true,
            message: '目前仅支持单个网址链接。检测到您输入了多个链接，请只粘贴一个链接进行美化。',
            isUrl: false
        };
    }
    
    // 2. 检查是否是单个有效的 URL
    try {
        const url = new URL(input.trim());
        // 检查协议是否为 http 或 https
        if (url.protocol !== 'http:' && url.protocol !== 'https:') {
            return {
                hasError: true,
                message: '不支持的链接协议。请使用 http:// 或 https:// 开头的网址。',
                isUrl: false
            };
        }
        return {
            hasError: false,
            message: '',
            isUrl: true
        };
    } catch (_) {
        // 3. 如果不是标准 URL，但看起来像链接（例如包含 http 但格式有误）
        if (input.toLowerCase().includes('http')) {
            // 再次检查是否有多个 http 出现
            const httpCount = (input.match(/http/gi) || []).length;
            if (httpCount > 1) {
                return {
                    hasError: true,
                    message: '目前仅支持单个网址链接。检测到您输入了多个链接，请只粘贴一个链接进行美化。',
                    isUrl: false
                };
            }
        }
        
        // 不是有效的 URL，作为普通文本处理
        return {
            hasError: false,
            message: '',
            isUrl: false
        };
    }
}

/**
 * 下载文件
 */
function downloadFile() {
    const downloadBtn = document.getElementById('downloadBtn');
    const url = downloadBtn.dataset.downloadUrl;
    if (url) {
        window.open(url, '_blank');
    }
}

/**
 * 验证是否为有效的 URL（保留用于向后兼容）
 */
function isValidUrl(string) {
    try {
        new URL(string);
        return true;
    } catch (_) {
        return false;
    }
}
