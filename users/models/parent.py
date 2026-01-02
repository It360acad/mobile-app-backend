from django.db import models
from .user import User

class Parent(models.Model):

  RELATIONSHIP_CHOICES = [
    ('father', 'Father'),
    ('mother', 'Mother'),
    ('guardian', 'Guardian'),
  ]

  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
  parent_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
  occupation = models.CharField(max_length=200, blank=True, null=True)
  relationship_to_student = models.CharField(max_length=200, blank=True, null=True, choices=[('father', 'Father'), ('mother', 'Mother'), ('guardian', 'Guardian')])
  
  def __str__(self):
      return f"Parent: {self.user.email}"

