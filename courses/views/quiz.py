from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from courses.models import Quiz
from courses.serializer.quiz import QuizSerializer, QuizListSerializer


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='course_pk',
            type=int,
            location=OpenApiParameter.PATH,
            description='Course ID (from nested route)',
        ),
        OpenApiParameter(
            name='lesson_pk',
            type=int,
            location=OpenApiParameter.PATH,
            description='Lesson ID (from nested route)',
        ),
    ]
)
class QuizViewSet(viewsets.ModelViewSet):
  queryset = Quiz.objects.all()
  serializer_class = QuizSerializer
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
      return QuizListSerializer
    return QuizSerializer

  def get_queryset(self):
    """Filter quizzes by lesson if provided in query params or URL"""
    queryset = Quiz.objects.all()
    
    # If nested under lesson, filter by lesson from URL
    lesson_id = self.kwargs.get('lesson_pk') or self.request.query_params.get('lesson_id')
    if lesson_id:
      queryset = queryset.filter(lesson_id=lesson_id)
    
    return queryset.order_by('-created_at')

  def perform_create(self, serializer):
    """Automatically set created_by, updated_by, and lesson if nested"""
    # If nested under lesson, set lesson from URL then
    lesson_id = self.kwargs.get('lesson_pk')
    if lesson_id:
      serializer.save(
        created_by=self.request.user,
        updated_by=self.request.user,
        lesson_id=lesson_id
      )
    else:
      serializer.save(
        created_by=self.request.user,
        updated_by=self.request.user
      )

  def perform_update(self, serializer):
    """Automatically update updated_by"""
    serializer.save(updated_by=self.request.user)

