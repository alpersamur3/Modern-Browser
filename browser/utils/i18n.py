"""
Internationalization (i18n) module using gettext with .po/.mo files.
"""
import os
import gettext
import locale
import logging

log = logging.getLogger(__name__)

LOCALES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "locales"
)

_current_lang = "tr"
_translations = None


def set_language(lang_code: str):
    """Set the current language and load translations."""
    global _current_lang, _translations
    _current_lang = lang_code
    try:
        _translations = gettext.translation(
            "messages",
            localedir=LOCALES_DIR,
            languages=[lang_code],
            fallback=True
        )
        _translations.install()
        log.info(f"Language set to: {lang_code}")
    except Exception as e:
        log.warning(f"Could not load translations for '{lang_code}': {e}")
        _translations = gettext.NullTranslations()
        _translations.install()


def _(text: str) -> str:
    """Translate a string using the current language."""
    global _translations
    if _translations is None:
        set_language(_current_lang)
    return _translations.gettext(text)


def get_current_language() -> str:
    """Get the current language code."""
    return _current_lang


def get_available_languages() -> dict:
    """Return available languages with display names."""
    return {
        "tr": "Türkçe",
        "en": "English",
        "de": "Deutsch",
        "fr": "Français",
        "es": "Español",
    }


# Initialize default language
set_language(_current_lang)
