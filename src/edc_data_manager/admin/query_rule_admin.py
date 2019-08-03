from django import forms
from django.contrib import admin
from django.contrib.admin.decorators import register
from django_audit_fields.admin import ModelAdminAuditFieldsMixin, audit_fieldset_tuple
from edc_model_admin.model_admin_simple_history import SimpleHistoryAdmin

from ..admin_site import edc_data_manager_admin
from ..forms import QueryRuleForm
from ..models import QueryRule, get_rule_handler_choices
from .actions import (
    update_query_rules_action,
    toggle_active_flag,
    copy_query_rule_action,
)


class QueryRuleModelAdminMixin:

    readonly_fields = ("reference",)

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "rule_handler_name":
            kwargs["choices"] = get_rule_handler_choices()
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def form_name(self, obj=None):
        data_dictionaries = [
            dd for dd in obj.data_dictionaries.all().order_by("number")
        ]
        return ", ".join(list(set([dd.model_verbose_name for dd in data_dictionaries])))

    def questions(self, obj=None):
        numbers = [
            str(dd.number) for dd in obj.data_dictionaries.all().order_by("number")
        ]
        return ", ".join(numbers)

    def field_names(self, obj=None):
        fields = [
            dd.field_name for dd in obj.data_dictionaries.all().order_by("field_name")
        ]
        return ", ".join(fields)

    def timepoints(self, obj=None):
        fields = [v.visit_code for v in obj.visit_schedule.all().order_by("timepoint")]
        return ", ".join(fields)

    def query_timing(self, obj=None):
        return (
            f"{obj.timing} {obj.get_timing_units_display()} "
            f"from {obj.reference_date}"
        )

    def requisition(self, obj=None):
        return obj.requisition_panel

    def rule(self, obj=None):
        return obj.rule_handler_name


@register(QueryRule, site=edc_data_manager_admin)
class QueryRuleAdmin(
    QueryRuleModelAdminMixin, ModelAdminAuditFieldsMixin, SimpleHistoryAdmin
):

    form = QueryRuleForm

    actions = [update_query_rules_action, toggle_active_flag, copy_query_rule_action]

    list_display = (
        "title",
        "active",
        "form_name",
        "questions",
        "field_names",
        "requisition",
        "timepoints",
        "query_timing",
        "query_priority",
        "rule",
    )

    list_filter = ("query_priority", "active", "rule_handler_name")

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
                    "rule_handler_name",
                    "sender",
                    "active",
                    "comment",
                )
            },
        ],
        ["Reference", {"classes": ("collapse",), "fields": ("reference",)}],
        audit_fieldset_tuple,
    )
