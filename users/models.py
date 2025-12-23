from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom User Model
class User(AbstractUser):
  email = models.EmailField(unique=True, blank=False, verbose_name='email address')
  password = models.CharField(max_length=128, blank=False, verbose_name='password')
  role = models.CharField(max_length=20, blank=False, verbose_name='role', choices=[ ('student', 'Student'), ('teacher', 'Teacher')], default='student')
  is_verified = models.BooleanField(default=False, verbose_name='email verified')
  
  # Use email as the username field
  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = []  # No additional required fields

  def __str__(self):
    return self.email