from __future__ import annotations

from django.db import models

from edc_model.models import BaseUuidModel, HistoricalRecords

from .reference_model_mixins import ReferenceModelMixin


class GradingData(ReferenceModelMixin, BaseUuidModel):

    grade = models.IntegerField()

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.description} GRADE {self.grade}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Grading Reference"
        verbose_name_plural = "Grading References"
