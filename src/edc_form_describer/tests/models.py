from django.db import models
from django.utils import timezone

from edc_constants.choices import YES_NO
from edc_crf.model_mixins import CrfModelMixin
from edc_model.models import BaseUuidModel
from edc_visit_tracking.model_mixins import VisitModelMixin


class SubjectVisit(VisitModelMixin, BaseUuidModel):
    subject_identifier = models.CharField(max_length=25)

    report_datetime = models.DateTimeField(default=timezone.now)


class MyModel(CrfModelMixin, BaseUuidModel):
    report_datetime = models.DateTimeField(default=timezone.now)

    f1 = models.CharField(verbose_name="Is it what it is?", max_length=10, choices=YES_NO)

    f2 = models.CharField(
        verbose_name="Are they serious?", max_length=10, default="", blank=True
    )

    f3 = models.CharField(
        verbose_name="Are you worried?", max_length=10, default="", blank=False
    )

    f4 = models.CharField(
        verbose_name="Would they dare?", max_length=10, default="", blank=False
    )

    f5 = models.CharField(
        verbose_name="What am I going to tell them?",
        max_length=10,
        default="",
        blank=False,
    )

    summary_one = models.CharField(
        verbose_name="summary_one", max_length=10, default="", blank=True
    )

    summary_two = models.CharField(
        verbose_name="summary_two", max_length=10, default="", blank=True
    )
