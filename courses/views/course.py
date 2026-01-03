
from rest_framework import viewsets
from courses.models import Course
from courses.serializer.course import CourseSerializer, CourseListSerializer
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated


class CourseViewSet(viewsets.ModelViewSet):
  queryset = Course.objects.all()
  serializer_class = CourseSerializer

  def get_permissions(self):
    if self.action in ['list', 'retrieve']:
      return [AllowAny()]
    elif self.action in ['create', 'update', 'destroy']:
      return [IsAdminUser()]
    return [IsAuthenticated()]

  def get_serializer_class(self):
    if self.action == 'list':
      return CourseListSerializer
    return CourseSerializer


  def perform_create(self, serializer):
    serializer.save(created_by=self.request.user)

  def perform_update(self, serializer):
    serializer.save(updated_by=self.request.user)

  def perform_destroy(self, instance):
    instance.delete()