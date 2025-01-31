from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from redis.exceptions import RedisError
from .models import FAQ
from .serializers import FAQSerializer, FAQAdminSerializer

class FAQViewSet(viewsets.ModelViewSet):
    """
    API endpoint for FAQs with language support and Redis caching
    """
    queryset = FAQ.objects.filter(is_active=True)
    
    def get_serializer_class(self):
        if self.request.user.is_staff and self.action in ['create', 'update', 'partial_update']:
            return FAQAdminSerializer
        return FAQSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['language'] = self.request.query_params.get('lang', 'en')
        return context
    
    def _get_cache_key_for_list(self, language):
        """Generate a cache key for the FAQ list in a specific language"""
        return f'faq_list:{language}'
    
    def _get_cache_key_for_languages(self):
        """Generate a cache key for the by_language view"""
        return 'faq_list:all_languages'
    
    def _safe_cache_get(self, key):
        """Safely get data from cache, handling potential Redis errors"""
        try:
            return cache.get(key)
        except (RedisError, ImproperlyConfigured):
            return None
    
    def _safe_cache_set(self, key, value, timeout=None):
        """Safely set data in cache, handling potential Redis errors"""
        try:
            timeout = timeout or getattr(settings, 'CACHE_TTL', 60 * 15)
            cache.set(key, value, timeout=timeout)
        except (RedisError, ImproperlyConfigured):
            pass
    
    def list(self, request, *args, **kwargs):
        """
        List FAQs with language support and Redis caching
        """
        language = request.query_params.get('lang', 'en')
        cache_key = self._get_cache_key_for_list(language)
        
        # Try to get from cache
        cached_data = self._safe_cache_get(cache_key)
        if cached_data is not None:
            return Response(cached_data)
        
        # If not in cache or cache failed, generate response
        response = super().list(request, *args, **kwargs)
        
        # Try to cache the response data
        self._safe_cache_set(cache_key, response.data)
        return response
    
    @action(detail=False, methods=['get'])
    def by_language(self, request):
        """
        Get FAQs grouped by available languages with Redis caching
        """
        cache_key = self._get_cache_key_for_languages()
        
        # Try to get from cache
        cached_data = self._safe_cache_get(cache_key)
        if cached_data is not None:
            return Response(cached_data)
        
        # If not in cache or cache failed, generate response
        languages = ['en', 'hi', 'bn']
        result = {}
        
        for lang in languages:
            list_cache_key = self._get_cache_key_for_list(lang)
            lang_data = self._safe_cache_get(list_cache_key)
            
            if lang_data is None:
                serializer = FAQSerializer(
                    self.get_queryset(),
                    many=True,
                    context={'language': lang, 'request': request}
                )
                lang_data = serializer.data
                self._safe_cache_set(list_cache_key, lang_data)
            
            result[lang] = lang_data
        
        # Try to cache the complete response
        self._safe_cache_set(cache_key, result)
        return Response(result)
    
    def perform_update(self, serializer):
        """Clear relevant caches when an FAQ is updated"""
        instance = serializer.instance
        languages = ['en', 'hi', 'bn']
        
        # Clear individual FAQ caches
        for lang in languages:
            try:
                cache.delete(self._get_cache_key_for_list(lang))
            except (RedisError, ImproperlyConfigured):
                pass
        
        # Clear the by_language cache
        try:
            cache.delete(self._get_cache_key_for_languages())
        except (RedisError, ImproperlyConfigured):
            pass
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Clear relevant caches when an FAQ is deleted"""
        languages = ['en', 'hi', 'bn']
        
        # Clear individual FAQ caches
        for lang in languages:
            try:
                cache.delete(self._get_cache_key_for_list(lang))
            except (RedisError, ImproperlyConfigured):
                pass
        
        # Clear the by_language cache
        try:
            cache.delete(self._get_cache_key_for_languages())
        except (RedisError, ImproperlyConfigured):
            pass
        
        instance.delete() 