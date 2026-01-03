from notification.models import Notification, NotificationPreference
from rest_framework import serializers
from users.serializers import UserSerializer


class NotificationSerializer(serializers.ModelSerializer):
  """Serializer for the Notification model"""
  user = UserSerializer(read_only=True)
  recipient_type = serializers.ChoiceField(choices=Notification.RECIPIENT_TYPES, read_only=True)
  notification_type = serializers.ChoiceField(choices=Notification.NOTIFICATION_TYPES, read_only=True)
  class Meta:
    model = Notification
    fields = ['id', 'user', 'recipient_type', 'notification_type', 'title', 'message', 'action_url', 'related_object_id', 'related_object_type', 'is_read', 'read_at', 'email_sent', 'email_sent_at', 'created_at']

  def get_time_ago(self, obj):
    from django.utils import timezone
    delta = timezone.now() - obj.created_at

    if delta.days > 0:
      return f"{delta.days} days ago"
    elif delta.hours > 0:
      return f"{delta.hours} hours ago"
    elif delta.minutes > 0:
      return f"{delta.minutes} minutes ago"
    else:
      return f"{delta.seconds} seconds ago"
    

class NotificationPreferenceSerializer(serializers.ModelSerializer):
  """Serializer for the NotificationPreference model"""
  class Meta:
    model = NotificationPreference
    fields = ['id', 'user', 'email_enrollment', 'email_payment', 'email_course_updates', 'email_reminders', 'email_marketing', 'push_enabled', 'created_at', 'updated_at']

    