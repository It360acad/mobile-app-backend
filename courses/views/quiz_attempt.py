from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from courses.models.quiz_attempt import QuizAttempt
from courses.serializer.quiz_attempt import QuizAttemptSerializer
from courses.permissions import IsEnrolledOrAdmin

class QuizAttemptViewSet(viewsets.ModelViewSet):
    """
    ViewSet for tracking quiz attempts.
    - Students can start and complete attempts.
    - Admins can see all attempts.
    """
    queryset = QuizAttempt.objects.all()
    serializer_class = QuizAttemptSerializer
    permission_classes = [IsAuthenticated, IsEnrolledOrAdmin]

    def get_queryset(self):
        user = self.request.user
        queryset = QuizAttempt.objects.select_related('quiz', 'user')
        
        # Filter by quiz if provided in URL (nested)
        quiz_pk = self.kwargs.get('quiz_pk')
        if quiz_pk:
            queryset = queryset.filter(quiz_id=quiz_pk)
            
        if user.is_staff or getattr(user, 'role', '') == 'admin':
            return queryset
        
        return queryset.filter(user=user)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark an attempt as completed with a score"""
        attempt = self.get_object()
        
        if attempt.completed_at:
            return Response(
                {'error': 'This attempt has already been completed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        score = request.data.get('score')
        if score is None:
            return Response(
                {'error': 'Score is required to complete an attempt.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        attempt.complete_attempt(float(score))
        
        return Response(self.get_serializer(attempt).data)

