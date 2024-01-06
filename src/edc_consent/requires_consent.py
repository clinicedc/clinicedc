from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from edc_utils import formatted_datetime, to_utc
from edc_utils.date import to_local

from .exceptions import ConsentError, NotConsentedError
from .site_consents import site_consents


class RequiresConsent:
    def __init__(
        self,
        model: str = None,
        subject_identifier: str = None,
        report_datetime: datetime = None,
        consent_model: str = None,
    ):
        self.model = model
        self.subject_identifier = subject_identifier
        self.consent_model = consent_model
        self.report_datetime = to_utc(report_datetime)
        self.consent_definition = site_consents.get_consent_definition(
            model=consent_model,
            report_datetime=report_datetime,
        )
        self.consent_model_cls = self.consent_definition.model_cls
        self.version = self.consent_definition.version
        if not self.subject_identifier:
            raise ConsentError(
                f"Cannot lookup {self.consent_model} instance for subject. "
                f"Got 'subject_identifier' is None."
            )
        self.consented_or_raise()

    def consented_or_raise(self):
        try:
            self.consent_model_cls.objects.get(
                subject_identifier=self.subject_identifier,
                version=self.version,
                consent_datetime__lte=self.report_datetime,
            )
        except ObjectDoesNotExist:
            date_string = formatted_datetime(to_local(self.report_datetime))
            raise NotConsentedError(
                f"Consent is required. Could not find a valid consent when saving model "
                f"'{self.model}' for subject '{self.subject_identifier}' using "
                f"date '{date_string}'. On which date was the subject consented? "
                f"See consent definition `{self.consent_definition.display_name}`."
            )
