from datetime import datetime

from edc_consent.utils import get_consent_model_cls
from edc_form_validators import FormValidator
from edc_screening.stubs import SubjectScreeningModelStub
from edc_screening.utils import get_subject_screening_model_cls
from edc_utils import age


class CrfFormValidatorMixin(FormValidator):
    @property
    def age_in_years(self) -> int:
        return age(self.subject_consent.dob, self.report_datetime).years

    @property
    def subject_screening(self) -> SubjectScreeningModelStub:
        return get_subject_screening_model_cls().objects.get(
            subject_identifier=self.subject_identifier
        )

    @property
    def subject_identifier(self) -> str:
        try:
            subject_identifier = self.instance.subject_visit.subject_idenfifier
        except AttributeError:
            subject_identifier = self.cleaned_data.get("subject_visit").subject_identifier
        return subject_identifier

    @property
    def subject_consent(self):
        return get_consent_model_cls().objects.get(subject_identifier=self.subject_identifier)

    @property
    def report_datetime(self) -> datetime:
        return self.cleaned_data.get("subject_visit").report_datetime
