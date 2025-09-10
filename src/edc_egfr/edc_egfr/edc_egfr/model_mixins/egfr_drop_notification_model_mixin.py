from django.db import models
from edc_constants.constants import COMPLETE, INCOMPLETE, NEW, OPEN
from edc_lab.choices import SERUM_CREATININE_UNITS
from edc_lab_panel.model_mixin_factory import reportable_result_model_mixin_factory
from edc_model import REPORT_STATUS
from edc_reportable.units import EGFR_UNITS, MICROMOLES_PER_LITER
from edc_vitals.models import WeightField


class EgfrDropNotificationModelMixin(
    reportable_result_model_mixin_factory(
        utest_id="egfr",
        verbose_name="eGFR",
        decimal_places=4,
        default_units=EGFR_UNITS,
        max_digits=8,
        units_choices=((EGFR_UNITS, EGFR_UNITS),),
        exclude_attrs_for_reportable=True,
    ),
    reportable_result_model_mixin_factory(
        utest_id="creatinine",
        verbose_name="Serum creatinine",
        decimal_places=2,
        default_units=MICROMOLES_PER_LITER,
        max_digits=8,
        units_choices=((SERUM_CREATININE_UNITS, SERUM_CREATININE_UNITS),),
        exclude_attrs_for_reportable=True,
    ),
    models.Model,
):
    creatinine_date = models.DateField(verbose_name="Serum creatinine date")

    weight = WeightField(null=True, blank=True)

    egfr_percent_change = models.DecimalField(
        verbose_name="Percent change from baseline",
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
