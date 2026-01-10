# Server Setup Guide - Gunicorn vs Daphne

## The Problem

**Gunicorn (WSGI)** does **NOT** support WebSocket connections. If you're running Gunicorn, the chat system won't work.

## The Solution

Use **Daphne (ASGI)** server instead. Daphne handles both:
- ✅ HTTP requests (REST API)
- ✅ WebSocket connections (Chat)

## Quick Start

### Option 1: Use the startup script (Recommended)

```bash
./start_server.sh
```

This will start Daphne on `http://127.0.0.1:8000` with both HTTP and WebSocket support.

### Option 2: Run Daphne directly

```bash
# Activate your virtual environment first
source .venv/bin/activate
# or
source /home/whoami/Documents/Builds/django/venv/bin/activate

# Start Daphne
daphne -b 127.0.0.1 -p 8000 it360acad_backend.asgi:application
```

### Option 3: Use Django's development server (for testing only)

```bash
python manage.py runserver
```

**Note:** Django's `runserver` supports WebSocket in development mode, but it's not recommended for production.

## When to Use What

### Use **Daphne** when:
- ✅ You need WebSocket support (Chat)
- ✅ You want both HTTP and WebSocket in one server
- ✅ Production deployment (Render uses this)

### Use **Gunicorn** when:
- ❌ You **don't** need WebSocket support
- ✅ You only need HTTP REST API
- ✅ You want better performance for HTTP-only workloads

## Current Setup

Your `start.sh` (for Render) already uses Daphne:
```bash
exec daphne -b 0.0.0.0 -p ${PORT} it360acad_backend.asgi:application
```

## Testing the Chat

Once Daphne is running, test the WebSocket connection:

```bash
# In another terminal
python test_websocket_client.py <user_id> <parent_id> <token>
```

Or use the test script:
```bash
./start_chat_server.sh  # This also uses Daphne
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'daphne'"

Install Daphne:
```bash
pip install daphne
```

### "Connection refused" when connecting to WebSocket

1. Make sure Daphne is running (not Gunicorn)
2. Check the port matches (default: 8000)
3. Verify the URL: `ws://127.0.0.1:8000/ws/chat/<parent_id>/?token=<token>`

### "401 Unauthorized" on WebSocket connection

1. Make sure you're passing the JWT token: `?token=<your_jwt_token>`
2. Verify the token is valid and not expired
3. Check that the user exists and is authenticated

## Summary

| Server | HTTP API | WebSocket Chat | Use Case |
|--------|----------|----------------|----------|
| **Gunicorn** | ✅ | ❌ | HTTP-only production |
| **Daphne** | ✅ | ✅ | Full-stack with chat |
| **runserver** | ✅ | ✅ | Development only |

**For your chat system, always use Daphne!**

