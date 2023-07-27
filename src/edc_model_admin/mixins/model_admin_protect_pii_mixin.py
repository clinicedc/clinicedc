from __future__ import annotations

from copy import copy

from django.db.models.constants import LOOKUP_SEP
from django_crypto_fields.utils import get_encrypted_fields
from edc_auth.auth_objects import PII, PII_VIEW


class ModelAdminProtectPiiMixin:
    """Removes encrypted fields from changelist.

    Place first in the MRO.

    Removes encrypted fields and methods returning encrypted
    field values from changelist for users not in PII / PII_VIEW
    groups.

    IMPORTANT: If you declare a method which returns PII to
    the changelist, add the method name to `extra_pii_attrs`.
    """

    extra_pii_attrs: list[str] | None = []

    def get_extra_pii_attrs(self) -> list[str | tuple[str, str]]:
        return self.extra_pii_attrs or []

    def get_encrypted_fields(self) -> list[str]:
        encrypted_fields = [f.name for f in get_encrypted_fields(self.model)]
        encrypted_fields.extend(self.get_extra_pii_attrs())
        encrypted_fields = list(set(encrypted_fields))
        return encrypted_fields

    def get_list_display(self, request) -> tuple[str]:
        list_display = super().get_list_display(request)
        if not request.user.groups.filter(name__in=[PII, PII_VIEW]).exists():
            # TODO: search replace from list_display if extra_pii_attr has tuple
            list_display = [f for f in list_display if f not in self.get_encrypted_fields()]
            list_display = tuple(list_display)
        return list_display

    def get_list_display_links(self, request, list_display) -> list[str] | None:
        list_display_links = super().get_list_display_links(request, list_display)
        if not request.user.groups.filter(name__in=[PII, PII_VIEW]).exists():
            return None
        return list_display_links

    def get_search_fields(self, request) -> tuple[str]:
        search_fields = super().get_search_fields(request)
        if search_fields:
            search_fields = list(search_fields)
            if not request.user.groups.filter(name__in=[PII, PII_VIEW]).exists():
                for field in search_fields:
                    if field.split(LOOKUP_SEP)[0] in self.get_encrypted_fields():
                        search_fields.remove(field)
            else:
                encrypted_fields = self.get_encrypted_fields()
                for field in copy(search_fields):
                    if field.split(LOOKUP_SEP)[0] in encrypted_fields:
                        try:
                            field.split(LOOKUP_SEP)[1]
                        except IndexError:
                            index = search_fields.index(field)
                            search_fields[index] = f"{field}{LOOKUP_SEP}exact"
            search_fields = tuple(search_fields)
        return search_fields
