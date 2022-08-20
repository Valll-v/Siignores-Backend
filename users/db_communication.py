from users.models import CustomUser


def get_user(**kwargs) -> CustomUser:
    return CustomUser.objects.filter(
        **kwargs
    ).first()


def set_code(code: str, user: CustomUser):
    user.registration_code = code
    user.save()
