from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms
from django.apps import apps as django_apps
from django.conf import settings

from ..site_consents import SiteConsentError, site_consents

if TYPE_CHECKING:
    from ..consent import Consent


class ConsentFormValidatorMixin:

    """Validator mixin for form validators that require consent.

    Call `get_consent_for_period_or_raise` in clean()."""

    consent_model = settings.SUBJECT_CONSENT_MODEL

    def get_consent_for_period_or_raise(self) -> Consent:
        default_consent_group = django_apps.get_app_config("edc_consent").default_consent_group
        try:
            consent_object = site_consents.get_consent_for_period(
                model=self.consent_model,
                report_datetime=self.report_datetime,
                consent_group=default_consent_group,
            )
        except SiteConsentError as e:
            raise forms.ValidationError(e)
        return consent_object
