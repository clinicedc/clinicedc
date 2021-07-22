from django.db import models
from edc_crf.model_mixins import CrfModelMixin
from edc_model import models as edc_models

from ..model_mixins import SubjectVisitMissedModelMixin
from .subject_visit_mised_reasons import SubjectVisitMissedReasons


class SubjectVisitMissed(
    CrfModelMixin,
    SubjectVisitMissedModelMixin,
    edc_models.BaseUuidModel,
):

    missed_reasons = models.ManyToManyField(
        SubjectVisitMissedReasons, blank=True, related_name="+"
    )

    class Meta(CrfModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        verbose_name = "Missed Visit Report"
        verbose_name_plural = "Missed Visit Report"
