from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist


def is_blinded_trial():
    return getattr(settings, "EDC_RANDOMIZATION_BLINDED_TRIAL", True)


def is_blinded_user(username):
    if is_blinded_trial():
        _is_blinded_user = True
        unblinded_users = getattr(settings, "EDC_RANDOMIZATION_UNBLINDED_USERS", [])
        try:
            user = get_user_model().objects.get(
                username=username, is_staff=True, is_active=True
            )
        except ObjectDoesNotExist:
            pass
        else:
            if user.username in unblinded_users:
                _is_blinded_user = False
    else:
        _is_blinded_user = False
    return _is_blinded_user
