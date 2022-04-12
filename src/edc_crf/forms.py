from datetime import datetime
from typing import Optional

from edc_consent.utils import get_consent_model_cls
from edc_screening.utils import get_subject_screening_model_cls
from edc_utils import age, to_utc
from edc_visit_tracking.stubs import SubjectVisitModelStub


class PrnFormValidatorMixin:
    """A mixin of common properties needed for CRF validation
    to be declared with FormValidator.

    Assumes model has a key to subject_visit
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


class CrfFormValidatorMixin(PrnFormValidatorMixin):
    @property
    def subject_visit(self) -> Optional[SubjectVisitModelStub]:
        """Returns a subject visit model instance or None"""
        try:
            subject_visit = self.instance.subject_visit
        except AttributeError:
            subject_visit = self.cleaned_data.get("subject_visit")
        return subject_visit

    @property
    def subject_identifier(self) -> str:
        return self.subject_visit.subject_identifier
