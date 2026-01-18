from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

# Custom User Manager
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


# Custom User Model
class User(AbstractUser):
  email = models.EmailField(unique=True, blank=False, verbose_name='email address')
  password = models.CharField(max_length=128, blank=False, verbose_name='password')
  phone_number = models.CharField(max_length=20, blank=False, default='', verbose_name='phone number', help_text='Required for registration')
  role = models.CharField(max_length=20, blank=False, verbose_name='role', choices=[ ('student', 'Student'), ('parent', 'Parent'), ('admin', 'Admin')], default='student')
  is_verified = models.BooleanField(default=False, verbose_name='email verified')
  
  # Use email as the username field
  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = ['phone_number']  # Required fields for createsuperuser
  
  # Use custom manager
  objects = UserManager()

  def __str__(self):
    return self.email

