from django.http import HttpRequest, JsonResponse
from django.shortcuts import render

# Create your views here.
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from applications.models import App


class ApplicationView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema()
    def post(self, request):
        app = App(
            name=request.data["name"]
        )
        app.set_id()
        token = app.generate_token()
        app.save()
        return JsonResponse(
            {
                "app_id": app.id,
                "token": token
            }
        )
