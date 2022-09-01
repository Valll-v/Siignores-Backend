from rest_framework.serializers import ModelSerializer
from .models import Chat, ChatUser

class ChatSerializer(ModelSerializer):
    class Meta:
        model = Chat
        fields = ('course', 'name')


class UserChatSerializer(ModelSerializer):
    class Meta:
        model = ChatUser
        fields = ('chat', 'user')