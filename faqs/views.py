from django.shortcuts import render
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from redis.exceptions import RedisError
from .models import FAQ

def faq_list(request):
    language_code = request.GET.get('lang', 'en')
    faqs = FAQ.objects.filter(is_active=True)
    
    # Prepare FAQ data with translations
    faq_data = []
    for faq in faqs:
        try:
            answer = faq.get_translated_text('answer', language_code)
            # Extract the HTML content from the Quill field
            answer_html = answer.html if hasattr(answer, 'html') else str(answer)
            
            faq_data.append({
                'question': faq.get_translated_text('question', language_code),
                'answer': answer_html
            })
        except (RedisError, ImproperlyConfigured) as e:
            # Fallback to direct database access if cache fails
            if language_code == 'en':
                answer = faq.answer
            else:
                translated_field = f"answer_{language_code}"
                answer = getattr(faq, translated_field, None) or faq.answer
            
            answer_html = answer.html if hasattr(answer, 'html') else str(answer)
            
            faq_data.append({
                'question': getattr(faq, f"question_{language_code}", None) or faq.question,
                'answer': answer_html
            })
    
    return render(request, 'faqs/faq_list.html', {
        'faqs': faq_data,
        'current_language': language_code
    })
