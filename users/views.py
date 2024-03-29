from xml.dom import ValidationErr
from applications.models import App
from django.contrib.auth.tokens import default_token_generator
from django.http import JsonResponse
from django.utils.timezone import now
from djoser import signals, utils
from djoser.compat import get_user_email
from djoser.conf import settings
from djoser.utils import encode_uid
from djoser.views import UserViewSet
from rest_framework import status, generics
from rest_framework.decorators import action
from rest_framework.response import Response

from applications.models import App
from users.models import CustomUser
from loguru import logger
import users.db_communication as db
from users.serializers import CustomUserSerializer, CustomAdminSerializer, CustomUserProfileSerializer


class CustomUserViewSet(UserViewSet):

    def get_permissions(self):
        if self.action == "check_code":
            self.permission_classes = settings.PERMISSIONS.check_code
        if self.action == "change_photo":
            self.permission_classes = settings.PERMISSIONS.change_photo
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
        except CustomUser.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Can't find user in this app")

    @action(["post"], detail=False)
    def check_code(self, request, *args, **kwargs):
        data = request.data
        try:
            user = CustomUser.objects.get(email=data['email'], app=data['app'])
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
            print(serializer.data)
            user = CustomUser.objects.get(email=serializer.data['email'], app=serializer.data['app'])
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='You forgot about email or app')
        except Exception as ex:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='You with this email does not exist')
        if not user.password:
            user.set_password(serializer.data["password"])
            user.save()
            logger.debug(
                f'password {serializer.data["password"]} set for user with email {serializer.data["email"]}')
        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED, data='Password already set')
        token = utils.login_user(self.request, user)
        token_serializer_class = settings.SERIALIZERS.token
        return Response(
            data=token_serializer_class(token).data, status=status.HTTP_200_OK
        )

    @action(["put"], detail=False)
    def change_photo(self, request, *args, **kwargs):
        user = self.get_instance()
        user.photo = request.FILES["photo"]
        user.save()
        return Response(CustomUserProfileSerializer(user).data)

    @action(["post"], detail=False)
    def reset_password(self, request, *args, **kwargs):
        user = CustomUser.objects.get(email=request.data['email'], app=request.data['app'])
        if user:
            context = {"user": user}
            to = [get_user_email(user)]
            settings.EMAIL.password_reset(self.request, context).send(to)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(["post"], detail=False)
    def reset_password_confirm(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.user.set_password(serializer.data["new_password"])
        if hasattr(serializer.user, "last_login"):
            serializer.user.last_login = now()
        serializer.user.save()
        if settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            context = {"user": serializer.user}
            to = [get_user_email(serializer.user)]
            settings.EMAIL.password_changed_confirmation(self.request, context).send(to)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(["post"], detail=False)
    def add_superuser(self, request, *args, **kwargs):
        user = request.user
        if user.group != 'DM':
            return Response(status=status.HTTP_403_FORBIDDEN, data="Only for admins")
        if "group" in request.data:
            if request.data["group"] == 'DM':
                request.data["app"] = App.objects.get(name='admin_app').token
        else:
            Response(status=status.HTTP_400_BAD_REQUEST, data="Can't find group in request")
        new_user = CustomAdminSerializer(data=request.data)
        if new_user.is_valid():
            user = new_user.save()
        else:
            return Response(new_user.errors)
        try:
            user.is_active = True
            user.set_password(request.data["password"])
            user.save()
            return Response(CustomAdminSerializer(user).data)
        except Exception as ex:
            user.delete()
            return Response(status=status.HTTP_400_BAD_REQUEST, data=f"You forgot about some fields: {str(ex)}")

    @action(["get"], detail=False)
    def get_users(self, request, app_id):
        user = request.user
        app = App.objects.get(id=app_id)
        if user.group == 'ST' or (user.group == 'US' and user.app != app):
            return Response(status=status.HTTP_403_FORBIDDEN,
                            data="You are simp student, get away. Or that not your app, get away anyway")        
        return JsonResponse(
            {
                "users": [CustomUserProfileSerializer(user).data for user in CustomUser.objects.filter(app=app,
                                                                                                       group='US')]
            }
        )
    
@action(["delete"], detail=False)
def delete(self, request):
    user = request.user
    user.delete()
    return Response(status=status.HTTP_200_OK)



class CustomTokenCreateView(utils.ActionViewMixin, generics.GenericAPIView):
    """
    Use this endpoint to obtain user authentication token.
    """

    serializer_class = settings.SERIALIZERS.token_create
    permission_classes = settings.PERMISSIONS.token_create

    def _action(self, email, app=None):
        if app:
            token = utils.login_user(self.request,
                                     CustomUser.objects.get(email=email, app=app))
        else:
            token = utils.login_user(self.request,
                                     CustomUser.objects.get(email=email))
        token_serializer_class = settings.SERIALIZERS.token
        return Response(
            data=token_serializer_class(token).data, status=status.HTTP_200_OK
        )

    def post(self, request, **kwargs):
        data = request.data
        if 'app' not in data:
            user = db.get_user(email=data["email"])
            if not user:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data='Wrong email or password. Try another app or email')
            data["id"] = user.id
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            return self._action(data["email"])
        else:
            user = db.get_user(email=data["email"], app=data['app'])
            if not user:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data='Wrong email or password. Try another app or email')
            data["id"] = user.id
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            return self._action(data["email"], data['app'])