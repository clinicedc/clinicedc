from django.db import models
from django.db.models.deletion import PROTECT
from edc_base.utils import get_utcnow
from edc_base.model_mixins import BaseUuidModel

from ..model_mixins import LocatorModelMixin


class SubjectVisit(models.Model):

    subject_identifier = models.CharField(max_length=25)

    report_datetime = models.DateTimeField(default=get_utcnow)


class SubjectLocator(LocatorModelMixin, BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)
