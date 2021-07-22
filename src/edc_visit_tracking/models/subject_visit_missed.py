from django.conf import settings
from django.db import models
from edc_crf.crf_model_mixin import CrfModelMixin
from edc_model import models as edc_models

from ..model_mixins import SubjectVisitMissedModelMixin
from .subject_visit_mised_reasons import SubjectVisitMissedReasons


class SubjectVisitMissed(
    CrfModelMixin,
    SubjectVisitMissedModelMixin,
    edc_models.BaseUuidModel,
):

    subject_visit = models.OneToOneField(
        settings.SUBJECT_VISIT_MODEL,
        on_delete=models.PROTECT,
        related_name="edc_subject_visit",
    )

    missed_reasons = models.ManyToManyField(
        SubjectVisitMissedReasons, blank=True, related_name="missed_reasons"
    )

    class Meta(CrfModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        verbose_name = "Missed Visit Report"
        verbose_name_plural = "Missed Visit Report"
