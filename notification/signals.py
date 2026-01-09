

from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import User
from notification.models import Notification, NotificationPreference
import logging
from courses.models.enrollment import CourseEnrollment


logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_notification_preferences(sender, instance, created, **kwargs):
  """ Auto-create notification preferences for new users"""
  if created:
    NotificationPreference.objects.create(user=instance)
    logger.info(f"Notification preferences created for user: {instance.email}")


# Send notification to user when they are enrolled in a course
@receiver(post_save, sender=CourseEnrollment)
def send_enrollment_notification(sender, instance: CourseEnrollment, created, **kwargs):
  """ Send notification to user when they are enrolled in a course"""
  if created:
    notification = Notification.objects.create(
      user=instance.user,
      title=f"You are enrolled in {instance.course.title} at {instance.enrolled_at}",
      message=f"You are enrolled in {instance.course.title} at {instance.enrolled_at}",
      notification_type='enrollment',
      recipient_type='student',
      is_read=False
    )
    logger.info(f"Enrollment notification created for user: {instance.user.email}")
    
    # Send email notification asynchronously using Celery
    try:
      from .tasks import send_notification_email
      send_notification_email.delay(notification.id)
      logger.info(f"Email notification queued for notification {notification.id}")
    except Exception as e:
      logger.error(f"Failed to queue email notification: {str(e)}")
    
    return notification


