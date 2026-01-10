# Quick Chat Test Guide

## Setup (One Time)

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run migrations:**
```bash
python manage.py makemigrations
python manage.py migrate
```

## Testing in Two Terminals

### Terminal 1: Start Server

```bash
cd /home/whoami/Documents/Builds/django/it360acad/it360acad_backend
source .venv/bin/activate
./start_chat_server.sh
```

Or manually:
```bash
daphne -b 0.0.0.0 -p 8000 it360acad_backend.asgi:application
```

### Terminal 2: Get JWT Tokens

First, get tokens for two users (e.g., a student and a parent):

```bash
# Login as User 1 (Student)
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "student@example.com", "password": "your_password"}'

# Login as User 2 (Parent)  
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "parent@example.com", "password": "your_password"}'
```

Copy the `access` tokens from both responses.

### Terminal 2: Connect as User 1

```bash
cd /home/whoami/Documents/Builds/django/it360acad/it360acad_backend
source .venv/bin/activate
python test_websocket_client.py 1 2 YOUR_TOKEN_1
```

Where:
- `1` = User 1's ID (student)
- `2` = User 2's ID (parent they want to chat with)
- `YOUR_TOKEN_1` = JWT token for User 1

### Terminal 3: Connect as User 2

```bash
cd /home/whoami/Documents/Builds/django/it360acad/it360acad_backend
source .venv/bin/activate
python test_websocket_client.py 2 1 YOUR_TOKEN_2
```

Where:
- `2` = User 2's ID (parent)
- `1` = User 1's ID (student they want to chat with)
- `YOUR_TOKEN_2` = JWT token for User 2

## Test Flow

1. **Start server** in Terminal 1
2. **Connect User 1** in Terminal 2
3. **Connect User 2** in Terminal 3
4. **Type messages** in either terminal
5. **See messages** appear in both terminals

## Example Session

**Terminal 2 (User 1):**
```
🔌 Connecting to ws://localhost:8000/ws/chat/2/...
   User ID: 1
   Parent ID: 2

✅ Connected successfully!
📨 Listening for messages...
💬 Type messages to send (or 'quit' to exit)
--------------------------------------------------
Hello! 👋
📤 Sent: Hello! 👋
📥 Received: Hello! 👋 (from user 1)
```

**Terminal 3 (User 2):**
```
🔌 Connecting to ws://localhost:8000/ws/chat/1/...
   User ID: 2
   Parent ID: 1

✅ Connected successfully!
📨 Listening for messages...
💬 Type messages to send (or 'quit' to exit)
--------------------------------------------------
📥 Received: Hello! 👋 (from user 1)
Hi there! How are you?
📤 Sent: Hi there! How are you?
```

## Troubleshooting

### Server won't start
- Check if port 8000 is in use: `lsof -i :8000`
- Verify Redis/Upstash is accessible
- Check `REDIS_URL` is set correctly

### Can't connect
- Verify token is valid (not expired)
- Check user IDs are correct
- Ensure server is running

### Messages not received
- Verify both clients are connected
- Check they're using correct user/parent IDs
- Check server logs for errors

## Quick Commands Reference

```bash
# Start server
./start_chat_server.sh

# Test client
python test_websocket_client.py <user_id> <parent_id> <token>

# Check server status
curl http://localhost:8000/api/docs/
```

