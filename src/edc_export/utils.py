import os
from typing import Iterable

from django import forms
from django.utils.html import format_html

from .auth_objects import EXPORT_PII


def get_export_folder() -> str:
    from django.conf import settings

    if path := getattr(settings, "EDC_EXPORT_EXPORT_FOLDER", None):
        return os.path.expanduser(path)
    return os.path.join(settings.MEDIA_ROOT, "data_folder", "export")


def get_upload_folder() -> str:
    from django.conf import settings

    if path := getattr(settings, "EDC_EXPORT_UPLOAD_FOLDER", None):
        return os.path.expanduser(path)
    return os.path.join(settings.MEDIA_ROOT, "data_folder", "upload")


def get_export_pii_users() -> list[str]:
    from django.conf import settings

    return getattr(settings, "EDC_EXPORT_EXPORT_PII_USERS", [])


def raise_if_prohibited_from_export_pii_group(username: str, groups: Iterable) -> None:
    """A user form validation to prevent adding an unlisted
    user to the EXPORT_PII group.

    See also edc_auth's UserForm.
    """
    if EXPORT_PII in [grp.name for grp in groups] and username not in get_export_pii_users():
        raise forms.ValidationError(
            {
                "groups": format_html(
                    "This user is not allowed to export PII data. You may not add "
                    f"this user to the <U>{EXPORT_PII}</U> group."
                )
            }
        )
