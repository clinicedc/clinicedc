from django.db import models
from edc_model.models import BaseUuidModel
from edc_utils import get_utcnow


class SubjectScreening(BaseUuidModel):
    screening_identifier = models.CharField(max_length=25, unique=True)

    report_datetime = models.DateTimeField(default=get_utcnow)

    age_in_years = models.IntegerField()

    eligible = models.BooleanField(default=True)

    refused = models.BooleanField(default=True)
