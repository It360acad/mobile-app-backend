from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from courses.models import Quiz
from courses.serializer.quiz import QuizSerializer, QuizListSerializer
from courses.permissions import IsEnrolledOrAdmin


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
  permission_classes = [IsAuthenticated, IsEnrolledOrAdmin]

  def get_permissions(self):
    """Admins can do everything, enrolled users can view"""
    if self.action in ['create', 'update', 'partial_update', 'destroy']:
      return [IsAdminUser()]
    return [IsAuthenticated(), IsEnrolledOrAdmin()]

  def get_serializer_class(self):
    """Use lightweight serializer for list view"""
    if self.action == 'list':
      return QuizListSerializer
    return QuizSerializer

  def get_queryset(self):
    """Filter quizzes by lesson and enrollment status"""
    user = self.request.user
    queryset = Quiz.objects.all()
    
    # If nested under lesson, filter by lesson from URL
    lesson_id = self.kwargs.get('lesson_pk') or self.request.query_params.get('lesson_id')
    if lesson_id:
      queryset = queryset.filter(lesson_id=lesson_id)
    
    # If nested under course, filter by course from URL
    course_id = self.kwargs.get('course_pk')
    if course_id:
      queryset = queryset.filter(lesson__course_id=course_id)
    
    # Students can only see quizzes from courses they are enrolled in
    if user.is_authenticated and not (user.is_staff or getattr(user, 'role', '') == 'admin'):
      enrolled_courses = CourseEnrollment.objects.filter(
          user=user, 
          status='active'
      ).values_list('course_id', flat=True)
      queryset = queryset.filter(lesson__course_id__in=enrolled_courses)
    
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

