from djoser.serializers import UserSerializer, TokenSerializer
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from users.models import CustomUser


class CustomUserSerializer(UserSerializer):
    class Meta:
        model = CustomUser
        fields = ('app', 'email', 'firstname', 'lastname')


class CustomAdminSerializer(UserSerializer):
    class Meta:
        model = CustomUser
        fields = ('group', 'app', 'email', 'firstname', 'lastname')


class CustomUserProfileSerializer(UserSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'photo', 'email', 'firstname', 'lastname')


class CustomUserActivationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    registration_code = serializers.CharField()

    class Meta:
        model = CustomUser

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        self.user = CustomUser.objects.get(email=self.initial_data.get("email", ""),
                                           app_id=self.initial_data.get("app", ""))
        if self.user.registration_code == self.initial_data.get("registration_code", ""):
            self.user.is_active = True
            self.user.save()
            return validated_data
        else:
            return validated_data


class CustomUserSetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    app = serializers.CharField()

    class Meta:
        model = CustomUser