# Celery Setup on Render with Upstash Redis

This guide shows you how to configure Celery with Upstash Redis on Render.

## Overview

On Render, you need **two services**:
1. **Web Service** - Your Django application (already set up)
2. **Background Worker** - Celery worker to process tasks (new service)

## Step 1: Get Your Upstash Redis Connection URL

1. Go to [Upstash Console](https://console.upstash.com/)
2. Select your Redis database
3. Go to the **Details** or **Connection** tab
4. Find the **Redis URL** under **TCP** section (NOT REST API)
5. Copy the connection string - it should look like:
   ```
   rediss://default:YOUR_PASSWORD@apparent-labrador-33734.upstash.io:6379
   ```

**Important:** 
- Use the **Redis URL** (TCP), not the REST API URL
- Make sure it starts with `rediss://` (with TLS) or `redis://` (without TLS)
- Upstash typically requires TLS, so use `rediss://`

## Step 2: Configure Environment Variables

### For Your Web Service (Django App)

In Render dashboard → Your Web Service → **Environment** tab, add:

```bash
# Upstash Redis for Celery
REDIS_URL=rediss://default:YOUR_PASSWORD@apparent-labrador-33734.upstash.io:6379
CELERY_BROKER_URL=rediss://default:YOUR_PASSWORD@apparent-labrador-33734.upstash.io:6379
CELERY_RESULT_BACKEND=rediss://default:YOUR_PASSWORD@apparent-labrador-33734.upstash.io:6379
```

**Replace `YOUR_PASSWORD`** with the actual password from Upstash.

### For Your Background Worker Service

You'll add the same variables in Step 3.

## Step 3: Create Background Worker Service

1. In Render dashboard, click **New +** → **Background Worker**

2. Configure the service:
   - **Name**: `it360acad-backend-worker` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `celery -A it360acad_backend worker --loglevel=info`
   - **Plan**: Choose your plan (Free tier available, but note: free services spin down after inactivity)

3. **Connect to the same repository** as your web service

4. **Environment Variables** - Add the same Redis variables:
   ```bash
   # Django Settings
   SECRET_KEY=your-secret-key-here (same as web service)
   DEBUG=False
   DB_URL=postgresql://... (same as web service)
   ALLOWED_HOSTS=your-service-name.onrender.com
   
   # Upstash Redis for Celery
   REDIS_URL=rediss://default:YOUR_PASSWORD@apparent-labrador-33734.upstash.io:6379
   CELERY_BROKER_URL=rediss://default:YOUR_PASSWORD@apparent-labrador-33734.upstash.io:6379
   CELERY_RESULT_BACKEND=rediss://default:YOUR_PASSWORD@apparent-labrador-33734.upstash.io:6379
   
   # Other environment variables (same as web service)
   DJANGO_SETTINGS_MODULE=it360acad_backend.settings
   ```

5. Click **Create Background Worker**

## Step 4: Verify Configuration

### Check Web Service Logs

After deployment, check your web service logs to ensure:
- No Celery connection errors
- Django starts successfully

### Check Worker Service Logs

Check your background worker logs. You should see:
```
[INFO] Connected to rediss://default:**@apparent-labrador-33734.upstash.io:6379//
[INFO] celery@hostname ready.
```

### Test Task Execution

1. Open **Shell** in your web service on Render
2. Run:
   ```bash
   python manage.py test_celery
   ```
3. Check worker logs to see the task being processed

## Step 5: Production Considerations

### Worker Concurrency

For production, you may want to adjust worker concurrency:

**Start Command** (in Background Worker settings):
```bash
celery -A it360acad_backend worker --loglevel=info --concurrency=4
```

### Auto-scaling (Paid Plans)

On Render paid plans, you can:
- Set minimum instances for the worker
- Configure auto-scaling based on queue length

### Monitoring

Monitor your services:
- **Web Service**: Check for task queuing errors
- **Worker Service**: Check for task execution errors
- **Upstash Dashboard**: Monitor Redis commands and usage

## Environment Variables Summary

### Required for Both Services:

| Variable | Description | Example |
|----------|-------------|---------|
| `REDIS_URL` | Upstash Redis connection URL | `rediss://default:pass@host:6379` |
| `CELERY_BROKER_URL` | Same as REDIS_URL | `rediss://default:pass@host:6379` |
| `CELERY_RESULT_BACKEND` | Same as REDIS_URL | `rediss://default:pass@host:6379` |
| `SECRET_KEY` | Django secret key | (same for both services) |
| `DB_URL` | Database connection | (same for both services) |
| `DEBUG` | Debug mode | `False` |

### Web Service Only:

| Variable | Description |
|----------|-------------|
| `ALLOWED_HOSTS` | Allowed hostnames |
| `RENDER_EXTERNAL_HOSTNAME` | Auto-set by Render |

## Troubleshooting

### Worker Not Starting

1. **Check Build Logs**: Ensure all dependencies installed
2. **Check Start Command**: Verify the command is correct
3. **Check Environment Variables**: Ensure `REDIS_URL` is set correctly

### Connection Errors

1. **SSL/TLS Issues**: 
   - Ensure using `rediss://` (with double 's') for TLS
   - Check that SSL configuration is in `settings.py` (already configured)

2. **Authentication Errors**:
   - Verify password in connection URL is correct
   - Check for extra spaces or quotes

3. **Network Issues**:
   - Ensure Upstash database is accessible from Render
   - Check firewall settings if applicable

### Tasks Not Executing

1. **Worker Not Running**: 
   - Check worker service is running (not spun down)
   - On free tier, worker spins down after 15 min inactivity

2. **Queue Mismatch**:
   - If using task routing, ensure worker listens to correct queue:
   ```bash
   celery -A it360acad_backend worker --loglevel=info -Q notifications
   ```

3. **Check Logs**:
   - Web service logs: Task queuing errors
   - Worker service logs: Task execution errors

### Free Tier Limitations

On Render free tier:
- Services spin down after 15 minutes of inactivity
- Worker will need to "wake up" when first task arrives
- Consider upgrading for production use

## Quick Reference

### Start Commands

**Web Service:**
```bash
./start.sh
```

**Background Worker:**
```bash
celery -A it360acad_backend worker --loglevel=info
```

### Environment Variables Template

```bash
# Copy these to both services in Render dashboard
REDIS_URL=rediss://default:YOUR_PASSWORD@YOUR_HOST:6379
CELERY_BROKER_URL=rediss://default:YOUR_PASSWORD@YOUR_HOST:6379
CELERY_RESULT_BACKEND=rediss://default:YOUR_PASSWORD@YOUR_HOST:6379
```

## Next Steps

1. ✅ Configure environment variables in both services
2. ✅ Deploy both services
3. ✅ Test task execution
4. ✅ Monitor logs for any issues
5. ✅ Set up monitoring/alerts (optional)

Your Celery setup is now ready for production on Render! 🚀

