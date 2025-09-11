from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms

from edc_sites import site_sites
from edc_utils import formatted_date
from edc_utils.date import to_utc

from ..consent_definition import ConsentDefinition
from ..exceptions import (
    ConsentDefinitionDoesNotExist,
    ConsentDefinitionNotConfiguredForUpdate,
    NotConsentedError,
)
from ..site_consents import site_consents

if TYPE_CHECKING:
    from ..stubs import ConsentLikeModel


__all__ = ["RequiresConsentModelFormMixin"]


class RequiresConsentModelFormMixin:
    """Model form mixin for CRF or PRN forms to access the consent.

    Use with CrfModelMixin, etc
    """

    def clean(self):
        cleaned_data = super().clean()
        consent_obj = self.validate_against_consent()
        self.validate_against_dob(consent_obj)
        return cleaned_data

    def validate_against_dob(self, consent_obj):
        if consent_obj and to_utc(self.report_datetime).date() < consent_obj.dob:
            dte_str = formatted_date(consent_obj.dob)
            raise forms.ValidationError(f"Report datetime cannot be before DOB. Got {dte_str}")

    def validate_against_consent(self) -> ConsentLikeModel | None:
        """Raise an exception if the report datetime doesn't make
        sense relative to the consent.
        """
        consent_obj = None
        if self.report_datetime:
            try:
                consent_obj = site_consents.get_consent_or_raise(
                    subject_identifier=self.get_subject_identifier(),
                    report_datetime=self.report_datetime,
                    site_id=self.site.id,
                )
            except (NotConsentedError, ConsentDefinitionNotConfiguredForUpdate) as e:
                raise forms.ValidationError({"__all__": str(e)})
        return consent_obj

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
