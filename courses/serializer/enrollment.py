from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from courses.models.enrollment import CourseEnrollment
from courses.serializer.course import CourseListSerializer


class CourseEnrollmentSerializer(serializers.ModelSerializer):
    """Full enrollment details"""
    course_details = CourseListSerializer(source='course', read_only=True)
    student_email = serializers.EmailField(source='user.email', read_only=True)
    student_name = serializers.CharField(source='user.get_full_name', read_only=True)
    is_completed = serializers.SerializerMethodField()
    
    @extend_schema_field(serializers.BooleanField())
    def get_is_completed(self, obj) -> bool:
        """Check if enrollment is completed"""
        return obj.is_completed
    
    class Meta:
        model = CourseEnrollment
        fields = [
            'id',
            'user',
            'student_email',
            'student_name',
            'course',
            'course_details',
            'enrolled_at',
            'completed_at',
            'last_accessed',
            'progress_percentage',
            'status',
            'is_completed',
            'total_watch_time_minutes',
            'quiz_average_score',
            'enrollment_notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'enrolled_at',
            'last_accessed',
            'created_at',
            'updated_at',
        ]


class StudentEnrollmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for student to request enrollment"""
    
    class Meta:
        model = CourseEnrollment
        fields = ['course', 'enrollment_notes']
    
    def validate_course(self, value):
        """Validate course enrollment"""
        if not value.is_published:
            raise serializers.ValidationError("This course is not available for enrollment.")
        
        user = self.context['request'].user
        
        # Check if user is a student
        if not hasattr(user, 'student_profile'):
            raise serializers.ValidationError("Only students can enroll in courses.")
        
        # Check if already enrolled
        if CourseEnrollment.objects.filter(user=user, course=value).exists():
            raise serializers.ValidationError("You are already enrolled in this course.")
        
        return value
    
    def create(self, validated_data):
        """Create enrollment"""
        user = self.context['request'].user
        validated_data['user'] = user
        validated_data['status'] = 'active'
        return super().create(validated_data)
