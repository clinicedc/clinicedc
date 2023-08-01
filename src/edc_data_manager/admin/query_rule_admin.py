from django.contrib import admin
from django.contrib.admin.decorators import register
from django_audit_fields.admin import ModelAdminAuditFieldsMixin, audit_fieldset_tuple
from django_revision.modeladmin_mixin import ModelAdminRevisionMixin
from edc_model_admin.history import SimpleHistoryAdmin
from edc_model_admin.mixins import (
    ModelAdminFormAutoNumberMixin,
    ModelAdminFormInstructionsMixin,
    ModelAdminInstitutionMixin,
    ModelAdminNextUrlRedirectMixin,
    ModelAdminRedirectOnDeleteMixin,
    TemplatesModelAdminMixin,
)

from ..admin_site import edc_data_manager_admin
from ..forms import QueryRuleForm
from ..models import QueryRule, get_rule_handler_choices
from .actions import (
    copy_query_rule_action,
    toggle_active_flag,
    update_query_rules_action,
)


class QueryRuleModelAdminMixin:
    readonly_fields = ("reference",)

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "rule_handler_name":
            kwargs["choices"] = get_rule_handler_choices()
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    @staticmethod
    def form_name(obj=None):
        data_dictionaries = [dd for dd in obj.data_dictionaries.all().order_by("number")]
        return ", ".join(list(set([dd.model_verbose_name for dd in data_dictionaries])))

    @staticmethod
    def questions(obj=None):
        numbers = [str(dd.number) for dd in obj.data_dictionaries.all().order_by("number")]
        return ", ".join(numbers)

    @staticmethod
    def field_names(obj=None):
        fields = [dd.field_name for dd in obj.data_dictionaries.all().order_by("field_name")]
        return ", ".join(fields)

    @staticmethod
    def timepoints(obj=None):
        fields = [v.visit_code for v in obj.visit_schedule.all().order_by("timepoint")]
        return ", ".join(fields)

    @staticmethod
    def query_timing(obj=None):
        return f"{obj.timing} {obj.get_timing_units_display()} " f"from {obj.reference_date}"

    @staticmethod
    def requisition(obj=None):
        return obj.requisition_panel

    @staticmethod
    def rule(obj=None):
        return obj.rule_handler_name


@register(QueryRule, site=edc_data_manager_admin)
class QueryRuleAdmin(
    QueryRuleModelAdminMixin,
    TemplatesModelAdminMixin,
    ModelAdminNextUrlRedirectMixin,  # add
    ModelAdminFormInstructionsMixin,  # add
    ModelAdminFormAutoNumberMixin,
    ModelAdminRevisionMixin,  # add
    ModelAdminInstitutionMixin,  # add
    ModelAdminRedirectOnDeleteMixin,
    ModelAdminAuditFieldsMixin,
    SimpleHistoryAdmin,
):
    form = QueryRuleForm

    actions = (
        update_query_rules_action,
        toggle_active_flag,
        copy_query_rule_action,
    )

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
