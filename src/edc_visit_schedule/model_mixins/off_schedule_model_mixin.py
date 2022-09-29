from __future__ import annotations

from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from edc_identifier.managers import SubjectIdentifierManager
from edc_identifier.model_mixins import UniqueSubjectIdentifierFieldMixin
from edc_model.validators import datetime_not_future
from edc_protocol.validators import datetime_not_before_study_start
from edc_sites.models import CurrentSiteManager as BaseCurrentSiteManager
from edc_utils import convert_php_dateformat, get_utcnow

from ..site_visit_schedules import site_visit_schedules

if TYPE_CHECKING:
    from ..schedule import Schedule
    from ..visit_schedule import VisitSchedule


class CurrentSiteManager(BaseCurrentSiteManager):
    use_in_migrations = True

    def get_by_natural_key(self, subject_identifier):
        return self.get(subject_identifier=subject_identifier)


class OffScheduleModelMixin(UniqueSubjectIdentifierFieldMixin, models.Model):
    """Model mixin for a schedule's OffSchedule model."""

    offschedule_datetime_field_attr: str = "offschedule_datetime"

    offschedule_datetime = models.DateTimeField(
        verbose_name="Date and time subject taken off schedule",
        validators=[datetime_not_before_study_start, datetime_not_future],
        default=get_utcnow,
    )

    report_datetime = models.DateTimeField(editable=False)

    objects = SubjectIdentifierManager()

    def __str__(self):
        formatted_datetime = self.report_datetime.astimezone(
            ZoneInfo(settings.TIME_ZONE)
        ).strftime(convert_php_dateformat(settings.SHORT_DATETIME_FORMAT))
        return f"{self.subject_identifier} {formatted_datetime}"

    def natural_key(self):
        return (self.subject_identifier,)

    def save(self, *args, **kwargs):
        if not self.offschedule_datetime_field_attr:
            raise ImproperlyConfigured(
                f"Model attr 'offschedule_datetime_field_attr' "
                f"cannot be None. See model {self.__class__.__name__}"
            )
        if self.offschedule_datetime_field_attr != "offschedule_datetime":
            self.offschedule_datetime = getattr(self, self.offschedule_datetime_field_attr)
        try:
            self.offschedule_datetime.date()
        except AttributeError:
            raise ImproperlyConfigured(
                f"Field class must be DateTimeField. See {self.__class__}."
                f"{self.offschedule_datetime_field_attr}."
            )

        datetime_not_before_study_start(self.offschedule_datetime)
        datetime_not_future(self.offschedule_datetime)
        self.report_datetime = self.offschedule_datetime
        super().save(*args, **kwargs)

    @property
    def visit_schedule(self) -> VisitSchedule:
        """Returns a visit schedule object."""
        return site_visit_schedules.get_by_offschedule_model(
            offschedule_model=self._meta.label_lower
        )[0]

    @property
    def schedule(self) -> Schedule:
        """Returns a schedule object."""
        return site_visit_schedules.get_by_offschedule_model(
            offschedule_model=self._meta.label_lower
        )[1]

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["id", "subject_identifier", "offschedule_datetime", "site"])
        ]
