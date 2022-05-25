from datetime import date

from django.db import models
from edc_constants.choices import YES_NO
from edc_constants.constants import YES
from edc_dx import Diagnoses
from edc_dx.utils import calculate_dx_date_if_estimated
from edc_model import models as edc_models


class InitialReviewModelError(Exception):
    pass


class InitialReviewModelMixin(models.Model):

    dx_ago = edc_models.DurationYMDField(
        verbose_name="How long ago was the patient diagnosed?",
        null=True,
        blank=True,
        help_text="If possible, provide the exact date below instead of estimating here.",
    )

    dx_date = models.DateField(
        verbose_name="Date patient diagnosed",
        null=True,
        blank=True,
        help_text="If possible, provide the exact date here instead of estimating above.",
    )

    dx_estimated_date = models.DateField(
        verbose_name="Estimated diagnoses date",
        null=True,
        help_text="Calculated based on response to `dx_ago`",
        editable=False,
    )

    dx_date_estimated = models.CharField(
        verbose_name="Was the diagnosis date estimated?",
        max_length=15,
        choices=YES_NO,
        default=YES,
        editable=False,
    )

    def save(self, *args, **kwargs):
        diagnoses = Diagnoses(
            subject_identifier=self.subject_visit.subject_identifier,
            report_datetime=self.subject_visit.report_datetime,
            lte=True,
        )
        if not diagnoses.get_dx_by_model(self) == YES:
            raise InitialReviewModelError(
                "No diagnosis has been recorded. See clinical review. "
                "Perhaps catch this in the form."
            )
        self.dx_estimated_date, self.dx_date_estimated = calculate_dx_date_if_estimated(
            self.dx_date,
            self.dx_ago,
            self.report_datetime,
        )
        super().save(*args, **kwargs)  # type: ignore

    def get_best_dx_date(self) -> date:
        return self.dx_date or self.dx_estimated_date

    class Meta:
        abstract = True
        # TODO: add contraint on diagnosis, this is a singlton
