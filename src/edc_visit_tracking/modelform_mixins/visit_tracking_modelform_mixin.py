from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from django import forms
from edc_appointment.constants import MISSED_APPT

from ..constants import MISSED_VISIT

if TYPE_CHECKING:
    from edc_appointment.models import Appointment


class VisitTrackingModelFormMixin:
    report_datetime_field_attr = "report_datetime"

    def clean(self):
        cleaned_data = super().clean()
        if (
            cleaned_data.get("reason")
            and self.appointment.appt_timing != MISSED_APPT
            and cleaned_data.get("reason") == MISSED_VISIT
        ):
            raise forms.ValidationError(
                {"reason": "Invalid. Appointment is missed. Expected visit to be missed also."}
            )
        elif (
            cleaned_data.get("reason")
            and self.appointment.appt_timing == MISSED_APPT
            and cleaned_data.get("reason") != MISSED_VISIT
        ):
            raise forms.ValidationError(
                {
                    "reason": (
                        "Invalid. Appointment is not missed. "
                        "Did not expected a missed visit."
                    )
                }
            )
        return cleaned_data

    @property
    def subject_identifier(self) -> str:
        return self.cleaned_data.get("subject_identifier") or self.instance.subject_identifier

    @property
    def report_datetime(self) -> datetime:
        return self.cleaned_data.get(self.report_datetime_field_attr) or getattr(
            self.instance, self.report_datetime_field_attr
        )

    @property
    def appointment(self) -> Appointment:
        return self.cleaned_data.get("appointment") or self.instance.appointment
