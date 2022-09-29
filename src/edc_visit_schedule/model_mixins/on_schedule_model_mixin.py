from __future__ import annotations

from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from django.conf import settings
from django.db import models
from edc_identifier.managers import SubjectIdentifierManager
from edc_identifier.model_mixins import UniqueSubjectIdentifierFieldMixin
from edc_model.models import HistoricalRecords
from edc_model.validators import datetime_not_future
from edc_protocol.validators import datetime_not_before_study_start
from edc_utils import convert_php_dateformat, get_utcnow

from ..site_visit_schedules import site_visit_schedules

if TYPE_CHECKING:
    from ..schedule import Schedule
    from ..visit_schedule import VisitSchedule


class OnScheduleModelMixin(UniqueSubjectIdentifierFieldMixin, models.Model):
    """A model mixin for a schedule's onschedule model."""

    onschedule_datetime = models.DateTimeField(
        validators=[datetime_not_before_study_start, datetime_not_future],
        default=get_utcnow,
    )

    report_datetime = models.DateTimeField(editable=False)

    objects = SubjectIdentifierManager()

    history = HistoricalRecords(inherit=True)

    def __str__(self):
        formatted_datetime = self.report_datetime.astimezone(
            ZoneInfo(settings.TIME_ZONE)
        ).strftime(convert_php_dateformat(settings.SHORT_DATETIME_FORMAT))
        return f"{self.subject_identifier} {formatted_datetime}"

    def natural_key(self):
        return (self.subject_identifier,)

    def save(self, *args, **kwargs):
        self.report_datetime = self.onschedule_datetime
        super().save(*args, **kwargs)

    def put_on_schedule(self):
        _, schedule = site_visit_schedules.get_by_onschedule_model(self._meta.label_lower)
        schedule.put_on_schedule(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=self.onschedule_datetime,
        )

    @property
    def visit_schedule(self) -> VisitSchedule:
        """Returns a visit schedule object."""
        return site_visit_schedules.get_by_onschedule_model(
            onschedule_model=self._meta.label_lower
        )[0]

    @property
    def schedule(self) -> Schedule:
        """Returns a schedule object."""
        return site_visit_schedules.get_by_onschedule_model(
            onschedule_model=self._meta.label_lower
        )[1]

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["id", "subject_identifier", "onschedule_datetime", "site"])
        ]
