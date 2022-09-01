import json 
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message, Chat, ChatUser, Notification
from loguru import logger
from djoser.conf import settings
from users.models import CustomUser
 
class ChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        args = self.scope['path'].split('/')
        token = args[-1]
        user = await self.get_user(token)
        self.room_name = user.id
        self.room_group_name = 'chat_%s' % self.room_name
        logger.info(f'Created new room: {self.room_name}')
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
 
    # Метод для отключения пользователя
    async def disconnect(self, close_code):
        # Отключаем пользователя
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
 
    # Декоратор для работы с БД в асинхронном режиме
    @database_sync_to_async
    # Функция для создания нового сообщения в БД
    def new_message(self, from_id, chat_id, message):
        # Создаём сообщение в БД
        Message.objects.create(
            from_user_id = from_id,
            chat_id = chat_id,
            message=message
        )

    
    @database_sync_to_async
    def get_user(self, token):
        return CustomUser.objects.get(id=settings.TOKEN_MODEL.objects.get(key=token).user_id)

    @database_sync_to_async
    def get_user_by_id(self, user_id):
        return CustomUser.objects.get(id=user_id)
    
    @database_sync_to_async
    def get_chat_users(self, chat_id):
        return Chat.objects.get_chat_users(chat_id)
 
    # Принимаем сообщение от пользователя
    async def receive(self, text_data=None, bytes_data=None):
        # Форматируем сообщение из JSON
        logger.debug(text_data)
        text_data_json = json.loads(text_data)
        # Получаем текст сообщения
        message = text_data_json['message']
        chat_id = text_data_json['chat_id']
        
        # Добавляем сообщение в БД 
        await self.new_message(from_id=int(self.room_name), chat_id=chat_id, message=message)
        
        # Отправляем сообщение 
        logger.debug(await self.get_chat_users(chat_id))
        
        sender = await self.get_user_by_id(self.room_name)


        for user_id in await self.get_chat_users(chat_id):
            await self.channel_layer.group_send(
                'chat_' + str(user_id['id']),
                {
                    'type': 'chat_message',
                    'chat_id': chat_id,
                    'from': {
                        'id': sender.id,
                        'firstname': sender.firstname,
                        'lastname': sender.lastname,
                        'photo': sender.photo.url if sender.photo else None
                    },
                    'message': message,
                }
            )
    
    # Метод для отправки сообщения клиентам
    async def chat_message(self, event):
        # Получаем сообщение от receive
        message = event['message']
        # Отправляем сообщение клиентам
        # user = await self.get_user_by_id(int(event['from']))
        await self.send(text_data=json.dumps({
            'chat_id': event['chat_id'],
            'from': event['from'],
            'message': message,
        }, ensure_ascii=False))


    async def notify(self, event):
        logger.debug(event)
        self.new_message(
            user_id=self.room_name,
            message=event['message']
        )
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': event['message'],
            'notifications': event['notifications']
        }, ensure_ascii=False))
