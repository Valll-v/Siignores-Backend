from djoser import email
from random import randint
from users.models import CustomUser


class ActivationEmail(email.ActivationEmail):
    template_name = 'activation.html'

    def get_context_data(self):
        context = super().get_context_data()
        email = context.get("user")
        code = str(randint(100_000, 1_000_000 - 1))
        CustomUser.objects.get(email=email).set_registration_code(code)
        context["code"] = code
        return context