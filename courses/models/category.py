from django.db import models
from users.models import User


class Category(models.Model):
  name = models.CharField(max_length=255, verbose_name='name')
  slug = models.SlugField(unique=True, verbose_name='slug')
  created_at = models.DateTimeField(auto_now_add=True, verbose_name='created at')
  updated_at = models.DateTimeField(auto_now=True, verbose_name='updated at')
  created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_categories')
  updated_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='updated_categories')
  courses_count = models.IntegerField(default=0, verbose_name='course count')

  class Meta:
    verbose_name = 'Category'
    verbose_name_plural = 'Categories'
    ordering = ['name']

  def __str__(self):
    return self.name




