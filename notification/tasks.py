"""
Celery tasks for notification app

This module contains all background tasks related to notifications.
Tasks are modular and can be easily extended for different notification types.
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Notification, NotificationPreference
from users.models import User
import logging

logger = logging.getLogger('notification')


@shared_task(bind=True, max_retries=3)
def send_notification_email(self, notification_id):
    """
    Send email notification for a given notification ID.
    
    Args:
        notification_id: The ID of the Notification instance
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        notification = Notification.objects.get(id=notification_id)
        
        # Check if email was already sent
        if notification.email_sent:
            logger.info(f"Email already sent for notification {notification_id}")
            return True
        
        # Check user's email preferences
        try:
            preferences = notification.user.notification_preferences
            # Check if user has email enabled for this notification type
            if not getattr(preferences, f'email_{notification.notification_type}', True):
                logger.info(f"User {notification.user.email} has disabled email for {notification.notification_type}")
                notification.email_sent = True  # Mark as sent to avoid retrying
                notification.save(update_fields=['email_sent'])
                return False
        except NotificationPreference.DoesNotExist:
            # If preferences don't exist, default to sending
            pass
        
        # Send email
        send_mail(
            subject=notification.title,
            message=notification.message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notification.user.email],
            fail_silently=False,
        )
        
        # Update notification
        notification.email_sent = True
        notification.email_sent_at = timezone.now()
        notification.save(update_fields=['email_sent', 'email_sent_at'])
        
        logger.info(f"Email sent successfully for notification {notification_id} to {notification.user.email}")
        return True
        
    except Notification.DoesNotExist:
        logger.error(f"Notification {notification_id} not found")
        return False
    except Exception as exc:
        logger.error(f"Error sending email for notification {notification_id}: {str(exc)}")
        # Retry the task
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@shared_task
def send_bulk_notification_emails(notification_ids):
    """
    Send email notifications for multiple notifications.
    
    Args:
        notification_ids: List of notification IDs to send emails for
        
    Returns:
        dict: Summary of results
    """
    results = {'success': 0, 'failed': 0, 'skipped': 0}
    
    for notification_id in notification_ids:
        try:
            result = send_notification_email.delay(notification_id)
            if result:
                results['success'] += 1
            else:
                results['skipped'] += 1
        except Exception as e:
            logger.error(f"Failed to queue email for notification {notification_id}: {str(e)}")
            results['failed'] += 1
    
    logger.info(f"Bulk email task completed: {results}")
    return results


@shared_task
def send_custom_email(subject, message, recipient_email, from_email=None):
    """
    Send a custom email notification.
    
    Args:
        subject: Email subject
        message: Email message body
        recipient_email: Recipient email address
        from_email: Sender email (defaults to DEFAULT_FROM_EMAIL)
        
    Returns:
        bool: True if email was sent successfully
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email or settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        logger.info(f"Custom email sent successfully to {recipient_email}")
        return True
    except Exception as e:
        logger.error(f"Error sending custom email to {recipient_email}: {str(e)}")
        return False


@shared_task
def send_otp_email(recipient_email, otp_code, purpose='verification'):
    """
    Send OTP code via email (can replace synchronous email sending in authentication).
    
    Args:
        recipient_email: Recipient email address
        otp_code: OTP code to send
        purpose: Purpose of OTP (verification, password_reset, etc.)
        
    Returns:
        bool: True if email was sent successfully
    """
    try:
        subject_map = {
            'verification': 'OTP Verification - IT360 Academy',
            'password_reset': 'Password Reset OTP - IT360 Academy',
        }
        
        message_map = {
            'verification': f'Your IT360 Academy Registration OTP is: {otp_code}\n\nThis code will expire in 10 minutes.\n\nIf you did not request this code, please ignore this email.',
            'password_reset': f'Your IT360 Academy Password Reset OTP is: {otp_code}\n\nThis code will expire in 15 minutes.\n\nIf you did not request a password reset, please ignore this email.',
        }
        
        subject = subject_map.get(purpose, 'OTP Code - IT360 Academy')
        message = message_map.get(purpose, f'Your IT360 Academy OTP is: {otp_code}')
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        logger.info(f"OTP email sent successfully to {recipient_email} for {purpose}")
        return True
    except Exception as e:
        logger.error(f"Error sending OTP email to {recipient_email}: {str(e)}")
        return False


@shared_task
def cleanup_old_notifications(days_old=90):
    """
    Clean up old read notifications.
    
    Args:
        days_old: Delete notifications older than this many days (default: 90)
        
    Returns:
        int: Number of notifications deleted
    """
    try:
        from datetime import timedelta
        cutoff_date = timezone.now() - timedelta(days=days_old)
        
        deleted_count, _ = Notification.objects.filter(
            is_read=True,
            created_at__lt=cutoff_date
        ).delete()
        
        logger.info(f"Cleaned up {deleted_count} old notifications")
        return deleted_count
    except Exception as e:
        logger.error(f"Error cleaning up old notifications: {str(e)}")
        return 0
