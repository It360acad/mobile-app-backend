from rest_framework import serializers
from courses.models.bookmark import CourseBookmark
from courses.serializer.course import CourseListSerializer

class CourseBookmarkSerializer(serializers.ModelSerializer):
    course_details = CourseListSerializer(source='course', read_only=True)
    
    class Meta:
        model = CourseBookmark
        fields = ['id', 'user', 'course', 'course_details', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def validate(self, attrs):
        user = self.context['request'].user
        course = attrs.get('course')
        
        if CourseBookmark.objects.filter(user=user, course=course).exists():
            raise serializers.ValidationError("You have already bookmarked this course.")
        
        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

