from django.http import JsonResponse, HttpResponseServerError
from loguru import logger
from .models import Message
from rest_framework import viewsets
from .models import Chat, Notification
from rest_framework.permissions import IsAuthenticated


class ChatView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get(self, request, chat_id):
        try:
            users = Chat.objects.get_chat_users(chat_id)
            return JsonResponse({
                'count': len(users),
                'users': users,
                'messages': Message.objects.get_chat_messages(chat_id)
            }, safe=False)
        except Exception as err:
            logger.exception(err)
            return HttpResponseServerError(f'Something goes wrong: {err}')
    

    def get_user_chats(self, request):
        try:
            chats = Chat.objects.get_user_chats(request.user.id)
            return JsonResponse({
                'count': len(chats),
                'chats': chats
            }, safe=False)
        except Exception as err:
            logger.exception(err)
            return HttpResponseServerError(f'Something goes wrong: {err}')
    

    def get_notifications(self, request):
        try:
            notifications = Notification.objects.get_user_notifications(request.user.id)
            logger.debug(notifications)
            return JsonResponse({
                'count': len(notifications),
                'chats': notifications
            }, safe=False)
        except Exception as err:
            logger.exception(err)
            return HttpResponseServerError(f'Something goes wrong: {err}')