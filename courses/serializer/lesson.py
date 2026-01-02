from courses.models.lesson import Lesson
from rest_framework import serializers
from users.serializers import UserSerializer


class LessonSerializer(serializers.ModelSerializer):
    """Serializer for the Lesson model"""
    
    created_by = UserSerializer(read_only=True)
    updated_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'description', 'video_url',
            'duration', 'order', 'is_published', 'course', 'created_at', 
            'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
    
    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError('Lesson title cannot be empty')
        return value.strip()
    
    def create(self, validated_data):
        """Set created_by and updated_by from the request user"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
            validated_data['updated_by'] = request.user
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update updated_by from the request user"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['updated_by'] = request.user
        
        return super().update(instance, validated_data)


class LessonListSerializer(serializers.ModelSerializer):
    """Serializer for the Lesson model in list view"""
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'description', 'video_url', 'duration', 
            'order', 'is_published', 'course', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

