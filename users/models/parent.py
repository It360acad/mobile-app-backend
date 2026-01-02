from django.db import models
from .user import User

class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
    
    def __str__(self):
        return f"Parent: {self.user.email}"

