from django.db import models
from django.utils import timezone

from edc_model.models import BaseUuidModel


class SubjectScreening(BaseUuidModel):
    screening_identifier = models.CharField(max_length=25, unique=True)

    report_datetime = models.DateTimeField(default=timezone.now)

    age_in_years = models.IntegerField()

    eligible = models.BooleanField(default=True)

    refused = models.BooleanField(default=True)
