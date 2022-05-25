from django.contrib import admin
from django.utils.safestring import mark_safe
from edc_document_status.fieldsets import document_status_fieldset_tuple
from edc_document_status.modeladmin_mixins import DocumentStatusModelAdminMixin
from edc_model_admin import SimpleHistoryAdmin, audit_fieldset_tuple
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin
from edc_visit_schedule import OnScheduleError, off_schedule_or_raise
from edc_visit_schedule.fieldsets import (
    visit_schedule_fields,
    visit_schedule_fieldset_tuple,
)

from .admin_actions import appointment_mark_as_done, appointment_mark_as_new
from .admin_site import edc_appointment_admin
from .constants import NEW_APPT
from .forms import AppointmentForm
from .models import Appointment


@admin.register(Appointment, site=edc_appointment_admin)
class AppointmentAdmin(
    ModelAdminSubjectDashboardMixin, DocumentStatusModelAdminMixin, SimpleHistoryAdmin
):

    show_cancel = True
    form = AppointmentForm
    actions = [appointment_mark_as_done, appointment_mark_as_new]
    date_hierarchy = "appt_datetime"
    list_display = (
        "subject_identifier",
        "__str__",
        "dashboard",
        "appt_datetime",
        "appt_type",
        "appt_status",
        "appt_timing",
        "schedule_name",
    )
    list_filter = ("visit_code", "appt_datetime", "appt_type", "appt_status", "appt_timing")

    additional_instructions = mark_safe(
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

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj=obj)
        return (
            list(readonly_fields)
            + list(visit_schedule_fields)
            + [
                "subject_identifier",
                "timepoint",
                "timepoint_datetime",
                "visit_code_sequence",
                "facility_name",
            ]
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
