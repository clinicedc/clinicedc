from __future__ import annotations

from typing import TYPE_CHECKING

from .get_user_codenames_or_raise import get_user_codenames_or_raise

if TYPE_CHECKING:
    from django.contrib.auth.models import User


def get_change_codenames(user: User) -> list[str]:
    """Returns a list of codenames for this user that are prefixed
    with add/change/delete.
    """
    codenames = get_user_codenames_or_raise(user)
    return [c for c in codenames if "add" in c or "change" in c or "delete" in c]
