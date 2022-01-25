from django.db import models
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


class SubjectScreeningWithEligibilitySimple(
    ScreeningModelMixin, EligibilityModelMixin, BaseUuidModel
):

    pass
