from django.db import models
from edc_constants.choices import YES_NO
from edc_constants.constants import YES
from edc_model import models as edc_models
from edc_model.utils import duration_to_date


class NcdInitialReviewModelMixin(models.Model):
    ncd_condition_label: str = None

    med_start_ago = edc_models.DurationYMDField(
        verbose_name=(
            "If the patient is taking medicines for ncd_condition_label, "
            "how long have they been taking these?"
        ),
        null=True,
        blank=True,
    )

    med_start_estimated_date = models.DateField(
        verbose_name="Estimated medication start date",
        null=True,
        editable=False,
    )

    med_start_date_is_estimated = models.CharField(
        verbose_name="Was the medication start date estimated?",
        max_length=15,
        choices=YES_NO,
        default=YES,
        editable=False,
    )

    def save(self, *args, **kwargs):
        if self.med_start_ago:
            self.med_start_estimated_date = duration_to_date(
                self.med_start_ago, self.report_datetime
            )
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
