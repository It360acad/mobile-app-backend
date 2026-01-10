#!/bin/bash
# Start Daphne server for both HTTP and WebSocket support
# This replaces Gunicorn when you need WebSocket functionality

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "/home/whoami/Documents/Builds/django/venv" ]; then
    source /home/whoami/Documents/Builds/django/venv/bin/activate
fi

PORT="${PORT:-8000}"

echo "🚀 Starting Daphne (ASGI) server..."
echo "📍 HTTP endpoint: http://127.0.0.1:${PORT}"
echo "🔌 WebSocket endpoint: ws://127.0.0.1:${PORT}/ws/chat/<parent_id>/"
echo ""
echo "Daphne handles both HTTP (REST API) and WebSocket (Chat) connections"
echo "Press Ctrl+C to stop"
echo ""

daphne -b 127.0.0.1 -p ${PORT} it360acad_backend.asgi:application

