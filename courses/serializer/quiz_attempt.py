from rest_framework import serializers
from courses.models.quiz_attempt import QuizAttempt

class QuizAttemptSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='user.get_full_name', read_only=True)
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'user', 'student_name', 'quiz', 'quiz_title', 
            'score', 'started_at', 'completed_at', 
            'time_spent_minutes', 'is_passed'
        ]
        read_only_fields = ['id', 'user', 'started_at', 'completed_at', 'time_spent_minutes', 'is_passed']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

