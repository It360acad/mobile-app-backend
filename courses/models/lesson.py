from django.db import models
from courses.models.course import Course
from users.models import User


class Lesson(models.Model):
  title = models.CharField(max_length=200, verbose_name='title')
  description = models.TextField(blank=True, verbose_name='description')
  content = models.TextField(verbose_name='content')
  video_url = models.URLField(blank=True, verbose_name='video url')
  video_file = models.FileField(upload_to='courses/lessons/videos/', blank=True, verbose_name='video file')
  duration = models.IntegerField(default=0, verbose_name='duration in minutes')
  order = models.IntegerField(default=0, verbose_name='order')
  is_published = models.BooleanField(default=False, verbose_name='is published')
  created_at = models.DateTimeField(auto_now_add=True, verbose_name='created at')
  updated_at = models.DateTimeField(auto_now=True, verbose_name='updated at')
  course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
  created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_lessons')
  updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updated_lessons')

  class Meta:
    verbose_name = 'Lesson'
    verbose_name_plural = 'Lessons'
    ordering = ['order', 'created_at']

  def __str__(self):
    return self.title

