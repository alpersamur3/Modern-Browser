"""
Constants and Configuration for Modern Browser
"""

# Application Info
APP_NAME = "Modern Browser"
APP_VERSION = "2.0.0"
APP_ORGANIZATION = "ModernBrowser"
APP_DOMAIN = "modernbrowser.app"

# Default URLs
DEFAULT_HOME_URL = "https://www.google.com"
DEFAULT_NEW_TAB_URL = "about:blank"

# Search Engines
SEARCH_ENGINES = {
    "Google": "https://www.google.com/search?q={}",
    "DuckDuckGo": "https://duckduckgo.com/?q={}",
    "Bing": "https://www.bing.com/search?q={}",
    "Yahoo": "https://search.yahoo.com/search?p={}",
    "Yandex": "https://yandex.com/search/?text={}",
    "Ecosia": "https://www.ecosia.org/search?q={}",
    "Brave": "https://search.brave.com/search?q={}"
}

# Default Search Engine
DEFAULT_SEARCH_ENGINE = "Google"

# History Settings
MAX_HISTORY_ITEMS = 10000
HISTORY_DISPLAY_LIMIT = 100

# Bookmarks Settings
MAX_BOOKMARK_FOLDERS = 100

# Download Settings
DEFAULT_DOWNLOAD_PATH = ""  # Will use system default
MAX_CONCURRENT_DOWNLOADS = 5

# Ad Blocker Filter Lists
AD_BLOCK_LISTS = [
    "https://easylist.to/easylist/easylist.txt",
    "https://easylist.to/easylist/easyprivacy.txt"
]

# Zoom Settings
ZOOM_MIN = 25
ZOOM_MAX = 500
ZOOM_DEFAULT = 100
ZOOM_STEP = 10

# Tab Settings
MAX_TAB_TITLE_LENGTH = 20
MIN_TAB_WIDTH = 50

# UI Colors - Light Theme
LIGHT_THEME = {
    "bg_primary": "#ffffff",
    "bg_secondary": "#f5f5f5",
    "bg_tertiary": "#e8e8e8",
    "text_primary": "#1a1a1a",
    "text_secondary": "#666666",
    "accent": "#1a73e8",
    "accent_hover": "#1557b0",
    "border": "#dadce0",
    "success": "#34a853",
    "warning": "#fbbc05",
    "error": "#ea4335",
    "private_tab": "#7c4dff"
}

# UI Colors - Dark Theme
DARK_THEME = {
    "bg_primary": "#202124",
    "bg_secondary": "#292a2d",
    "bg_tertiary": "#35363a",
    "text_primary": "#e8eaed",
    "text_secondary": "#9aa0a6",
    "accent": "#8ab4f8",
    "accent_hover": "#aecbfa",
    "border": "#5f6368",
    "success": "#81c995",
    "warning": "#fdd663",
    "error": "#f28b82",
    "private_tab": "#bb86fc"
}

# Keyboard Shortcuts
SHORTCUTS = {
    "new_tab": "Ctrl+T",
    "close_tab": "Ctrl+W",
    "new_window": "Ctrl+N",
    "private_tab": "Ctrl+Shift+N",
    "reopen_tab": "Ctrl+Shift+T",
    "next_tab": "Ctrl+Tab",
    "prev_tab": "Ctrl+Shift+Tab",
    "address_bar": "Ctrl+L",
    "find": "Ctrl+F",
    "bookmark": "Ctrl+D",
    "bookmarks_panel": "Ctrl+Shift+B",
    "history_panel": "Ctrl+H",
    "downloads_panel": "Ctrl+J",
    "zoom_in": "Ctrl++",
    "zoom_out": "Ctrl+-",
    "zoom_reset": "Ctrl+0",
    "fullscreen": "F11",
    "refresh": "F5",
    "hard_refresh": "Ctrl+Shift+R",
    "dev_tools": "F12",
    "view_source": "Ctrl+U",
    "print": "Ctrl+P",
    "screenshot": "Ctrl+Shift+S",
    "reader_mode": "Ctrl+Shift+R",
    "settings": "Ctrl+,",
    "quit": "Ctrl+Q"
}

# User Agent
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36 ModernBrowser/2.0"
)

# File Types for Downloads
DOWNLOAD_FILE_TYPES = {
    "documents": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".rtf"],
    "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico"],
    "videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"],
    "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma"],
    "archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
    "executables": [".exe", ".msi", ".dmg", ".app", ".deb", ".rpm"]
}

