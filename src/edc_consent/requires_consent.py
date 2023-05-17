from datetime import datetime
from typing import Optional

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from edc_utils import convert_php_dateformat

from .exceptions import NotConsentedError
from .site_consents import SiteConsentError, site_consents


class RequiresConsent:
    def __init__(
        self,
        model: Optional[str] = None,
        subject_identifier: Optional[str] = None,
        report_datetime: Optional[datetime] = None,
        consent_model: Optional[str] = None,
        consent_group: Optional[str] = None,
    ):
        self.version = None
        self.model = model
        self.subject_identifier = subject_identifier
        self.consent_model = consent_model
        self.report_datetime = report_datetime
        self.consent_object = site_consents.get_consent_for_period(
            model=consent_model,
            consent_group=consent_group,
            report_datetime=report_datetime,
        )
        self.consent_model_cls = self.consent_object.model_cls
        self.version = self.consent_object.version
        if not self.subject_identifier:
            raise SiteConsentError(
                f"Cannot lookup {self.consent_model} instance for subject. "
                f"Got 'subject_identifier' is None."
            )
        self.consented_or_raise()

    def consented_or_raise(self):
        try:
            self.consent_model_cls.objects.get(
                subject_identifier=self.subject_identifier, version=self.version
            )
        except ObjectDoesNotExist:
            formatted_report_datetime = self.report_datetime.strftime(
                convert_php_dateformat(settings.SHORT_DATE_FORMAT)
            )
            raise NotConsentedError(
                f"Consent is required. Cannot find '{self.consent_model} "
                f"version {self.version}' when saving model '{self.model}' for "
                f"subject '{self.subject_identifier}' with date "
                f"'{formatted_report_datetime}'. "
                f"See also `all_post_consent_models` in the visit schedule."
            )
