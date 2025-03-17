from django.db import models
from edc_qareports.model_mixins import QaReportModelMixin, qa_reports_permissions


class StockOut(QaReportModelMixin, models.Model):

    subject_identifier = models.CharField(max_length=50, null=True)

    site_id = models.IntegerField(null=True)

    visit_code = models.DecimalField(max_digits=8, decimal_places=1, null=True)

    appt_datetime = models.DateTimeField(null=True)

    baseline_datetime = models.DateTimeField(null=True)

    relative_days = models.IntegerField(null=True)

    class Meta(QaReportModelMixin.Meta):
        verbose_name = "Stock out"
        verbose_name_plural = "Stock out"
        default_permissions = qa_reports_permissions