# Languages
SUPPORTED_LANGUAGES = {
    "tr": "Türkçe",
    "en": "English",
    "de": "Deutsch",
    "fr": "Français",
    "es": "Español",
    "it": "Italiano",
    "pt": "Português",
    "ru": "Русский",
    "ja": "日本語",
    "zh": "中文",
    "ko": "한국어",
    "ar": "العربية"
}

DEFAULT_LANGUAGE = "tr"

# Translations
TRANSLATIONS = {
    "tr": {
        "new_tab": "Yeni Sekme",
        "private_tab": "Gizli Sekme",
        "back": "Geri",
        "forward": "İleri",
        "reload": "Yenile",
        "home": "Ana Sayfa",
        "bookmarks": "Yer İmleri",
        "history": "Geçmiş",
        "downloads": "İndirmeler",
        "settings": "Ayarlar",
        "dark_mode": "Karanlık Mod",
        "zoom_in": "Yakınlaştır",
        "zoom_out": "Uzaklaştır",
        "fullscreen": "Tam Ekran",
        "find": "Bul",
        "print": "Yazdır",
        "developer_tools": "Geliştirici Araçları",
        "view_source": "Kaynağı Görüntüle",
        "about": "Hakkında",
        "quit": "Çıkış",
        "add_bookmark": "Yer İmi Ekle",
        "remove_bookmark": "Yer İmini Kaldır",
        "clear_history": "Geçmişi Temizle",
        "clear_downloads": "İndirmeleri Temizle",
        "search_placeholder": "Ara veya URL gir...",
        "no_bookmarks": "Henüz yer imi yok",
        "no_history": "Henüz geçmiş yok",
        "no_downloads": "Henüz indirme yok",
        "download_started": "İndirme başladı",
        "download_completed": "İndirme tamamlandı",
        "download_failed": "İndirme başarısız",
        "screenshot_saved": "Ekran görüntüsü kaydedildi",
        "reader_mode": "Okuma Modu",
        "ad_blocker": "Reklam Engelleyici",
        "password_manager": "Parola Yöneticisi",
        "extensions": "Uzantılar",
        "themes": "Temalar",
        "privacy": "Gizlilik",
        "security": "Güvenlik",
        "general": "Genel",
        "appearance": "Görünüm",
        "search_engine": "Arama Motoru",
        "homepage": "Ana Sayfa",
        "language": "Dil",
        "close_tab": "Sekmeyi Kapat",
        "duplicate_tab": "Sekmeyi Kopyala",
        "pin_tab": "Sekmeyi Sabitle",
        "mute_tab": "Sekmeyi Sessize Al",
        "reload_all": "Tümünü Yenile",
        "close_other": "Diğerlerini Kapat",
        "close_right": "Sağdakileri Kapat"
    },
    "en": {
        "new_tab": "New Tab",
        "private_tab": "Private Tab",
        "back": "Back",
        "forward": "Forward",
        "reload": "Reload",
        "home": "Home",
        "bookmarks": "Bookmarks",
        "history": "History",
        "downloads": "Downloads",
        "settings": "Settings",
        "dark_mode": "Dark Mode",
        "zoom_in": "Zoom In",
        "zoom_out": "Zoom Out",
        "fullscreen": "Fullscreen",
        "find": "Find",
        "print": "Print",
        "developer_tools": "Developer Tools",
        "view_source": "View Source",
        "about": "About",
        "quit": "Quit",
        "add_bookmark": "Add Bookmark",
        "remove_bookmark": "Remove Bookmark",
        "clear_history": "Clear History",
        "clear_downloads": "Clear Downloads",
        "search_placeholder": "Search or enter URL...",
        "no_bookmarks": "No bookmarks yet",
        "no_history": "No history yet",
        "no_downloads": "No downloads yet",
        "download_started": "Download started",
        "download_completed": "Download completed",
        "download_failed": "Download failed",
        "screenshot_saved": "Screenshot saved",
        "reader_mode": "Reader Mode",
        "ad_blocker": "Ad Blocker",
        "password_manager": "Password Manager",
        "extensions": "Extensions",
        "themes": "Themes",
        "privacy": "Privacy",
        "security": "Security",
        "general": "General",
        "appearance": "Appearance",
        "search_engine": "Search Engine",
        "homepage": "Homepage",
        "language": "Language",
        "close_tab": "Close Tab",
        "duplicate_tab": "Duplicate Tab",
        "pin_tab": "Pin Tab",
        "mute_tab": "Mute Tab",
        "reload_all": "Reload All",
        "close_other": "Close Others",
        "close_right": "Close Tabs to Right"
    }
}
