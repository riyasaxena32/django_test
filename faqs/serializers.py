from rest_framework import serializers
from .models import FAQ

class FAQSerializer(serializers.ModelSerializer):
    """Serializer for FAQ model with language-based translations"""
    question = serializers.SerializerMethodField()
    answer = serializers.SerializerMethodField()
    
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'created_at', 'updated_at', 'is_active']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_question(self, obj):
        lang = self.context.get('language', 'en')
        return obj.get_translated_text('question', lang)
    
    def get_answer(self, obj):
        lang = self.context.get('language', 'en')
        answer = obj.get_translated_text('answer', lang)
        return answer.html if hasattr(answer, 'html') else str(answer)

class FAQAdminSerializer(serializers.ModelSerializer):
    """Serializer for FAQ model with all fields for admin operations"""
    class Meta:
        model = FAQ
        fields = [
            'id', 'question', 'answer',
            'question_hi', 'answer_hi',
            'question_bn', 'answer_bn',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at'] 