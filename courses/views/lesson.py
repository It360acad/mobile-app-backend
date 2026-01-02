from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from courses.models import Lesson
from courses.serializer.lesson import LessonSerializer, LessonListSerializer
from courses.permissions import IsEnrolledOrAdmin


class LessonViewSet(viewsets.ModelViewSet):
  queryset = Lesson.objects.all()
  serializer_class = LessonSerializer
  permission_classes = [IsAuthenticated, IsEnrolledOrAdmin]

  def get_permissions(self):
    """Admins can do everything, enrolled users can view"""
    if self.action in ['create', 'update', 'partial_update', 'destroy']:
      return [IsAdminUser()]
    return [IsAuthenticated(), IsEnrolledOrAdmin()]

  def get_serializer_class(self):
    """Use lightweight serializer for list view"""
    if self.action == 'list':
      return LessonListSerializer
    return LessonSerializer

  def get_queryset(self):
    """Filter lessons by course and enrollment status"""
    user = self.request.user
    queryset = Lesson.objects.all()
    
    # Filter by course if course_id is provided (query param or nested URL)
    course_id = self.request.query_params.get('course_id') or self.kwargs.get('course_pk')
    if course_id:
      queryset = queryset.filter(course_id=course_id)
    
    # Students can only see lessons from courses they are enrolled in
    if user.is_authenticated and not (user.is_staff or getattr(user, 'role', '') == 'admin'):
      enrolled_courses = CourseEnrollment.objects.filter(
          user=user, 
          status='active'
      ).values_list('course_id', flat=True)
      queryset = queryset.filter(course_id__in=enrolled_courses)
      
    return queryset.order_by('order', 'created_at')

  def perform_create(self, serializer):
    """Automatically set created_by and updated_by"""
    serializer.save(
      created_by=self.request.user,
      updated_by=self.request.user
    )

  def perform_update(self, serializer):
    """Automatically update updated_by"""
    serializer.save(updated_by=self.request.user)