from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from courses.models.course import Course
from users.models import User

class CourseReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_reviews')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5"
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Course Review'
        verbose_name_plural = 'Course Reviews'
        unique_together = [['user', 'course']]
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user.email} for {self.course.title}: {self.rating}"

