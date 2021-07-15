from django.db import models
from django.utils.safestring import mark_safe
from edc_constants.choices import YES_NO_NA
from edc_constants.constants import NOT_APPLICABLE
from edc_model import models as edc_models

from ...utils import get_list_model_app


class ClinicalReviewHtnModelMixin(models.Model):

    htn_test = models.CharField(
        verbose_name="Since last seen, was the patient tested for hypertension?",
        max_length=15,
        choices=YES_NO_NA,
        default=NOT_APPLICABLE,
        help_text=mark_safe(
            "Note: Select `not applicable` if diagnosis previously reported. <BR>"
            "`Since last seen` includes today.<BR>"
            "If `yes', complete the initial review CRF<BR>"
            "If `not applicable`, complete the review CRF."
        ),
    )

    htn_test_date = models.DateField(
        verbose_name="Date test requested",
        null=True,
        blank=True,
    )

    htn_reason = models.ManyToManyField(
        f"{get_list_model_app()}.reasonsfortesting",
        related_name="htn_test_reason",
        verbose_name="Why was the patient tested for hypertension?",
        blank=True,
    )

    htn_reason_other = edc_models.OtherCharField()

    htn_dx = models.CharField(
        verbose_name=mark_safe(
            "As of today, was the patient <u>newly</u> diagnosed with hypertension?"
        ),
        max_length=15,
        choices=YES_NO_NA,
        default=NOT_APPLICABLE,
    )

    class Meta:
        abstract = True
