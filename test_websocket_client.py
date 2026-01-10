#!/usr/bin/env python3
"""
WebSocket client for testing chat functionality
Usage: python test_websocket_client.py <user_id> <parent_id> <token>
"""
import asyncio
import websockets
import json
import sys
import os

# Add Django to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'it360acad_backend.settings')

async def test_websocket(user_id, parent_id, token):
    """Test WebSocket connection"""
    uri = f"ws://localhost:8000/ws/chat/{parent_id}/"
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    print(f"🔌 Connecting to {uri}...")
    print(f"   User ID: {user_id}")
    print(f"   Parent ID: {parent_id}")
    print()
    
    try:
        async with websockets.connect(uri, extra_headers=list(headers.items())) as websocket:
            print("✅ Connected successfully!")
            print("📨 Listening for messages...")
            print("💬 Type messages to send (or 'quit' to exit)")
            print("-" * 50)
            
            # Create tasks for sending and receiving
            async def send_messages():
                while True:
                    try:
                        message = await asyncio.get_event_loop().run_in_executor(
                            None, input
                        )
                        if message.lower() == 'quit':
                            await websocket.close()
                            break
                        
                        data = {"message": message}
                        await websocket.send(json.dumps(data))
                        print(f"📤 Sent: {message}")
                    except websockets.exceptions.ConnectionClosed:
                        break
                    except Exception as e:
                        print(f"❌ Error sending: {e}")
                        break
            
            async def receive_messages():
                try:
                    async for message in websocket:
                        data = json.loads(message)
                        if 'message' in data:
                            print(f"📥 Received: {data['message']} (from user {data.get('sender_id', 'unknown')})")
                        else:
                            print(f"📥 Received: {data}")
                except websockets.exceptions.ConnectionClosed:
                    print("🔌 Connection closed")
                except Exception as e:
                    print(f"❌ Error receiving: {e}")
            
            # Run both tasks
            await asyncio.gather(
                send_messages(),
                receive_messages()
            )
            
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ Connection failed: {e}")
        print("💡 Make sure:")
        print("   1. Server is running (daphne or runserver)")
        print("   2. Token is valid")
        print("   3. User has permission to access chat")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python test_websocket_client.py <user_id> <parent_id> <token>")
        print("\nExample:")
        print("  python test_websocket_client.py 1 2 eyJ0eXAiOiJKV1QiLCJhbGc...")
        sys.exit(1)
    
    user_id = sys.argv[1]
    parent_id = sys.argv[2]
    token = sys.argv[3]
    
    asyncio.run(test_websocket(user_id, parent_id, token))

