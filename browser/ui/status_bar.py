"""
Modern Status Bar for Browser
"""

from PyQt5.QtWidgets import (QStatusBar, QLabel, QProgressBar, QWidget, 
                             QHBoxLayout, QPushButton, QToolButton)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon
from ..utils.constants import LIGHT_THEME, DARK_THEME


class StatusBar(QStatusBar):
    """Modern status bar with progress indicator and various info"""
    
    # Signals
    zoom_clicked = pyqtSignal()
    ad_blocker_clicked = pyqtSignal()
    
    def __init__(self, parent=None, dark_mode=False):
        super().__init__(parent)
        self.dark_mode = dark_mode
        self._setup_ui()
        self._apply_style()
    
    def _setup_ui(self):
        """Setup status bar UI"""
        self.setFixedHeight(28)
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(150)
        self.progress_bar.setFixedHeight(16)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        
        # URL label for link hover
        self.url_label = QLabel()
        self.url_label.setMaximumWidth(600)
        
        # Spacer
        spacer = QWidget()
        spacer.setFixedWidth(10)
        
        # Zoom indicator
        self.zoom_btn = QToolButton()
        self.zoom_btn.setText("100%")
        self.zoom_btn.setFixedWidth(50)
        self.zoom_btn.clicked.connect(self.zoom_clicked.emit)
        self.zoom_btn.setToolTip("Tıklayarak yakınlaştırmayı sıfırlayın")
        
        # Security indicator
        self.security_label = QLabel("🔒")
        self.security_label.setToolTip("Güvenli bağlantı")
        
        # Ad blocker indicator
        self.ad_block_btn = QToolButton()
        self.ad_block_btn.setText("🛡️ 0")
        self.ad_block_btn.clicked.connect(self.ad_blocker_clicked.emit)
        self.ad_block_btn.setToolTip("Engellenen reklam sayısı")
        
        # Download indicator
        self.download_label = QLabel()
        self.download_label.hide()
        
        # Add widgets to status bar
        self.addWidget(self.progress_bar)
        self.addWidget(self.url_label, 1)
        self.addPermanentWidget(self.download_label)
        self.addPermanentWidget(self.ad_block_btn)
        self.addPermanentWidget(self.security_label)
        self.addPermanentWidget(self.zoom_btn)
    
    def _apply_style(self):
        """Apply styling"""
        theme = DARK_THEME if self.dark_mode else LIGHT_THEME
        
        self.setStyleSheet(f"""
            QStatusBar {{
                background-color: {theme['bg_secondary']};
                color: {theme['text_secondary']};
                border-top: 1px solid {theme['border']};
                font-size: 12px;
            }}
            
            QProgressBar {{
                border: none;
                border-radius: 3px;
                background-color: {theme['bg_tertiary']};
            }}
            
            QProgressBar::chunk {{
                background-color: {theme['accent']};
                border-radius: 3px;
            }}
            
            QToolButton {{
                background: transparent;
                border: none;
                padding: 2px 6px;
                color: {theme['text_secondary']};
                border-radius: 3px;
            }}
            
            QToolButton:hover {{
                background-color: {theme['bg_tertiary']};
            }}
            
            QLabel {{
                color: {theme['text_secondary']};
                padding: 0 4px;
            }}
        """)
    
    def set_dark_mode(self, dark_mode):
        """Toggle dark mode"""
        self.dark_mode = dark_mode
        self._apply_style()
    
    def show_progress(self, progress):
        """Show/update progress bar"""
        if progress > 0 and progress < 100:
            self.progress_bar.show()
            self.progress_bar.setValue(progress)
        else:
            self.progress_bar.hide()
    
    def hide_progress(self):
        """Hide progress bar"""
        self.progress_bar.hide()
    
    def set_url_text(self, text):
        """Set URL label text (for link hover)"""
        self.url_label.setText(text)
    
    def clear_url_text(self):
        """Clear URL label"""
        self.url_label.clear()
    
    def set_zoom(self, percentage):
        """Update zoom indicator"""
        self.zoom_btn.setText(f"{percentage}%")
    
    def set_security(self, is_secure):
        """Update security indicator"""
        if is_secure:
            self.security_label.setText("🔒")
            self.security_label.setToolTip("Güvenli bağlantı (HTTPS)")
            self.security_label.setStyleSheet("color: #34a853;")
        else:
            self.security_label.setText("⚠️")
            self.security_label.setToolTip("Güvensiz bağlantı")
            self.security_label.setStyleSheet("color: #ea4335;")
    
    def set_blocked_count(self, count):
        """Update ad blocker count"""
        self.ad_block_btn.setText(f"🛡️ {count}")
    
    def show_download_status(self, text):
        """Show download status"""
        self.download_label.setText(f"⬇️ {text}")
        self.download_label.show()
    
    def hide_download_status(self):
        """Hide download status"""
        self.download_label.hide()
    
    def show_message(self, message, timeout=3000):
        """Show temporary message"""
        self.showMessage(message, timeout)
