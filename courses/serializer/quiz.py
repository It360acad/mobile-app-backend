from courses.models.quiz import Quiz
from rest_framework import serializers
from users.serializer import UserSerializer


class QuizSerializer(serializers.ModelSerializer):
    """Serializer for the Quiz model"""
    
    created_by = UserSerializer(read_only=True)
    updated_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'passing_score', 'time_limit',
            'is_published', 'lesson', 'created_at', 'updated_at',
            'created_by', 'updated_by'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
    
    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError('Quiz title cannot be empty')
        return value.strip()
    
    


class QuizListSerializer(serializers.ModelSerializer):
    """Serializer for the Quiz model in list view"""
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'passing_score', 'time_limit',
            'is_published', 'lesson', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

