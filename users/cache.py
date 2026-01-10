"""
Redis caching utilities for users app
"""
from django.core.cache import cache
from django.conf import settings
import json
import logging

logger = logging.getLogger('users')

# Cache keys
CACHE_KEY_USER_LIST = 'users:list'
CACHE_KEY_USER_DETAIL = 'users:detail:{user_id}'
CACHE_KEY_USER_BY_EMAIL = 'users:email:{email}'
CACHE_TIMEOUT = 60 * 60  # 1 hour default


def get_cached_user_list():
    """
    Get cached list of users.
    
    Returns:
        list: List of serialized user data, or None if not cached
    """
    try:
        cached_data = cache.get(CACHE_KEY_USER_LIST)
        if cached_data:
            logger.debug(f"Cache hit for user list")
            return json.loads(cached_data) if isinstance(cached_data, str) else cached_data
        logger.debug(f"Cache miss for user list")
        return None
    except Exception as e:
        logger.error(f"Error getting cached user list: {str(e)}")
        return None


def set_cached_user_list(users_data, timeout=CACHE_TIMEOUT):
    """
    Cache the list of users.
    
    Args:
        users_data: List of serialized user data
        timeout: Cache timeout in seconds (default: 1 hour)
    """
    try:
        # Serialize to JSON string for storage
        if isinstance(users_data, list):
            serialized = json.dumps(users_data)
        else:
            serialized = json.dumps(users_data) if not isinstance(users_data, str) else users_data
        
        cache.set(CACHE_KEY_USER_LIST, serialized, timeout)
        logger.info(f"Cached user list ({len(users_data) if isinstance(users_data, list) else 'N/A'} users)")
    except Exception as e:
        logger.error(f"Error caching user list: {str(e)}")


def get_cached_user(user_id):
    """
    Get cached user by ID.
    
    Args:
        user_id: User ID
        
    Returns:
        dict: Serialized user data, or None if not cached
    """
    try:
        cached_data = cache.get(CACHE_KEY_USER_DETAIL.format(user_id=user_id))
        if cached_data:
            logger.debug(f"Cache hit for user {user_id}")
            return json.loads(cached_data) if isinstance(cached_data, str) else cached_data
        return None
    except Exception as e:
        logger.error(f"Error getting cached user {user_id}: {str(e)}")
        return None


def set_cached_user(user_id, user_data, timeout=CACHE_TIMEOUT):
    """
    Cache a single user.
    
    Args:
        user_id: User ID
        user_data: Serialized user data
        timeout: Cache timeout in seconds (default: 1 hour)
    """
    try:
        serialized = json.dumps(user_data) if not isinstance(user_data, str) else user_data
        cache.set(CACHE_KEY_USER_DETAIL.format(user_id=user_id), serialized, timeout)
        logger.debug(f"Cached user {user_id}")
    except Exception as e:
        logger.error(f"Error caching user {user_id}: {str(e)}")


def invalidate_user_list_cache():
    """
    Invalidate the user list cache.
    Call this when users are created, updated, or deleted.
    """
    try:
        cache.delete(CACHE_KEY_USER_LIST)
        logger.info("Invalidated user list cache")
    except Exception as e:
        logger.error(f"Error invalidating user list cache: {str(e)}")


def invalidate_user_cache(user_id):
    """
    Invalidate cache for a specific user.
    
    Args:
        user_id: User ID
    """
    try:
        cache.delete(CACHE_KEY_USER_DETAIL.format(user_id=user_id))
        cache.delete(CACHE_KEY_USER_BY_EMAIL.format(email='*'))  # Pattern matching not supported, but we invalidate list
        logger.debug(f"Invalidated cache for user {user_id}")
    except Exception as e:
        logger.error(f"Error invalidating user cache {user_id}: {str(e)}")


def invalidate_all_user_caches():
    """
    Invalidate all user-related caches.
    Useful for bulk operations or when you want to clear everything.
    """
    try:
        invalidate_user_list_cache()
        # Note: Individual user caches will expire naturally
        # For a complete clear, you'd need to track all user IDs or use cache.clear()
        logger.info("Invalidated all user caches")
    except Exception as e:
        logger.error(f"Error invalidating all user caches: {str(e)}")

