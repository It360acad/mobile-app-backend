from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


class CourseEnrollment(models.Model):
    """Track student enrollments in courses"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
        ('suspended', 'Suspended'),
    ]
    
    # Student who is enrolled
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='enrollments',
        help_text='Student enrolled in the course'
    )
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='enrollments')
    
    # Enrollment tracking
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(auto_now=True)
    
    # Progress tracking
    progress_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        db_index=True
    )
    
    # Performance
    total_watch_time_minutes = models.IntegerField(default=0)
    quiz_average_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Metadata
    enrollment_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Course Enrollment'
        verbose_name_plural = 'Course Enrollments'
        unique_together = [['user', 'course']]
        ordering = ['-enrolled_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['course', 'status']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.course.title}"
    
    def clean(self):
        """Validate enrollment"""
        # Check if user is a student
        if not hasattr(self.user, 'student_profile'):
            raise ValidationError("Only students can enroll in courses.")
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Update course enrollment count (only count active enrollments)
        self.course.enrollment_count = self.course.enrollments.filter(
            status='active'
        ).count()
        self.course.save(update_fields=['enrollment_count'])
    
    @property
    def is_active(self):
        """Check if enrollment is active"""
        return self.status == 'active'
