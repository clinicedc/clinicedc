from django.contrib.sites.models import Site
from django.db import models


class QaReportLogSummary(models.Model):
    username = models.CharField(max_length=100)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    report_model = models.CharField(max_length=100)
    first_accessed = models.DateTimeField()
    last_accessed = models.DateTimeField()
    access_count = models.IntegerField()

    class Meta:
        managed = False
        db_table = "qa_report_log_summary_view"
        verbose_name = "QA Report Log Summary"
        verbose_name_plural = "QA Report Log Summary"
