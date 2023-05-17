from django.db import models
from django.utils import timezone
from edc_sites.models import SiteModelMixin


class ResultItemModelMixin(SiteModelMixin, models.Model):
    report_datetime = models.DateTimeField(null=True)

    utestid = models.CharField(max_length=25, null=True)

    value = models.CharField(max_length=25, null=True)

    quantifier = models.CharField(max_length=25, null=True)

    value_datetime = models.DateTimeField(null=True)

    reference = models.CharField(max_length=25, null=True)

    pending_datetime = models.DateTimeField(default=timezone.now)

    pending = models.BooleanField(default=True)

    resulted_datetime = models.DateTimeField(null=True)

    resulted = models.BooleanField(default=False)

    class Meta:
        abstract = True
