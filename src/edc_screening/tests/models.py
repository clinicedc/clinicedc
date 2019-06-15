from django.db import models
from edc_model.models import BaseUuidModel

from ..model_mixins import ScreeningModelMixin

# from ..subject_screening_eligibility import SubjectScreeningEligibility


class SubjectScreening(ScreeningModelMixin, BaseUuidModel):

    # eligibility_cls = SubjectScreeningEligibility

    pass
