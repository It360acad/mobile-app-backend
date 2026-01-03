from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from courses.models.review import CourseReview
from courses.models.enrollment import CourseEnrollment
from courses.serializer.review import CourseReviewSerializer

class CourseReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for course reviews.
    - Anyone can see reviews.
    - Enrolled students can create/update their own reviews.
    - Only admins can delete reviews.
    """
    queryset = CourseReview.objects.all()
    serializer_class = CourseReviewSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = CourseReview.objects.select_related('user', 'course')
        course_pk = self.kwargs.get('course_pk')
        if course_pk:
            queryset = queryset.filter(course_id=course_pk)
        return queryset

    def create(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get('course')
        
        # Ensure user is a student
        if getattr(user, 'role', '') != 'student':
            return Response(
                {'error': 'Only students can leave reviews.'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        # Check for enrollment
        if not CourseEnrollment.objects.filter(user=user, course_id=course_id, status='active').exists():
            return Response(
                {'error': 'You must be enrolled in this course to leave a review.'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        review = self.get_object()
        if review.user != request.user:
            return Response(
                {'error': 'You can only edit your own reviews.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # Only admins or staff can delete reviews
        if not (request.user.is_staff or getattr(request.user, 'role', '') == 'admin'):
            return Response(
                {'error': 'Only admins can delete reviews.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

