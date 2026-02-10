import re
import logging

from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from ..utils.constants import APP_NAME, APP_ORGANIZATION

log = logging.getLogger(__name__)

DEFAULT_AD_DOMAINS = [
    "doubleclick.net", "googlesyndication.com", "googleadservices.com",
    "google-analytics.com", "adservice.google.com", "pagead2.googlesyndication.com",
    "adnxs.com", "adsrvr.org", "advertising.com", "amazon-adsystem.com",
    "facebook.com/tr", "connect.facebook.net/signals",
    "ads.yahoo.com", "analytics.yahoo.com",
    "ads.twitter.com", "static.ads-twitter.com",
    "ad.doubleclick.net", "stats.g.doubleclick.net",
    "scorecardresearch.com", "quantserve.com", "outbrain.com",
    "taboola.com", "criteo.com", "rubiconproject.com",
    "pubmatic.com", "openx.net", "casalemedia.com",
    "moatads.com", "turn.com", "bidswitch.net",
    "adform.net", "mathtag.com", "serving-sys.com",
]

DEFAULT_AD_PATTERNS = [
    r"/ads?[/\?]", r"/advert", r"/banner", r"/popup",
    r"[\?&]ad_", r"[\?&]ads=", r"/ad[sx]?[_\-/]",
    r"/track(er|ing)?[/\?]", r"/pixel[/\?]", r"/beacon[/\?]",
    r"\.gif\?.*click", r"/click\?", r"/impression[/\?]",
]

DEFAULT_ELEMENT_SELECTORS = [
    "ins.adsbygoogle", "div[id^='div-gpt-ad']",
    ".ad-container", ".ad-wrapper", "#ad-wrapper",
    ".adsbygoogle", ".ad-slot", ".ad-unit",
    "[data-ad]", "[data-ads]", "[data-adzone]",
    "[id*='google_ads']", "[class*='google-ad']",
    "[class*='advert-']", "[id*='advert-']",
    "[class*='sponsor-badge']", "[id*='sponsored-content']",
]


class AdBlocker(QWebEngineUrlRequestInterceptor):
    _instance = None

    def __new__(cls, parent=None):
        if cls._instance is None:
            obj = super().__new__(cls)
            obj._initialized = False
            cls._instance = obj
        return cls._instance

    def __init__(self, parent=None):
        if self._initialized:
            return
        super().__init__(parent)
        self._initialized = True
        self._enabled = True
        self._blocked_count = 0
        self._blocked_domains = set(DEFAULT_AD_DOMAINS)
        self._blocked_patterns = [re.compile(p, re.IGNORECASE) for p in DEFAULT_AD_PATTERNS]
        self._custom_rules = []
        self._whitelist = set()

    def interceptRequest(self, info):
        if not self._enabled:
            return
        url = info.requestUrl().toString()
        host = info.requestUrl().host().lower()
        if host in self._whitelist:
            return
        for domain in self._blocked_domains:
            if domain in host or domain in url:
                info.block(True)
                self._blocked_count += 1
                return
        for pattern in self._blocked_patterns:
            if pattern.search(url):
                info.block(True)
                self._blocked_count += 1
                return
        for rule in self._custom_rules:
            try:
                if rule.search(url):
                    info.block(True)
                    self._blocked_count += 1
                    return
            except Exception:
                continue

    def is_enabled(self):
        return self._enabled

    def set_enabled(self, enabled):
        self._enabled = enabled
        if not enabled:
            self._blocked_count = 0

    def toggle(self):
        self._enabled = not self._enabled
        if not self._enabled:
            self._blocked_count = 0
        return self._enabled

    def get_blocked_count(self):
        return self._blocked_count

    def reset_count(self):
        self._blocked_count = 0

    def add_custom_rule(self, pattern):
        try:
            compiled = re.compile(pattern, re.IGNORECASE)
            self._custom_rules.append(compiled)
            return True
        except re.error:
            log.warning("Geçersiz kural: %s", pattern)
            return False

    def remove_custom_rule(self, index):
        if 0 <= index < len(self._custom_rules):
            self._custom_rules.pop(index)
            return True
        return False

    def add_to_whitelist(self, domain):
        self._whitelist.add(domain.lower())

    def remove_from_whitelist(self, domain):
        self._whitelist.discard(domain.lower())

    def get_whitelist(self):
        return list(self._whitelist)

    def clear_whitelist(self):
        self._whitelist.clear()

    def get_stats(self):
        return {
            'enabled': self._enabled,
            'blocked_count': self._blocked_count,
            'rules_count': len(self._blocked_domains) + len(self._blocked_patterns) + len(self._custom_rules),
            'whitelist_count': len(self._whitelist),
        }


class ElementHider:
    @classmethod
    def get_hide_css(cls):
        selectors = ", ".join(DEFAULT_ELEMENT_SELECTORS)
        return f"{selectors} {{ display: none !important; visibility: hidden !important; }}"

    @classmethod
    def inject_element_hiding(cls, tab):
        url = tab.url().toString()
        if not url or url.startswith('about:') or url.startswith('data:'):
            return
        css = cls.get_hide_css()
        safe = css.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
        script = "(function(){if(!document||!document.head)return;if(document.querySelector('style[data-adblocker]'))return;var s=document.createElement('style');s.type='text/css';s.setAttribute('data-adblocker','true');s.innerHTML=`" + safe + "`;document.head.appendChild(s);})();"
        tab.page().runJavaScript(script)
