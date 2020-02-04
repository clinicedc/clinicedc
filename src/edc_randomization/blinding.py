from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist


def is_blinded_trial():
    return getattr(settings, "EDC_RANDOMIZATION_BLINDED_TRIAL", True)


def is_blinded_user(username):
    if is_blinded_trial():
        is_blinded_user = True
        unblinded_users = getattr(settings, "EDC_RANDOMIZATION_UNBLINDED_USERS", [])
        User = django_apps.get_model("auth.user")
        try:
            user = User.objects.get(username=username, is_staff=True, is_active=True)
        except ObjectDoesNotExist:
            pass
        else:
            if user.username in unblinded_users:
                is_blinded_user = False
    else:
        is_blinded_user = False
    return is_blinded_user
