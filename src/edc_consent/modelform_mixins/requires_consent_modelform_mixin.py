from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from edc_utils import floor_secs, formatted_date, formatted_datetime
from edc_utils.date import to_local, to_utc

from ..constants import DEFAULT_CONSENT_GROUP
from ..site_consents import site_consents
from ..utils import get_consent_model_name

if TYPE_CHECKING:
    from ..model_mixins import ConsentModelMixin


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
            consent = self.get_consent_or_raise()
            if floor_secs(to_utc(self.report_datetime)) < floor_secs(consent.consent_datetime):
                dte_str = formatted_datetime(to_local(consent.consent_datetime))
                raise forms.ValidationError(
                    f"Report datetime cannot be before consent datetime. Got {dte_str}."
                )
            if to_utc(self.report_datetime).date() < consent.dob:
                dte_str = formatted_date(consent.dob)
                raise forms.ValidationError(
                    f"Report datetime cannot be before DOB. Got {dte_str}"
                )

    @property
    def consent_group(self) -> str:
        try:
            consent_group = self._meta.model._meta.consent_group
        except AttributeError:
            consent_group = DEFAULT_CONSENT_GROUP
        return consent_group

    @property
    def consent_model(self) -> str:
        return get_consent_model_name()

    def get_consent_or_raise(self) -> ConsentModelMixin:
        """Return an instance of the consent model"""
        consent_object = site_consents.get_consent(
            report_datetime=self.report_datetime,
            consent_group=self.consent_group,
            consent_model=self.consent_model,
        )
        try:
            obj = consent_object.model_cls.consent.consent_for_period(
                subject_identifier=self.subject_identifier,
                report_datetime=self.report_datetime,
            )
        except ObjectDoesNotExist:
            raise forms.ValidationError(
                f"`{consent_object.model_cls._meta.verbose_name}` does not exist "
                f"to cover this subject on {formatted_datetime(self.report_datetime)}"
            )
        return obj
