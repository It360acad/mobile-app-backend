from django.db import models
from courses.models.quiz import Quiz
from users.models import User
from django.utils import timezone

class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Track time used in minutes
    time_spent_minutes = models.IntegerField(default=0, help_text="Time used to complete the quiz in minutes")
    
    is_passed = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Quiz Attempt'
        verbose_name_plural = 'Quiz Attempts'
        ordering = ['-started_at']

    def __str__(self):
        return f"Attempt by {self.user.email} on {self.quiz.title}"

    def complete_attempt(self, score):
        self.score = score
        self.completed_at = timezone.now()
        
        # Calculate time spent
        duration = self.completed_at - self.started_at
        self.time_spent_minutes = int(duration.total_seconds() / 60)
        
        # Check if passed
        if self.score >= self.quiz.passing_score:
            self.is_passed = True
            
        self.save()

