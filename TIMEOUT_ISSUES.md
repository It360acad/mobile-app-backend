# Gunicorn Worker Timeout Issues - Root Cause Analysis

## ✅ RESOLVED

**Root Cause Confirmed:** Redis cache operations were hanging due to missing socket timeouts.

**Evidence:**
- After switching to LocMemCache, responses became fast
- Error log: "Error invalidating user list cache: Timeout connecting to server"
- Gunicorn workers timing out after 30 seconds

## Error Symptoms
```
[CRITICAL] WORKER TIMEOUT (pid:109684)
[ERROR] Worker (pid:109684) was sent SIGKILL! Perhaps out of memory?
Error invalidating user list cache: Timeout connecting to server
```

## Root Causes (FIXED)

### 1. **Redis Cache Operations** (Most Likely)
**Location:** `users/cache.py`, `it360acad_backend/settings.py`

**Problem:**
- `cache.get()` and `cache.set()` calls have no socket timeout
- Redis cache config missing `SOCKET_TIMEOUT` and `SOCKET_CONNECT_TIMEOUT`
- If Redis/Upstash is slow or unreachable, operations hang indefinitely

**Files:**
- `users/cache.py` lines 26, 52, 69, 90
- `it360acad_backend/settings.py` lines 393-396, 407-409

**✅ FIXED:** Added timeouts to Redis cache config in `settings.py`:
```python
'OPTIONS': {
    'CLIENT_CLASS': 'django_redis.client.DefaultClient',
    'SOCKET_CONNECT_TIMEOUT': 5,  # Connection timeout in seconds
    'SOCKET_TIMEOUT': 5,  # Socket timeout for operations (prevents hanging)
    'CONNECTION_POOL_KWARGS': {
        'retry_on_timeout': True,
        'max_connections': 50,
    },
}
```

**Note:** Cache operations in `users/cache.py` already have try/except blocks that handle timeouts gracefully, so errors are logged but don't crash the request.

### 2. **Paystack API Calls** (High Likelihood)
**Location:** `payments/services.py`

**Problem:**
- `requests.post()` and `requests.get()` have no `timeout` parameter
- Default requests timeout is `None` (hangs forever)
- If Paystack API is slow/unreachable, requests block indefinitely

**Files:**
- `payments/services.py` lines 43, 61, 83

**✅ FIXED:** Added `timeout=10` to all Paystack API calls in `payments/services.py`:
```python
REQUEST_TIMEOUT = 10  # Class constant
response = requests.post(url, headers=self.header, json=data, timeout=self.REQUEST_TIMEOUT)
response = requests.get(url, headers=self.header, timeout=self.REQUEST_TIMEOUT)
```

### 3. **Database Queries** (Possible)
**Location:** `it360acad_backend/settings.py`

**Problem:**
- Only `connect_timeout: 10` is set
- No `socket_timeout` for query operations
- Slow queries can still block workers

**Fix:** Add socket timeout:
```python
db_config['OPTIONS'] = {
    **existing_options,
    'connect_timeout': 10,
    'options': '-c statement_timeout=30000',  # 30 seconds query timeout
}
```

## ✅ Fixes Applied

1. **✅ Redis Cache:** Added `SOCKET_CONNECT_TIMEOUT: 5` and `SOCKET_TIMEOUT: 5` to prevent hanging
2. **✅ Paystack API:** Added `timeout=10` to all `requests.post()` and `requests.get()` calls
3. **⚠️ Gunicorn Timeout:** Still at 30s - consider increasing to 60-120s if needed (in `gunicorn_config.py`)

## How It Works Now

- **Redis timeouts:** If Redis is slow/unreachable, operations fail after 5 seconds (not 30+)
- **Cache error handling:** `users/cache.py` already has try/except blocks, so timeouts are logged but don't crash requests
- **Paystack timeouts:** API calls fail after 10 seconds instead of hanging indefinitely
- **Graceful degradation:** If cache fails, requests fall back to database (slower but works)

## How to Verify

Check your logs for:
- Redis connection errors
- Paystack API timeouts
- Slow database queries
- Which endpoints are timing out (check `request_id` in logs)

