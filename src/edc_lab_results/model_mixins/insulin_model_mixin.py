from django.db import models
from edc_constants.choices import YES_NO
from edc_glucose.model_mixins import FastingModelMixin
from edc_lab.choices import RESULT_QUANTIFIER
from edc_lab.constants import EQ
from edc_reportable import IU_LITER, IU_LITER_DISPLAY
from edc_reportable.choices import REPORTABLE


class InsulinModelMixin(FastingModelMixin, models.Model):

    ins_value = models.DecimalField(
        verbose_name="Insulin",
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
    )

    ins_quantifier = models.CharField(
        max_length=10,
        choices=RESULT_QUANTIFIER,
        default=EQ,
    )

    ins_units = models.CharField(
        verbose_name="units",
        max_length=15,
        choices=(
            (IU_LITER, IU_LITER),
            (IU_LITER_DISPLAY, IU_LITER_DISPLAY),
        ),
        default=IU_LITER,
        null=True,
        blank=True,
    )

    ins_abnormal = models.CharField(
        verbose_name="abnormal", choices=YES_NO, max_length=25, null=True, blank=True
    )

    ins_reportable = models.CharField(
        verbose_name="reportable",
        choices=REPORTABLE,
        max_length=25,
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True
