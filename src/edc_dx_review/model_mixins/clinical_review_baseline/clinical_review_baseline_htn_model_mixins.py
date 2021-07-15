from django.db import models
from django.utils.html import format_html
from edc_constants.choices import YES_NO, YES_NO_NA
from edc_constants.constants import NOT_APPLICABLE
from edc_model import models as edc_models
from edc_model.utils import estimated_date_from_ago


class ClinicalReviewBaselineHtnModelMixin(models.Model):

    htn_test = models.CharField(
        verbose_name="Has the patient ever tested for Hypertension?",
        max_length=15,
        choices=YES_NO,
    )

    htn_test_ago = edc_models.DurationYMDField(
        verbose_name="If Yes, how long ago was the patient tested for Hypertension?",
        null=True,
        blank=True,
    )

    htn_test_estimated_date = models.DateField(
        null=True,
        blank=True,
        help_text="calculated by the EDC using `htn_test_ago`",
    )

    htn_test_date = models.DateField(
        verbose_name="Date of patient's most recent Hypertension test?",
        validators=[edc_models.date_not_future],
        null=True,
        blank=True,
    )

    htn_dx = models.CharField(
        verbose_name=format_html("Has the patient ever been diagnosed with Hypertension"),
        max_length=15,
        choices=YES_NO_NA,
        default=NOT_APPLICABLE,
        help_text="If yes, complete form `Hypertension Initial Review`",
    )

    def save(self, *args, **kwargs):
        self.htn_test_estimated_date = estimated_date_from_ago(self, "htn_test_ago")
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
