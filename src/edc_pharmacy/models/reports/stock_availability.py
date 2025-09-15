from django.db import models

from edc_qareports.model_mixins import QaReportModelMixin, qa_reports_permissions


class StockAvailability(QaReportModelMixin, models.Model):
    subject_identifier = models.CharField(max_length=50, default="")

    visit_code = models.DecimalField(max_digits=8, decimal_places=1, null=True)

    appt_date = models.DateField(null=True)

    baseline_date = models.DateField(null=True)

    relative_days = models.IntegerField(null=True)

    codes = models.TextField(default="")

    bins = models.TextField(default="")

    class Meta(QaReportModelMixin.Meta):
        verbose_name = "Stock availability"
        verbose_name_plural = "Stock availability"
        default_permissions = qa_reports_permissions
