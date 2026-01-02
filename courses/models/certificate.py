from django.db import models
from courses.models.course import Course
from users.models import User

class Certificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates')
    
    certificate_id = models.CharField(max_length=100, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    certificate_url = models.URLField(blank=True)
    
    class Meta:
        verbose_name = 'Certificate'
        verbose_name_plural = 'Certificates'
        unique_together = [['user', 'course']]
        ordering = ['-issued_at']

    def __str__(self):
        return f"Certificate: {self.user.email} - {self.course.title}"

