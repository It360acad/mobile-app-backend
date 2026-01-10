# Chat System - Frontend Integration Guide

This guide explains how to integrate the real-time chat system into your frontend application.

## Quick Start

```javascript
// 1. Get JWT token from login
const response = await fetch('/api/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'user@example.com', password: 'password' })
});
const { tokens } = await response.json();
const token = tokens.access;

// 2. Connect to WebSocket
const parentId = 123; // ID of the parent you want to chat with
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const ws = new WebSocket(`${protocol}//${window.location.host}/ws/chat/${parentId}/?token=${token}`);

// 3. Handle messages
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
};

// 4. Send message
ws.send(JSON.stringify({ message: 'Hello!' }));
```

## Table of Contents

- [Overview](#overview)
- [WebSocket Connection](#websocket-connection)
- [Authentication](#authentication)
- [Message Format](#message-format)
- [Implementation Examples](#implementation-examples)
  - [React](#react-example)
  - [Vue.js](#vuejs-example)
  - [Vanilla JavaScript](#vanilla-javascript-example)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)
- [API Reference](#api-reference)

## Overview

The chat system uses **WebSocket** for real-time bidirectional communication between users. It supports:
- ✅ Real-time messaging
- ✅ Message history (automatically loaded on connect)
- ✅ JWT authentication
- ✅ Automatic message persistence
- ✅ Read status tracking

## WebSocket Connection

### Connection URL

```
ws://your-domain/ws/chat/<parent_id>/
```

**Production (Render):**
```
wss://your-app.onrender.com/ws/chat/<parent_id>/
```

**Development:**
```
ws://localhost:8000/ws/chat/<parent_id>/
```

### URL Parameters

- `<parent_id>`: The ID of the parent user you want to chat with
  - If you're a **student**, this is the parent's ID
  - If you're a **parent**, this is the other parent's ID (for parent-to-parent chat)

### Protocol

- **Development**: `ws://` (WebSocket)
- **Production**: `wss://` (Secure WebSocket - required for HTTPS sites)

## Authentication

The WebSocket connection requires JWT authentication. Include your access token in the connection headers.

### Getting the Token

First, authenticate via the REST API:

```javascript
// Login endpoint
POST /api/auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

// Response
{
  "user": { ... },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

### Using the Token

Since browsers don't support custom headers in WebSocket connections, pass the token as a query parameter:

```javascript
const token = "eyJ0eXAiOiJKV1QiLCJhbGc..."; // From login response
const wsUrl = `wss://your-domain/ws/chat/${parentId}/?token=${token}`;
const ws = new WebSocket(wsUrl);
```

**Note:** The backend supports authentication via query parameter `?token=<jwt_token>`.

## Message Format

### Sending Messages

Send messages as JSON:

```json
{
  "message": "Hello, how are you?"
}
```

### Receiving Messages

Messages are received as JSON with the following structure:

**New messages (from other users):**
```json
{
  "message": "Hello, how are you?",
  "sender_id": 123
}
```

**Previous messages (on connect):**
```json
{
  "sender_id": 123,
  "reciever_id": 456,
  "content": "Hello, how are you?",
  "timestamp": "2024-01-10T12:00:00Z",
  "is_read": false
}
```

## Implementation Examples

### React Example

```jsx
import { useState, useEffect, useRef } from 'react';

