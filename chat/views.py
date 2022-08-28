from django.http import JsonResponse, HttpResponseServerError
from loguru import logger
from .models import Message
from rest_framework import viewsets
from .models import Chat


# @api_view(['GET'])
# def get_chat(request: HttpRequest, chat_id):
#     try:
#         return JsonResponse(Message.objects.get_chat_messages(chat_id), safe=False)
#     except Exception as err:
#         logger.exception(err)
#         return HttpResponseServerError(f'Something goes wrong: {err}')


class ChatView(viewsets.ViewSet):
    def get(self, request, chat_id):
        try:
            return JsonResponse(Message.objects.get_chat_messages(chat_id), safe=False)
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