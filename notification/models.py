from django.db import models
from users.models import User


class Notification(models.Model):
    """In-app notifications"""
    
    NOTIFICATION_TYPES = [
        ('enrollment', 'Course Enrollment'),
        ('payment', 'Payment'),
        ('course_update', 'Course Update'),
        ('assignment', 'Assignment'),
        ('quiz', 'Quiz'),
        ('certificate', 'Certificate'),
        ('reminder', 'Reminder'),
        ('message', 'Message'),
        ('system', 'System'),
    ]
    
    RECIPIENT_TYPES = [
        ('student', 'Student'),
        ('parent', 'Parent'),
        ('admin', 'Admin'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    recipient_type = models.CharField(max_length=20, choices=RECIPIENT_TYPES, default='student', db_index=True)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, db_index=True)
    title = models.CharField(max_length=200)
    message = models.TextField()
    action_url = models.CharField(max_length=500, blank=True)
    related_object_id = models.IntegerField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, blank=True)
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.title}"
    
    def mark_as_read(self):
        from django.utils import timezone
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])


class NotificationPreference(models.Model):
    """User notification preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    email_enrollment = models.BooleanField(default=True)
    email_payment = models.BooleanField(default=True)
    email_course_updates = models.BooleanField(default=True)
    email_reminders = models.BooleanField(default=True)
    email_marketing = models.BooleanField(default=False)
    push_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'
    
    def __str__(self):
        return f"{self.user.email} - Preferences"

        