from django.db import models
from django.utils import timezone

from edc_sites.model_mixins import SiteModelMixin


class ResultItemModelMixin(SiteModelMixin, models.Model):
    report_datetime = models.DateTimeField(null=True)

    utestid = models.CharField(max_length=25, default="")

    value = models.CharField(max_length=25, default="")

    quantifier = models.CharField(max_length=25, default="")

    value_datetime = models.DateTimeField(null=True)

    reference = models.CharField(max_length=25, default="")

    pending_datetime = models.DateTimeField(default=timezone.now)

    pending = models.BooleanField(default=True)

    resulted_datetime = models.DateTimeField(null=True)

    resulted = models.BooleanField(default=False)

    class Meta:
        abstract = True
