from django.contrib import admin
from django.urls.base import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django_audit_fields.admin import audit_fieldset_tuple
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin
from edc_model_admin.history import SimpleHistoryAdmin
from edc_sites.admin import SiteModelAdminMixin

from ..admin_site import edc_action_item_admin
from ..forms import ActionItemForm
from ..models import ActionItem


@admin.register(ActionItem, site=edc_action_item_admin)
class ActionItemAdmin(
    SiteModelAdminMixin,
    ModelAdminSubjectDashboardMixin,
    SimpleHistoryAdmin,
):
    form = ActionItemForm

    save_on_top = True
    show_cancel = True

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "action_identifier",
                    "subject_identifier",
                    "report_datetime",
                    "action_type",
                    "priority",
                    "status",
                    "instructions",
                )
            },
        ),
        (
            "Reference Information",
            {
                "classes": ("collapse",),
                "fields": (
                    "related_action_item",
                    "parent_action_item",
                    "auto_created",
                    "auto_created_comment",
                ),
            },
        ),
        (
            "Email",
            {"classes": ("collapse",), "fields": ("emailed", "emailed_datetime")},
        ),
        audit_fieldset_tuple,
    )

    radio_fields = {"status": admin.VERTICAL}

    list_display = (
        "identifier",
        "dashboard",
        "subject_identifier",
        "status",
        "action_type",
        "priority",
        "emailed",
        "parent_action",
        "related_action_item",
        "created",
    )

    list_filter = (
        "status",
        "priority",
        "emailed",
        "report_datetime",
        "action_type__name",
    )

    search_fields = (
        "subject_identifier",
        "action_identifier",
        "related_action_item__action_identifier",
        "parent_action_item__action_identifier",
        "action_type__name",
        "action_type__display_name",
        "id",
    )

    ordering = ("action_type__display_name",)

    date_hierarchy = "created"

    additional_instructions = format_html(
        "<B><U>Important:</U> This form is usually auto-filled based on a clinical event. "
        "DO NOT DELETE unless you know what you are doing.</B>"
    )

    def get_readonly_fields(self, request, obj=None) -> tuple:
        readonly_fields = super().get_readonly_fields(request, obj=obj)
        readonly_fields = readonly_fields + (
            "action_identifier",
            "instructions",
            "auto_created",
            "auto_created_comment",
            "reference_model",
            "emailed",
            "emailed_datetime",
            "related_action_item",
            "parent_action_item",
        )
        if obj:
            readonly_fields = readonly_fields + (
                "subject_identifier",
                "report_datetime",
                "action_type",
            )
        return readonly_fields

    @staticmethod
    def parent_action(obj):
        """Returns an url to the parent action item
        for display in admin.
        """
        if obj.parent_action_item:
            url_name = "_".join(obj._meta.label_lower.split("."))
            namespace = edc_action_item_admin.name
            url = reverse(f"{namespace}:{url_name}_changelist")
            return format_html(
                '<a data-toggle="tooltip" title="go to parent action item" '
                'href="{}?q={}">{}</a>',
                mark_safe(url),  # nosec B308, B703
                mark_safe(obj.parent_action_item.action_identifier),  # nosec B308, B703
                mark_safe(obj.parent_action_item.identifier),  # nosec B308, B703
            )
        return None

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "action_type":
            kwargs["queryset"] = db_field.related_model.objects.filter(create_by_user=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
