from django.db import models
from edc_utils import get_utcnow
from edc_model.models import BaseUuidModel


class SubjectVisit(BaseUuidModel):

    subject_identifier = models.CharField(max_length=25)

    report_datetime = models.DateTimeField(default=get_utcnow)
