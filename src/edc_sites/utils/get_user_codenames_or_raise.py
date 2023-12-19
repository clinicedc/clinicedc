from __future__ import annotations

from typing import TYPE_CHECKING

from edc_auth.auth_objects import ACCOUNT_MANAGER_ROLE
from edc_auth.utils import get_codenames_for_role

if TYPE_CHECKING:
    from django.contrib.auth.models import User


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
