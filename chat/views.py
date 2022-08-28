from django.http import HttpRequest, JsonResponse, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from loguru import logger
import json
from rest_framework.decorators import api_view
from .models import Message


@api_view(['GET'])
@csrf_exempt
def get_chat(request: HttpRequest, chat_id):
    try:
        return JsonResponse(Message.objects.get_chat_messages(chat_id), safe=False)
    except Exception as err:
        logger.exception(err)
        return HttpResponseServerError(f'Something goes wrong: {err}')