function ChatComponent({ parentId, token }) {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);

  useEffect(() => {
    // Determine WebSocket protocol based on environment
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // Pass token as query parameter (browsers don't support custom headers)
    const wsUrl = `${protocol}//${window.location.host}/ws/chat/${parentId}/?token=${token}`;
    
    // Create WebSocket connection
    const ws = new WebSocket(wsUrl);

    wsRef.current = ws;

    // Connection opened
    ws.onopen = () => {
      console.log('✅ WebSocket connected');
      setIsConnected(true);
    };

    // Message received
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      // Check if it's a previous message (has 'content' field) or new message
      if (data.content) {
        // Previous message format
        setMessages(prev => [...prev, {
          id: Date.now() + Math.random(),
          senderId: data.sender_id,
          receiverId: data.reciever_id,
          content: data.content,
          timestamp: data.timestamp,
          isRead: data.is_read,
          isPrevious: true
        }]);
      } else {
        // New message format
        setMessages(prev => [...prev, {
          id: Date.now() + Math.random(),
          senderId: data.sender_id,
          content: data.message,
          timestamp: new Date().toISOString(),
          isRead: false,
          isPrevious: false
        }]);
      }
    };

    // Connection closed
    ws.onclose = () => {
      console.log('❌ WebSocket disconnected');
      setIsConnected(false);
    };

    // Error handling
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };

    // Cleanup on unmount
    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, [parentId, token]);

  // Send message
  const sendMessage = () => {
    if (newMessage.trim() && wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        message: newMessage.trim()
      }));
      setNewMessage('');
    }
  };

  // Handle Enter key
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-status">
        {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
      </div>
      
      <div className="messages">
        {messages.map((msg) => (
          <div key={msg.id} className={`message ${msg.senderId === currentUserId ? 'sent' : 'received'}`}>
            <p>{msg.content}</p>
            <span className="timestamp">
              {new Date(msg.timestamp).toLocaleTimeString()}
            </span>
          </div>
        ))}
      </div>
      
      <div className="input-area">
        <input
          type="text"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type a message..."
          disabled={!isConnected}
        />
        <button onClick={sendMessage} disabled={!isConnected || !newMessage.trim()}>
          Send
        </button>
      </div>
    </div>
  );
}

export default ChatComponent;
```

### Vue.js Example

```vue
<template>
  <div class="chat-container">
    <div class="chat-status">
      {{ isConnected ? '🟢 Connected' : '🔴 Disconnected' }}
    </div>
    
    <div class="messages">
      <div
        v-for="msg in messages"
        :key="msg.id"
        :class="['message', msg.senderId === currentUserId ? 'sent' : 'received']"
      >
        <p>{{ msg.content }}</p>
        <span class="timestamp">
          {{ formatTime(msg.timestamp) }}
        </span>
      </div>
    </div>
    
    <div class="input-area">
      <input
        v-model="newMessage"
        @keypress.enter="sendMessage"
        placeholder="Type a message..."
        :disabled="!isConnected"
      />
      <button @click="sendMessage" :disabled="!isConnected || !newMessage.trim()">
        Send
      </button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue';

export default {
  name: 'ChatComponent',
  props: {
    parentId: {
      type: Number,
      required: true
    },
    token: {
      type: String,
      required: true
    },
    currentUserId: {
      type: Number,
      required: true
    }
  },
  setup(props) {
    const messages = ref([]);
    const newMessage = ref('');
    const isConnected = ref(false);
    let ws = null;

    const connectWebSocket = () => {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      // Pass token as query parameter (browsers don't support custom headers)
      const wsUrl = `${protocol}//${window.location.host}/ws/chat/${props.parentId}/?token=${props.token}`;
      
      ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('✅ WebSocket connected');
        isConnected.value = true;
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.content) {
          // Previous message
          messages.value.push({
            id: Date.now() + Math.random(),
            senderId: data.sender_id,
            receiverId: data.reciever_id,
            content: data.content,
            timestamp: data.timestamp,
            isRead: data.is_read,
            isPrevious: true
          });
        } else {
          // New message
          messages.value.push({
            id: Date.now() + Math.random(),
            senderId: data.sender_id,
            content: data.message,
            timestamp: new Date().toISOString(),
            isRead: false,
            isPrevious: false
          });
        }
      };

      ws.onclose = () => {
        console.log('❌ WebSocket disconnected');
        isConnected.value = false;
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        isConnected.value = false;
      };
    };

    const sendMessage = () => {
      if (newMessage.value.trim() && ws?.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
          message: newMessage.value.trim()
        }));
        newMessage.value = '';
      }
    };

    const formatTime = (timestamp) => {
      return new Date(timestamp).toLocaleTimeString();
    };

    onMounted(() => {
      // Note: WebSocket doesn't support custom headers in browser
      // You'll need to pass token via query params or use a library
      connectWebSocket();
    });

    onUnmounted(() => {
      if (ws) {
        ws.close();
      }
    });

    return {
      messages,
      newMessage,
      isConnected,
      sendMessage,
      formatTime
    };
  }
};
</script>
```

### Vanilla JavaScript Example

```javascript
class ChatClient {
  constructor(parentId, token, currentUserId) {
    this.parentId = parentId;
    this.token = token;
    this.currentUserId = currentUserId;
    this.messages = [];
    this.ws = null;
    this.isConnected = false;
    this.onMessageCallback = null;
    this.onStatusChangeCallback = null;
  }

  connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // Pass token as query parameter (browsers don't support custom headers)
    const wsUrl = `${protocol}//${window.location.host}/ws/chat/${this.parentId}/?token=${this.token}`;
    
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('✅ WebSocket connected');
      this.isConnected = true;
      this.notifyStatusChange();
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleMessage(data);
    };

    this.ws.onclose = () => {
      console.log('❌ WebSocket disconnected');
      this.isConnected = false;
      this.notifyStatusChange();
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.isConnected = false;
      this.notifyStatusChange();
    };
  }

  handleMessage(data) {
    let message;
    
    if (data.content) {
      // Previous message format
      message = {
        id: Date.now() + Math.random(),
        senderId: data.sender_id,
        receiverId: data.reciever_id,
        content: data.content,
        timestamp: data.timestamp,
        isRead: data.is_read,
        isPrevious: true
      };
    } else {
      // New message format
      message = {
        id: Date.now() + Math.random(),
        senderId: data.sender_id,
        content: data.message,
        timestamp: new Date().toISOString(),
        isRead: false,
        isPrevious: false
      };
    }

    this.messages.push(message);
    
    if (this.onMessageCallback) {
      this.onMessageCallback(message);
    }
  }

  sendMessage(content) {
    if (content.trim() && this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        message: content.trim()
      }));
      return true;
    }
    return false;
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  onMessage(callback) {
    this.onMessageCallback = callback;
  }

  onStatusChange(callback) {
    this.onStatusChangeCallback = callback;
  }

  notifyStatusChange() {
    if (this.onStatusChangeCallback) {
      this.onStatusChangeCallback(this.isConnected);
    }
  }
}

// Usage
const chat = new ChatClient(
  123, // parentId
  'your-jwt-token', // token
  456 // currentUserId
);

chat.onMessage((message) => {
  console.log('New message:', message);
  // Update UI
});

chat.onStatusChange((isConnected) => {
  console.log('Connection status:', isConnected);
  // Update UI
});

chat.connect();

// Send a message
chat.sendMessage('Hello!');
```

## Error Handling

### Common Errors

1. **Connection Refused (401 Unauthorized)**
   - **Cause**: Invalid or expired JWT token
   - **Solution**: Refresh the token and reconnect

2. **Connection Closed Unexpectedly**
   - **Cause**: Network issues, server restart, or token expiration
   - **Solution**: Implement reconnection logic

3. **Invalid Message Format**
   - **Cause**: Sending malformed JSON
   - **Solution**: Always send valid JSON: `{"message": "text"}`

### Reconnection Strategy

```javascript
class ReconnectingChatClient {
  constructor(parentId, token, currentUserId) {
    this.parentId = parentId;
    this.token = token;
    this.currentUserId = currentUserId;
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000; // 1 second
  }

