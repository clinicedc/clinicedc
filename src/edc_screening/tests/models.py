from django.db import models
from edc_constants.constants import YES
from edc_model.models import BaseUuidModel

from edc_screening.model_mixins import EligibilityModelMixin

from ..model_mixins import ScreeningModelMixin
from .eligibility import MyScreeningEligibility


class SubjectScreening(ScreeningModelMixin, BaseUuidModel):
    thing = models.CharField(max_length=10, null=True)


class SubjectScreeningWithEligibility(
    ScreeningModelMixin, EligibilityModelMixin, BaseUuidModel
):
    eligibility_cls = MyScreeningEligibility

    alive = models.CharField(max_length=10, default=YES)


class SubjectScreeningWithEligibilitySimple(
    ScreeningModelMixin, EligibilityModelMixin, BaseUuidModel
):
    pass
