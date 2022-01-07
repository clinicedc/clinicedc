from edc_model.models import BaseUuidModel

from edc_screening.model_mixins import EligibilityModelMixin
from edc_screening.screening_eligibility import ScreeningEligibility

from ..model_mixins import ScreeningModelMixin


class MyScreeningEligibility(ScreeningEligibility):
    def assess_eligibility(self):
        return True

    def update_model(self) -> None:
        pass


class SubjectScreening(ScreeningModelMixin, BaseUuidModel):

    pass


class SubjectScreeningWithEligibility(
    ScreeningModelMixin, EligibilityModelMixin, BaseUuidModel
):

    eligibility_cls = MyScreeningEligibility
