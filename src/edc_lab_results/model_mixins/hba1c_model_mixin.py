from django.db import models
from edc_constants.choices import YES_NO
from edc_lab.choices import RESULT_QUANTIFIER
from edc_lab.constants import EQ
from edc_reportable import PERCENT
from edc_reportable.choices import REPORTABLE


class Hba1cModelMixin(models.Model):
    is_poc = models.CharField(
        verbose_name="Was a point-of-care test used?",
        max_length=15,
        choices=YES_NO,
        null=True,
    )

    hba1c_value = models.DecimalField(
        verbose_name="HbA1c value",
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
    )

    hba1c_quantifier = models.CharField(
        max_length=10,
        choices=RESULT_QUANTIFIER,
        default=EQ,
        null=True,
        blank=True,
    )

    hba1c_units = models.CharField(
        verbose_name="units",
        max_length=15,
        default=PERCENT,
        null=True,
        blank=True,
    )

    hba1c_abnormal = models.CharField(
        verbose_name="abnormal", choices=YES_NO, max_length=25, null=True, blank=True
    )

    hba1c_reportable = models.CharField(
        verbose_name="reportable",
        choices=REPORTABLE,
        max_length=25,
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True
