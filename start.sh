#!/usr/bin/env bash
# Startup script for Render deployment
# Runs Django/Daphne (ASGI server) for both HTTP and WebSocket support, plus Celery worker
# This script MUST be used as the Start Command in Render dashboard
# Note: Daphne handles both REST API (HTTP) and Chat (WebSocket) connections

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

# Start Daphne (ASGI server) for WebSocket support
# Daphne handles both HTTP and WebSocket connections
# The --bind parameter MUST come last to override any Render-added bind settings
echo "🚀 Starting Daphne (ASGI) server on port ${PORT}..."
echo "📍 HTTP endpoint: http://0.0.0.0:${PORT} (internal)"
echo "🔌 WebSocket endpoint: ws://0.0.0.0:${PORT}/ws/chat/<parent_id>/ (internal)"
echo "✅ Server ready! Use your Render domain for public access:"
echo "   HTTP: https://your-app.onrender.com"
echo "   WebSocket: wss://your-app.onrender.com/ws/chat/<parent_id>/?token=<jwt_token>"
exec daphne -b 0.0.0.0 -p ${PORT} it360acad_backend.asgi:application

