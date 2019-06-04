from django.contrib import admin
from django.contrib.admin.decorators import register
from django_audit_fields.admin import audit_fieldset_tuple
from edc_action_item.fieldsets import action_fieldset_tuple
from edc_model_admin.inlines import StackedInlineMixin
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin
from edc_model_admin import SimpleHistoryAdmin

from ..admin_site import edc_data_manager_admin
from ..forms import DataManagerQueryForm
from ..models import DataManagerQuery, Query

from .query_admin import QueryAdminInline


@register(DataManagerQuery, site=edc_data_manager_admin)
class DataManagerQueryAdmin(ModelAdminSubjectDashboardMixin, SimpleHistoryAdmin):

    show_cancel = False

    form = DataManagerQueryForm

    radio_fields = {"status": admin.VERTICAL}

    autocomplete_fields = ["registered_subject", "sender", "recipients"]

    inlines = [QueryAdminInline]

    list_display = (
        "title",
        "subject",
        "report_datetime",
        "dashboard",
        "status",
        "dm",
        "to",
        "reference",
    )

    list_filter = ("status", "report_datetime")

    search_fields = (
        "title",
        "action_identifier",
        "sender__first_name",
        "sender__last_name",
        "sender__email",
        "sender__username",
        "registered_subject__subject_identifier",
        "recipients_as_list",
    )

    fieldsets = (
        [
            None,
            {
                "fields": (
                    "title",
                    "report_datetime",
                    "registered_subject",
                    "sender",
                    "recipients",
                )
            },
        ],
        ["Comments", {"fields": ("comment", "response")}],
        ["Status", {"fields": ("status",)}],
        action_fieldset_tuple,
        audit_fieldset_tuple,
    )

    def dm(self, obj):
        return obj.sender.first_name

    def to(self, obj):
        return ", ".join(
            [f"{o.first_name} {o.last_name}" for o in obj.recipients.all()]
        )

    def subject(self, obj):
        return obj.registered_subject

    def reference(self, obj):
        return obj.action_identifier[-9:]
