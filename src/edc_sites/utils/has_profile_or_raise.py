from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured

if TYPE_CHECKING:
    from django.contrib.auth.models import User


def has_profile_or_raise(user: User) -> bool:
    """Raises if user instance does not have a UserProfile
    relation.

    `UserProfile` relation is set up in edc_auth. If `userprofile`
    relation is missing, confirm `edc_auth` is in INSTALLED_APPS.
    """

    user = get_user_model().objects.get(id=user.id)
    userprofile = getattr(user, "userprofile", None)
    if not userprofile:
        raise ImproperlyConfigured(
            "User instance has no `userprofile`. User accounts must have a relation "
            "to `UserProfile`. See edc_sites."
        )
    return True
