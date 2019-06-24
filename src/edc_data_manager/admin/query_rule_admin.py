from django.contrib import admin
from django.contrib.admin.decorators import register
from django_audit_fields.admin import ModelAdminAuditFieldsMixin, audit_fieldset_tuple
from edc_model_admin.model_admin_simple_history import SimpleHistoryAdmin

from ..rule import update_query_rules_action
from ..admin_site import edc_data_manager_admin
from ..models import CrfQueryRule, RequisitionQueryRule


class QueryRuleModelAdminMixin:
    def form_name(self, obj=None):
        data_dictionaries = [
            dd for dd in obj.data_dictionaries.all().order_by("number")
        ]
        return ", ".join(list(set([dd.model_verbose_name for dd in data_dictionaries])))

    def question_numbers(self, obj=None):
        numbers = [
            str(dd.number) for dd in obj.data_dictionaries.all().order_by("number")
        ]
        return ", ".join(numbers)

    def field_names(self, obj=None):
        fields = [
            dd.field_name for dd in obj.data_dictionaries.all().order_by("field_name")
        ]
        return ", ".join(fields)

    def query_timing(self, obj=None):
        return (
            f"{obj.timing} {obj.get_timing_units_display()} "
            f"from {obj.reference_date}"
        )


@register(CrfQueryRule, site=edc_data_manager_admin)
class CrfQueryRuleAdmin(
    QueryRuleModelAdminMixin, ModelAdminAuditFieldsMixin, SimpleHistoryAdmin
):

    actions = [update_query_rules_action]

    list_display = (
        "title",
        "form_name",
        "question_numbers",
        "field_names",
        "requisition_panel",
        "query_timing",
        "query_priority",
        "active",
    )

    list_filter = ("query_priority", "active")

    radio_fields = {
        "reference_date": admin.VERTICAL,
        "timing_units": admin.VERTICAL,
        "query_priority": admin.VERTICAL,
    }

    autocomplete_fields = [
        "sender",
        "visit_schedule",
        "visit_schedule_exclude",
        "data_dictionaries",
        "requisition_panel",
        "recipients",
    ]

    fieldsets = (
        [
            None,
            {
                "fields": (
                    "title",
                    "data_dictionaries",
                    "requisition_panel",
                    "visit_schedule",
                    "visit_schedule_exclude",
                    "query_text",
                    "query_priority",
                    "recipients",
                    ("timing", "timing_units"),
                    "sender",
                    "active",
                    "comment",
                )
            },
        ],
        audit_fieldset_tuple,
    )


@register(RequisitionQueryRule, site=edc_data_manager_admin)
class RequisitionQueryRuleAdmin(
    QueryRuleModelAdminMixin, ModelAdminAuditFieldsMixin, SimpleHistoryAdmin
):

    list_display = (
        "title",
        "requisition_panel",
        "query_timing",
        "query_priority",
        "active",
    )

    list_filter = ("query_priority", "active")

    radio_fields = {"timing_units": admin.VERTICAL, "query_priority": admin.VERTICAL}

    autocomplete_fields = [
        "sender",
        "visit_schedule",
        "visit_schedule_exclude",
        "requisition_panel",
    ]

    fieldsets = (
        [
            None,
            {
                "fields": (
                    "title",
                    "requisition_panel",
                    "visit_schedule",
                    "visit_schedule_exclude",
                    "query_text",
                    "query_priority",
                    "recipients",
                    ("timing", "timing_units"),
                    "active",
                    "comment",
                )
            },
        ],
        audit_fieldset_tuple,
    )
