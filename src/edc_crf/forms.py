from __future__ import annotations

from datetime import datetime

from edc_consent.utils import get_consent_model_cls
from edc_screening.utils import get_subject_screening_model_cls
from edc_utils import age, to_utc
from edc_visit_tracking.model_mixins import VisitModelMixin
from edc_visit_tracking.modelform_mixins import get_related_visit


class PrnFormValidatorMixin:
    """A mixin of common properties needed for PRN validation
    to be declared with FormValidator.
    """

    @property
    def subject_identifier(self) -> str | None:
        return self.cleaned_data.get("subject_identifier") or self.instance.subject_identifier

    @property
    def report_datetime(self) -> datetime | None:
        return self.cleaned_data.get("report_datetime") or self.instance.report_datetime

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
    """Assumes model is a CRF and has a key to related/subject_visit.

    Declare with FormValidator (not modelform).
    """

    @property
    def related_visit(self) -> VisitModelMixin:
        """Returns a subject visit model instance or None"""
        return get_related_visit(
            self, related_visit_model_attr=self.instance.related_visit_model_attr()
        )

    @property
    def subject_identifier(self) -> str:
        return self.related_visit.subject_identifier

    @property
    def report_datetime(self) -> datetime:
        return self.cleaned_data.get("report_datetime") or self.instance.report_datetime
