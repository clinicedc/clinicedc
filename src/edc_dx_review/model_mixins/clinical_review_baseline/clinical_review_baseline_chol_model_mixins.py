from django.db import models
from django.utils.html import format_html
from edc_constants.choices import YES_NO, YES_NO_NA
from edc_constants.constants import NOT_APPLICABLE
from edc_model import models as edc_models
from edc_model.models import date_not_future
from edc_model.utils import estimated_date_from_ago


class ClinicalReviewBaselineCholModelMixin(models.Model):

    chol_test = models.CharField(
        verbose_name="Has the patient ever tested for High Cholesterol?",
        max_length=15,
        choices=YES_NO,
    )

    chol_test_ago = edc_models.DurationYMDField(
        verbose_name="If Yes, how long ago was the patient tested for High Cholesterol?",
        null=True,
        blank=True,
    )

    chol_test_estimated_date = models.DateField(
        null=True,
        blank=True,
        help_text="calculated by the EDC using `chol_test_ago`",
    )

    chol_test_date = models.DateField(
        verbose_name="Date of patient's most recent Cholesterol test?",
        validators=[date_not_future],
        null=True,
        blank=True,
    )

    chol_dx = models.CharField(
        verbose_name=format_html("Have you ever been diagnosed with High Cholesterol"),
        max_length=15,
        choices=YES_NO_NA,
        default=NOT_APPLICABLE,
        help_text="If yes, complete form `High Cholesterol Initial Review`",
    )

    def save(self, *args, **kwargs):
        self.chol_test_estimated_date = estimated_date_from_ago(self, "chol_test_ago")
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
