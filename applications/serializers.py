from rest_framework import serializers

from applications.models import App
from users.models import CustomUser


class AppSerializer(serializers.Serializer):
    class Meta:
        model = App
        fields = ['name']


