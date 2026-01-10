"""
Signals for user model to handle cache invalidation
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from users.models import User
from users.cache import invalidate_user_list_cache, invalidate_user_cache
import logging

logger = logging.getLogger('users')


@receiver(post_save, sender=User)
def invalidate_user_cache_on_save(sender, instance, created, **kwargs):
    """
    Invalidate cache when a user is created or updated.
    """
    if created:
        # New user created - invalidate list cache
        invalidate_user_list_cache()
        logger.info(f"Invalidated user list cache after creating user {instance.id}")
    else:
        # User updated - invalidate both user and list cache
        invalidate_user_cache(instance.id)
        invalidate_user_list_cache()
        logger.info(f"Invalidated cache for updated user {instance.id}")


@receiver(post_delete, sender=User)
def invalidate_user_cache_on_delete(sender, instance, **kwargs):
    """
    Invalidate cache when a user is deleted.
    """
    invalidate_user_cache(instance.id)
    invalidate_user_list_cache()
    logger.info(f"Invalidated cache for deleted user {instance.id}")

