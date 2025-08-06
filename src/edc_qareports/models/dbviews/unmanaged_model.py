from django.contrib.sites.models import Site
from django.db import models
from django_db_views.db_view import DBView

from ...model_mixins import qa_reports_permissions
from .view_definition import get_view_definition


class QaReportLogSummary(DBView):
    username = models.CharField(max_length=100)
    site = models.ForeignKey(Site, on_delete=models.DO_NOTHING)
    report_model = models.CharField(max_length=100)
    first_accessed = models.DateTimeField()
    last_accessed = models.DateTimeField()
    access_count = models.IntegerField()

    view_definition = get_view_definition()

    class Meta:
        managed = False
        db_table = "qa_report_log_summary_view"
        verbose_name = "QA Report Log Summary"
        verbose_name_plural = "QA Report Log Summary"
        default_permissions = qa_reports_permissions
