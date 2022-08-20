from djoser import email
from random import randint

from templated_mail.mail import BaseEmailMessage

from users.models import CustomUser

import users.db_communication as db


def generate_code():
    return randint(100000, 999999)


class ActivationEmail(email.ActivationEmail):
    template_name = 'users/activation.html'

    def get_context_data(self):
        context = super().get_context_data()
        email = context.get("user")
        code = str(randint(100_000, 1_000_000 - 1))
        CustomUser.objects.get(email=email).set_registration_code(code)
        context["code"] = code
        return context


class PasswordResetEmail(BaseEmailMessage):
    template_name = "users/password_reset.html"

    def get_context_data(self):
        context = super().get_context_data()
        user = context.get("user")
        code = str(generate_code())
        db.set_code(code, db.get_user(email=user))
        context["code"] = code
        return context
