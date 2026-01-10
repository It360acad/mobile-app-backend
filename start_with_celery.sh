#!/usr/bin/env bash
# Combined startup script for Django + Celery
# This runs both the web server and Celery worker in the same process
# NOTE: For production, it's better to use separate services

set -o errexit

# Get PORT from environment (Render sets this automatically)
PORT="${PORT:-8000}"

# Start Celery worker in background
echo "🚀 Starting Celery worker..."
celery -A it360acad_backend worker --loglevel=info --detach --pidfile=/tmp/celery_worker.pid --logfile=/tmp/celery_worker.log

# Wait a moment for Celery to start
sleep 2

# Start gunicorn (this will be the main process)
echo "🚀 Starting Django/Gunicorn..."
exec gunicorn it360acad_backend.wsgi:application \
    --config gunicorn_config.py \
    --bind "0.0.0.0:${PORT}"

