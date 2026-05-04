from django.db import models

from edc_model.models import BaseUuidModel


class VisitScheduleSummary(BaseUuidModel):
    visit_schedule_name = models.CharField(verbose_name="Visit schedule name", max_length=150)

    schedule_name = models.CharField(verbose_name="Schedule name", max_length=150)

    label = models.CharField(verbose_name="Label", max_length=301, unique=True)

    visits = models.IntegerField(default=0)

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = "Visit schedule summary"
        verbose_name_plural = "Visit schedule summary"
