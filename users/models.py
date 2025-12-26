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