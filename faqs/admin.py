from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.utils import timezone
from .models import FAQ

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = [
        'question_preview', 
        'translation_status', 
        'last_translated_display',
        'is_active',
        'created_at'
    ]
    list_filter = [
        'is_active', 
        'auto_translate', 
        ('last_translated', admin.EmptyFieldListFilter),
        'created_at'
    ]
    search_fields = [
        'question', 'answer__html',
        'question_hi', 'answer_hi__html',
        'question_bn', 'answer_bn__html'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'last_translated',
        'translation_preview_hi', 'translation_preview_bn'
    ]
    actions = ['update_translations', 'toggle_active_status']
    list_per_page = 20
    save_on_top = True
    
    fieldsets = [
        ('English Content', {
            'fields': ['question', 'answer', 'is_active'],
            'classes': ['wide']
        }),
        ('Translation Settings', {
            'fields': ['auto_translate', 'last_translated'],
            'classes': ['collapse'],
            'description': 'Configure automatic translation settings'
        }),
        ('Hindi Translation', {
            'fields': ['question_hi', 'answer_hi', 'translation_preview_hi'],
            'classes': ['collapse'],
            'description': 'Hindi version of the FAQ'
        }),
        ('Bengali Translation', {
            'fields': ['question_bn', 'answer_bn', 'translation_preview_bn'],
            'classes': ['collapse'],
            'description': 'Bengali version of the FAQ'
        }),
        ('Metadata', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse'],
            'description': 'FAQ creation and modification timestamps'
        })
    ]
    
    def question_preview(self, obj):
        """Show a preview of the question with a link to edit"""
        preview = obj.question[:75] + '...' if len(obj.question) > 75 else obj.question
        url = reverse('admin:faqs_faq_change', args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, preview)
    question_preview.short_description = 'Question'
    
    def last_translated_display(self, obj):
        """Display last translation time with color coding"""
        if not obj.last_translated:
            return format_html(
                '<span style="color: red;">Never translated</span>'
            )
        
        time_diff = timezone.now() - obj.last_translated
        if time_diff.days > 30:
            color = 'red'
            status = f'Old ({time_diff.days} days ago)'
        elif time_diff.days > 7:
            color = 'orange'
            status = f'{time_diff.days} days ago'
        else:
            color = 'green'
            status = 'Recent'
            
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            status
        )
    last_translated_display.short_description = 'Translation Age'
    
    def translation_status(self, obj):
        """Display translation status with colored indicators"""
        status_html = []
        
        hi_complete = obj.question_hi and obj.answer_hi
        hi_status = '✓' if hi_complete else '✗'
        hi_color = 'green' if hi_complete else 'red'
        hi_title = 'Hindi translation complete' if hi_complete else 'Hindi translation missing'
        status_html.append(
            f'<span title="{hi_title}" style="color: {hi_color};">HI: {hi_status}</span>'
        )
        
        bn_complete = obj.question_bn and obj.answer_bn
        bn_status = '✓' if bn_complete else '✗'
        bn_color = 'green' if bn_complete else 'red'
        bn_title = 'Bengali translation complete' if bn_complete else 'Bengali translation missing'
        status_html.append(
            f'<span title="{bn_title}" style="color: {bn_color};">BN: {bn_status}</span>'
        )
        
        return format_html(
            '<div style="white-space: nowrap;">{}</div>',
            mark_safe('&nbsp;|&nbsp;'.join(status_html))
        )
    translation_status.short_description = 'Translations'
    
    def translation_preview_hi(self, obj):
        """Show Hindi translation preview"""
        if not obj.question_hi or not obj.answer_hi:
            return "Hindi translation not available"
        return format_html(
            '<strong>Question:</strong><br>{}<br><br>'
            '<strong>Answer:</strong><br>{}',
            obj.question_hi,
            mark_safe(obj.answer_hi.html if hasattr(obj.answer_hi, 'html') else obj.answer_hi)
        )
    translation_preview_hi.short_description = 'Hindi Preview'
    
    def translation_preview_bn(self, obj):
        """Show Bengali translation preview"""
        if not obj.question_bn or not obj.answer_bn:
            return "Bengali translation not available"
        return format_html(
            '<strong>Question:</strong><br>{}<br><br>'
            '<strong>Answer:</strong><br>{}',
            obj.question_bn,
            mark_safe(obj.answer_bn.html if hasattr(obj.answer_bn, 'html') else obj.answer_bn)
        )
    translation_preview_bn.short_description = 'Bengali Preview'
    
    def toggle_active_status(self, request, queryset):
        """Toggle active status for selected FAQs"""
        for faq in queryset:
            faq.is_active = not faq.is_active
            faq.save()
        
        self.message_user(
            request,
            f"Toggled active status for {queryset.count()} FAQs."
        )
    toggle_active_status.short_description = "Toggle active status"
    
    def update_translations(self, request, queryset):
        """Update translations for selected FAQs"""
        updated = 0
        for faq in queryset:
            if faq.auto_translate:
                faq.update_translations()
                faq.save()
                updated += 1
        
        skipped = queryset.count() - updated
        message = f"Updated translations for {updated} FAQs."
        if skipped:
            message += f" Skipped {skipped} FAQs (auto-translate disabled)."
        
        self.message_user(request, message)
    update_translations.short_description = "Update translations"
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/custom_admin.js',)
