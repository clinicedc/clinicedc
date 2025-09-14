from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from django import forms

from edc_appointment.constants import MISSED_APPT
from edc_sites.modelform_mixins import SiteModelFormMixin
from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.visit_schedule import VisitSchedule

from ..constants import MISSED_VISIT

if TYPE_CHECKING:
    from django.contrib.sites.models import Site

    from edc_appointment.models import Appointment


class VisitTrackingModelFormMixin(SiteModelFormMixin):
    report_datetime_field_attr = "report_datetime"

    def clean(self):
        cleaned_data = super().clean()
        if (
            cleaned_data.get("reason")
            and self.appointment.appt_timing != MISSED_APPT
            and cleaned_data.get("reason") == MISSED_VISIT
        ):
            raise forms.ValidationError(
                {
                    "reason": (
                        "Invalid. Appointment is missed. Expected visit to be missed also."
                    )
                }
            )
        if (
            cleaned_data.get("reason")
            and self.appointment.appt_timing == MISSED_APPT
            and cleaned_data.get("reason") != MISSED_VISIT
        ):
            raise forms.ValidationError(
                {
                    "reason": (
                        "Invalid. Appointment is not missed. Did not expected a missed visit."
                    )
                }
            )
        return cleaned_data

    @property
    def subject_identifier(self) -> str:
        return self.get_subject_identifier()

    def get_subject_identifier(self) -> str:
        return self.appointment.subject_identifier

    @property
    def report_datetime(self) -> datetime:
        return self.cleaned_data.get(self.report_datetime_field_attr) or getattr(
            self.instance, self.report_datetime_field_attr
        )

    @property
    def appointment(self) -> Appointment:
        return self.cleaned_data.get("appointment") or self.instance.appointment

    @property
    def visit_schedule_name(self) -> str:
        return self.visit_schedule.name

    @property
    def schedule_name(self) -> str:
        return self.schedule.name

    @property
    def visit_schedule(self) -> VisitSchedule:
        return self.appointment.visit_schedule

    @property
    def schedule(self) -> Schedule:
        return self.appointment.schedule

    @property
    def site(self) -> Site:
        return self.cleaned_data.get("site") or self.appointment.site
