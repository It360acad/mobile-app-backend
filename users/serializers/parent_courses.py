"""
Serializers for parent's children's course enrollments
"""
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from courses.models.enrollment import CourseEnrollment
from courses.serializer.course import CourseListSerializer
from users.models import Student
from users.serializers.user import UserDetailSerializer


class ChildEnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for a child's enrollment in a course"""
    course = CourseListSerializer(read_only=True)
    student_name = serializers.CharField(source='user.get_full_name', read_only=True)
    student_email = serializers.EmailField(source='user.email', read_only=True)
    is_active = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()
    
    class Meta:
        model = CourseEnrollment
        fields = [
            'id',
            'course',
            'student_name',
            'student_email',
            'enrolled_at',
            'completed_at',
            'last_accessed',
            'progress_percentage',
            'status',
            'is_active',
            'is_completed',
            'total_watch_time_minutes',
            'quiz_average_score',
            'enrollment_notes',
        ]
        read_only_fields = fields
    
    @extend_schema_field(serializers.BooleanField())
    def get_is_active(self, obj) -> bool:
        """Check if enrollment is active"""
        return obj.is_active
    
    @extend_schema_field(serializers.BooleanField())
    def get_is_completed(self, obj) -> bool:
        """Check if enrollment is completed"""
        return obj.is_completed


class ChildWithCoursesSerializer(serializers.Serializer):
    """Serializer for a child with their enrolled courses"""
    child = UserDetailSerializer(read_only=True)
    student_id = serializers.CharField(read_only=True)
    current_class = serializers.CharField(read_only=True)
    current_school = serializers.CharField(read_only=True)
    enrollments = ChildEnrollmentSerializer(many=True, read_only=True)
    total_enrollments = serializers.IntegerField(read_only=True)
    active_enrollments = serializers.IntegerField(read_only=True)
    completed_enrollments = serializers.IntegerField(read_only=True)


class ParentChildrenCoursesSerializer(serializers.Serializer):
    """Serializer for parent's view of all children's courses"""
    parent_name = serializers.CharField(read_only=True)
    parent_email = serializers.EmailField(read_only=True)
    total_children = serializers.IntegerField(read_only=True)
    children = ChildWithCoursesSerializer(many=True, read_only=True)
    total_enrollments = serializers.IntegerField(read_only=True)
    total_active_enrollments = serializers.IntegerField(read_only=True)
    total_completed_enrollments = serializers.IntegerField(read_only=True)

