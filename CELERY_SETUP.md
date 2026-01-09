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

2. Install and start Redis (message broker):
```bash
# On Ubuntu/Debian
sudo pacman -S redis-server
sudo systemctl start redis


3. Verify Redis is running:
```bash
redis-cli ping
# Should return: PONG
```

## Configuration

Celery configuration is in `it360acad_backend/settings.py`:

- `CELERY_BROKER_URL`: Redis connection URL (default: `redis://localhost:6379/0`)
- `CELERY_RESULT_BACKEND`: Redis connection URL for results (default: `redis://localhost:6379/0`)

You can override these via environment variables:
```bash
export CELERY_BROKER_URL=redis://localhost:6379/0
export CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## Running Celery Worker

Start the Celery worker in a separate terminal:

```bash
# From project root
celery -A it360acad_backend worker --loglevel=info

# For development with auto-reload
celery -A it360acad_backend worker --loglevel=info --reload

# With specific queue (if using task routing)
celery -A it360acad_backend worker --loglevel=info -Q notifications
```

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

1. Set environment variables for Redis:
   - Use Redis Cloud or similar service
   - Set `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND`

2. Run worker as a separate process/service:
   ```bash
   celery -A it360acad_backend worker --loglevel=info --concurrency=4
   ```

3. For Render, add a separate "Background Worker" service with:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `celery -A it360acad_backend worker --loglevel=info`

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
   - Verify Redis is running: `redis-cli ping`
   - Check connection URL format
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

