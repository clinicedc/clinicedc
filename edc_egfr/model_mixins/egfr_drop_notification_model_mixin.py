from django.db import models
from django.utils.html import format_html
from edc_constants.constants import COMPLETE, INCOMPLETE, NEW, NOT_APPLICABLE, OPEN
from edc_crf.crf_status_model_mixin import CrfStatusModelMixin
from edc_lab.choices import SERUM_CREATININE_UNITS_NA
from edc_model import REPORT_STATUS


class EgfrDropNotificationModelMixin(CrfStatusModelMixin, models.Model):

    creatinine_date = models.DateField(verbose_name="Creatinine result date")

    creatinine_value = models.DecimalField(
        verbose_name=format_html("Creatinine <u>level</u>"),
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )

    creatinine_units = models.CharField(
        verbose_name="Units (creatinine)",
        max_length=15,
        choices=SERUM_CREATININE_UNITS_NA,
        default=NOT_APPLICABLE,
    )

    egfr_percent_change = models.DecimalField(
        verbose_name="Change from baseline",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Copied from RFT result eGFR section.",
    )

    narrative = models.TextField(
        verbose_name="Narrative",
        null=True,
        blank=True,
    )

    report_status = models.CharField(max_length=15, choices=REPORT_STATUS, default=NEW)

    def save(self, *args, **kwargs):
        if self.report_status == OPEN:
            self.crf_status = INCOMPLETE
        else:
            self.crf_status = COMPLETE
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "eGFR Drop Notification"
        verbose_name_plural = "eGFR Drop Notifications"
        abstract = True
