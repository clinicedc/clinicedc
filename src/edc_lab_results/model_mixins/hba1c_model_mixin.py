from django.db import models

from edc_constants.choices import YES_NO
from edc_glucose.model_mixins import Hba1cModelMixin as BaseHba1cModelMixin
from edc_reportable.choices import REPORTABLE


class Hba1cModelMixin(BaseHba1cModelMixin, models.Model):
    is_poc = models.CharField(
        verbose_name="Was a point-of-care test used?",
        max_length=15,
        choices=YES_NO,
        default="",
    )

    hba1c_abnormal = models.CharField(
        verbose_name="abnormal", choices=YES_NO, max_length=25, default="", blank=True
    )

    hba1c_reportable = models.CharField(
        verbose_name="reportable",
        choices=REPORTABLE,
        max_length=25,
        default="",
        blank=True,
    )

    class Meta:
        abstract = True
