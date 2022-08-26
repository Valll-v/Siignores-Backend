import random

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.apps import apps
from django.db import models
from django.db.models import ForeignKey
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager

from django.db import models


class CustomUserManager(UserManager):
    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        # Lookup the real model class from the global app registry so this
        # manager method can be used in migrations. This is fine because
        # managers are by definition working on the real model.
        GlobalUserModel = apps.get_model(self.model._meta.app_label, self.model._meta.object_name)
        username = GlobalUserModel.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):

    class Group(models.TextChoices):
        ADMIN = 'DM', _('Admin')
        USER = 'US', _('User')
        STUDENT = 'ST', _('Student')

    app = models.ForeignKey('applications.App', models.CASCADE, blank=False, null=False, related_name="app")
    firstname = models.CharField(max_length=100, null=False, blank=False)
    lastname = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField()
    password = models.CharField(max_length=100, null=True, blank=True)
    registration_code = models.IntegerField(null=True, blank=True, default=0)
    is_active = models.BooleanField(default=False)
    counts_of_type = models.IntegerField(default=0)
    photo = models.ImageField(null=True, blank=True, upload_to="media/", verbose_name='Аватарка')
    group = models.CharField(
        max_length=2,
        choices=Group.choices,
        default=Group.STUDENT,
    )

    USERNAME_FIELD = 'id'

    objects = CustomUserManager()

    class Meta:
        managed = True
        db_table = 'users'
        unique_together = ('email', 'app')

    def set_registration_code(self, code: int):
        self.registration_code = code
        self.save()

    def __str__(self):
        return self.email + ' ' + str(self.app_id)
