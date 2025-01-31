from django.db import models
from django.core.cache import cache
from django.conf import settings
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from django_quill.fields import QuillField
from .services import TranslationService
import json

class FAQ(models.Model):
    question = models.TextField(verbose_name="Question (English)")
    answer = QuillField(verbose_name="Answer (English)")
    
    question_hi = models.TextField(verbose_name="Question (Hindi)", blank=True, null=True)
    answer_hi = QuillField(verbose_name="Answer (Hindi)", blank=True, null=True)
    question_bn = models.TextField(verbose_name="Question (Bengali)", blank=True, null=True)
    answer_bn = QuillField(verbose_name="Answer (Bengali)", blank=True, null=True)
    
    auto_translate = models.BooleanField(
        default=True,
        verbose_name="Auto-translate",
        help_text="Automatically translate content to other languages"
    )
    last_translated = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        help_text="Last time translations were updated"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.question[:100]
    
    def _get_cache_key(self, field_name, language_code):
        return f'faq:{self.id}:{field_name}:{language_code}'
    
    def _get_quill_html(self, value):
        """Extract HTML content from a Quill field or JSON string"""
        if hasattr(value, 'html'):
            return value.html
        if isinstance(value, str):
            try:
                data = json.loads(value)
                return data.get('html', '')
            except json.JSONDecodeError:
                return value
        return str(value)
    
    def translate_field(self, field_name: str, target_lang: str) -> bool:
        """Translate a specific field to the target language"""
        if not self.auto_translate or target_lang == 'en':
            return False
            
        source_value = getattr(self, field_name)
        if not source_value:
            return False
            
        translation_service = TranslationService()
        
        if isinstance(source_value, QuillField) or field_name == 'answer':
            html_content = self._get_quill_html(source_value)
            translated_text = translation_service.translate_html(
                html_content,
                target_lang
            )
            
            if translated_text:
                if hasattr(translated_text, 'text'):
                    translated_text = translated_text.text
                
                translated_data = {
                    "delta": {"ops": [{"insert": f"{translated_text}\n"}]},
                    "html": translated_text
                }
                target_field = f"{field_name}_{target_lang}"
                setattr(self, target_field, json.dumps(translated_data))
                self.last_translated = timezone.now()
                return True
        else:
            translated_text = translation_service.translate_text(
                str(source_value),
                target_lang
            )
            
            if translated_text:
                if hasattr(translated_text, 'text'):
                    translated_text = translated_text.text
                    
                target_field = f"{field_name}_{target_lang}"
                setattr(self, target_field, translated_text)
                self.last_translated = timezone.now()
                return True
            
        return False
    
    def update_translations(self, fields=None):
        """Update translations for all or specific fields"""
        if not self.auto_translate:
            return
            
        fields_to_translate = fields or ['question', 'answer']
        target_languages = ['hi', 'bn']
        
        for field in fields_to_translate:
            for lang in target_languages:
                self.translate_field(field, lang)
    
    def get_translated_text(self, field_name, language_code):
        """Get translated text for a field and language, using cache"""
        cache_key = self._get_cache_key(field_name, language_code)
        
        cached_value = cache.get(cache_key)
        if cached_value is not None:
            return cached_value
        
        if language_code == 'en':
            value = getattr(self, field_name)
        else:
            translated_field = f"{field_name}_{language_code}"
            value = getattr(self, translated_field, None)
            
            if not value and self.auto_translate:
                self.translate_field(field_name, language_code)
                value = getattr(self, translated_field, None)
            
            if not value:
                value = getattr(self, field_name)
        
        cache.set(cache_key, value, timeout=getattr(settings, 'CACHE_TTL', 60 * 15))
        return value
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        
        if not is_new:
            languages = ['en', 'hi', 'bn']
            fields = ['question', 'answer']
            
            for lang in languages:
                for field in fields:
                    cache_key = self._get_cache_key(field, lang)
                    cache.delete(cache_key)
        
        super().save(*args, **kwargs)
        
        if self.auto_translate:
            self.update_translations()


@receiver(pre_save, sender=FAQ)
def update_translations_on_change(sender, instance, **kwargs):
    """Update translations when English content changes"""
    if instance.pk:
        try:
            old_instance = FAQ.objects.get(pk=instance.pk)
            fields_to_translate = []
            
            if old_instance.question != instance.question:
                fields_to_translate.append('question')
            if old_instance.answer != instance.answer:
                fields_to_translate.append('answer')
            
            if fields_to_translate and instance.auto_translate:
                instance.update_translations(fields_to_translate)
        except FAQ.DoesNotExist:
            pass

class SimpleQuestion(models.Model):
    """A simplified model for basic testing without Quill fields"""
    question = models.TextField(verbose_name="Question")
    answer = models.TextField(verbose_name="Answer")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question[:100]

    class Meta:
        verbose_name = "Simple Question"
        verbose_name_plural = "Simple Questions"
        ordering = ['-created_at']
