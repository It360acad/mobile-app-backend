# Upstash Redis Setup for Celery

## Finding Your Redis Connection URL

Upstash provides **two different connection methods**:

1. **REST API** (HTTP-based) - What you currently have
   - URL: `https://apparent-labrador-33734.upstash.io`
   - Token: `AYPGAAIncDI5NTBhZjhjNWEzODY0ZGUzYjFiZDc4YWMyNWJiMDIzMnAyMzM3MzQ`
   - Used for: HTTP-based Redis clients (like `upstash-redis` SDK)
   - ❌ **NOT compatible with Celery**

2. **Native Redis URL** (TCP-based) - What Celery needs
   - Format: `redis://default:<password>@<host>:<port>` or `rediss://default:<password>@<host>:<port>`
   - Used for: Native Redis protocol clients (like `redis-py`, Celery)
   - ✅ **Required for Celery**

## Steps to Get Your Redis URL

1. **Go to Upstash Console**: https://console.upstash.com/

2. **Select your Redis database** (the one named "apparent-labrador-33734" or similar)

3. **Look for "Redis URL" or "Connection String"** section
   - It's usually in the database details page
   - Look for tabs/sections like: "Details", "Connection", or "Connect"
   - It will be labeled as "Redis URL" or "Connection String" (NOT "REST API")

4. **Copy the connection string** - It will look like:
   ```
   redis://default:YOUR_PASSWORD@apparent-labrador-33734.upstash.io:PORT
   ```
   or with TLS:
   ```
   rediss://default:YOUR_PASSWORD@apparent-labrador-33734.upstash.io:PORT
   ```

5. **Add to your `.env.local` file**:
   ```bash
   CELERY_BROKER_URL=redis://default:YOUR_PASSWORD@apparent-labrador-33734.upstash.io:PORT
   CELERY_RESULT_BACKEND=redis://default:YOUR_PASSWORD@apparent-labrador-33734.upstash.io:PORT
   ```

## Alternative: If You Can't Find the Redis URL

If your Upstash database only shows REST API (some serverless plans), you have two options:

### Option 1: Use Upstash REST API SDK (Not for Celery)
This won't work with Celery, but you can use it for direct Redis operations:
```python
from upstash_redis import Redis
redis = Redis.from_env()
```

### Option 2: Create a New Upstash Database with Native Redis Support
1. Create a new Redis database in Upstash
2. Make sure to select a plan that supports native Redis connections
3. Look for "Redis URL" in the connection details

## Quick Test

After adding the Redis URL to `.env.local`, test it:

```bash
python manage.py test_celery
```

## Visual Guide

In the Upstash dashboard, you should see something like:

```
┌─────────────────────────────────────┐
│  Database: apparent-labrador-33734  │
├─────────────────────────────────────┤
│  REST API                            │
│  URL: https://...                    │  ← You have this
│  Token: AYPGAA...                    │  ← You have this
├─────────────────────────────────────┤
│  Redis URL                           │
│  redis://default:xxx@...:port       │  ← You need this!
└─────────────────────────────────────┘
```

The Redis URL section might be in a different tab or below the REST API section.

