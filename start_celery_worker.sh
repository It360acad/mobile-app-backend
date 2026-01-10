#!/bin/bash
# Script to start Celery worker in the background

# Activate virtual environment
source .venv/bin/activate

# Start Celery worker
echo "🚀 Starting Celery worker..."
celery -A it360acad_backend worker --loglevel=info --detach --pidfile=celery_worker.pid --logfile=logs/celery_worker.log

echo "✅ Celery worker started in background"
echo "📋 PID file: celery_worker.pid"
echo "📝 Log file: logs/celery_worker.log"
echo ""
echo "To stop the worker:"
echo "  ./stop_celery_worker.sh"
echo ""
echo "To view logs:"
echo "  tail -f logs/celery_worker.log"

