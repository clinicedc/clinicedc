from django.db import models
from edc_constants.choices import YES_NO
from edc_constants.constants import YES
from edc_crf.model_mixins import SingletonCrfModelMixin
from edc_dx import raise_on_unknown_diagnosis_labels
from edc_visit_schedule.utils import raise_if_not_baseline


class ClinicalReviewBaselineModelMixin(SingletonCrfModelMixin, models.Model):
    complications = models.CharField(
        verbose_name="Since last seen, has the patient had any complications",
        max_length=15,
        choices=YES_NO,
        help_text="If YES, complete the `Complications` CRF",
    )

    def save(self, *args, **kwargs):
        raise_if_not_baseline(self.related_visit)
        raise_on_unknown_diagnosis_labels(self, "_dx", YES)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
        verbose_name = "Clinical Review: Baseline"
        verbose_name_plural = "Clinical Review: Baseline"
