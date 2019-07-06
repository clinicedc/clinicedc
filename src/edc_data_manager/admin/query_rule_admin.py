from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.decorators import register
from django.urls.base import reverse
from django.utils.safestring import mark_safe
from django_audit_fields.admin import ModelAdminAuditFieldsMixin, audit_fieldset_tuple
from edc_model_admin.model_admin_simple_history import SimpleHistoryAdmin
from edc_utils import get_utcnow, formatted_datetime

from ..admin_site import edc_data_manager_admin
from ..models import CrfQueryRule, RequisitionQueryRule, get_rule_handler_choices


class CrfQueryRuleForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = CrfQueryRule


class RequisitionQueryRuleForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = RequisitionQueryRule


def update_crf_query_rules_action(modeladmin, request, queryset):

    if queryset:
        from edc_data_manager.tasks import update_crf_query_rules_task

        if settings.CELERY_ENABLED:
            update_crf_query_rules_task.delay(pks=[o.pk for o in queryset])
            dte = get_utcnow()
            taskresult_url = reverse(
                "admin:django_celery_results_taskresult_changelist"
            )
            msg = mark_safe(
                f"Updating data queries in the background. "
                f"Started at {formatted_datetime(dte)}. "
                f"An updated digest will be email upon completion. "
                f'You may also check in <a href="{taskresult_url}?'
                f'task_name=update_crf_query_rules">task results</A>. '
            )
        else:
            results = update_crf_query_rules_task(pks=[o.pk for o in queryset])
            msg = mark_safe(
                f"Done updating data queries. Created {results.get('created')}, "
                f"resolved {results.get('resolved')}."
            )
        messages.add_message(request, messages.SUCCESS, msg)


update_crf_query_rules_action.short_description = (
    "Create or update automated CRF queries"
)


class QueryRuleModelAdminMixin:
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "rule_handler_name":
            kwargs["choices"] = get_rule_handler_choices()
        return super().formfield_for_choice_field(db_field, request, **kwargs)

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

    form = CrfQueryRuleForm

    actions = [update_crf_query_rules_action]

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
                    "rule_handler_name",
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

    form = RequisitionQueryRuleForm

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
