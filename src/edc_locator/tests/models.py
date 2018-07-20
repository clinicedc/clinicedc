from django.db import models
from edc_base.utils import get_utcnow
from edc_base.model_mixins import BaseUuidModel


class SubjectVisit(BaseUuidModel):

    subject_identifier = models.CharField(max_length=25)

    report_datetime = models.DateTimeField(default=get_utcnow)
