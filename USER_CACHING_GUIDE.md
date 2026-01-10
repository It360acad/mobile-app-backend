# User List Caching with Redis

This guide explains how user list caching works in the application.

## Overview

User lists and individual user data are cached in Redis (Upstash) to improve performance and reduce database queries.

## How It Works

### 1. Cache Storage
- **Location**: Redis/Upstash (same connection as Celery, but database 1)
- **Key Prefix**: `it360acad`
- **Default Timeout**: 1 hour (3600 seconds)

### 2. Cached Data
- **User List**: All users (`users:list`)
- **Individual Users**: Single user by ID (`users:detail:{user_id}`)

### 3. Cache Flow

#### List Users Endpoint (`GET /api/users/`)
1. Check Redis cache for user list
2. If found (cache hit): Return cached data immediately
3. If not found (cache miss): Query database, cache the result, return data

#### Retrieve User Endpoint (`GET /api/users/{id}/`)
1. Check Redis cache for specific user
2. If found: Return cached data
3. If not found: Query database, cache the result, return data

### 4. Cache Invalidation

Cache is automatically invalidated when:
- ✅ User is created (invalidates list cache)
- ✅ User is updated (invalidates user cache + list cache)
- ✅ User is deleted (invalidates user cache + list cache)
- ✅ User is updated via API (PUT/PATCH endpoints)

## Configuration

### Environment Variables

The cache uses the same Redis connection as Celery:
```bash
REDIS_URL=rediss://default:PASSWORD@host:6379
```

Cache uses database 1, Celery uses database 0 (same Redis instance, different databases).

### Settings

Cache configuration is in `it360acad_backend/settings.py`:
- Uses `django-redis` backend
- SSL/TLS support for Upstash
- 1 hour default timeout

## Usage

### Manual Cache Operations

You can manually manage cache using the cache utilities:

```python
from users.cache import (
    get_cached_user_list,
    set_cached_user_list,
    invalidate_user_list_cache,
    get_cached_user,
    set_cached_user,
    invalidate_user_cache,
    invalidate_all_user_caches
)

# Get cached user list
cached_list = get_cached_user_list()

# Invalidate cache manually
invalidate_user_list_cache()
invalidate_user_cache(user_id=123)
```

### In Views

The views automatically handle caching:
- `UserListView` - Caches and retrieves user list
- `UserRetrieveView` - Caches and retrieves individual users
- `UserUpdateView` - Invalidates cache on update

## Cache Keys

- `it360acad:users:list` - User list cache
- `it360acad:users:detail:{user_id}` - Individual user cache

## Performance Benefits

### Before Caching
- Every request queries the database
- Slower response times
- Higher database load

### After Caching
- First request: Database query + cache write
- Subsequent requests: Cache read (much faster)
- Reduced database load
- Faster API responses

## Monitoring

### Check Cache Status

```python
from django.core.cache import cache

# Check if cache is working
cache.set('test', 'value', 60)
value = cache.get('test')
print(f"Cache test: {value}")  # Should print 'value'
```

### View Cache in Redis

If you have Redis CLI access:
```bash
redis-cli
> KEYS it360acad:users:*
> GET it360acad:users:list
```

## Troubleshooting

### Cache Not Working

1. **Check Redis Connection**:
   - Verify `REDIS_URL` is set correctly
   - Check Redis is accessible
   - Test connection: `python manage.py shell` → `from django.core.cache import cache; cache.set('test', 'ok')`

2. **Check django-redis Installation**:
   ```bash
   pip install django-redis==5.4.0
   ```

3. **Check Logs**:
   - Look for cache-related errors in application logs
   - Check for SSL/TLS connection issues

### Cache Not Invalidating

- Verify signals are registered (check `users/apps.py`)
- Check logs for invalidation messages
- Manually invalidate if needed: `invalidate_user_list_cache()`

### Performance Issues

- Adjust cache timeout in settings (currently 1 hour)
- Consider caching strategy for large user lists
- Monitor Redis memory usage

## Best Practices

1. ✅ **Automatic Invalidation**: Cache is automatically invalidated on create/update/delete
2. ✅ **Timeout**: Cache expires after 1 hour (prevents stale data)
3. ✅ **Error Handling**: Cache failures don't break the app (falls back to database)
4. ✅ **Logging**: Cache operations are logged for debugging

## Future Enhancements

Possible improvements:
- Cache user lists filtered by role
- Cache paginated results
- Cache user search results
- Implement cache warming strategies

