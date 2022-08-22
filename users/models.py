from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    firstname = models.CharField(max_length=100, null=False, blank=False)
    lastname = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100, null=True, blank=True)
    registration_code = models.IntegerField(null=True, blank=True, default=0)
    is_active = models.BooleanField(default=False)
    counts_of_type = models.IntegerField(default=0)
    photo = models.ImageField(null=True, blank=True, upload_to="media/", verbose_name='Аватарка')

    USERNAME_FIELD = 'email'

    objects = UserManager()

    class Meta:
        managed = True
        db_table = 'users'

    def set_registration_code(self, code: int):
        self.registration_code = code
        self.save()
