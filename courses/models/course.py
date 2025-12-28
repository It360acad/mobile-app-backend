from django.db import models
from courses.models.category import Category
from users.models import User


class Course(models.Model):
  LEVEL_CHOICES = [
    ('beginner', 'Beginner'),
    ('intermediate', 'Intermediate'),
    ('advanced', 'Advanced'),
  ]

  STATUS_CHOICES = [
    ('active', 'Active'),
    ('inactive', 'Inactive'),
  ]

  title = models.CharField(max_length=200, verbose_name='title')
  description = models.TextField(verbose_name='description')
  created_at = models.DateTimeField(auto_now_add=True, verbose_name='created at')
  updated_at = models.DateTimeField(auto_now=True, verbose_name='updated at')
  price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='price')
  is_published = models.BooleanField(default=False, verbose_name='is published')
  status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive', verbose_name='status')
  level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner', verbose_name='level')
  cover_image = models.ImageField(upload_to='courses/covers/', blank=True, verbose_name='cover image')
  cover_video = models.FileField(upload_to='courses/covers/', blank=True, verbose_name='cover video')
  enrollment_count = models.IntegerField(default=0, verbose_name='enrollment count')
  duration = models.IntegerField(default=0, verbose_name='duration')
  slug = models.SlugField(unique=True, verbose_name='slug')
  start_date = models.DateField(verbose_name='start date')
  end_date = models.DateField(verbose_name='end date')
  category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='courses')
  created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_courses')
  updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updated_courses')

  class Meta:
    verbose_name = 'Course'
    verbose_name_plural = 'Courses'
    ordering = ['-created_at']

  def __str__(self):
    return self.title

