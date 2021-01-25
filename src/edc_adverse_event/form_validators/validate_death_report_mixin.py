import arrow

from dateutil import tz
from django import forms
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from edc_constants.constants import DEAD
from edc_utils import convert_php_dateformat
from edc_adverse_event.get_ae_model import get_ae_model


class DeathDateValidator:
    def __init__(self, cleaned_data=None, instance=None, death_date_field=None):
        self._death_report_date = None
        self._death_report = None
        self._subject_identifier = None
        self.cleaned_data = cleaned_data
        self.instance = instance
        self.death_date_field = death_date_field or "death_date"

    @property
    def subject_identifier(self):
        if not self._subject_identifier:
            self._subject_identifier = (
                self.cleaned_data.get("subject_identifier")
                or self.instance.subject_identifier
            )
        return self._subject_identifier

    @property
    def death_report(self):
        if not self._death_report:
            try:
                self._death_report = get_ae_model("deathreport").objects.get(
                    subject_identifier=self.subject_identifier
                )
            except ObjectDoesNotExist:
                pass
        return self._death_report

    @property
    def death_report_date(self):
        """Returns the localized death date from the death report"""
        if not self._death_report_date:
            try:
                self._death_report_date = getattr(
                    self.death_report, self.death_date_field
                )
            except AttributeError:
                self._death_report_date = arrow.get(
                    getattr(self.death_report, self.death_date_field),
                    tz.gettz(settings.TIME_ZONE),
                ).date()
            except ValueError:
                pass
        return self._death_report_date


class ValidateDeathReportMixin:

    offschedule_reason_field = "termination_reason"
    death_date_field = "death_date"

    def validate_death_report_if_deceased(self):
        """Validates death report exists of termination_reason
        is "DEAD.

        Death "date" is the naive date of the settings.TIME_ZONE datetime.

        Note: uses __date field lookup. If using mysql don't forget
        to load timezone info.
        """

        validator = DeathDateValidator(
            cleaned_data=self.cleaned_data,
            instance=self.instance,
            death_date_field=self.death_date_field,
        )

        if self.cleaned_data.get(self.offschedule_reason_field):
            if (
                self.cleaned_data.get(self.offschedule_reason_field).name == DEAD
                and not validator.death_report
            ):
                raise forms.ValidationError(
                    {
                        self.offschedule_reason_field: "Patient is deceased, please complete "
                        "death report form first."
                    }
                )
            elif (
                self.cleaned_data.get(self.offschedule_reason_field).name != DEAD
                and validator.death_report
            ):
                raise forms.ValidationError(
                    {
                        self.offschedule_reason_field: "Invalid selection. A death report was submitted"
                    }
                )

        if not self.cleaned_data.get(self.death_date_field) and validator.death_report:
            raise forms.ValidationError(
                {
                    self.death_date_field: "This field is required. A death report was submitted."
                }
            )
        elif self.cleaned_data.get(self.death_date_field) and validator.death_report:
            try:
                death_date = self.cleaned_data.get(self.death_date_field).date()
            except AttributeError:
                death_date = self.cleaned_data.get(self.death_date_field)
            if validator.death_report_date != death_date:
                expected = validator.death_report_date.strftime(
                    convert_php_dateformat(settings.SHORT_DATE_FORMAT)
                )
                got = death_date.strftime(
                    convert_php_dateformat(settings.SHORT_DATE_FORMAT)
                )
                raise forms.ValidationError(
                    {
                        self.death_date_field: "Date does not match Death Report. "
                        f"Expected {expected}. Got {got}."
                    }
                )
