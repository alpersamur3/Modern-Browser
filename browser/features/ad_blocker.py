"""
Ad Blocker for Modern Browser
"""

import re
from PyQt5.QtCore import QObject, pyqtSignal, QSettings
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from ..utils.constants import APP_NAME, APP_ORGANIZATION


class AdBlocker(QWebEngineUrlRequestInterceptor):
    """
    URL Request Interceptor for blocking ads and trackers
    """
    
    # Common ad domains and patterns
    DEFAULT_BLOCK_LIST = [
        # Ad networks
        r'doubleclick\.net',
        r'googlesyndication\.com',
        r'googleadservices\.com',
        r'google-analytics\.com',
        r'googletagmanager\.com',
        r'facebook\.com/tr',
        r'facebook\.net/signals',
        r'analytics\.facebook\.com',
        r'ads\.yahoo\.com',
        r'adservice\.google\.com',
        r'pagead2\.googlesyndication\.com',
        r'adsserver\.',
        r'adserver\.',
        r'adservice\.',
        r'advertising\.',
        r'banner\.ads\.',
        r'banners\.',
        r'clicktrack\.',
        r'tracking\.',
        r'tracker\.',
        r'\.ads\.',
        r'\/ads\/',
        r'\/ad\/',
        r'\.ad\.',
        
        # Analytics and tracking
        r'analytics\.',
        r'pixel\.',
        r'stats\.',
        r'beacon\.',
        r'collect\.',
        r'metrics\.',
        r'telemetry\.',
        r'segment\.com',
        r'segment\.io',
        r'mixpanel\.com',
        r'amplitude\.com',
        r'hotjar\.com',
        r'crazyegg\.com',
        r'fullstory\.com',
        r'mouseflow\.com',
        r'luckyorange\.com',
        r'inspectlet\.com',
        
        # Social media trackers
        r'connect\.facebook\.net',
        r'platform\.twitter\.com',
        r'platform\.linkedin\.com',
        r'widgets\.pinterest\.com',
        
        # Ad exchanges
        r'pubmatic\.com',
        r'openx\.net',
        r'rubiconproject\.com',
        r'criteo\.com',
        r'criteo\.net',
        r'taboola\.com',
        r'outbrain\.com',
        r'mgid\.com',
        r'revcontent\.com',
        r'adnxs\.com',
        r'adsrvr\.org',
        r'bidswitch\.net',
        r'casalemedia\.com',
        r'contextweb\.com',
        r'spotxchange\.com',
        r'yieldlab\.net',
        
        # Malware/suspicious
        r'malware\.',
        r'phishing\.',
        r'suspicious\.',
    ]
    
    # Patterns to allow (whitelist)
    DEFAULT_ALLOW_LIST = [
        r'google\.com/search',
        r'google\.com/complete',
        r'google\.com/maps',
        r'googleapis\.com',
        r'gstatic\.com',
        r'recaptcha\.net',
    ]
    
    _instance = None
    blocked_count = 0
    
    def __new__(cls, parent=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, parent=None):
        if self._initialized:
            return
        
        super().__init__(parent)
        self._initialized = True
        self.settings = QSettings(APP_ORGANIZATION, APP_NAME)
        self.enabled = self.settings.value("security/ad_blocker", True, type=bool)
        
        self.block_patterns = []
        self.allow_patterns = []
        self.custom_rules = []
        
        self._compile_patterns()
        self._load_custom_rules()
    
    def _compile_patterns(self):
        """Compile regex patterns for faster matching"""
        self.block_patterns = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in self.DEFAULT_BLOCK_LIST
        ]
        self.allow_patterns = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in self.DEFAULT_ALLOW_LIST
        ]
    
    def _load_custom_rules(self):
        """Load user's custom blocking rules"""
        rules_json = self.settings.value("ad_blocker/custom_rules", "[]")
        try:
            import json
            self.custom_rules = json.loads(rules_json)
            # Compile custom patterns
            for rule in self.custom_rules:
                if rule.get('enabled', True):
                    pattern = re.compile(rule['pattern'], re.IGNORECASE)
                    if rule.get('type') == 'allow':
                        self.allow_patterns.append(pattern)
                    else:
                        self.block_patterns.append(pattern)
        except:
            self.custom_rules = []
    
    def _save_custom_rules(self):
        """Save custom rules to storage"""
        import json
        self.settings.setValue("ad_blocker/custom_rules", json.dumps(self.custom_rules))
    
    def interceptRequest(self, info):
        """Intercept and potentially block requests"""
        if not self.enabled:
            return
        
        url = info.requestUrl().toString()
        
        # Check allow list first
        for pattern in self.allow_patterns:
            if pattern.search(url):
                return  # Allow the request
        
        # Check block list
        for pattern in self.block_patterns:
            if pattern.search(url):
                info.block(True)
                AdBlocker.blocked_count += 1
                return
    
    def set_enabled(self, enabled):
        """Enable or disable the ad blocker"""
        self.enabled = enabled
        self.settings.setValue("security/ad_blocker", enabled)
    
    def is_enabled(self):
        """Check if ad blocker is enabled"""
        return self.enabled
    
    def toggle(self):
        """Toggle ad blocker on/off"""
        self.set_enabled(not self.enabled)
        return self.enabled
    
    def add_custom_rule(self, pattern, rule_type='block', enabled=True):
        """Add a custom blocking/allowing rule"""
        rule = {
            'pattern': pattern,
            'type': rule_type,
            'enabled': enabled
        }
        self.custom_rules.append(rule)
        
        # Compile and add pattern
        compiled = re.compile(pattern, re.IGNORECASE)
        if rule_type == 'allow':
            self.allow_patterns.append(compiled)
        else:
            self.block_patterns.append(compiled)
        
        self._save_custom_rules()
        return rule
    
    def remove_custom_rule(self, pattern):
        """Remove a custom rule"""
        self.custom_rules = [r for r in self.custom_rules if r['pattern'] != pattern]
        self._save_custom_rules()
        # Recompile patterns
        self._compile_patterns()
        self._load_custom_rules()
    
    def get_custom_rules(self):
        """Get all custom rules"""
        return self.custom_rules
    
    def clear_custom_rules(self):
        """Clear all custom rules"""
        self.custom_rules = []
        self._save_custom_rules()
        self._compile_patterns()
    
    def get_blocked_count(self):
        """Get total number of blocked requests"""
        return AdBlocker.blocked_count
    
    def reset_blocked_count(self):
        """Reset blocked count"""
        AdBlocker.blocked_count = 0
    
    def is_blocked(self, url):
        """Check if a URL would be blocked"""
        if not self.enabled:
            return False
        
        # Check allow list first
        for pattern in self.allow_patterns:
            if pattern.search(url):
                return False
        
        # Check block list
        for pattern in self.block_patterns:
            if pattern.search(url):
                return True
        
        return False
    
    def add_domain_to_whitelist(self, domain):
        """Add a domain to the whitelist"""
        pattern = re.escape(domain).replace(r'\*', '.*')
        self.add_custom_rule(pattern, 'allow')
    
    def add_domain_to_blocklist(self, domain):
        """Add a domain to the blocklist"""
        pattern = re.escape(domain).replace(r'\*', '.*')
        self.add_custom_rule(pattern, 'block')


