from typing import Tuple

from django.contrib import admin
from django_audit_fields import audit_fieldset_tuple
from edc_model import DEFAULT_BASE_FIELDS

from .admin_site import edc_identifier_admin
from .models import IdentifierModel


@admin.register(IdentifierModel, site=edc_identifier_admin)
class IdentifierModelAdmin(admin.ModelAdmin):
    fieldsets = (
        [
            None,
            {
                "fields": (
                    "identifier",
                    "protocol_number",
                    "name",
                    "subject_identifier",
                    "site",
                    "model",
                    "sequence_number",
                    "identifier_type",
                    "linked_identifier",
                    "device_id",
                    "identifier_prefix",
                )
            },
        ],
        audit_fieldset_tuple,
    )

    list_display = (
        "identifier",
        "subject_identifier",
        "identifier_type",
        "site",
        "linked_identifier",
        "created",
        "user_created",
        "hostname_created",
    )
    list_filter = (
        "identifier_type",
        "name",
        "site",
        "device_id",
        "created",
        "user_created",
    )
    search_fields = ("identifier", "subject_identifier", "linked_identifier")

    def get_readonly_fields(self, request, obj=None) -> Tuple[str, ...]:
        return (
            "identifier",
            "protocol_number",
            "subject_identifier",
            "name",
            "site",
            "model",
            "sequence_number",
            "identifier_type",
            "linked_identifier",
            "device_id",
            "identifier_prefix",
        ) + tuple(DEFAULT_BASE_FIELDS)