  connect() {
    // ... connection logic ...
    
    this.ws.onclose = (event) => {
      if (!event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1); // Exponential backoff
        console.log(`Reconnecting in ${delay}ms... (attempt ${this.reconnectAttempts})`);
        setTimeout(() => this.connect(), delay);
      }
    };
  }
}
```

## Best Practices

### 1. Token Management

- Store tokens securely (use `localStorage` or `sessionStorage`)
- Refresh tokens before they expire
- Handle token refresh automatically

```javascript
// Token refresh example
async function refreshTokenIfNeeded() {
  const token = localStorage.getItem('access_token');
  const decoded = jwt_decode(token);
  const now = Date.now() / 1000;
  
  if (decoded.exp - now < 300) { // Refresh if expires in less than 5 minutes
    const refreshToken = localStorage.getItem('refresh_token');
    const response = await fetch('/api/auth/token/refresh/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: refreshToken })
    });
    const data = await response.json();
    localStorage.setItem('access_token', data.access);
    return data.access;
  }
  return token;
}
```

### 2. Connection Lifecycle

- Connect when component mounts or user opens chat
- Disconnect when component unmounts or user closes chat
- Handle page visibility changes (pause/resume)

```javascript
// Handle page visibility
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    // Pause or disconnect
  } else {
    // Reconnect if needed
  }
});
```

### 3. Message Handling

- Distinguish between previous messages (on connect) and new messages
- Sort messages by timestamp
- Handle duplicate messages (use unique IDs)

### 4. UI/UX

- Show connection status indicator
- Display "typing..." indicator (if implemented)
- Show message timestamps
- Handle long messages gracefully
- Scroll to bottom on new messages

### 5. Security

- Always use `wss://` in production
- Never expose tokens in client-side code
- Validate message content on frontend before sending
- Sanitize received messages before displaying

## API Reference

### WebSocket Endpoint

```
ws://domain/ws/chat/<parent_id>/
```

**Parameters:**
- `parent_id` (path parameter): ID of the parent user

**Headers:**
- `Authorization: Bearer <access_token>` (Note: Browser WebSocket API doesn't support custom headers directly. See workaround below)

### Authentication Method

The backend supports JWT authentication via **query parameter** (since browsers don't support custom headers in WebSocket connections):

```javascript
const wsUrl = `wss://domain/ws/chat/${parentId}/?token=${token}`;
const ws = new WebSocket(wsUrl);
```

**Security Note:** While passing tokens in query parameters is less secure than headers, it's the standard approach for browser WebSocket connections. The token is still encrypted and should be handled securely:
- Use HTTPS/WSS in production
- Store tokens securely (localStorage/sessionStorage)
- Implement token refresh before expiration
- Clear tokens on logout

### Message Types

**Send:**
```json
{
  "message": "Your message text"
}
```

**Receive (New Message):**
```json
{
  "message": "Message content",
  "sender_id": 123
}
```

**Receive (Previous Message):**
```json
{
  "sender_id": 123,
  "reciever_id": 456,
  "content": "Message content",
  "timestamp": "2024-01-10T12:00:00Z",
  "is_read": false
}
```

## Testing

### Test Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat/123/');
ws.onopen = () => console.log('Connected!');
ws.onmessage = (event) => console.log('Message:', event.data);
ws.onerror = (error) => console.error('Error:', error);
```

### Test with cURL (for debugging)

```bash
# Note: cURL doesn't support WebSocket directly
# Use wscat or similar tool instead
npm install -g wscat

wscat -c "ws://localhost:8000/ws/chat/123/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Troubleshooting

### Connection Issues

1. **Check CORS settings** - Ensure your backend allows WebSocket connections from your frontend domain
2. **Check firewall/proxy** - Some proxies block WebSocket connections
3. **Verify URL format** - Use `wss://` for HTTPS sites, `ws://` for HTTP
4. **Check token validity** - Ensure token hasn't expired

### Message Issues

1. **Check JSON format** - Messages must be valid JSON
2. **Verify message structure** - Must include `message` field
3. **Check console errors** - Look for parsing errors

## Support

For issues or questions:
1. Check server logs for WebSocket connection errors
2. Verify Redis/Channel layers are running
3. Ensure Celery worker is running (for notifications)
4. Check browser console for WebSocket errors

---

**Last Updated:** January 2024
**Version:** 1.0.0

