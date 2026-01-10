# Celery Setup Guide

This project uses Celery for asynchronous background task processing, primarily for email notifications and other notification-related tasks.

## Architecture

The Celery setup is modular:
- **Main Project** (`it360acad_backend/`): Contains the Celery instance configuration
- **Notification App** (`notification/`): Contains notification-specific tasks
- **Other Apps**: Can define their own tasks in `tasks.py` files

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. **Choose your Redis setup:**

   **Option A: Local Redis (Development)**
   ```bash
   # On Arch Linux/Manjaro
   sudo pacman -S redis
   sudo systemctl start redis
   
   # Verify Redis is running:
   redis-cli ping
   # Should return: PONG
   ```

   **Option B: Upstash Redis (Cloud - Recommended for Production)**
   - No local installation needed
   - See "Upstash Redis Setup" section below

## Configuration

Celery configuration is in `it360acad_backend/settings.py`:
- `CELERY_BROKER_URL`: Redis connection URL (default: `redis://localhost:6379/0`)
- `CELERY_RESULT_BACKEND`: Redis connection URL for results (default: same as `CELERY_BROKER_URL`)

You can override these via environment variables:
```bash
export CELERY_BROKER_URL=redis://localhost:6379/0
export CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## Upstash Redis Setup

Upstash Redis is a serverless Redis service perfect for production deployments.

### Step 1: Get Your Connection URL

1. Go to [Upstash Console](https://console.upstash.com/)
2. Create a new Redis database (or select an existing one)
3. Go to your database details page
4. Find the **"Redis URL"** or **"Connection String"** section
5. Copy the connection URL - it will look like one of these:
   - `redis://default:<password>@<host>:<port>`
   - `rediss://default:<password>@<host>:<port>` (with TLS/SSL)

### Step 2: Configure Environment Variables

Add the Upstash Redis connection URL to your `.env` file:

```bash
# .env or .env.local
CELERY_BROKER_URL=redis://default:YOUR_PASSWORD@YOUR_HOST:YOUR_PORT
CELERY_RESULT_BACKEND=redis://default:YOUR_PASSWORD@YOUR_HOST:YOUR_PORT
```

**Important Notes:**
- If your Upstash Redis uses TLS (most do), use `rediss://` instead of `redis://` (note the double 's')
- Replace `YOUR_PASSWORD`, `YOUR_HOST`, and `YOUR_PORT` with values from your Upstash dashboard
- The password is usually a long alphanumeric string provided by Upstash

### Step 3: Example Connection String

Your connection string from Upstash will look something like:
```
redis://default:AxZXc1234AbCdEf5678GhIjKlMnOpQrStUvWxYz@usw1-xyz-12345.upstash.io:12345
```

Or with TLS:
```
rediss://default:AxZXc1234AbCdEf5678GhIjKlMnOpQrStUvWxYz@usw1-xyz-12345.upstash.io:12345
```

### Step 4: Test Connection

After setting the environment variable, test the connection:

```bash
# Start Celery worker
celery -A it360acad_backend worker --loglevel=info

# If connection is successful, you'll see:
# [INFO/MainProcess] Connected to redis://...
```

### Troubleshooting Upstash Connection

1. **Connection timeout:**
   - Ensure your Upstash database is in the same region as your application
   - Check firewall settings if applicable

2. **TLS/SSL errors:**
   - Use `rediss://` (with double 's') if your Upstash database requires TLS
   - Some Upstash databases require TLS by default

3. **Authentication errors:**
   - Double-check the password in your connection string
   - Ensure there are no extra spaces or quotes in the environment variable

4. **Verify connection string format:**
   ```bash
   # Check your environment variable
   echo $CELERY_BROKER_URL
   ```

## Running Celery Worker

### Option 1: Background Process (Recommended)

Use the provided scripts:

```bash
# Start worker in background
./start_celery_worker.sh

# Stop worker
./stop_celery_worker.sh

# View logs
tail -f logs/celery_worker.log
```

### Option 2: Manual (Foreground)

Start the Celery worker in a separate terminal:

```bash
# From project root
celery -A it360acad_backend worker --loglevel=info

# For development with auto-reload
celery -A it360acad_backend worker --loglevel=info --reload

# With specific queue (if using task routing)
celery -A it360acad_backend worker --loglevel=info -Q notifications
```

**Note:** The worker will continuously poll Redis for tasks. This is normal behavior and will show up as commands in your Upstash dashboard. The worker needs to run continuously to process background tasks.

## Testing Celery Setup

### Quick Test (Recommended)

Use the built-in Django management command to test everything:

1. **Start Celery worker** (in one terminal):
   ```bash
   celery -A it360acad_backend worker --loglevel=info
   ```

