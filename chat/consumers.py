

import json
from datetime import datetime
from django.db import models
from chat.models import Message
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):

  async def connect(self):
    self.parent_id = int(self.scope['url_route']['kwargs']['parent_id'])
    self.user = self.scope['user']

    self.room_group_name = f'chat_{min(self.parent_id, self.user.id)}_{max(self.parent_id, self.user.id)}'
    await self.channel_layer.group_add(self.room_group_name, self.channel_name)
    await self.accept()

    # Fetch previous messages between these two users
    previous_messages = await self.fetch_messages(self.user.id, self.parent_id)

    for msg in previous_messages:
      await self.send(text_data=json.dumps({
        "sender_id": msg["sender_id"],
        "reciever_id": msg["reciever_id"],
        "content": msg["content"],
        "timestamp": msg["timestamp"],
        "is_read": msg["is_read"],
      }))

  async def disconnect(self, close_code):
    await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

  async def receive(self, text_data):
    data = json.loads(text_data)
    message = data['message']

    # Save message to database
    await self.save_message(self.user.id, self.parent_id, message)

    # Broadcast message to room group
    await self.channel_layer.group_send(self.room_group_name, {
      "type": "chat_message",
      "content": message,
      "sender_id": self.user.id,
    })

  async def chat_message(self, event):
    await self.send(text_data=json.dumps({
      'message': event['content'],
      'sender_id': event['sender_id'],
    }))

  @database_sync_to_async
  def fetch_messages(self, sender_id, reciever_id):
    """Fetch previous messages between two users"""
    messages = Message.objects.filter(
      (models.Q(sender_id=sender_id, reciever_id=reciever_id) |
       models.Q(sender_id=reciever_id, reciever_id=sender_id))
    ).order_by('timestamp')
    return [
      {
        "sender_id": msg.sender.id,
        "reciever_id": msg.reciever.id,
        "content": msg.content,
        "timestamp": msg.timestamp.isoformat(),
        "is_read": msg.is_read,
      } for msg in messages
    ]

  @database_sync_to_async
  def save_message(self, sender_id, reciever_id, content):
    """Save message to database"""
    from users.models import User
    sender = User.objects.get(id=sender_id)
    reciever = User.objects.get(id=reciever_id)
    Message.objects.create(
      sender=sender,
      reciever=reciever,
      content=content
    )