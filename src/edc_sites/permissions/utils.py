from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from edc_auth.auth_objects import ACCOUNT_MANAGER_ROLE
from edc_auth.utils import get_codenames_for_role


def get_change_codenames(user: User) -> list[str]:
    """Returns a list of codenames for this user that are prefixed
    with add/change/delete.
    """
    codenames = get_user_codenames_or_raise(user)
    return [c for c in codenames if "add" in c or "change" in c or "delete" in c]


def get_user_codenames_or_raise(user: User) -> list[str]:
    """Returns a list of all codenames for this user."""
    codenames = [
        perm.codename
        for perm in user.user_permissions.all()
        if perm.codename not in get_codenames_for_role(ACCOUNT_MANAGER_ROLE)
    ]
    if not codenames:
        raise PermissionError("User has not been allocated permission to anything.")
    return codenames


def has_profile_or_raise(user: User) -> bool:
    """Raises if user instance does not have a UserProfile
    relation.

    `UserProfile` relation is set up in edc_auth. If `userprofile`
    relation is missing, confirm `edc_auth` is in INSTALLED_APPS.
    """
    user = User.objects.get(id=user.id)
    userprofile = getattr(user, "userprofile", None)
    if not userprofile:
        raise ImproperlyConfigured(
            "User instance has no `userprofile`. User accounts must have a relation "
            "to `UserProfile`. See edc_sites."
        )
    return True
