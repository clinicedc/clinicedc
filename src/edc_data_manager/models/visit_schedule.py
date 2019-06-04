from django.db import models
from edc_model.models import BaseUuidModel, HistoricalRecords


class VisitSchedule(BaseUuidModel):

    visit_schedule_name = models.CharField(max_length=150)

    schedule_name = models.CharField(max_length=150)

    visit_code = models.CharField(max_length=150)

    visit_name = models.CharField(max_length=150)

    timepoint = models.IntegerField()

    active = models.BooleanField(default=False)

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.visit_code} -- {self.visit_schedule_name}.{self.schedule_name}"

    class Meta:
        ordering = ("visit_schedule_name", "schedule_name", "visit_code")
