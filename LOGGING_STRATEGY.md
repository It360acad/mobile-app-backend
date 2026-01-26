# Logging Strategy Guide for IT360 Academy Backend

This guide provides optimized logging configurations for different deployment environments, with special focus on memory-constrained platforms like Render.

## 🔍 Current Memory Issue Analysis

### The Problem
Your Render deployment is running out of memory. This can be caused by:

1. **Excessive Request Logging**: Every API call creates log entries
2. **Large Log Files**: Multiple 15-20MB log files in memory
3. **Console + File Dual Logging**: Writing to both console and files
4. **Debug Level Logging**: Too much detail in production
5. **Log Buffer Accumulation**: Logs staying in memory too long

### Memory Usage by Logging Strategy

| Strategy | Estimated Memory | Use Case |
|----------|-----------------|----------|
| **No Logging** | ~5MB | Extreme memory constraints |
| **Console Only** | ~10-15MB | Render/Heroku production |
| **Minimal Files** | ~20-30MB | VPS with some disk space |
| **Full Logging** | ~50-100MB | Development/dedicated servers |

## 🎯 Recommended Solutions

### Option 1: Console-Only Logging (Recommended for Render)

**Best for**: Render, Heroku, memory-constrained environments

```python
# In settings.py
from .logger.ProductionLogger import LOGGING

# Environment variables to set:
DISABLE_FILE_LOGGING=True
LOG_FORMAT=json
DJANGO_LOG_LEVEL=WARNING
```

**Benefits**:
- ✅ Minimal memory usage (~10-15MB)
- ✅ Works with cloud log aggregators
- ✅ No disk space usage
- ✅ Render captures console output automatically

**Drawbacks**:
- ❌ No persistent logs on server
- ❌ Depends on platform log retention

### Option 2: Minimal File Logging

**Best for**: VPS, dedicated servers with disk space

```python
# Keep only critical errors in files
LOGGING['handlers'] = {
    'console': {...},
    'critical_only': {
        'level': 'ERROR',
        'maxBytes': 1024 * 1024 * 2,  # 2MB max
        'backupCount': 1,  # Only 1 backup
    }
}
```

### Option 3: Disable Request Logging Middleware

**Memory Savings**: ~30-50% reduction

Replace your current middleware:

```python
# In settings.py MIDDLEWARE
# REPLACE:
'it360acad_backend.middleware.RequestLoggingMiddleware',

# WITH ONE OF:
'it360acad_backend.middleware_optimized.OptimizedRequestLoggingMiddleware',  # Reduced logging
'it360acad_backend.middleware_optimized.MinimalRequestLoggingMiddleware',    # Errors only
'it360acad_backend.middleware_optimized.NoRequestLoggingMiddleware',         # Almost none
```

## 🚀 Quick Implementation Guide

### Step 1: Choose Your Strategy

For **Render production** (recommended):
```bash
# Set in Render environment variables
DISABLE_FILE_LOGGING=True
LOG_FORMAT=json
DJANGO_LOG_LEVEL=WARNING
DEBUG=False
```

### Step 2: Update Settings

```python
# In it360acad_backend/settings.py

# REPLACE:
from .logger.Logger import LOGGING

# WITH:
from .logger.ProductionLogger import LOGGING
```

### Step 3: Update Middleware (Optional)

