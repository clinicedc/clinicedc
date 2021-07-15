from django.db import models
from edc_constants.choices import YES_NO
from edc_dx import get_condition_abbreviations
from edc_model.utils import estimated_date_from_ago
from edc_visit_schedule.constants import DAY1


class ClinicalReviewBaselineError(Exception):
    pass


class ClinicalReviewBaselineModelMixin(models.Model):

    complications = models.CharField(
        verbose_name="Since last seen, has the patient had any complications",
        max_length=15,
        choices=YES_NO,
        help_text="If Yes, complete the `Complications` CRF",
    )

    def save(self, *args, **kwargs):
        if (
            self.subject_visit.visit_code != DAY1
            and self.subject_visit.visit_code_sequence != 0
        ):
            raise ClinicalReviewBaselineError(
                f"This model is only valid at baseline. Got `{self.subject_visit}`."
            )
        for prefix in get_condition_abbreviations():
            setattr(
                self,
                f"{prefix}_test_estimated_date",
                estimated_date_from_ago(self, f"{prefix}_test_ago"),
            )
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
        verbose_name = "Clinical Review: Baseline"
        verbose_name_plural = "Clinical Review: Baseline"
