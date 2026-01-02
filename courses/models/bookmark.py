from django.db import models
from courses.models.course import Course
from users.models import User

class CourseBookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_bookmarks')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Course Bookmark'
        verbose_name_plural = 'Course Bookmarks'
        unique_together = [['user', 'course']]
        ordering = ['-created_at']

    def __str__(self):
        return f"Bookmark: {self.user.email} - {self.course.title}"

