from django.db import models
from .user import User

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
  date_of_birth = models.DateField(blank=True, null=True, verbose_name='date of birth')
  gender = models.CharField(max_length=20, blank=True, verbose_name='gender', choices=GENDER_CHOICES)


  class Meta:
    verbose_name = 'Profile'
    verbose_name_plural = 'Profiles'

  def __str__(self):
    return self.user.email

  def get_profile_picture(self):
    if hasattr(self, 'profile_picture') and self.profile_picture:
      return self.profile_picture.url
    return None

