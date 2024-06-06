from __future__ import annotations

from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext as _
from edc_model_admin.list_filters import FutureDateListFilter

from edc_appointment.choices import APPT_STATUS
from edc_appointment.constants import (
    ATTENDED_APPT,
    COMPLETE_APPT,
    IN_PROGRESS_APPT,
    INCOMPLETE_APPT,
)


class AppointmentListFilter(FutureDateListFilter):
    title = _("Appointment date")

    parameter_name = "appt_datetime"
    field_name = "appt_datetime"


class AppointmentStatusListFilter(SimpleListFilter):
    title = _("Status")

    parameter_name = "appt_status"
    field_name = "appt_status"

    def lookups(self, request, model_admin) -> tuple:
        return APPT_STATUS + ((ATTENDED_APPT, "Attended (In progress, incomplete, done)"),)

    def queryset(self, request, queryset):
        qs = None
        if self.value() == ATTENDED_APPT:
            qs = queryset.filter(
                appt_status__in=[IN_PROGRESS_APPT, INCOMPLETE_APPT, COMPLETE_APPT]
            )
        elif self.value():
            qs = queryset.filter(appt_status=self.value())
        return qs
