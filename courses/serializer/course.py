from courses.models.course import Course
from rest_framework import serializers
from users.serializer import UserSerializer
from django.utils.text import slugify


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for the Course model"""
    
    created_by = UserSerializer(read_only=True)
    updated_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'slug', 'price', 'is_published', 
            'status', 'level', 'cover_image', 'cover_video', 'enrollment_count', 
            'duration', 'start_date', 'end_date', 'category', 'created_at', 
            'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'created_by', 'updated_by', 
            'enrollment_count'
        ]
        extra_kwargs = {
            'slug': {'required': False},
        }
    
    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError('Course title cannot be empty')
        return value.strip()
    
    def create(self, validated_data):
        """Auto-generate slug if not provided"""
        if 'slug' not in validated_data or not validated_data['slug']:
            validated_data['slug'] = slugify(validated_data['title'])
        
        # Set created_by from the request user
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
            validated_data['updated_by'] = request.user
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update course and auto-regenerate slug if name changed"""
        if 'title' in validated_data and validated_data['title'] != instance.title:
            if 'slug' not in validated_data:
                validated_data['slug'] = slugify(validated_data['title'])
        
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['updated_by'] = request.user
        
        return super().update(instance, validated_data)


class CourseListSerializer(serializers.ModelSerializer):
    """Serializer for the Course model in list view"""
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'price', 'is_published', 'status', 
            'level', 'cover_image', 'enrollment_count', 'duration', 
            'start_date', 'end_date', 'category', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'enrollment_count']

