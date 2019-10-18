import arrow

from dateutil import tz
from django import forms
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from edc_constants.constants import DEAD
from edc_utils import convert_php_dateformat
from edc_adverse_event.get_ae_model import get_ae_model


class ValidateDeathReportMixin:
    def validate_death_report_if_deceased(self):
        """Validates death report exists of termination_reason
        is "DEAD.

        Death "date" is the naive date of the settings.TIME_ZONE datetime.

        Note: uses __date field lookup. If using mysql don't forget
        to load timezone info.
        """
        subject_identifier = (
            self.cleaned_data.get("subject_identifier")
            or self.instance.subject_identifier
        )

        try:
            death_report = get_ae_model("deathreport").objects.get(
                subject_identifier=subject_identifier
            )
        except ObjectDoesNotExist:
            if self.cleaned_data.get("termination_reason") == DEAD:
                raise forms.ValidationError(
                    {
                        "termination_reason": "Patient is deceased, please complete "
                        "death report form first."
                    }
                )
        else:
            local_death_datetime = arrow.get(
                death_report.death_datetime, tz.gettz(settings.TIME_ZONE)
            )
            if self.cleaned_data.get("death_date") and (
                local_death_datetime.date() != self.cleaned_data.get("death_date")
            ):
                expected = local_death_datetime.date().strftime(
                    convert_php_dateformat(settings.SHORT_DATE_FORMAT)
                )
                got = self.cleaned_data.get("death_date").strftime(
                    convert_php_dateformat(settings.SHORT_DATE_FORMAT)
                )
                raise forms.ValidationError(
                    {
                        "death_date": "Date does not match Death Report. "
                        f"Expected {expected}. Got {got}."
                    }
                )
