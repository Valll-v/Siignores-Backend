from django.db import models
from datetime import datetime
from courses.models import Course
from datetime import datetime
from loguru import logger


class ChatManager(models.Manager):
    def get_chat_users(self, chat_id):
        return [{
            'id': chat_user.user.id,
            'firstname': chat_user.user.firstname,
            'lastname': chat_user.user.lastname,
            'photo': chat_user.user.photo.url if chat_user.user.photo else None
        } for chat_user in ChatUser.objects.filter(chat_id=chat_id)]
    

    def get_user_chats(self, user_id):
        return [{
            'chat_id': chat_user.chat.id,
            'chat_name': chat_user.chat.name,
            'users_count': len(self.get_chat_users(chat_user.chat.id))
        } for chat_user in ChatUser.objects.filter(user_id=user_id)]


class Chat(models.Model):
    name = models.CharField(max_length=100)
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='chat_course')

    objects = ChatManager()

    class Meta:
        managed = True
        db_table = 'chat'


class ChatUser(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='chat_user_user')
    chat = models.ForeignKey('chat.Chat', on_delete=models.CASCADE, related_name='chat_user_chat')


    class Meta:
        managed = True
        db_table = 'chat_user'


class MessageManager(models.Manager):
    def get_chat_messages(self, chat_id):
        return [{
            'from': {
                'id': message.from_user.id,
                'firstname':  message.from_user.firstname,
                'lastname':  message.from_user.lastname,
                'photo':  message.from_user.photo.url if  message.from_user.photo else None
            },
            'time': message.time,
            'message': message.message
        } for message in self.filter(chat_id=chat_id)]


class Message(models.Model):
    from_user = models.ForeignKey('users.CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='from_user')
    chat = models.ForeignKey('chat.Chat', on_delete=models.CASCADE, related_name='message_chat')
    message = models.CharField(max_length=2000)
    time = models.DateTimeField(default=datetime.now)

    objects = MessageManager()

    class Meta:
        managed = True
        db_table = 'message'


class NotificationManager(models.Manager):
    def get_user_notifications(self, user_id):
        notifications = list(self.filter(user_id=user_id, is_viewed=False))
        for notification in notifications:
            notification.is_viewed = True
            notification.save()
        return [{
            'id': n.id,
            'time': n.time,
            'message': n.message
        } for n in notifications]

class Notification(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    message = models.CharField(max_length=200)
    time = models.DateTimeField(default=datetime.now)
    is_viewed = models.BooleanField(default=False)

    objects = NotificationManager()

    class Meta:
        managed = True
        db_table = 'notifications'