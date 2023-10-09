from __future__ import annotations

import calendar
from typing import TYPE_CHECKING, Any

from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext as _
from django_audit_fields.admin import audit_fieldset_tuple
from edc_constants.constants import NOT_APPLICABLE
from edc_document_status.fieldsets import document_status_fieldset_tuple
from edc_document_status.modeladmin_mixins import DocumentStatusModelAdminMixin
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin
from edc_model_admin.history import SimpleHistoryAdmin
from edc_sites.admin import SiteModelAdminMixin
from edc_visit_schedule.exceptions import OnScheduleError
from edc_visit_schedule.fieldsets import (
    visit_schedule_fields,
    visit_schedule_fieldset_tuple,
)
from edc_visit_schedule.utils import off_schedule_or_raise

from ..admin_site import edc_appointment_admin
from ..choices import APPT_STATUS, APPT_TIMING, DEFAULT_APPT_REASON_CHOICES
from ..constants import NEW_APPT, SKIPPED_APPT
from ..forms import AppointmentForm
from ..models import Appointment, AppointmentType
from ..utils import get_allow_skipped_appt_using
from .actions import appointment_mark_as_done, appointment_mark_as_new
from .list_filters import AppointmentListFilter

if TYPE_CHECKING:
    from django.db.models import QuerySet


