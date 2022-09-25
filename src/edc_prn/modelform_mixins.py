from __future__ import annotations

from datetime import datetime

from edc_consent.utils import get_consent_model_cls
from edc_screening.utils import get_subject_screening_model_cls
from edc_utils import age, to_utc


class PrnFormValidatorMixin:
    """A mixin of common properties needed for PRN validation
    to be declared with FormValidator.
    """

    @property
    def subject_identifier(self) -> str:
        return self.cleaned_data.get("subject_identifier")

    @property
    def report_datetime(self) -> datetime:
        try:
            return self.cleaned_data.get("report_datetime")
        except AttributeError:
            return self.subject_visit.report_datetime

    @property
    def subject_screening(self):
        return get_subject_screening_model_cls().objects.get(
            subject_identifier=self.subject_identifier
        )

    @property
    def subject_consent(self):
        return get_consent_model_cls().objects.get(subject_identifier=self.subject_identifier)

    @property
    def age_in_years(self) -> int:
        return age(self.subject_consent.dob, to_utc(self.report_datetime)).years
