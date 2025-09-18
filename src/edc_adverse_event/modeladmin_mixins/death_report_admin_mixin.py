from __future__ import annotations

from django.contrib import admin
from django.contrib.admin import display
from django.template.loader import render_to_string
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from django_audit_fields.admin import audit_fieldset_tuple

from edc_action_item.fieldsets import action_fieldset_tuple
from edc_action_item.modeladmin_mixins import ActionItemModelAdminMixin
from edc_constants.constants import CANCELLED, OTHER
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin
from edc_model_admin.list_filters import ReportDateListFilter
from edc_pdf_reports.admin import PdfButtonModelAdminMixin, print_selected_to_pdf_action

from ..utils import get_adverse_event_app_label
from .list_filters import CauseOfDeathListFilter, DeathDateListFilter


@admin.action(permissions=["view"], description="Print Death Reports as PDF")
def print_to_pdf_action(modeladmin, request, queryset):
    return print_selected_to_pdf_action(modeladmin, request, queryset)


class DeathReportModelAdminMixin(
    PdfButtonModelAdminMixin, ModelAdminSubjectDashboardMixin, ActionItemModelAdminMixin
):
    form = None

    add_form_template: str = "edc_adverse_event/admin/change_form.html"
    change_list_template = "edc_adverse_event/admin/change_list.html"
    change_form_template = "edc_adverse_event/admin/change_form.html"

    ordering = ("-report_datetime",)

    actions = [print_to_pdf_action]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "subject_identifier",
                    "report_datetime",
                    "death_datetime",
                    "study_day",
                    "death_as_inpatient",
                )
            },
        ),
        (
            "Opinion of Local Study Doctor",
            {"fields": ("cause_of_death", "cause_of_death_other", "narrative")},
        ),
        action_fieldset_tuple,
        audit_fieldset_tuple,
    )

    radio_fields = {
        "death_as_inpatient": admin.VERTICAL,
        "cause_of_death": admin.VERTICAL,
    }

    def get_search_fields(self, request) -> tuple[str, ...]:
        search_fields = super().get_search_fields(request)
        custom_fields = ("subject_identifier", "action_identifier")
        return tuple(set(search_fields + custom_fields))

    def get_list_display(self, request) -> tuple[str, ...]:
        list_display = super().get_list_display(request)
        custom_fields = (
            "subject_identifier",
            "dashboard",
            "pdf_button",
            "ae_button",
            "tmg_button",
            "report_datetime_with_ago",
            "death_datetime_with_ago",
            "cause_of_death_column",
            "action_item_column",
            "parent_action_item_column",
            "related_action_item_column",
        )
        return custom_fields + tuple(
            f for f in list_display if f not in custom_fields and f != "__str__"
        )

    def get_list_filter(self, request) -> tuple[str, ...]:
        list_filter = super().get_list_filter(request)
        custom_fields = (
            ReportDateListFilter,
            DeathDateListFilter,
            CauseOfDeathListFilter,
        )
        return custom_fields + tuple(f for f in list_filter if f not in custom_fields)

    @display(
        description="Cause of death",
        ordering="cause_of_death__display_name",
    )
    def cause_of_death_column(self, obj):
        cause_of_death = getattr(obj.cause_of_death, "name", obj.cause_of_death)
        if cause_of_death == OTHER:
            cause_of_death = f"Other: {obj.cause_of_death_other}"
        else:
            cause_of_death = getattr(obj.cause_of_death, "display_name", obj.cause_of_death)
        return cause_of_death

    @display(description="Report date", ordering="report_datetime")
    def report_datetime_with_ago(self, obj=None):
        return render_to_string(
            "edc_adverse_event/datetime_with_ago.html",
            dict(utc_date=timezone.now().date, report_datetime=obj.report_datetime),
        )

    @display(description="Death date", ordering="death_datetime")
    def death_datetime_with_ago(self, obj=None):
        return render_to_string(
            "edc_adverse_event/datetime_with_ago.html",
            dict(utc_date=timezone.now().date, report_datetime=obj.death_datetime),
        )

    @display(description="Action item", ordering="action_identifier")
    def action_item_column(self, obj):
        return self.get_action_item_column(obj.action_item, as_button=False)

    @display(description="Parent action", ordering="parent_action_item__action_identifier")
    def parent_action_item_column(self, obj):
        return self.get_action_item_column(obj.parent_action_item, as_button=True)

    @display(description="Related action", ordering="related_action_item__action_identifier")
    def related_action_item_column(self, obj):
        return self.get_action_item_column(obj.related_action_item, as_button=True)

    @staticmethod
    def get_action_item_column(action_item, as_button: bool | None = None):
        if action_item:
            verbose_name = action_item.reference_model_cls._meta.verbose_name
            app_label = action_item.reference_model_cls._meta.app_label
            model_name = action_item.reference_model_cls._meta.model_name
            url_name = (
                f"{get_adverse_event_app_label()}_admin:{app_label}_{model_name}_changelist"
            )
            url = reverse(url_name)
            return render_to_string(
                "edc_adverse_event/action_item_column.html",
                dict(
                    q=action_item.action_identifier,
                    url=url,
                    action_identifier=action_item.action_identifier[-9:],
                    title=verbose_name,
                    status=action_item.status,
                    status_display=action_item.get_status_display(),
                    CANCELLED=CANCELLED,
                    as_button=as_button,
                ),
            )
        return None

    @display(description="AE")
    def ae_button(self, obj):
        context = dict(
            subject_identifier=obj.subject_identifier,
            changelist_url=reverse(
                f"{self.admin_site.name}:{obj._meta.app_label}_aeinitial_changelist"
            ),
        )
        return render_to_string(
            template_name="edc_adverse_event/ae_button.html", context=context
        )

    @display(description="TMG")
    def tmg_button(self, obj):
        try:
            changelist_url = reverse(
                f"{self.admin_site.name}:{obj._meta.app_label}_deathreporttmg_changelist"
            )
        except NoReverseMatch:
            changelist_url = None
        context = dict(
            subject_identifier=obj.subject_identifier,
            changelist_url=changelist_url,
        )
        return render_to_string(
            template_name="edc_adverse_event/tmg_button.html", context=context
        )
