from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from edc_metadata.utils import has_keyed_metadata
from edc_utils import convert_php_dateformat
from edc_utils.date import to_local
from edc_visit_schedule.exceptions import ScheduledVisitWindowError

from edc_appointment.utils import get_appointment_by_datetime


class NextAppointmentCrfModelFormMixin:
    appt_date_fld = "appt_date"
    visit_code_fld = "visitschedule"

    def clean(self):
        cleaned_data = super().clean()
        self.validate_suggested_date_with_future_appointments()
        self.validate_suggested_visit_code()
        return cleaned_data

    @property
    def allow_create_interim(self) -> str:
        return self.cleaned_data.get("allow_create_interim", False)

    @property
    def suggested_date(self) -> date | None:
        return self.cleaned_data.get(self.appt_date_fld)

    @property
    def suggested_visit_code(self) -> str | None:
        return getattr(
            self.cleaned_data.get(self.visit_code_fld),
            "visit_code",
            self.cleaned_data.get(self.visit_code_fld),
        )

    def validate_suggested_date_with_future_appointments(self):
        if self.suggested_date and (
            self.related_visit.appointment.next.related_visit
            or has_keyed_metadata(self.related_visit.appointment.next)
        ):
            if (
                self.suggested_date
                != to_local(self.related_visit.appointment.next.appt_datetime).date()
            ):
                appointment = self.related_visit.appointment.next
                date_format = convert_php_dateformat(settings.SHORT_DATE_FORMAT)
                next_appt_date = (
                    to_local(appointment.appt_datetime).date().strftime(date_format)
                )
                raise forms.ValidationError(
                    {
                        self.appt_date_fld: _(
                            "Invalid. Next visit report already submitted. Expected "
                            "`%(dt)s`. See `%(visit_code)s`."
                        )
                        % {
                            "dt": next_appt_date,
                            "visit_code": appointment.visit_code,
                        }
                    }
                )

        if (
            self.suggested_date
            and self.suggested_date
            > to_local(self.related_visit.appointment.next.appt_datetime).date()
            and has_keyed_metadata(self.related_visit.appointment.next)
        ):
            appointment = self.related_visit.appointment.next
            date_format = convert_php_dateformat(settings.SHORT_DATE_FORMAT)
            raise forms.ValidationError(
                {
                    self.appt_date_fld: _(
                        "Invalid. Expected a date before appointment "
                        "`%(visit_code)s` on "
                        "%(dt_str)s."
                    )
                    % {
                        "visit_code": appointment.visit_code,
                        "dt_str": to_local(appointment.appt_datetime)
                        .date()
                        .strftime(date_format),
                    }
                }
            )

    def validate_suggested_visit_code(self):
        if suggested_date := self.suggested_date:
            subject_visit = self.cleaned_data.get("subject_visit")
            try:
                appointment = get_appointment_by_datetime(
                    self.as_datetime(suggested_date),
                    subject_identifier=subject_visit.subject_identifier,
                    visit_schedule_name=subject_visit.visit_schedule.name,
                    schedule_name=subject_visit.schedule.name,
                    raise_if_in_gap=False,
                )
            except ScheduledVisitWindowError as e:
                raise forms.ValidationError({self.appt_date_fld: str(e)})
            if not appointment:
                raise forms.ValidationError(
                    {self.appt_date_fld: _("Invalid. Must be within the followup period.")}
                )

            if (
                self.suggested_visit_code
                and self.suggested_visit_code != appointment.visit_code
            ):
                date_format = convert_php_dateformat(settings.SHORT_DATE_FORMAT)
                raise forms.ValidationError(
                    {
                        self.visit_code_fld: _(
                            "Expected %(visit_code)s using %(dt_str)s from above."
                        )
                        % {
                            "visit_code": appointment.visit_code,
                            "dt_str": suggested_date.strftime(date_format),
                        }
                    }
                )
            if appointment == subject_visit.appointment:
                if self.allow_create_interim:
                    pass
                else:
                    raise forms.ValidationError(
                        {
                            self.appt_date_fld: (
                                _(
                                    "Invalid. Cannot be within window period "
                                    "of the current appointment."
                                )
                            )
                        }
                    )
            elif self.allow_create_interim:
                raise forms.ValidationError(
                    {
                        "allow_create_interim": _(
                            "Cannot override if date is not within window period "
                            "of the current appointment."
                        )
                    }
                )

    @staticmethod
    def as_datetime(dt: date) -> datetime:
        return datetime(dt.year, dt.month, dt.day, 23, 59, 59, tzinfo=ZoneInfo("UTC"))
