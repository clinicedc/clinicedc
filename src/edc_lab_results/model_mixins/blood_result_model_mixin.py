from __future__ import annotations

from typing import Any

from django.db import models

from edc_constants.choices import YES_NO, YES_NO_NA

from ..calculate_missing import calculate_missing
from ..get_summary import get_summary


class BloodResultsFieldsModelMixin(models.Model):
    results_abnormal = models.CharField(
        verbose_name="Are any of the above results abnormal?",
        choices=YES_NO,
        max_length=25,
        help_text=(
            "Abnormal results present at baseline or continuing from baseline not included."
        ),
    )

    results_reportable = models.CharField(
        verbose_name="If any results are abnormal, are results within grade 3 or above?",
        max_length=25,
        choices=YES_NO_NA,
        help_text=(
            "If YES, this value will open Adverse Event Form. Grade 3 and 4 results "
            "present at baseline or continuing from baseline not included"
        ),
    )

    summary = models.TextField(default="", blank=True)

    reportable_summary = models.TextField(default="", blank=True)

    abnormal_summary = models.TextField(default="", blank=True)

    errors = models.TextField(default="", blank=True)

    missing_count = models.IntegerField(
        default=0,
        editable=False,
        help_text="A count of fields left blank",
    )

    missing = models.TextField(
        default="",
        editable=False,
        help_text="calculated string of field names that have been left blank",
    )

    class Meta:
        abstract = True


class BloodResultsMethodsModelMixin(models.Model):
    """Requires additional attrs `subject_visit` and `requisition`"""

    def save(self, *args, **kwargs):
        reportable, abnormal, errors = self.get_summary()
        self.summary = "\n".join(reportable + abnormal)
        self.reportable_summary = "\n".join(reportable)
        self.abnormal_summary = "\n".join(abnormal)
        self.errors = "\n".join(errors)
        self.missing_count, self.missing = calculate_missing(self, self.lab_panel)
        super().save(*args, **kwargs)

    def get_summary(self):
        return get_summary(self)

    def get_summary_options(self: Any) -> dict:
        # note: gender and dob are queried from RegisteredSubject
        # in reportables
        return dict(
            subject_identifier=self.subject_visit.subject_identifier,
            report_datetime=self.report_datetime,
            age_units="years",
        )

    def get_action_item_reason(self):
        return self.summary

    @property
    def abnormal(self: Any):
        return self.results_abnormal

    @property
    def reportable(self: Any):
        return self.results_reportable

    class Meta:
        abstract = True


class BloodResultsModelMixin(
    BloodResultsFieldsModelMixin, BloodResultsMethodsModelMixin, models.Model
):
    """For each `result` the field name or its prefix should
    match with a value in reportables.

    For example:
        field_name = creatinine_value
        reportables name: creatinine
        value_field_suffix = "_value"

        -OR-

        field_name = creatinine
        reportables name: creatinine
        value_field_suffix = None

    Requires additional attrs `subject_visit` and `requisition`
    from CrfWithRequisitionModelMixin

    """

    class Meta:
        abstract = True
