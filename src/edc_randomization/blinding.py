from typing import Iterable

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.utils.html import format_html

from .auth_objects import RANDO_UNBLINDED


def get_unblinded_users() -> list[str]:
    unblinded_users = getattr(settings, "EDC_RANDOMIZATION_UNBLINDED_USERS", [])
    if not trial_is_blinded() and unblinded_users:
        raise ImproperlyConfigured(
            "Did not expect a list of unblinded users. Got settings."
            "EDC_RANDOMIZATION_BLINDED_TRIAL=False but "
            f"EDC_RANDOMIZATION_UNBLINDED_USERS={unblinded_users}"
        )
    return unblinded_users


def trial_is_blinded() -> bool:
    """Default is True"""
    blinded_trial = getattr(settings, "EDC_RANDOMIZATION_BLINDED_TRIAL", True)
    if blinded_trial is None:
        blinded_trial = True
    return blinded_trial


def user_is_blinded(username) -> bool:
    if blinded := trial_is_blinded():
        try:
            user = get_user_model().objects.get(
                username=username, is_staff=True, is_active=True
            )
        except ObjectDoesNotExist:
            blinded = True
        else:
            if user.username in get_unblinded_users():
                blinded = False
    return blinded


def raise_if_prohibited_from_unblinded_rando_group(username: str, groups: Iterable) -> None:
    """A user form validation to prevent adding an unlisted
    user to the RANDO_UNBLINDED group.

    See also edc_auth's UserForm.
    """
    if RANDO_UNBLINDED in [grp.name for grp in groups] and user_is_blinded(username):
        raise forms.ValidationError(
            {
                "groups": format_html(
                    "This user is not unblinded and may not added "
                    "to the <U>RANDO_UNBLINDED</U> group."
                )
            }
        )