2. **Run the test command** (in another terminal):
   ```bash
   python manage.py test_celery
   ```

   This will:
   - ✅ Check if Celery app is configured
   - ✅ Test Redis/Upstash connection
   - ✅ Queue and execute a test task
   - ✅ Show you the results

3. **Test with sync execution** (wait for result):
   ```bash
   python manage.py test_celery --sync
   ```

### Manual Testing

You can also test manually using Django shell:

```bash
python manage.py shell
```

Then in the shell:
```python
from notification.tasks import test_celery_connection

# Async execution (fire and forget)
result = test_celery_connection.delay("Hello from test!")
print(f"Task ID: {result.id}")

# Wait a moment, then check result
import time
time.sleep(2)
if result.ready():
    print(f"Result: {result.result}")
```

### What to Look For

**✅ Success indicators:**
- Worker terminal shows: `[INFO/MainProcess] Task notification.tasks.test_celery_connection[...] received`
- Worker terminal shows: `✅ Celery test task executed! Message: ...`
- Test command shows all green checkmarks

**❌ Common issues:**
- Connection errors → Check `CELERY_BROKER_URL` in `.env`
- Task not executing → Make sure worker is running
- Import errors → Make sure all dependencies are installed

## Running Celery Beat (for periodic tasks)

If you need scheduled/periodic tasks:

```bash
celery -A it360acad_backend beat --loglevel=info
```

## Available Tasks

### Notification Tasks (`notification.tasks`)

1. **`send_notification_email(notification_id)`**
   - Sends email for a specific notification
   - Respects user notification preferences
   - Retries on failure (max 3 times)

2. **`send_bulk_notification_emails(notification_ids)`**
   - Sends emails for multiple notifications
   - Returns summary of results

3. **`send_custom_email(subject, message, recipient_email, from_email=None)`**
   - Sends a custom email notification

4. **`send_otp_email(recipient_email, otp_code, purpose='verification')**
   - Sends OTP codes via email
   - Supports 'verification' and 'password_reset' purposes

5. **`cleanup_old_notifications(days_old=90)`**
   - Cleans up old read notifications
   - Default: deletes notifications older than 90 days

## Usage Examples

### In Views/Code

```python
from notification.tasks import send_notification_email, send_otp_email

# Send notification email asynchronously
send_notification_email.delay(notification.id)

# Send OTP email
send_otp_email.delay(
    recipient_email='user@example.com',
    otp_code='123456',
    purpose='verification'
)

# Send custom email
from notification.tasks import send_custom_email
send_custom_email.delay(
    subject='Welcome!',
    message='Welcome to IT360 Academy',
    recipient_email='user@example.com'
)
```

### In Signals

Signals automatically queue email notifications when notifications are created (see `notification/signals.py`).

## Monitoring

### Flower (Optional - Web-based monitoring tool)

```bash
pip install flower
celery -A it360acad_backend flower
# Access at http://localhost:5555
```

### Check Worker Status

```bash
celery -A it360acad_backend inspect active
celery -A it360acad_backend inspect stats
```

## Production Deployment

For production (e.g., Render, Heroku):

1. **Set Upstash Redis connection:**
   - Create an Upstash Redis database
   - Add `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` environment variables in your hosting platform
   - Use the connection string from Upstash dashboard

2. **Run worker as a separate process/service:**
   ```bash
   celery -A it360acad_backend worker --loglevel=info --concurrency=4
   ```

3. **For Render, add a separate "Background Worker" service:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `celery -A it360acad_backend worker --loglevel=info`
   - Environment Variables: Add `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` with your Upstash connection string

## Troubleshooting

1. **Worker not picking up tasks:**
   - Ensure Redis is running
   - Check `CELERY_BROKER_URL` is correct
   - Verify worker is running: `celery -A it360acad_backend inspect active`

2. **Tasks failing:**
   - Check worker logs
   - Verify email configuration in settings
   - Check notification preferences

3. **Redis connection errors:**
   - **Local Redis:** Verify Redis is running: `redis-cli ping`
   - **Upstash Redis:** Check connection URL format and ensure TLS is used if required (`rediss://`)
   - Verify environment variables are set correctly
   - Check firewall/network settings if using cloud Redis
   - Ensure Redis is accessible from your environment

## Adding New Tasks

To add tasks in other apps:

1. Create `tasks.py` in your app:
```python
from celery import shared_task

@shared_task
def my_task(param1, param2):
    # Your task logic
    pass
```

2. Celery will automatically discover tasks from all installed apps.

3. Use the task:
```python
from myapp.tasks import my_task
my_task.delay(param1, param2)
```

