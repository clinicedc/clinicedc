import arrow
from dateutil import tz
from django import forms
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from edc_constants.constants import DEAD
from edc_utils import convert_php_dateformat

from edc_adverse_event.get_ae_model import get_ae_model


class RequiresDeathReportFormValidatorMixin:

    """A form validator mixin used by forms that refer to the death report.

    For example: off study report, study termination, etc.

        class StudyTerminationFormValidator(
            DeathReportFormValidatorMixin, FormValidator):

            def clean(self):

                self.validate_death_report_if_deceased()
                ...
    """

    offschedule_reason_field = "termination_reason"
    death_date_field = "death_date"

    def validate_death_report_if_deceased(self):
        """Validates death report exists of termination_reason
        is "DEAD.

        Death "date" is the naive date of the settings.TIME_ZONE datetime.

        Note: uses __date field lookup. If using mysql don't forget
        to load timezone info.
        """

        if self.cleaned_data.get(self.offschedule_reason_field):
            if (
                self.cleaned_data.get(self.offschedule_reason_field).name == DEAD
                and not self.death_report
            ):
                raise forms.ValidationError(
                    {
                        self.offschedule_reason_field: "Patient is deceased, please complete "
                        "death report form first."
                    }
                )
            elif (
                self.cleaned_data.get(self.offschedule_reason_field).name != DEAD
                and self.death_report
            ):
                raise forms.ValidationError(
                    {
                        self.offschedule_reason_field: (
                            "Invalid selection. A death report was submitted"
                        )
                    }
                )

        if not self.cleaned_data.get(self.death_date_field) and self.death_report:
            raise forms.ValidationError(
                {
                    self.death_date_field: (
                        "This field is required. A death report was submitted."
                    )
                }
            )
        elif self.cleaned_data.get(self.death_date_field) and self.death_report:
            self.match_date_of_death_or_raise()

    @property
    def subject_identifier(self):
        return self.cleaned_data.get("subject_identifier") or self.instance.subject_identifier

    @property
    def death_report(self):
        """Returns a model instance or None"""
        try:
            return get_ae_model("deathreport").objects.get(
                subject_identifier=self.subject_identifier
            )
        except ObjectDoesNotExist:
            return None

    @property
    def death_report_date(self):
        """Returns the localized death date from the death report"""
        try:
            death_report_date = getattr(self.death_report, self.death_date_field)
        except AttributeError:
            death_report_date = arrow.get(
                getattr(self.death_report, self.death_date_field),
                tz.gettz(settings.TIME_ZONE),
            ).date()
        except ValueError:
            death_report_date = None
        return death_report_date

    def match_date_of_death_or_raise(self):
        """Raises an exception if the death date reported here does not match
        that from the Death Report."""
        try:
            death_date = self.cleaned_data.get(self.death_date_field).date()
        except AttributeError:
            death_date = self.cleaned_data.get(self.death_date_field)
        if self.death_report_date != death_date:
            expected = self.death_report_date.strftime(
                convert_php_dateformat(settings.SHORT_DATE_FORMAT)
            )
            got = death_date.strftime(convert_php_dateformat(settings.SHORT_DATE_FORMAT))
            raise forms.ValidationError(
                {
                    self.death_date_field: "Date does not match Death Report. "
                    f"Expected {expected}. Got {got}."
                }
            )
        return None
