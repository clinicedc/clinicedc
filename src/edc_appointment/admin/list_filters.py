from __future__ import annotations

from django.utils.translation import gettext as _
from edc_model_admin.list_filters import FutureDateListFilter


class AppointmentListFilter(FutureDateListFilter):
    title = _("Appointment date")

    parameter_name = "appt_datetime"
    field_name = "appt_datetime"
