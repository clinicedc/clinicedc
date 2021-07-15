from django.db import models
from django.utils.safestring import mark_safe
from edc_constants.choices import YES_NO_NA
from edc_constants.constants import NOT_APPLICABLE
from edc_model import models as edc_models

from ...utils import get_list_model_app


class ClinicalReviewDmModelMixin(models.Model):

    dm_test = models.CharField(
        verbose_name="Since last seen, was the patient tested for diabetes?",
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

    dm_test_date = models.DateField(
        verbose_name="Date test requested",
        null=True,
        blank=True,
    )

    dm_reason = models.ManyToManyField(
        f"{get_list_model_app()}.reasonsfortesting",
        related_name="dm_reason",
        verbose_name="Why was the patient tested for diabetes?",
        blank=True,
    )

    dm_reason_other = edc_models.OtherCharField()

    dm_dx = models.CharField(
        verbose_name=mark_safe(
            "As of today, was the patient <u>newly</u> diagnosed with diabetes?"
        ),
        max_length=15,
        choices=YES_NO_NA,
        default=NOT_APPLICABLE,
    )

    class Meta:
        abstract = True
