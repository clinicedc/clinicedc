from datetime import datetime
from typing import Optional

from edc_prn.form_validators import PrnFormValidatorMixin
from edc_visit_tracking.stubs import SubjectVisitModelStub


class CrfFormValidatorMixin(PrnFormValidatorMixin):
    """A mixin of common properties needed for CRF validation
    to be declared with FormValidator.

    Assumes model has a key to subject_visit
    """

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

    @property
    def report_datetime(self) -> datetime:
        try:
            return self.cleaned_data.get("report_datetime")
        except AttributeError:
            return self.subject_visit.report_datetime
