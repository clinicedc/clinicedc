from django.contrib import admin
from django_audit_fields.admin import ModelAdminAuditFieldsMixin, audit_fieldset_tuple
from edc_model_admin.history import SimpleHistoryAdmin
from edc_model_admin.mixins import TemplatesModelAdminMixin

from ..admin_site import edc_action_item_admin
from ..forms import ActionTypeForm
from ..models import ActionType


@admin.register(ActionType, site=edc_action_item_admin)
class ActionTypeAdmin(
    TemplatesModelAdminMixin, ModelAdminAuditFieldsMixin, SimpleHistoryAdmin
):
    date_hierarchy = "modified"
    empty_value_display = "-"
    list_per_page = 10
    show_cancel = True

    form = ActionTypeForm

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "display_name",
                    "reference_model",
                    "related_reference_model",
                    "show_on_dashboard",
                    "create_by_action",
                    "create_by_user",
                    "instructions",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "name",
        "display_name",
        "reference_model",
        "related_reference_model",
        "show_on_dashboard",
        "create_by_action",
        "create_by_user",
    )

    list_filter = (
        "create_by_action",
        "create_by_user",
        "show_on_dashboard",
        "reference_model",
        "related_reference_model",
    )

    search_fields = (
        "name",
        "display_name",
        "reference_model",
        "related_reference_model",
    )

    def get_readonly_fields(self, request, obj=None) -> tuple:
        readonly_fields = super().get_readonly_fields(request, obj=obj)
        return readonly_fields + (
            "name",
            "display_name",
            "reference_model",
            "related_reference_model",
            "show_on_dashboard",
            "create_by_action",
            "create_by_user",
            "instructions",
        )
