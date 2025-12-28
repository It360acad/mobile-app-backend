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
  role = models.CharField(max_length=20, blank=False, verbose_name='role', choices=[ ('student', 'Student'), ('parent', 'Parent'), ('admin', 'Admin')], default='student')
  is_verified = models.BooleanField(default=False, verbose_name='email verified')
  
  # Use email as the username field
  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = []  # No additional required fields
  
  # Use custom manager
  objects = UserManager()

  def __str__(self):
    return self.email


  
class Profile(models.Model):

  GENDER_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
  ]

  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
  bio = models.TextField(blank=True, verbose_name='bio')
  # profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, verbose_name='profile picture')
  date_joined = models.DateTimeField(auto_now_add=True, verbose_name='date joined')
  last_login = models.DateTimeField(auto_now=True, verbose_name='last login')
  address = models.TextField(blank=True, verbose_name='address')
  phone_number = models.CharField(max_length=20, blank=True, verbose_name='phone number')
  city = models.CharField(max_length=100, blank=True, verbose_name='city')
  state = models.CharField(max_length=100, blank=True, verbose_name='state')
  zip_code = models.CharField(max_length=20, blank=True, verbose_name='zip code')
  country = models.CharField(max_length=100, blank=True, verbose_name='country')
  date_of_birth = models.DateField(blank=True, verbose_name='date of birth')
  gender = models.CharField(max_length=20, blank=True, verbose_name='gender', choices=GENDER_CHOICES)


  class Meta:
    verbose_name = 'Profile'
    verbose_name_plural = 'Profiles'

  def __str__(self):
    return self.user.email

  def get_profile_picture(self):
    if self.profile_picture:
      return self.profile_picture.url
    return None