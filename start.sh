#!/usr/bin/env bash
# Startup script for Render deployment
# Runs both Django/Gunicorn and Celery worker in the same service
# This script MUST be used as the Start Command in Render dashboard

set -o errexit

# Get PORT from environment (Render sets this automatically)
PORT="${PORT:-8000}"

# Create logs directory if it doesn't exist
mkdir -p logs

# Start Celery worker in background
echo "🚀 Starting Celery worker..."
celery -A it360acad_backend worker \
    --loglevel=info \
    --detach \
    --pidfile=/tmp/celery_worker.pid \
    --logfile=logs/celery_worker.log

# Wait a moment for Celery to start
sleep 2

# Start gunicorn (this will be the main process)
# The --bind parameter MUST come last to override any Render-added bind settings
echo "🚀 Starting Django/Gunicorn on port ${PORT}..."
exec gunicorn it360acad_backend.wsgi:application \
    --config gunicorn_config.py \
    --bind "0.0.0.0:${PORT}"

