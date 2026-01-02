from rest_framework import permissions
from courses.models.enrollment import CourseEnrollment

class IsEnrolledOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow enrolled students or admins to access lessons/quizzes.
    """
    def has_object_permission(self, request, view, obj):
        # Admins and staff have full access
        if request.user.is_staff or getattr(request.user, 'role', '') == 'admin':
            return True
        
        # Check if the object is a Lesson or Quiz
        course = None
        if hasattr(obj, 'course'):
            course = obj.course
        elif hasattr(obj, 'lesson'):
            course = obj.lesson.course
            
        if not course:
            return False
            
        # Check for active enrollment
        return CourseEnrollment.objects.filter(
            user=request.user, 
            course=course,
            status='active'
        ).exists()