class ElementHider:
    """
    CSS-based element hiding for ads
    """
    
    # Common CSS selectors for ad elements
    HIDE_SELECTORS = [
        # Generic
        '[class*="ad-"]',
        '[class*="-ad"]',
        '[class*="_ad"]',
        '[class*="ad_"]',
        '[class*="ads-"]',
        '[class*="ads_"]',
        '[id*="ad-"]',
        '[id*="-ad"]',
        '[id*="_ad"]',
        '[id*="ad_"]',
        '[id*="ads-"]',
        '[id*="ads_"]',
        
        # Specific
        '.advertisement',
        '.advertising',
        '.ad-container',
        '.ad-wrapper',
        '.ad-banner',
        '.ad-block',
        '.ad-unit',
        '.adsbygoogle',
        '.adsense',
        '.sponsored',
        '.sponsor',
        '.promoted',
        '.promo-banner',
        
        # Social widgets (optional)
        '.fb-like',
        '.twitter-share',
        '.social-share',
        
        # Popups
        '.popup-ad',
        '.modal-ad',
        '.overlay-ad',
        '.interstitial',
    ]
    
    @classmethod
    def get_hide_css(cls):
        """Get CSS to hide ad elements"""
        selectors = ', '.join(cls.HIDE_SELECTORS)
        return f"""
        {selectors} {{
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            width: 0 !important;
            opacity: 0 !important;
        }}
        """
    
    @classmethod
    def inject_element_hiding(cls, browser_tab):
        """Inject element hiding CSS into a page"""
        css = cls.get_hide_css()
        browser_tab.inject_css(css)
