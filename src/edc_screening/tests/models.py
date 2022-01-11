from edc_constants.constants import YES
from edc_model.models import BaseUuidModel

from edc_screening.model_mixins import EligibilityModelMixin
from edc_screening.screening_eligibility import ScreeningEligibility

from ..model_mixins import ScreeningModelMixin


class MyScreeningEligibility(ScreeningEligibility):
    def assess_eligibility(self):
        self.eligible = YES
        self.reasons_ineligible = {}
        return True


class SubjectScreening(ScreeningModelMixin, BaseUuidModel):

    pass


class SubjectScreeningWithEligibility(
    ScreeningModelMixin, EligibilityModelMixin, BaseUuidModel
):

    eligibility_cls = MyScreeningEligibility
