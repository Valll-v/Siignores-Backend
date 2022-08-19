from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager



class CustomUser(AbstractBaseUser, PermissionsMixin):
    firstname = models.CharField(max_length=100, null=True, blank=True)
    lastname = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100, null=True, blank=True)
    registration_code = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=False)


    USERNAME_FIELD = 'email'

    class Meta:
        managed = True
        db_table = 'users'
    

    def set_registration_code(self, code: int):
        self.registration_code = code
        self.save()


