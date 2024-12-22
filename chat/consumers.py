import json
from django.contrib.auth import get_user_model

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatGroup, Message

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        print("Scope User:", self.scope["user"]) 
        print("User ID:", getattr(self.scope["user"], 'id', None))
        self.user = await self.get_user()
        self.room_group_name = None
        
        # Join user's personal group for direct messages
        self.personal_group = f"user_{self.user.id}"
        await self.channel_layer.group_add(
            self.personal_group,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        if self.room_group_name:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        
        await self.channel_layer.group_discard(
            self.personal_group,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'direct_message':
            recipient_id = data['recipient_id']
            content = data['content']
            
            # Save message to database
            message = await self.save_direct_message(recipient_id, content)
            
            # Send to recipient's personal group
            await self.channel_layer.group_send(
                f"user_{recipient_id}",
                {
                    'type': 'chat_message',
                    'message': {
                        'id': message.id,
                        'content': content,
                        'sender_id': self.user.id,
                        'sender_username': self.user.username,
                        'timestamp': str(message.timestamp)
                    }
                }
            )
        
        elif message_type == 'group_message':
            group_id = data['group_id']
            content = data['content']
            
            # Save message to database
            message = await self.save_group_message(group_id, content)
            
            # Send to group
            await self.channel_layer.group_send(
                f"group_{group_id}",
                {
                    'type': 'chat_message',
                    'message': {
                        'id': message.id,
                        'content': content,
                        'sender_id': self.user.id,
                        'sender_username': self.user.username,
                        'group_id': group_id,
                        'timestamp': str(message.timestamp)
                    }
                }
            )

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))

    @database_sync_to_async 
    def get_user(self): 
        return User.objects.get(id=self.scope["user"].id)
    
    @database_sync_to_async
    def save_direct_message(self, recipient_id, content):
        return Message.objects.create(
            sender=self.user,
            recipient_id=recipient_id,
            content=content
        )

    @database_sync_to_async
    def save_group_message(self, group_id, content):
        return Message.objects.create(
            sender=self.user,
            group_id=group_id,
            content=content
        )
