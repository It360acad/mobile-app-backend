"""
Celery configuration for IT360 Academy Backend

This module sets up the Celery instance for background task processing.
Tasks are defined in individual apps (e.g., notification/tasks.py) for modularity.
"""
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'it360acad_backend.settings')

# Create Celery app instance
app = Celery('it360acad_backend')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Explicitly override broker_url from Django settings after config is loaded
# This ensures REDIS_URL takes precedence over any old CELERY_BROKER_URL values
try:
    import django
    django.setup()
    from django.conf import settings
    if hasattr(settings, 'CELERY_BROKER_URL'):
        app.conf.broker_url = settings.CELERY_BROKER_URL
    if hasattr(settings, 'CELERY_RESULT_BACKEND'):
        app.conf.result_backend = settings.CELERY_RESULT_BACKEND
except Exception:
    # Django might not be initialized yet, settings will be loaded when Django starts
    pass

# Load task modules from all registered Django apps.
# This allows tasks to be defined in any app's tasks.py file
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task to test Celery setup"""
    print(f'Request: {self.request!r}')

