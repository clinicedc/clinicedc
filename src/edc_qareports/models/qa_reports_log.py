from django.contrib.sites.models import Site
from django.db import models
from edc_utils import get_utcnow


class QaReportLog(models.Model):

    username = models.CharField(max_length=100)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    report_model = models.CharField(max_length=100)
    accessed = models.DateTimeField(default=get_utcnow)

    class Meta:
        verbose_name = "QA Report Log"
        verbose_name_plural = "QA Report Logs"
        indexes = [models.Index(fields=["accessed"])]
