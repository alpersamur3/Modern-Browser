import os

APP_NAME = "Modern Browser"
APP_VERSION = "2.0.0"
APP_ORGANIZATION = "ModernBrowser"
APP_DOMAIN = "modernbrowser.app"

RESOURCES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "resources")
ICONS_DIR = os.path.join(RESOURCES_DIR, "icons")

DEFAULT_HOME_URL = "https://www.google.com"
DEFAULT_NEW_TAB_URL = "about:blank"

SEARCH_ENGINES = {
    "Google": "https://www.google.com/search?q={}",
    "DuckDuckGo": "https://duckduckgo.com/?q={}",
    "Bing": "https://www.bing.com/search?q={}",
    "Yahoo": "https://search.yahoo.com/search?p={}",
    "Yandex": "https://yandex.com/search/?text={}",
    "Ecosia": "https://www.ecosia.org/search?q={}",
    "Brave": "https://search.brave.com/search?q={}"
}
DEFAULT_SEARCH_ENGINE = "Google"

MAX_HISTORY_ITEMS = 10000
HISTORY_DISPLAY_LIMIT = 100
MAX_BOOKMARK_FOLDERS = 100

DEFAULT_DOWNLOAD_PATH = ""
MAX_CONCURRENT_DOWNLOADS = 5

AD_BLOCK_LISTS = [
    "https://easylist.to/easylist/easylist.txt",
    "https://easylist.to/easylist/easyprivacy.txt"
]

ZOOM_MIN = 25
ZOOM_MAX = 500
ZOOM_DEFAULT = 100
ZOOM_STEP = 10

MAX_TAB_TITLE_LENGTH = 20
MIN_TAB_WIDTH = 50

LIGHT_THEME = {
    "bg_primary": "#ffffff",
    "bg_secondary": "#f0f2f5",
    "bg_tertiary": "#e4e6eb",
    "bg_hover": "#d8dadf",
    "text_primary": "#1c1e21",
    "text_secondary": "#65676b",
    "text_muted": "#8a8d91",
    "accent": "#0866ff",
    "accent_hover": "#0553d4",
    "accent_light": "#e7f3ff",
    "border": "#ced0d4",
    "border_light": "#e4e6eb",
    "success": "#31a24c",
    "warning": "#f0b429",
    "error": "#e4002b",
    "private_tab": "#7c3aed",
    "shadow": "rgba(0, 0, 0, 0.08)",
    "card": "#ffffff",
    "card_hover": "#f5f6f7",
}

DARK_THEME = {
    "bg_primary": "#18191a",
    "bg_secondary": "#242526",
    "bg_tertiary": "#3a3b3c",
    "bg_hover": "#4e4f50",
    "text_primary": "#e4e6eb",
    "text_secondary": "#b0b3b8",
    "text_muted": "#8a8d91",
    "accent": "#2d88ff",
    "accent_hover": "#1a77f2",
    "accent_light": "#263c5c",
    "border": "#3e4042",
    "border_light": "#3a3b3c",
    "success": "#31a24c",
    "warning": "#f0b429",
    "error": "#f25c54",
    "private_tab": "#a78bfa",
    "shadow": "rgba(0, 0, 0, 0.25)",
    "card": "#242526",
    "card_hover": "#3a3b3c",
}

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
    "hard_refresh": "Ctrl+F5",
    "dev_tools": "F12",
    "view_source": "Ctrl+U",
    "print": "Ctrl+P",
    "screenshot": "Ctrl+Shift+S",
    "reader_mode": "Ctrl+Shift+R",
    "settings": "Ctrl+,",
    "quit": "Ctrl+Q"
}

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

DOWNLOAD_FILE_TYPES = {
    "documents": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".rtf"],
    "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico"],
    "videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"],
    "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma"],
    "archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
    "executables": [".exe", ".msi", ".dmg", ".app", ".deb", ".rpm"]
}

SUPPORTED_LANGUAGES = {
    "tr": "Turkce",
    "en": "English",
    "de": "Deutsch",
    "fr": "Francais",
    "es": "Espanol",
}
DEFAULT_LANGUAGE = "tr"

TRANSLATIONS = {
    "tr": {
        "new_tab": "Yeni Sekme",
        "private_tab": "Gizli Sekme",
        "back": "Geri",
        "forward": "Ileri",
        "reload": "Yenile",
        "home": "Ana Sayfa",
        "bookmarks": "Yer Imleri",
        "history": "Gecmis",
        "downloads": "Indirmeler",
        "settings": "Ayarlar",
        "dark_mode": "Karanlik Mod",
        "zoom_in": "Yakinlastir",
        "zoom_out": "Uzaklastir",
        "fullscreen": "Tam Ekran",
        "find": "Bul",
        "print": "Yazdir",
        "developer_tools": "Gelistirici Araclari",
        "view_source": "Kaynagi Goruntule",
        "about": "Hakkinda",
        "quit": "Cikis",
        "add_bookmark": "Yer Imi Ekle",
        "remove_bookmark": "Yer Imini Kaldir",
        "clear_history": "Gecmisi Temizle",
        "clear_downloads": "Indirmeleri Temizle",
        "search_placeholder": "Ara veya URL gir...",
        "no_bookmarks": "Henuz yer imi yok",
        "no_history": "Henuz gecmis yok",
        "no_downloads": "Henuz indirme yok",
        "download_started": "Indirme basladi",
        "download_completed": "Indirme tamamlandi",
        "download_failed": "Indirme basarisiz",
        "screenshot_saved": "Ekran goruntusu kaydedildi",
        "reader_mode": "Okuma Modu",
        "ad_blocker": "Reklam Engelleyici",
        "password_manager": "Parola Yoneticisi",
        "privacy": "Gizlilik",
        "security": "Guvenlik",
        "general": "Genel",
        "appearance": "Gorunum",
        "search_engine": "Arama Motoru",
        "homepage": "Ana Sayfa",
        "language": "Dil",
        "close_tab": "Sekmeyi Kapat",
        "duplicate_tab": "Sekmeyi Kopyala",
        "pin_tab": "Sekmeyi Sabitle",
        "mute_tab": "Sekmeyi Sessize Al",
        "reload_all": "Tumunu Yenile",
        "close_other": "Digerlerini Kapat",
        "close_right": "Sagdakileri Kapat",
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
        "close_right": "Close Tabs to Right",
    }
}
