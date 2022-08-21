from xml.dom import ValidationErr

from django.contrib.auth.tokens import default_token_generator
from django.http import JsonResponse
from djoser import signals
from djoser.compat import get_user_email
from djoser.conf import settings
from djoser.utils import encode_uid
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import CustomUser
from loguru import logger
import users.db_communication as db


class CustomUserViewSet(UserViewSet):

    def get_permissions(self):
        if self.action == "check_code":
            self.permission_classes = settings.PERMISSIONS.check_code
        return super().get_permissions()

    @action(["post"], detail=False)
    def activation(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.user
            user.is_active = True
            user.save()

            signals.user_activated.send(
                sender=self.__class__, user=user, request=self.request
            )

            if settings.SEND_CONFIRMATION_EMAIL:
                context = {"user": user}
                to = [get_user_email(user)]
                settings.EMAIL.confirmation(self.request, context).send(to)

            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationErr:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Wrong registration code")

    @action(["post"], detail=False)
    def check_code(self, request, *args, **kwargs):
        data = request.data
        try:
            user = db.get_user(email=data["email"])
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Please, enter email for validate your code?")
        if not user:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED, data="User does not exist")
        if user.registration_code == 0:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="You can't sending code now")
        try:
            print(user.registration_code)
            registration_code = data["registration_code"]
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Please, enter code?")
        if registration_code == user.registration_code:
            user.registration_code = "0"
            user.counts_of_type = 0
            user.save()
            return JsonResponse(
                {
                    "uid": encode_uid(user.pk),
                    "token": default_token_generator.make_token(user)
                }
            )
        else:
            user.counts_of_type += 1
            if user.counts_of_type == 3:
                user.registration_code = 0
                user.counts_of_type = 0
                user.save()
                return Response(status=status.HTTP_400_BAD_REQUEST, data="Try to send another code,"
                                                                         " that was the last try for you")
            user.save()
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Wrong code")

    @action(["post"], detail=False)
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = CustomUser.objects.get(email=serializer.data['email'])
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='User with this email does not exists')
        if not user.password:
            user.set_password(serializer.data["password"])
            user.save()
            logger.debug(
                f'password {serializer.data["password"]} set for user with email {serializer.data["email"]}')
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='Password already set')
        return JsonResponse(
            {
                "token": settings.TOKEN_MODEL.objects.get_or_create(user=user)
            }
        )


