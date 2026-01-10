#!/bin/bash
# Start Daphne server for WebSocket support

# Try to activate .venv first, fallback to system venv
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "/home/whoami/Documents/Builds/django/venv" ]; then
    source /home/whoami/Documents/Builds/django/venv/bin/activate
fi

echo "🚀 Starting Daphne server for WebSocket chat..."
echo "📍 Server will run on http://0.0.0.0:8000"
echo "🔌 WebSocket endpoint: ws://localhost:8000/ws/chat/<parent_id>/"
echo ""
echo "Press Ctrl+C to stop"
echo ""

daphne -b 0.0.0.0 -p 8000 it360acad_backend.asgi:application

