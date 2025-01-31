from googletrans import Translator
from django.core.cache import cache
from typing import Dict, Optional
import logging
import time

logger = logging.getLogger(__name__)

class TranslationService:
    """Service for handling translations using Google Translate"""
    
    SUPPORTED_LANGUAGES = {
        'en': 'english',
        'hi': 'hindi',
        'bn': 'bengali'
    }
    
    def __init__(self):
        self.translator = Translator()
        self.retry_count = 3
        self.retry_delay = 1  # seconds
    
    def _get_cache_key(self, text: str, target_lang: str) -> str:
        """Generate a cache key for translations"""
        # Use first 50 chars of text to keep cache key reasonable
        text_preview = text[:50] if text else ''
        return f'trans:{target_lang}:{hash(text_preview)}'
    
    def _translate_with_retry(self, text: str, target_lang: str) -> Optional[str]:
        """Attempt translation with retries on failure"""
        for attempt in range(self.retry_count):
            try:
                if attempt > 0:
                    time.sleep(self.retry_delay)
                
                translation = self.translator.translate(
                    text,
                    dest=target_lang,
                    src='en'
                )
                return translation.text
                
            except Exception as e:
                logger.warning(
                    f"Translation attempt {attempt + 1} failed: {str(e)}"
                )
                if attempt == self.retry_count - 1:
                    logger.error(
                        f"All translation attempts failed for text: {text[:100]}..."
                    )
                    return None
    
    def translate_text(self, text: str, target_lang: str) -> Optional[str]:
        """
        Translate text to target language with caching
        
        Args:
            text: Text to translate
            target_lang: Target language code (e.g., 'hi', 'bn')
            
        Returns:
            Translated text or None if translation fails
        """
        if not text or target_lang == 'en':
            return text
            
        # Check cache first
        cache_key = self._get_cache_key(text, target_lang)
        cached_translation = cache.get(cache_key)
        if cached_translation:
            return cached_translation
            
        # Perform translation
        translated_text = self._translate_with_retry(text, target_lang)
        if translated_text:
            # Cache successful translation for 24 hours
            cache.set(cache_key, translated_text, timeout=86400)
            return translated_text
            
        return None
    
    def translate_html(self, html: str, target_lang: str) -> Optional[str]:
        """
        Translate HTML content while preserving HTML tags
        
        Args:
            html: HTML content to translate
            target_lang: Target language code
            
        Returns:
            Translated HTML content or None if translation fails
        """
        if not html or target_lang == 'en':
            return html
            
        try:
            # Simple HTML tag preservation - can be enhanced for more complex HTML
            translation = self.translate_text(html, target_lang)
            if translation:
                # Preserve basic HTML tags from original
                for tag in ['<p>', '</p>', '<br>', '<strong>', '</strong>', '<em>', '</em>']:
                    translation = translation.replace(tag.lower(), tag)
            return translation
        except Exception as e:
            logger.error(f"HTML translation failed: {str(e)}")
            return None 