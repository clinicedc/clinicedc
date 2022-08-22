from typing import Any, Tuple

from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple
from edc_appointment.models import Appointment
from edc_constants.constants import OTHER
from edc_document_status.fieldsets import document_status_fieldset_tuple
from edc_document_status.modeladmin_mixins import DocumentStatusModelAdminMixin
from edc_visit_schedule.fieldsets import (
    visit_schedule_fields,
    visit_schedule_fieldset_tuple,
)

from ..constants import SCHEDULED, UNSCHEDULED


class VisitModelAdminMixin(DocumentStatusModelAdminMixin):

    """ModelAdmin subclass for models with a ForeignKey to
    'appointment', such as your visit model(s).

    In the child ModelAdmin class set the following attributes,
    for example:

        visit_attr = 'maternal_visit'
        dashboard_type = 'maternal'
    """

    date_hierarchy = "report_datetime"

    fieldsets = (
        (
            None,
            {
                "fields": [
                    "appointment",
                    "report_datetime",
                    "reason",
                    "reason_missed",
                    "reason_unscheduled",
                    "reason_unscheduled_other",
                    "info_source",
                    "info_source_other",
                    "comments",
                ]
            },
        ),
        visit_schedule_fieldset_tuple,
        document_status_fieldset_tuple,
        audit_fieldset_tuple,
    )

    radio_fields = {
        "reason": admin.VERTICAL,
        "reason_unscheduled": admin.VERTICAL,
        "reason_missed": admin.VERTICAL,
        "info_source": admin.VERTICAL,
        "require_crfs": admin.VERTICAL,
    }

    search_fields = (
        "id",
        "reason",
        "appointment__visit_code",
        "appointment__subject_identifier",
    )

    @staticmethod
    def subject_identifier(obj=None) -> str:
        return obj.appointment.subject_identifier

    @staticmethod
    def visit_reason(obj=None) -> str:
        if obj.reason != UNSCHEDULED:
            visit_reason = obj.get_reason_display()
        else:
            if obj.reason_unscheduled == OTHER:
                visit_reason = obj.reason_unscheduled_other
            else:
                visit_reason = obj.get_reason_unscheduled_display()
        return visit_reason

    @staticmethod
    def status(obj=None) -> str:
        return obj.study_status

    @staticmethod
    def scheduled_data(obj=None) -> str:
        return obj.get_require_crfs_display()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        db = kwargs.get("using")
        if db_field.name == "appointment" and request.GET.get("appointment"):
            kwargs["queryset"] = db_field.related_model._default_manager.using(db).filter(
                pk=request.GET.get("appointment")
            )
        else:
            kwargs["queryset"] = db_field.related_model._default_manager.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_list_display(self, request) -> Tuple[str, ...]:
        list_display = super().get_list_display(request)
        custom_fields = (
            "appointment",
            "subject_identifier",
            "report_datetime",
            "visit_reason",
            "status",
            "scheduled_data",
        )
        return custom_fields + tuple(f for f in list_display if f not in custom_fields)

    def get_list_filter(self, request) -> Tuple[str, ...]:
        list_filter = super().get_list_filter(request)
        custom_fields = (
            "report_datetime",
            "appointment__visit_code",
            "appointment__visit_code_sequence",
            "reason",
            "require_crfs",
        )
        return custom_fields + tuple(f for f in list_filter if f not in custom_fields)

    def get_readonly_fields(self, request, obj=None) -> Tuple[str, ...]:
        readonly_fields = super().get_readonly_fields(request, obj=obj)
        return tuple(set(readonly_fields + visit_schedule_fields))

    def get_changeform_initial_data(self, request: Any) -> dict:
        """Sets initial data for the form.

        Inherit from this add additional fields to set.

        Gets report_datetime from the appointment.appt_datetime
        and reason from the appointment.visit_code_sequence.
        """
        initial_data = super().get_changeform_initial_data(request)
        appointment_id = request.GET.get("appointment")
        appointment = Appointment.objects.get(id=appointment_id)
        initial_data.update(
            report_datetime=appointment.appt_datetime,
            reason=SCHEDULED if appointment.visit_code_sequence == 0 else UNSCHEDULED,
        )
        return initial_data
