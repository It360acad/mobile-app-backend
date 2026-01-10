#!/bin/bash
# Script to stop Celery worker gracefully (for local development)
# For Render: The worker runs with the main service and stops when service stops

# Check for PID file in current directory
if [ -f "celery_worker.pid" ]; then
    PID=$(cat celery_worker.pid)
    echo "🛑 Stopping Celery worker (PID: $PID)..."
    kill $PID 2>/dev/null || true
    rm celery_worker.pid
    echo "✅ Celery worker stopped"
fi

# Also check for PID file in /tmp (used by Render)
if [ -f "/tmp/celery_worker.pid" ]; then
    PID=$(cat /tmp/celery_worker.pid)
    echo "🛑 Stopping Celery worker (PID: $PID from /tmp)..."
    kill $PID 2>/dev/null || true
    rm /tmp/celery_worker.pid
    echo "✅ Celery worker stopped"
fi

# Kill any remaining Celery processes
pkill -f "celery.*it360acad_backend.*worker" 2>/dev/null && echo "✅ Killed remaining Celery processes" || echo "✅ No Celery processes found"

