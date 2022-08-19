from xml.dom import ValidationErr
from rest_framework import serializers
from users.models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'


class CustomUserActivationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    registration_code = serializers.CharField()


    class Meta:
        model = CustomUser
    

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        self.user = CustomUser.objects.get(email=self.initial_data.get("email", ""))
        if self.user.registration_code == self.initial_data.get("registration_code", ""):
            self.user.is_active = True
            self.user.save()
            return validated_data
        else:
            raise ValidationErr('Wrong registration code')


class CustomUserSetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


    class Meta:
        model = CustomUser
