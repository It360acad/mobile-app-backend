from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from courses.models import Lesson
from courses.serializer.lesson import LessonSerializer, LessonListSerializer


class LessonViewSet(viewsets.ModelViewSet):
  queryset = Lesson.objects.all()
  serializer_class = LessonSerializer
  permission_classes = [IsAuthenticated]

  def get_permissions(self):
    """List and retrieve are public, create/update/delete require admin"""
    if self.action in ['list', 'retrieve']:
      return [AllowAny()]
    elif self.action in ['create', 'update', 'destroy']:
      return [IsAdminUser()]
    return [IsAuthenticated()]

  def get_serializer_class(self):
    """Use lightweight serializer for list view"""
    if self.action == 'list':
      return LessonListSerializer
    return LessonSerializer

  def get_queryset(self):
    """Filter lessons by course if course_id is provided in query params"""
    queryset = Lesson.objects.all()
    course_id = self.request.query_params.get('course_id', None)
    if course_id:
      queryset = queryset.filter(course_id=course_id)
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