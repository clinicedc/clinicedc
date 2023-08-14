from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from django import forms
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from edc_constants.constants import DEAD
from edc_utils import convert_php_dateformat

from ..constants import DEATH_REPORT_NOT_FOUND
from ..utils import get_ae_model

if TYPE_CHECKING:
    from ..model_mixins import DeathReportModelMixin


class BaseRequiresDeathReportFormValidatorMixin:
    @property
    def subject_identifier(self) -> str:
        return self.cleaned_data.get("subject_identifier") or self.instance.subject_identifier

    @property
    def death_report_model_cls(self) -> DeathReportModelMixin:
        return get_ae_model("deathreport")

    @property
    def death_report(self) -> DeathReportModelMixin | None:
        """Returns a model instance, if found, or None, if not."""
        try:
            return self.death_report_model_cls.objects.get(
                subject_identifier=self.subject_identifier
            )
        except ObjectDoesNotExist:
            return None

    @property
    def death_report_or_raises(self) -> DeathReportModelMixin:
        """Returns a model instance or raises
        forms.ValidationError.
        """
        try:
            return self.death_report_model_cls.objects.get(
                subject_identifier=self.subject_identifier
            )
        except ObjectDoesNotExist:
            verbose_name = self.death_report_model_cls._meta.verbose_name
            self.raise_validation_error(f"`{verbose_name}` not found.", DEATH_REPORT_NOT_FOUND)

    @property
    def death_report_date(self) -> date:
        """Returns the localized death date from the death report
        instance.
        """
        death_report = self.death_report_or_raises
        value = getattr(death_report, getattr(death_report, "death_date_field"))

        try:
            death_report_date = value.astimezone(ZoneInfo("UTC")).date()
        except AttributeError:
            death_report_date = value
        return death_report_date


class RequiresDeathReportFormValidatorMixin(BaseRequiresDeathReportFormValidatorMixin):

    """A form validator mixin used by forms that refer to the
    death report.

    For example: off study report, study termination, etc.

        class StudyTerminationFormValidator(
            DeathReportFormValidatorMixin, FormValidator):

            def clean(self):

                self.validate_death_report_if_deceased()
                ...
    """

    offschedule_reason_field = "termination_reason"
    death_date_field = "death_date"  # on this form, for example, offschedule

    def validate_death_report_if_deceased(self) -> None:
        """Validates death report exists of termination_reason
        is "DEAD.

        Death "date" is the naive date of the settings.TIME_ZONE
        datetime.

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

    def match_date_of_death_or_raise(self) -> None:
        """Raises an exception if the death date reported here does
        not match that from the Death Report.
        """
        if death_date := self.cleaned_data.get(self.death_date_field):
            try:
                death_date = death_date.date()
            except AttributeError:
                pass
            if self.death_report_date and self.death_report_date != death_date:
                expected = self.death_report_date.strftime(
                    convert_php_dateformat(settings.SHORT_DATE_FORMAT)
                )
                actual = death_date.strftime(
                    convert_php_dateformat(settings.SHORT_DATE_FORMAT)
                )
                verbose_name = self.death_report_model_cls._meta.verbose_name
                raise forms.ValidationError(
                    {
                        self.death_date_field: (
                            f"Date does not match `{verbose_name}`. "
                            f"Expected {expected}. Got {actual}."
                        )
                    }
                )
        return None
