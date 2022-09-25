from __future__ import annotations

from django.conf import settings
from django.db import models
from edc_model.validators import datetime_not_future
from edc_protocol.validators import datetime_not_before_study_start
from edc_utils import get_utcnow
from edc_visit_schedule.model_mixins import CrfScheduleModelMixin

from ...managers import CrfModelManager
from ..base import VisitMethodsModelMixin


class VisitTrackingCrfModelMixin(VisitMethodsModelMixin, CrfScheduleModelMixin, models.Model):
    """Base mixin for all CRF models (used by edc-crf CrfModelMixin).

    CRFs have a OneToOne relation to the related visit model

    Assumes `subject_visit` is the related visit model field attr
    on the Index.

    See also: edc_crf CrfModelMixin
    """

    # assuming subject_visit
    subject_visit = models.OneToOneField(
        settings.SUBJECT_VISIT_MODEL, on_delete=models.PROTECT
    )

    report_datetime = models.DateTimeField(
        verbose_name="Report Date",
        validators=[datetime_not_before_study_start, datetime_not_future],
        default=get_utcnow,
        help_text=(
            "If reporting today, use today's date/time, otherwise use "
            "the date/time this information was reported."
        ),
    )

    objects = CrfModelManager()

    @property
    def subject_identifier(self) -> str | None:
        try:
            return self.related_visit.subject_identifier
        except AttributeError:
            return None

    @classmethod
    def related_visit_model_attr(cls) -> str:
        # assuming subject_visit
        return "subject_visit"

    class Meta:
        abstract = True
        # assuming subject_visit
        indexes = [
            models.Index(fields=["subject_visit", "site", "id"]),
            models.Index(fields=["subject_visit", "report_datetime"]),
        ]
