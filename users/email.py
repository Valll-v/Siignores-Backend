from djoser import email
from random import randint

from templated_mail.mail import BaseEmailMessage

from users.models import CustomUser

import users.db_communication as db


class ActivationEmail(email.ActivationEmail):
    template_name = 'users/activation.html'

    def get_context_data(self):
        context = super().get_context_data()
        user = context.get("user")
        email, app_id = str(user).split()
        code = str(randint(100_000, 1_000_000 - 1))
        CustomUser.objects.get(email=email, app_id=app_id).set_registration_code(code)
        context["code"] = code
        context["email"] = email
        return context


class PasswordResetEmail(BaseEmailMessage):
    template_name = "users/password_reset.html"

    def get_context_data(self):
        context = super().get_context_data()
        user = context.get("user")
        email, app_id = str(user).split()
        code = str(randint(100_000, 1_000_000 - 1))
        db.set_code(code, db.get_user(email=email, app_id=app_id))
        context["code"] = code
        return context
