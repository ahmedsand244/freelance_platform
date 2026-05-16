import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.room_group_name = f'chat_order_{self.order_id}'

        # Ensure user is authenticated
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        # Optional: Add authorization check to see if user is part of the order here

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        event_type = text_data_json.get('type', 'message')

        if event_type == 'typing':
            # Broadcast typing indicator
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_typing',
                    'sender_id': self.user.id,
                    'username': self.user.username,
                    'is_typing': text_data_json.get('is_typing', True)
                }
            )
        elif event_type == 'message':
            message = text_data_json.get('message', '')
            if message:
                # Save message to database
                await self.save_message(self.order_id, self.user.id, message)
                
                # Broadcast message to room
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'sender_id': self.user.id,
                        'username': self.user.username,
                    }
                )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        sender_id = event['sender_id']
        username = event['username']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': message,
            'sender_id': sender_id,
            'username': username,
        }))

    # Receive typing indicator from room group
    async def chat_typing(self, event):
        if event['sender_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'sender_id': event['sender_id'],
                'username': event['username'],
                'is_typing': event['is_typing']
            }))

    @database_sync_to_async
    def save_message(self, order_id, sender_id, text):
        from .models import OrderMessage, Order
        order = Order.objects.get(id=order_id)
        sender = User.objects.get(id=sender_id)
        OrderMessage.objects.create(order=order, sender=sender, text=text)
        
        # Ping the recipient's notification socket via channel layer!
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        # Determine recipient roughly
        client_user = order.user
        provider_user_list = [item.service.provider.user for item in order.items.all()]
        provider_user = provider_user_list[0] if provider_user_list else None
        
        recipient = client_user if sender_id == provider_user.id else provider_user
        
        if recipient:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{recipient.id}",
                {
                    "type": "send_notification",
                    "title": "New Message",
                    "message": f"{sender.username} sent you a message.",
                    "link": f"/en/services/order/{order_id}/chat/",
                    "count": 1
                }
            )


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return
            
        self.group_name = f"user_{self.user.id}"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def send_notification(self, event):
        """Called systematically when something triggers group_send"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'title': event.get('title'),
            'message': event.get('message'),
            'link': event.get('link', ''),
            'count': event.get('count', 0)
        }))
