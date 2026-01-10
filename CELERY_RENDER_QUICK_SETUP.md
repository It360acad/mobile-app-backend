# Quick Setup: Celery with Upstash Redis on Render

## ✅ Single Service Setup (No Separate Worker Needed!)

Your Django app and Celery worker run in the **same service** on Render.

## Setup Steps

### 1. Add Environment Variables in Render

In Render dashboard → Your Web Service → **Environment** tab, add:

```bash
REDIS_URL=rediss://default:YOUR_PASSWORD@apparent-labrador-33734.upstash.io:6379
CELERY_BROKER_URL=rediss://default:YOUR_PASSWORD@apparent-labrador-33734.upstash.io:6379
CELERY_RESULT_BACKEND=rediss://default:YOUR_PASSWORD@apparent-labrador-33734.upstash.io:6379
```

**Replace `YOUR_PASSWORD`** with your actual Upstash Redis password.

### 2. Verify Start Command

In Render dashboard → Your Web Service → **Settings**:
- **Start Command**: `./start.sh` ✅ (already configured)

The `start.sh` script automatically:
1. Starts Celery worker in background
2. Starts Django/Gunicorn

### 3. Deploy

That's it! When you deploy, both Django and Celery will start automatically.

## How It Works

```
Render Service
├── Celery Worker (background process)
│   └── Connects to Upstash Redis
└── Django/Gunicorn (main process)
    └── Queues tasks to Upstash Redis
```

## Local Development Commands

### Start Celery Worker (for local testing):
```bash
./start_celery_worker.sh
```

### Stop Celery Worker:
```bash
./stop_celery_worker.sh
```

### Start Only Celery (without Django):
```bash
./start_celery_only.sh
```

## Files

- `start.sh` - **Used by Render** - Starts both Django + Celery
- `start_celery_worker.sh` - Local dev: Start Celery in background
- `start_celery_only.sh` - Local dev: Start only Celery (foreground)
- `stop_celery_worker.sh` - Local dev: Stop Celery worker
- `build.sh` - Build script (installs deps, runs migrations)

## Testing

After deployment, test in Render Shell:
```bash
python manage.py test_celery
```

Check logs to see:
- ✅ Celery worker starting
- ✅ Task being processed
- ✅ Task completing successfully

## Troubleshooting

### Celery Not Starting
- Check `REDIS_URL` is set correctly
- Verify Upstash Redis is accessible
- Check service logs for errors

### Tasks Not Processing
- Verify Celery worker is running (check logs)
- Check Redis connection in logs
- Verify tasks are being queued

## That's It! 🎉

No separate Background Worker service needed. Just update your `.env` variables in Render and deploy!

