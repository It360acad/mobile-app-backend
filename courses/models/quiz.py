from django.db import models
from courses.models.course import Course
from courses.models.lesson import Lesson
from users.models import User


class Quiz(models.Model):
  title = models.CharField(max_length=200, verbose_name='title')
  description = models.TextField(blank=True, verbose_name='description')
  passing_score = models.IntegerField(default=70, verbose_name='passing score percentage')
  time_limit = models.IntegerField(default=0, verbose_name='time limit in minutes (0 = no limit)')
  is_published = models.BooleanField(default=False, verbose_name='is published')
  created_at = models.DateTimeField(auto_now_add=True, verbose_name='created at')
  updated_at = models.DateTimeField(auto_now=True, verbose_name='updated at')
  course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes', null=True, blank=True)
  lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='quizzes', null=True, blank=True)
  created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_quizzes')
  updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updated_quizzes')

  class Meta:
    verbose_name = 'Quiz'
    verbose_name_plural = 'Quizzes'
    ordering = ['-created_at']

  def __str__(self):
    return self.title