```python
# In MIDDLEWARE list
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    
    # CHOOSE ONE:
    'it360acad_backend.middleware_optimized.OptimizedRequestLoggingMiddleware',  # Recommended
    # 'it360acad_backend.middleware_optimized.MinimalRequestLoggingMiddleware',  # Minimal
    # 'it360acad_backend.middleware_optimized.NoRequestLoggingMiddleware',      # Emergency
    
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

### Step 4: Clean Up Existing Logs

```bash
# Remove large log files to free disk space
rm -f logs/*.log
rm -f logs/*.log.*

# Or keep only critical ones
find logs/ -name "*.log" -size +5M -delete
```

## 📊 Logging Level Strategy

### Production Levels (Memory Optimized)
```python
PRODUCTION_LOG_LEVELS = {
    'django': 'WARNING',           # Reduce Django framework noise
    'django.request': 'ERROR',     # Only log request errors
    'authentication': 'INFO',      # Keep auth logs for security
    'users': 'WARNING',           # Reduce user operation logs
    'courses': 'WARNING',         # Reduce course logs
    'payments': 'INFO',           # Keep payment logs for auditing
    'notification': 'WARNING',    # Reduce notification logs
    'api': 'WARNING',             # Only log API warnings/errors
    'celery': 'ERROR',            # Only log Celery errors
}
```

### Development Levels (Full Logging)
```python
DEVELOPMENT_LOG_LEVELS = {
    'django': 'INFO',
    'django.request': 'INFO',
    'authentication': 'DEBUG',
    'users': 'INFO',
    'courses': 'INFO',
    'payments': 'DEBUG',
    'notification': 'INFO',
    'api': 'INFO',
    'celery': 'INFO',
}
```

## 🔧 Advanced Optimizations

### 1. Async Logging (Experimental)
```python
# For high-traffic applications
LOGGING['handlers']['console_async'] = {
    'class': 'logging.handlers.QueueHandler',
    'queue': queue.Queue(),
    'target': {
        'class': 'logging.StreamHandler',
        'formatter': 'production',
    }
}
```

### 2. Log Sampling
```python
# Only log every Nth request to reduce volume
import random

class SamplingLoggingMiddleware:
    def __init__(self, sample_rate=0.1):  # Log 10% of requests
        self.sample_rate = sample_rate
    
    def should_log(self):
        return random.random() < self.sample_rate
```

### 3. External Log Services

For production, consider:
- **Render**: Built-in log streaming (free tier: 7 days retention)
- **Papertrail**: Centralized logging service
- **LogDNA/Mezmo**: Advanced log analysis
- **Datadog Logs**: Full observability platform

```python
# Example: Papertrail configuration
LOGGING['handlers']['papertrail'] = {
    'class': 'logging.handlers.SysLogHandler',
    'address': ('logs.papertrailapp.com', YOUR_PORT),
    'formatter': 'json',
}
```

## 🚨 Emergency Memory Fix

If your Render deployment is crashing due to memory:

### Immediate Actions (5 minutes)

1. **Disable all file logging**:
```bash
# Set in Render environment
DISABLE_FILE_LOGGING=True
```

2. **Disable request logging**:
```python
# In settings.py MIDDLEWARE, comment out:
# 'it360acad_backend.middleware.RequestLoggingMiddleware',
```

3. **Set minimal log levels**:
```bash
# Render environment variables
DJANGO_LOG_LEVEL=ERROR
LOG_FORMAT=json
```

### Verification
```bash
# Check memory usage after restart
python manage.py shell -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.1f} MB')
"
```

## 📈 Monitoring and Alerts

### Memory Usage Tracking
```python
# Add to your health check endpoint
import psutil
import os

def get_memory_usage():
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    return {
        'memory_mb': round(memory_mb, 1),
        'memory_percent': round(process.memory_percent(), 1),
        'status': 'warning' if memory_mb > 400 else 'ok'
    }
```

### Log Volume Monitoring
```python
# Monitor log production rate
def log_stats():
    return {
        'log_files': len(os.listdir('logs')),
        'total_log_size_mb': sum(
            os.path.getsize(f'logs/{f}') 
            for f in os.listdir('logs')
        ) / 1024 / 1024
    }
```

## 🎯 Platform-Specific Recommendations

### Render.com
```bash
# Environment Variables
DISABLE_FILE_LOGGING=True
LOG_FORMAT=json
DJANGO_LOG_LEVEL=WARNING
USE_MINIMAL_MIDDLEWARE=True
```

### Heroku
```bash
# Same as Render + 
HEROKU_APP_NAME=your-app-name
# Heroku captures logs automatically
```

### Railway.app
```bash
# Railway has better memory limits
DISABLE_FILE_LOGGING=False
LOG_FORMAT=json
DJANGO_LOG_LEVEL=INFO
```

### VPS/Dedicated Server
```bash
# Full logging available
DISABLE_FILE_LOGGING=False
LOG_FORMAT=detailed
DJANGO_LOG_LEVEL=INFO
ENABLE_FILE_ROTATION=True
```

## ✅ Testing Your Configuration

### Memory Test Script
```python
# test_memory_usage.py
import psutil
import os
import time
import requests

def test_memory_under_load():
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024
    
    # Make 100 API calls
    for i in range(100):
        try:
            requests.get('http://localhost:8000/api/auth/check-email-exists/?email=test@test.com')
        except:
            pass
        
        if i % 10 == 0:
            current_memory = process.memory_info().rss / 1024 / 1024
            print(f"Request {i}: {current_memory:.1f} MB ({current_memory - initial_memory:+.1f})")
    
    final_memory = process.memory_info().rss / 1024 / 1024
    print(f"Memory increase: {final_memory - initial_memory:.1f} MB")

if __name__ == '__main__':
    test_memory_under_load()
```

### Log Volume Test
```bash
# Check log production over time
python manage.py shell -c "
import logging
logger = logging.getLogger('api')
for i in range(1000):
    logger.info(f'Test log message {i}')
"

# Check file sizes
ls -lh logs/
```

## 🔄 Migration Checklist

- [ ] Backup current logs if needed
- [ ] Set environment variables
- [ ] Update settings.py imports
- [ ] Update middleware (optional)
- [ ] Test memory usage
- [ ] Monitor for 24 hours
- [ ] Verify critical logs still captured
- [ ] Update deployment documentation

## 🆘 Troubleshooting

### High Memory Usage Persists
1. Check for memory leaks in application code
2. Monitor database connection pooling
3. Review Celery worker memory usage
4. Consider using uWSGI instead of Gunicorn

### Missing Critical Logs
1. Ensure ERROR level logs still captured
2. Add specific loggers for critical operations
3. Consider external logging service
4. Set up log alerts for critical events

### Performance Impact
1. Measure request response times before/after
2. Monitor CPU usage changes
3. Test under realistic load
4. Adjust log levels if needed

Remember: **Logging should never break your application**. It's better to have minimal logging and a working app than detailed logs and crashes.