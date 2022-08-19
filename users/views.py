from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import CustomUser
from loguru import logger


class CustomUserViewSet(UserViewSet):
    @action(["post"], detail=False)
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = CustomUser.objects.get(email=serializer.data['email'])
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='User with such email does not exists')

        if not user.password:
            user.set_password(serializer.data["password"])
            user.save()
            logger.debug(f'password {serializer.data["password"]} setted for user with email {serializer.data["email"]}')
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='Password is already set')
        return Response(status=status.HTTP_204_NO_CONTENT)