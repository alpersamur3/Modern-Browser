"""
Reader Mode for Modern Browser
"""

from PyQt5.QtCore import QObject, pyqtSignal


class ReaderMode(QObject):
    """Provides a clean, distraction-free reading experience"""
    
    # Signals
    mode_changed = pyqtSignal(bool)  # is_active
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._active = False
        self._original_html = None
        self._browser_tab = None
        
        # Reader mode settings
        self.font_family = "Georgia, serif"
        self.font_size = 18
        self.line_height = 1.8
        self.max_width = 700
        self.background_color = "#fafafa"
        self.text_color = "#333333"
        self.link_color = "#0066cc"
    
    @property
    def is_active(self):
        return self._active
    
    def get_extraction_script(self):
        """JavaScript to extract main content from page"""
        return """
        (function() {
            // Helper functions
            function getTextLength(element) {
                return (element.textContent || element.innerText || '').trim().length;
            }
            
            function getScore(element) {
                let score = 0;
                const tag = element.tagName.toLowerCase();
                
                // Positive signals
                if (['article', 'main', 'section'].includes(tag)) score += 25;
                if (element.id && /article|content|post|story/i.test(element.id)) score += 25;
                if (element.className && /article|content|post|story/i.test(element.className)) score += 25;
                
                // Text density
                const textLength = getTextLength(element);
                score += Math.min(textLength / 100, 50);
                
                // Paragraph count
                const paragraphs = element.getElementsByTagName('p').length;
                score += Math.min(paragraphs * 5, 30);
                
                // Negative signals
                if (/sidebar|nav|header|footer|comment|ad|menu|related/i.test(element.id)) score -= 50;
                if (/sidebar|nav|header|footer|comment|ad|menu|related/i.test(element.className)) score -= 50;
                
                return score;
            }
            
            // Find best content element
            let bestElement = null;
            let bestScore = 0;
            
            const candidates = document.querySelectorAll('article, main, section, div');
            for (const element of candidates) {
                const score = getScore(element);
                if (score > bestScore) {
                    bestScore = score;
                    bestElement = element;
                }
            }
            
            // Get content
            let title = document.title;
            const h1 = document.querySelector('h1');
            if (h1) title = h1.textContent || h1.innerText;
            
            let content = '';
            if (bestElement) {
                // Clone and clean
                const clone = bestElement.cloneNode(true);
                
                // Remove unwanted elements
                const unwanted = clone.querySelectorAll('script, style, nav, aside, footer, .ad, .ads, .social, .share, .comments');
                unwanted.forEach(el => el.remove());
                
                content = clone.innerHTML;
            } else {
                // Fallback to body
                content = document.body.innerHTML;
            }
            
            // Get images
            const images = bestElement ? 
                Array.from(bestElement.getElementsByTagName('img')).map(img => ({
                    src: img.src,
                    alt: img.alt
                })) : [];
            
            return {
                title: title,
                content: content,
                url: window.location.href,
                images: images
            };
        })();
        """
    
    def get_reader_html(self, data, dark_mode=False):
        """Generate reader mode HTML"""
        bg_color = "#1a1a1a" if dark_mode else self.background_color
        text_color = "#e0e0e0" if dark_mode else self.text_color
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{data.get('title', 'Reader Mode')}</title>
            <style>
                * {{
                    box-sizing: border-box;
                }}
                
                html, body {{
                    margin: 0;
                    padding: 0;
                    background-color: {bg_color};
                    color: {text_color};
                    font-family: {self.font_family};
                    font-size: {self.font_size}px;
                    line-height: {self.line_height};
                }}
                
                .reader-container {{
                    max-width: {self.max_width}px;
                    margin: 0 auto;
                    padding: 40px 20px;
                }}
                
                .reader-title {{
                    font-size: 2em;
                    font-weight: bold;
                    margin-bottom: 10px;
                    line-height: 1.3;
                }}
                
                .reader-meta {{
                    color: {'#888' if dark_mode else '#666'};
                    font-size: 0.9em;
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 1px solid {'#333' if dark_mode else '#ddd'};
                }}
                
                .reader-content {{
                    text-align: justify;
                }}
                
                .reader-content p {{
                    margin: 1.5em 0;
                }}
                
                .reader-content h1, .reader-content h2, .reader-content h3 {{
                    margin-top: 2em;
                    margin-bottom: 0.5em;
                    line-height: 1.3;
                }}
                
                .reader-content img {{
                    max-width: 100%;
                    height: auto;
                    margin: 2em auto;
                    display: block;
                    border-radius: 8px;
                }}
                
                .reader-content a {{
                    color: {self.link_color};
                    text-decoration: none;
                }}
                
                .reader-content a:hover {{
                    text-decoration: underline;
                }}
                
                .reader-content blockquote {{
                    border-left: 4px solid {'#555' if dark_mode else '#ddd'};
                    margin: 1.5em 0;
                    padding: 0.5em 1em;
                    color: {'#aaa' if dark_mode else '#666'};
                    font-style: italic;
                }}
                
                .reader-content code {{
                    background: {'#2a2a2a' if dark_mode else '#f4f4f4'};
                    padding: 2px 6px;
                    border-radius: 4px;
                    font-family: 'Consolas', monospace;
                    font-size: 0.9em;
                }}
                
                .reader-content pre {{
                    background: {'#2a2a2a' if dark_mode else '#f4f4f4'};
                    padding: 1em;
                    border-radius: 8px;
                    overflow-x: auto;
                }}
                
                .reader-content pre code {{
                    padding: 0;
                    background: none;
                }}
                
                .reader-content ul, .reader-content ol {{
                    padding-left: 2em;
                }}
                
                .reader-content li {{
                    margin: 0.5em 0;
                }}
                
                .reader-toolbar {{
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    display: flex;
                    gap: 10px;
                    z-index: 1000;
                }}
                
                .reader-btn {{
                    background: {'#333' if dark_mode else '#fff'};
                    border: 1px solid {'#555' if dark_mode else '#ddd'};
                    padding: 8px 12px;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 14px;
                    color: {text_color};
                    transition: all 0.2s;
                }}
                
                .reader-btn:hover {{
                    background: {'#444' if dark_mode else '#f5f5f5'};
                }}
                
                @media (max-width: 768px) {{
                    .reader-container {{
                        padding: 20px 15px;
                    }}
                    
                    .reader-title {{
                        font-size: 1.5em;
                    }}
                    
                    html, body {{
                        font-size: 16px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="reader-toolbar">
                <button class="reader-btn" onclick="changeFontSize(-2)">A-</button>
                <button class="reader-btn" onclick="changeFontSize(2)">A+</button>
            </div>
            
            <div class="reader-container">
                <h1 class="reader-title">{data.get('title', '')}</h1>
                <div class="reader-meta">
                    <a href="{data.get('url', '')}" target="_blank">{data.get('url', '')}</a>
                </div>
                <div class="reader-content">
                    {data.get('content', '')}
                </div>
            </div>
            
            <script>
                function changeFontSize(delta) {{
                    const html = document.documentElement;
                    const currentSize = parseFloat(getComputedStyle(html).fontSize);
                    const newSize = Math.max(12, Math.min(28, currentSize + delta));
                    document.body.style.fontSize = newSize + 'px';
                }}
            </script>
        </body>
        </html>
        """
    
    def activate(self, browser_tab, dark_mode=False):
        """Activate reader mode for a tab"""
        self._browser_tab = browser_tab
        
        def on_content_extracted(data):
            if data and data.get('content'):
                html = self.get_reader_html(data, dark_mode)
                browser_tab.setHtml(html, browser_tab.url())
                self._active = True
                self.mode_changed.emit(True)
        
        # Extract content and convert to reader mode
        browser_tab.page().runJavaScript(
            self.get_extraction_script(),
            on_content_extracted
        )
    
    def deactivate(self, browser_tab):
        """Deactivate reader mode - reload original page"""
        self._active = False
        browser_tab.reload()
        self.mode_changed.emit(False)
    
    def toggle(self, browser_tab, dark_mode=False):
        """Toggle reader mode"""
        if self._active:
            self.deactivate(browser_tab)
        else:
            self.activate(browser_tab, dark_mode)
        return self._active
    
    def update_settings(self, **kwargs):
        """Update reader mode settings"""
        if 'font_family' in kwargs:
            self.font_family = kwargs['font_family']
        if 'font_size' in kwargs:
            self.font_size = kwargs['font_size']
        if 'line_height' in kwargs:
            self.line_height = kwargs['line_height']
        if 'max_width' in kwargs:
            self.max_width = kwargs['max_width']
        if 'background_color' in kwargs:
            self.background_color = kwargs['background_color']
        if 'text_color' in kwargs:
            self.text_color = kwargs['text_color']
