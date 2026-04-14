"""
Translation Service for FastAPI
Handles text translation using googletrans library
Provides caching to avoid repeated API calls
"""

from functools import lru_cache
import logging
from typing import List, Dict
from googletrans import Translator, LANGUAGES

logger = logging.getLogger(__name__)

# Initialize translator
translator = Translator()

# Language code mapping
LANGUAGE_MAP = {
    "en": "en",
    "te": "te",  # Telugu
    "hi": "hi",  # Hindi
    "ml": "ml",  # Malayalam
}

# Cache for translations to avoid repeated API calls
@lru_cache(maxsize=1000)
def translate_text_cached(text: str, target_lang: str, source_lang: str = "en") -> str:
    """
    Translate text with caching
    
    Args:
        text: Text to translate
        target_lang: Target language code
        source_lang: Source language code (default: English)
    
    Returns:
        Translated text
    """
    if not text or target_lang == source_lang:
        return text
    
    if target_lang not in LANGUAGE_MAP:
        logger.warning(f"Unsupported language: {target_lang}")
        return text
    
    try:
        result = translator.translate(text, src_language=LANGUAGE_MAP[source_lang], dest_language=LANGUAGE_MAP[target_lang])
        return result['text'] or text
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return text


def translate_batch(texts: List[str], target_lang: str, source_lang: str = "en") -> List[str]:
    """
    Translate multiple texts at once
    
    Args:
        texts: List of texts to translate
        target_lang: Target language code
        source_lang: Source language code (default: English)
    
    Returns:
        List of translated texts
    """
    if target_lang == source_lang or target_lang == "en":
        return texts
    
    return [translate_text_cached(text, target_lang, source_lang) for text in texts]


def get_supported_languages() -> Dict[str, str]:
    """Get dictionary of supported languages"""
    return {code: name for code, name in LANGUAGES.items() if code in LANGUAGE_MAP.values()}


def clear_translation_cache():
    """Clear the translation cache (useful for testing or manual refresh)"""
    translate_text_cached.cache_clear()
