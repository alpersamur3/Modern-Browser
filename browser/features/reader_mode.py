import html
import logging

from PyQt5.QtCore import QObject, pyqtSignal

log = logging.getLogger(__name__)

EXTRACT_CONTENT_JS = r'''
(function() {
    function getMainContent() {
        var selectors = ['article', '[role="main"]', 'main', '.post-content',
                         '.article-content', '.entry-content', '#content', '.content'];
        for (var i = 0; i < selectors.length; i++) {
            var el = document.querySelector(selectors[i]);
            if (el && el.textContent.trim().length > 200) {
                return el.innerHTML;
            }
        }
        var paragraphs = document.querySelectorAll('p');
        var html_parts = [];
        for (var j = 0; j < paragraphs.length; j++) {
            if (paragraphs[j].textContent.trim().length > 50) {
                html_parts.push(paragraphs[j].outerHTML);
            }
        }
        if (html_parts.length > 0) {
            return html_parts.join('\n');
        }
        return document.body ? document.body.innerHTML : '';
    }

    function getMetadata() {
        var title = document.title || '';
        var author = '';
        var desc = '';
        var metaAuthor = document.querySelector('meta[name="author"]');
        if (metaAuthor) author = metaAuthor.content;
        var metaDesc = document.querySelector('meta[name="description"]');
        if (metaDesc) desc = metaDesc.content;
        return {title: title, author: author, description: desc};
    }

    var content = getMainContent();
    var meta = getMetadata();
    return {content: content, title: meta.title, author: meta.author,
            description: meta.description};
})();
'''


class ReaderMode(QObject):
    mode_changed = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._active = False
        self._tab = None
        self._original_url = None

    @property
    def is_active(self):
        return self._active

    def toggle(self, tab, dark_mode=False):
        if self._active:
            self.deactivate()
        else:
            self.activate(tab, dark_mode)

    def activate(self, tab, dark_mode=False):
        self._tab = tab
        self._original_url = tab.url().toString()
        tab.page().runJavaScript(
            EXTRACT_CONTENT_JS,
            lambda result: self._apply_reader(result, dark_mode)
        )

    def _apply_reader(self, result, dark_mode):
        if not result or not self._tab:
            return

        content = result.get('content', '')
        raw_title = result.get('title', '')
        raw_author = result.get('author', '')

        safe_title = html.escape(raw_title)
        safe_author = html.escape(raw_author)

        page_html = self._build_reader_html(content, safe_title, safe_author, dark_mode)
        self._tab.setHtml(page_html)
        self._active = True
        self.mode_changed.emit(True)

    def deactivate(self):
        if self._tab and self._original_url:
            from PyQt5.QtCore import QUrl
            self._tab.setUrl(QUrl(self._original_url))
        self._active = False
        self._tab = None
        self._original_url = None
        self.mode_changed.emit(False)

    def _build_reader_html(self, content, title, author, dark_mode):
        bg = '#1a1a2e' if dark_mode else '#fefefe'
        fg = '#e0e0e0' if dark_mode else '#2d2d2d'
        accent = '#7c83ff' if dark_mode else '#4a90d9'
        link = '#9db4ff' if dark_mode else '#2563eb'
        border_color = '#333' if dark_mode else '#e0e0e0'
        code_bg = '#2d2d44' if dark_mode else '#f5f5f5'

        author_html = f'<p class="author">{author}</p>' if author else ''

        return f'''<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
        background-color: {bg};
        color: {fg};
        font-family: 'Georgia', 'Palatino', 'Times New Roman', serif;
        font-size: 19px;
        line-height: 1.8;
        max-width: 680px;
        margin: 0 auto;
        padding: 48px 24px;
    }}
    h1 {{
        font-family: 'Segoe UI', system-ui, sans-serif;
        font-size: 32px;
        line-height: 1.3;
        margin-bottom: 8px;
        color: {fg};
    }}
    .author {{
        color: {accent};
        font-size: 15px;
        margin-bottom: 32px;
        font-style: italic;
    }}
    p {{ margin-bottom: 1.2em; }}
    a {{ color: {link}; text-decoration: none; border-bottom: 1px solid transparent; }}
    a:hover {{ border-bottom-color: {link}; }}
    img {{ max-width: 100%; height: auto; border-radius: 8px; margin: 16px 0; }}
    blockquote {{
        border-left: 3px solid {accent};
        padding-left: 16px;
        margin: 16px 0;
        font-style: italic;
        opacity: 0.85;
    }}
    code {{
        background: {code_bg};
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.9em;
    }}
    pre {{
        background: {code_bg};
        padding: 16px;
        border-radius: 8px;
        overflow-x: auto;
        margin: 16px 0;
    }}
    pre code {{ background: none; padding: 0; }}
    hr {{ border: none; border-top: 1px solid {border_color}; margin: 32px 0; }}
    .reader-toolbar {{
        position: fixed;
        top: 16px;
        right: 16px;
        display: flex;
        gap: 8px;
    }}
    .reader-btn {{
        background: {code_bg};
        border: 1px solid {border_color};
        color: {fg};
        padding: 8px 12px;
        border-radius: 8px;
        cursor: pointer;
        font-size: 14px;
    }}
    .reader-btn:hover {{ background: {accent}; color: #fff; }}
</style>
</head>
<body>
<div class="reader-toolbar">
    <button class="reader-btn" onclick="document.body.style.fontSize=parseFloat(getComputedStyle(document.body).fontSize)+2+'px'">A+</button>
    <button class="reader-btn" onclick="document.body.style.fontSize=parseFloat(getComputedStyle(document.body).fontSize)-2+'px'">A-</button>
</div>
<h1>{title}</h1>
{author_html}
<hr>
{content}
</body>
</html>'''

    def set_font_size(self, size):
        if self._tab and self._active:
            self._tab.page().runJavaScript(f"document.body.style.fontSize='{size}px';")

    def cleanup(self):
        self._tab = None
        self._original_url = None
        self._active = False
