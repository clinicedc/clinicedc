from edc_constants.constants import DM
from edc_crf.crf_form_validator_mixins import CrfFormValidatorMixin
from edc_dx_review.utils import (
    raise_if_clinical_review_does_not_exist,
    raise_if_initial_review_does_not_exist,
)
from edc_form_validators import FormValidator
from edc_visit_schedule.utils import raise_if_baseline

from .glucose_form_validator_mixin import GlucoseFormValidatorMixin


class GlucoseFormValidator(
    GlucoseFormValidatorMixin,
    CrfFormValidatorMixin,
    FormValidator,
):
    """Declared as an example of the clean method to use with
    the mixin.
    """

    required_at_baseline = True
    require_diagnosis = False
    require_clinical_review_crf = True
    prefix = "glucose"

    def clean(self):
        if self.cleaned_data.get("subject_visit"):
            if not self.required_at_baseline:
                raise_if_baseline(self.cleaned_data.get("subject_visit"))
            self.raise_if_clinical_review_does_not_exist()
            if self.require_diagnosis:
                raise_if_initial_review_does_not_exist(
                    self.cleaned_data.get("subject_visit"), DM
                )
            self.validate_glucose_test()

    def raise_if_clinical_review_does_not_exist(self) -> None:
        if self.require_clinical_review_crf:
            return raise_if_clinical_review_does_not_exist(
                self.cleaned_data.get("subject_visit")
            )
        return None
