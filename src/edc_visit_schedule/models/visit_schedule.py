from django.db import models
from edc_model.models import BaseUuidModel, HistoricalRecords


class VisitSchedule(BaseUuidModel):

    visit_schedule_name = models.CharField(max_length=150)

    schedule_name = models.CharField(max_length=150)

    visit_code = models.CharField(max_length=150)

    visit_name = models.CharField(max_length=150)

    visit_title = models.CharField(max_length=150)

    timepoint = models.DecimalField(null=True, decimal_places=1, max_digits=6)

    active = models.BooleanField(default=False)

    history = HistoricalRecords()

    def __str__(self):
        return (
            f"{self.visit_code}@{self.timepoint}: {self.visit_title} "
            f"({self.visit_schedule_name}.{self.schedule_name})"
        )

    class Meta:
        ordering = ("visit_schedule_name", "schedule_name", "visit_code")
        unique_together = (
            ("visit_schedule_name", "schedule_name", "visit_code"),
            ("visit_schedule_name", "schedule_name", "timepoint"),
        )
        indexes = [
            models.Index(
                fields=[
                    "visit_schedule_name",
                    "schedule_name",
                    "visit_code",
                    "visit_name",
                    "visit_title",
                ]
            ),
            models.Index(fields=["visit_schedule_name", "schedule_name", "timepoint"]),
        ]
