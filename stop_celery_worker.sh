#!/bin/bash
# Script to stop Celery worker gracefully

if [ -f "celery_worker.pid" ]; then
    PID=$(cat celery_worker.pid)
    echo "🛑 Stopping Celery worker (PID: $PID)..."
    kill $PID
    rm celery_worker.pid
    echo "✅ Celery worker stopped"
else
    echo "❌ No Celery worker PID file found"
    echo "💡 Worker might not be running, or was started differently"
fi

