#!/usr/bin/env bash
# Start only Celery worker (for local development or separate worker service)
# For Render: Use start.sh which runs both Django and Celery

set -o errexit

# Create logs directory if it doesn't exist
mkdir -p logs

echo "🚀 Starting Celery worker..."
celery -A it360acad_backend worker \
    --loglevel=info \
    --pidfile=celery_worker.pid \
    --logfile=logs/celery_worker.log

