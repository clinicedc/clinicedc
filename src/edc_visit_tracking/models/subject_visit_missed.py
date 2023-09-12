from django.db import models
from edc_crf.model_mixins import CrfModelMixin
from edc_model.models import BaseUuidModel

from ..model_mixins import SubjectVisitMissedModelMixin
from .subject_visit import SubjectVisit
from .subject_visit_missed_reasons import SubjectVisitMissedReasons


class SubjectVisitMissed(
    CrfModelMixin,
    SubjectVisitMissedModelMixin,
    BaseUuidModel,
):
    subject_visit = models.OneToOneField(
        SubjectVisit,
        on_delete=models.PROTECT,
        related_name="edc_subject_visit",
    )

    missed_reasons = models.ManyToManyField(
        SubjectVisitMissedReasons, blank=True, related_name="default_missed_reasons"
    )

    class Meta(CrfModelMixin.Meta, BaseUuidModel.Meta):
        verbose_name = "Missed Visit Report"
        verbose_name_plural = "Missed Visit Report"
