from django.http import JsonResponse, HttpResponseServerError
from loguru import logger
from .models import ChatUser, Message
from rest_framework import viewsets
from .models import Chat, Notification
from rest_framework.permissions import IsAuthenticated
from .serializers import ChatSerializer, UserChatSerializer
from rest_framework.response import Response
from rest_framework import status


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
            return JsonResponse({
                'count': len(notifications),
                'chats': notifications
            }, safe=False)
        except Exception as err:
            logger.exception(err)
            return HttpResponseServerError(f'Something goes wrong: {err}')
    

    def create_chat(self, request):
        try:
            serializer = ChatSerializer(data=request.data)
            serializer.is_valid()
            chat = serializer.save()
            return Response(ChatSerializer(chat).data)
        except Exception as err:
            logger.exception(err)
            return HttpResponseServerError(f'Something goes wrong: {err}')
    
    
    def add_user(self, request):
        try:
            serializer = UserChatSerializer(data=request.data)
            serializer.is_valid()
            userchat = serializer.save()
            return Response(UserChatSerializer(userchat).data)
        except Exception as err:
            logger.exception(err)
            return HttpResponseServerError(f'Something goes wrong: {err}')
    

    def delete_user(self, request):
        try:
            serializer = UserChatSerializer(data=request.data)
            serializer.is_valid()
            chatuser = ChatUser.objects.filter(chat_id=serializer.data['chat'], user_id=serializer.data['user']).first()
            if not chatuser:
                return Response(status=status.HTTP_400_BAD_REQUEST, data="User not in this chat")
            chatuser.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as err:
            logger.exception(err)
            return HttpResponseServerError(f'Something goes wrong: {err}')