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
            'is_published', 'course', 'lesson', 'created_at', 'updated_at',
            'created_by', 'updated_by'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
    
    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError('Quiz title cannot be empty')
        return value.strip()
    
    def validate(self, data):
        """Ensure quiz is linked to either course or lesson, but not both"""
        course = data.get('course')
        lesson = data.get('lesson')
        
        if not course and not lesson:
            raise serializers.ValidationError(
                'Quiz must be linked to either a course or a lesson'
            )
        if course and lesson:
            raise serializers.ValidationError(
                'Quiz cannot be linked to both a course and a lesson'
            )
        
        return data
    
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


class QuizListSerializer(serializers.ModelSerializer):
    """Serializer for the Quiz model in list view"""
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'passing_score', 'time_limit',
            'is_published', 'course', 'lesson', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

