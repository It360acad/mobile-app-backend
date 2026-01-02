import secrets
import string
from django.db import models
from .user import User

def generate_linking_code():
    """Generates a code in format XXX-XXXXXXXXX (e.g., 58D-904783732)"""
    part1 = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(3))
    part2 = ''.join(secrets.choice(string.digits) for _ in range(9))
    return f"{part1}-{part2}"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    linking_code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    
    # Relationships
    parent = models.ForeignKey('users.Parent', on_delete=models.SET_NULL, related_name='students', null=True, blank=True, help_text='Primary parent')
    categories = models.ManyToManyField('courses.Category', related_name='students', blank=True, help_text='Categories student is interested in')
    
    current_class = models.CharField(max_length=200, blank=True, null=True)
    current_school = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
      verbose_name = 'Student'
      verbose_name_plural = 'Students'
      ordering = ['-user__date_joined']
      indexes = [
        models.Index(fields=['student_id']),
        models.Index(fields=['linking_code']),
      ]

    def __str__(self):
        return f"Student: {self.user.email}"

    def save(self, *args, **kwargs):
        if not self.linking_code:
            # Ensure unique linking code
            while True:
                code = generate_linking_code()
                if not Student.objects.filter(linking_code=code).exists():
                    self.linking_code = code
                    break
        super().save(*args, **kwargs)