@admin.register(Appointment, site=edc_appointment_admin)
class AppointmentAdmin(
    SiteModelAdminMixin,
    ModelAdminSubjectDashboardMixin,
    DocumentStatusModelAdminMixin,
    SimpleHistoryAdmin,
):
    show_cancel = True
    form = AppointmentForm
    actions = [appointment_mark_as_done, appointment_mark_as_new]
    date_hierarchy = "appt_datetime"
    list_display = (
        "appointment_subject",
        "full_visit_code",
        "appt_actions",
        "appointment_date",
        "appointment_type",
        "appt_status",
        "timing",
        "schedule_name",
    )
    list_filter = (
        AppointmentListFilter,
        "appt_status",
        "visit_code",
        "appt_type",
        "appt_timing",
    )

    additional_instructions = format_html(
        "To start or continue to edit FORMS for this subject, change the "
        'appointment status below to "In Progress" and click SAVE. <BR>'
        "<i>Note: You may only edit one appointment at a time. "
        "Before you move to another appointment, change the appointment "
        'status below to "Incomplete or "Done".</i>'
    )

    fieldsets = (
        (
            None,
            (
                {
                    "fields": (
                        "subject_identifier",
                        "appt_datetime",
                        "appt_type",
                        "appt_status",
                        "appt_reason",
                        "appt_timing",
                        "comment",
                    )
                }
            ),
        ),
        (
            "Timepoint",
            (
                {
                    "classes": ("collapse",),
                    "fields": (
                        "timepoint",
                        "timepoint_datetime",
                        "visit_code_sequence",
                        "facility_name",
                    ),
                }
            ),
        ),
        document_status_fieldset_tuple,
        visit_schedule_fieldset_tuple,
        audit_fieldset_tuple,
    )

    radio_fields = {
        "appt_type": admin.VERTICAL,
        "appt_status": admin.VERTICAL,
        "appt_reason": admin.VERTICAL,
        "appt_timing": admin.VERTICAL,
    }

    search_fields = ("subject_identifier",)

    def get_readonly_fields(self, request, obj=None) -> tuple:
        readonly_fields = super().get_readonly_fields(request, obj=obj)
        return (
            readonly_fields
            + visit_schedule_fields
            + (
                "subject_identifier",
                "timepoint",
                "timepoint_datetime",
                "visit_code_sequence",
                "facility_name",
            )
        )

    def has_delete_permission(self, request, obj=None):
        """Override to remove delete permissions if OnSchedule
        and visit_code_sequence == 0.

        See `edc_visit_schedule.off_schedule_or_raise()`
        """
        has_delete_permission = super().has_delete_permission(request, obj=obj)
        if has_delete_permission and obj:
            if obj.visit_code_sequence == 0 or (
                obj.visit_code_sequence != 0 and obj.appt_status != NEW_APPT
            ):
                try:
                    off_schedule_or_raise(
                        subject_identifier=obj.subject_identifier,
                        report_datetime=obj.appt_datetime,
                        visit_schedule_name=obj.visit_schedule_name,
                        schedule_name=obj.schedule_name,
                    )
                except OnScheduleError:
                    has_delete_permission = False
        return has_delete_permission

    @admin.display(description="Timing", ordering="appt_timing")
    def timing(self, obj=None):
        if obj.appt_status == NEW_APPT:
            return None
        return obj.get_appt_timing_display()

    @admin.display(description="Visit", ordering="visit_code")
    def full_visit_code(self, obj=None):
        """Returns a string of visit_code.visit_code_sequence"""
        return f"{obj.visit_code}.{obj.visit_code_sequence}"

    @admin.display(description="Appt. Date", ordering="appt_datetime")
    def appointment_date(self, obj=None):
        """Returns a string of visit_code.visit_code_sequence"""
        return f"{obj.appt_datetime.date()} {calendar.day_abbr[obj.appt_datetime.weekday()]}"

    @admin.display(description="Type", ordering="appt_type")
    def appointment_type(self, obj=None):
        """Returns a string of visit_code.visit_code_sequence"""
        return obj.get_appt_type_display()

    @admin.display(description="Subject", ordering="subject_identifier")
    def appointment_subject(self, obj=None):
        return obj.subject_identifier

    @admin.display(description="Options")
    def appt_actions(self, obj=None):
        dashboard_url = reverse(
            self.get_subject_dashboard_url_name(),
            kwargs=self.get_subject_dashboard_url_kwargs(obj),
        )
        call_url = "#"
        context = dict(
            dashboard_title=_("Go to subject's dashboard"),
            dashboard_url=dashboard_url,
            call_title=_("Call subject"),
            call_url=call_url,
        )
        return render_to_string("button.html", context=context)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "appt_type":
            kwargs["queryset"] = self.get_appt_type_queryset(request)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "appt_reason":
            kwargs["choices"] = self.get_appt_reason_choices(request)
        if db_field.name == "appt_status":
            kwargs["choices"] = self.get_appt_status_choices(request)
        if db_field.name == "appt_timing":
            kwargs["choices"] = self.get_appt_timing_choices(request)
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def get_appt_type_queryset(self, request) -> QuerySet:
        if not self.allow_skipped_appointments(request):
            return AppointmentType.objects.exclude(name=NOT_APPLICABLE).order_by(
                "display_index"
            )
        return AppointmentType.objects.all().order_by("display_index")

    def get_appt_reason_choices(self, request) -> tuple[Any, ...]:
        """Return a choices tuple.

        Important: left side of the tuple MUST have the default
        values of SCHEDULED_APPT and UNSCHEDULED_APPT.
        """
        return DEFAULT_APPT_REASON_CHOICES

    def get_appt_status_choices(self, request) -> tuple[Any, ...]:
        if not self.allow_skipped_appointments(request):
            return tuple([tpl for tpl in APPT_STATUS if tpl[0] != SKIPPED_APPT])
        return APPT_STATUS

    def get_appt_timing_choices(self, request) -> tuple[Any, ...]:
        if not self.allow_skipped_appointments(request):
            return tuple([tpl for tpl in APPT_TIMING if tpl[0] != NOT_APPLICABLE])
        return APPT_TIMING

    def allow_skipped_appointments(self, request) -> bool:
        """Returns True if settings.EDC_APPOINTMENT_ALLOW_SKIPPED_APPT_USING
        has value.

        Relates to use of `SKIPPED_APPT` feature.
        """
        return True if get_allow_skipped_appt_using() else False
