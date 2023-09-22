from django.db import models
from django.utils.translation import gettext_lazy as _
from edc_crf.model_mixins import CrfModelMixin
from edc_model.models import BaseUuidModel

from .subject_visit import SubjectVisit


class EmptyTimepoint(CrfModelMixin, BaseUuidModel):
    subject_visit = models.OneToOneField(
        SubjectVisit,
        on_delete=models.PROTECT,
        related_name="edc_subject_visit",
    )

    comment = models.TextField(max_length=150)

    class Meta(CrfModelMixin.Meta, BaseUuidModel.Meta):
        verbose_name = _("No data expected")
        verbose_name_plural = _("No data expected")
