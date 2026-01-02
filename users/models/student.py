from django.db import models
from .user import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    
    def __str__(self):
        return f"Student: {self.user.email}"
