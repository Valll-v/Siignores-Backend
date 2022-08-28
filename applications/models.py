from time import time

import jwt
from django.db import models


# Create your models here.
from signories.settings import SECRET_KEY


class App(models.Model):
    id = models.IntegerField()
    name = models.CharField(max_length=100, null=False, blank=False, verbose_name='Название')
    token = models.CharField(max_length=500, null=False, blank=False, verbose_name='Token Приложения', primary_key=True)

    def generate_token(self):
        token = jwt.encode({
            'nickname': self.name,
            'timestamp': str(time())
        }, key=SECRET_KEY)
        self.token = token
        return token

    class Meta:
        managed = True
        db_table = 'apps'

    def set_id(self):
        self.id = sorted(App.objects.all(), key=lambda x: x.id)[-1].id + 1 if App.objects.all() else 1
