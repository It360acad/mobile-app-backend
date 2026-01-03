from rest_framework import serializers
from courses.models.review import CourseReview
from users.serializers import UserDetailSerializer

class CourseReviewSerializer(serializers.ModelSerializer):
    user_details = UserDetailSerializer(source='user', read_only=True)
    
    class Meta:
        model = CourseReview
        fields = ['id', 'user', 'user_details', 'course', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate(self, attrs):
        user = self.context['request'].user
        course = attrs.get('course')
        
        # Check if already reviewed
        if self.instance is None and CourseReview.objects.filter(user=user, course=course).exists():
            raise serializers.ValidationError("You have already reviewed this course.")
        
        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

