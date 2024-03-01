from __future__ import annotations

from django import forms
from edc_sites import site_sites
from edc_utils import floor_secs, formatted_date, formatted_datetime
from edc_utils.date import to_local, to_utc

from .. import NotConsentedError
from ..consent_definition import ConsentDefinition
from ..exceptions import ConsentDefinitionDoesNotExist

__all__ = ["RequiresConsentModelFormMixin"]


class RequiresConsentModelFormMixin:
    """Model form mixin for CRF or PRN forms to access the consent.

    Use with CrfModelMixin, etc
    """

    def clean(self):
        cleaned_data = super().clean()
        self.validate_against_consent()
        return cleaned_data

    def validate_against_consent(self) -> None:
        """Raise an exception if the report datetime doesn't make
        sense relative to the consent.
        """
        if self.report_datetime:
            try:
                model_obj = self.consent_definition.get_consent_for(
                    subject_identifier=self.get_subject_identifier(),
                    report_datetime=self.report_datetime,
                )
            except NotConsentedError as e:
                raise forms.ValidationError({"__all__": str(e)})
            if floor_secs(to_utc(self.report_datetime)) < floor_secs(
                model_obj.consent_datetime
            ):
                dte_str = formatted_datetime(to_local(model_obj.consent_datetime))
                raise forms.ValidationError(
                    f"Report datetime cannot be before consent datetime. Got {dte_str}."
                )
            if to_utc(self.report_datetime).date() < model_obj.dob:
                dte_str = formatted_date(model_obj.dob)
                raise forms.ValidationError(
                    f"Report datetime cannot be before DOB. Got {dte_str}"
                )

    @property
    def consent_definition(self) -> ConsentDefinition:
        """Returns a consent_definition from the schedule"""
        schedule = getattr(self, "related_visit", self).schedule
        try:
            cdef = schedule.get_consent_definition(
                site=site_sites.get(self.site.id),
                report_datetime=self.report_datetime,
            )
        except ConsentDefinitionDoesNotExist as e:
            raise forms.ValidationError(e)
        return cdef
