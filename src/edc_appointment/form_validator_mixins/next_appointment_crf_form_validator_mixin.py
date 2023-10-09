from __future__ import annotations

import calendar
from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _
from edc_form_validators import INVALID_ERROR
from edc_utils.date import to_local

from ..utils import allow_clinic_on_weekend, get_allow_skipped_appt_using

if TYPE_CHECKING:
    from edc_facility.models import HealthFacility


class NextAppointmentCrfFormValidatorMixin:
    def __init__(self, **kwargs):
        self._clinic_days = None
        self._health_facility = None
        self.day_abbr = calendar.weekheader(3).split(" ")
        super().__init__(**kwargs)

    @property
    def visit_code_fld(self):
        return get_allow_skipped_appt_using().get(self._meta.model._meta.label_lower)[1]

    @property
    def dt_fld(self):
        return get_allow_skipped_appt_using().get(self._meta.model._meta.label_lower)[1]

    @property
    def clinic_days(self) -> list[int]:
        if not self._clinic_days:
            if self.cleaned_data.get("health_facility"):
                self._clinic_days = self.health_facility.clinic_days
        return self._clinic_days

    def validate_date_is_on_clinic_day(self):
        if appt_date := self.cleaned_data.get("appt_date"):
            if appt_date <= to_local(self.cleaned_data.get("report_datetime")).date():
                raise self.raise_validation_error(
                    {"appt_date": "Cannot be on or before the report datetime"}, INVALID_ERROR
                )
            if not allow_clinic_on_weekend() and appt_date.weekday() > calendar.FRIDAY:
                raise self.raise_validation_error(
                    {
                        "appt_date": _("Expected %(mon)s-%(fri)s. Got %(day)s")
                        % {
                            "mon": self.day_abbr[calendar.MONDAY],
                            "fri": self.day_abbr[calendar.FRIDAY],
                            "day": self.day_abbr[appt_date.weekday()],
                        }
                    },
                    INVALID_ERROR,
                )
            elif self.cleaned_data.get("subject_visit").site:
                if self.clinic_days and appt_date.weekday() not in self.clinic_days:
                    raise self.raise_validation_error(
                        {
                            "appt_date": _(
                                "Invalid clinic day. Expected %(expected)s. Got %(day_abbr)s"
                            )
                            % {
                                "expected": ", ".join(
                                    dict(zip(self.clinic_days, self.day_abbr)).values()
                                ),
                                "day_abbr": appt_date.strftime("%A"),
                            }
                        },
                        INVALID_ERROR,
                    )

    @property
    def health_facility(self) -> HealthFacility | None:
        if not self._health_facility:
            if self.cleaned_data.get("health_facility"):
                self._health_facility = self.cleaned_data.get("health_facility")
            else:
                raise self.raise_validation_error(
                    {"health_facility": _("This field is required.")}, INVALID_ERROR
                )
        return self._health_facility
