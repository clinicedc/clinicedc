from django.db import models
from edc_model.models import BaseUuidModel

from .model_mixins import ReferenceModelMixin


class GradingData(ReferenceModelMixin, BaseUuidModel):

    grade = models.IntegerField()

    def __str__(self):
        return f"{self.label}: {self.description} GRADE {self.grade}"

    class Meta:
        verbose_name = "Grading Reference"
        verbose_name_plural = "Grading References"
