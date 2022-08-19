from typing import Iterable

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import format_html

from .auth_objects import RANDO_UNBLINDED


def is_blinded_trial() -> bool:
    """Default is True"""
    return getattr(settings, "EDC_RANDOMIZATION_BLINDED_TRIAL", True)


def is_blinded_user(username) -> bool:
    """Default is True"""
    is_blinded = True
    unblinded_users = getattr(settings, "EDC_RANDOMIZATION_UNBLINDED_USERS", [])
    try:
        user = get_user_model().objects.get(username=username, is_staff=True, is_active=True)
    except ObjectDoesNotExist:
        pass
    else:
        if user.username in unblinded_users and is_blinded_trial():
            is_blinded = False
    return is_blinded


def raise_if_prohibited_from_unblinded_rando_group(username: str, groups: Iterable) -> None:
    """A user form validation to prevent adding an unlisted
    user to the RANDO_UNBLINDED group.

    See also edc_auth's UserForm.
    """
    if RANDO_UNBLINDED in [grp.name for grp in groups] and is_blinded_user(username):
        raise forms.ValidationError(
            {
                "groups": format_html(
                    "This user is not unblinded and may not added "
                    "to the <U>RANDO_UNBLINDED</U> group."
                )
            }
        )
