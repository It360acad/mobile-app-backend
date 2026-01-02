from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import logging

from courses.models.enrollment import CourseEnrollment
from courses.serializer.enrollment import (
    CourseEnrollmentSerializer,
    StudentEnrollmentCreateSerializer,
)

logger = logging.getLogger('courses')


class CourseEnrollmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing course enrollments
    
    Students can:
    - Enroll in courses
    - View their own enrollments
    - Drop courses
    
    Admins can:
    - View all enrollments
    - Manage enrollments
    """
    
    queryset = CourseEnrollment.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter enrollments based on user role and nested parameters"""
        user = self.request.user
        queryset = CourseEnrollment.objects.select_related('user', 'course')
        
        # Nested filtering: course/{course_pk}/enrollments/
        course_pk = self.kwargs.get('course_pk')
        if course_pk:
            queryset = queryset.filter(course_id=course_pk)
            
        # Nested filtering: student/{student_pk}/enrollments/ (or courses)
        student_pk = self.kwargs.get('student_pk')
        if student_pk:
            queryset = queryset.filter(user_id=student_pk)
        
        if user.is_staff or user.role == 'admin':
            return queryset.all()
        
        elif user.role == 'student':
            # Students see only their own enrollments
            return queryset.filter(user=user)
        
        return CourseEnrollment.objects.none()
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'create':
            return StudentEnrollmentCreateSerializer
        return CourseEnrollmentSerializer
    
    def create(self, request, *args, **kwargs):
        """Student enrolls in course"""
        
        # Only students can enroll
        if request.user.role != 'student':
            return Response(
                {'error': 'Only students can enroll in courses.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        enrollment = serializer.save()
        
        logger.info(
            f"Student enrolled in course",
            extra={
                'user_id': request.user.id,
                'course_id': enrollment.course.id,
                'action': 'enrollment_created',
            }
        )
        
        response_serializer = CourseEnrollmentSerializer(enrollment)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def my_enrollments(self, request):
        """Get current user's enrollments (student view)"""
        if request.user.role != 'student':
            return Response(
                {'error': 'This endpoint is for students only.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        enrollments = self.get_queryset().filter(user=request.user)
        
        # Filter by status if provided
        status_filter = request.query_params.get('status')
        if status_filter:
            enrollments = enrollments.filter(status=status_filter)
        
        serializer = self.get_serializer(enrollments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def drop(self, request, pk=None):
        """Drop a course"""
        enrollment = self.get_object()
        
        # Students can drop their own courses
        if request.user.role == 'student':
            if enrollment.user != request.user:
                return Response(
                    {'error': 'You can only drop your own enrollments.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        elif not request.user.is_staff:
            return Response(
                {'error': 'Permission denied.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if can be dropped
        if enrollment.status in ['dropped', 'completed']:
            return Response(
                {'error': f'Cannot drop a {enrollment.status} enrollment.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        enrollment.status = 'dropped'
        enrollment.save()
        
        logger.warning(
            f"Enrollment dropped",
            extra={
                'dropped_by': request.user.id,
                'student_id': enrollment.user.id,
                'enrollment_id': enrollment.id,
                'action': 'enrollment_dropped',
            }
        )
        
        return Response({
            'message': 'Course dropped successfully.',
            'enrollment': self.get_serializer(enrollment).data
        })
