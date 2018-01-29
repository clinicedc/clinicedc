from django.db import models
from edc_base.utils import get_utcnow


class SubjectVisit(models.Model):

    subject_identifier = models.CharField(max_length=25)

    report_datetime = models.DateTimeField(default=get_utcnow)
