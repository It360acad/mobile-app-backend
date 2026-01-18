from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from courses.models.bookmark import CourseBookmark
from courses.serializer.bookmark import CourseBookmarkSerializer

@extend_schema_view(
    list=extend_schema(parameters=[
        OpenApiParameter('student_id', int, OpenApiParameter.PATH, description='Student ID (from nested route)'),
    ]),
    retrieve=extend_schema(parameters=[
        OpenApiParameter('student_id', int, OpenApiParameter.PATH, description='Student ID (from nested route)'),
    ]),
    create=extend_schema(parameters=[
        OpenApiParameter('student_id', int, OpenApiParameter.PATH, description='Student ID (from nested route)'),
    ]),
    update=extend_schema(parameters=[
        OpenApiParameter('student_id', int, OpenApiParameter.PATH, description='Student ID (from nested route)'),
    ]),
    destroy=extend_schema(parameters=[
        OpenApiParameter('student_id', int, OpenApiParameter.PATH, description='Student ID (from nested route)'),
    ]),
)
class CourseBookmarkViewSet(viewsets.ModelViewSet):
    """
    ViewSet for students to bookmark courses.
    """
    queryset = CourseBookmark.objects.all()
    serializer_class = CourseBookmarkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = CourseBookmark.objects.select_related('course')
        
        # Nested filtering: students/{student_pk}/bookmarks/
        student_pk = self.kwargs.get('student_pk')
        if student_pk:
            queryset = queryset.filter(user_id=student_pk)
            
        if user.is_staff or user.role == 'admin':
            return queryset
        
        return queryset.filter(user=user)

    def create(self, request, *args, **kwargs):
        # Ensure only students can bookmark
        if request.user.role != 'student':
            return Response(
                {'error': 'Only students can bookmark courses.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)

