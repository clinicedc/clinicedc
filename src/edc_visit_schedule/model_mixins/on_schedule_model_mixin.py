from django.db import models
from edc_model.models import datetime_not_future
from edc_protocol.validators import datetime_not_before_study_start
from edc_utils import get_utcnow

from ..site_visit_schedules import site_visit_schedules
from .schedule_model_mixin import ScheduleModelMixin


class OnScheduleModelMixin(ScheduleModelMixin):
    """A model mixin for a schedule's onschedule model.
    """

    onschedule_datetime = models.DateTimeField(
        validators=[datetime_not_before_study_start, datetime_not_future],
        default=get_utcnow,
    )

    def save(self, *args, **kwargs):
        self.report_datetime = self.onschedule_datetime
        super().save(*args, **kwargs)

    def put_on_schedule(self):
        _, schedule = site_visit_schedules.get_by_onschedule_model(
            self._meta.label_lower
        )
        schedule.put_on_schedule(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=self.onschedule_datetime,
        )

    @property
    def visit_schedule(self):
        """Returns a visit schedule object.
        """
        return site_visit_schedules.get_by_onschedule_model(
            onschedule_model=self._meta.label_lower
        )[0]

    @property
    def schedule(self):
        """Returns a schedule object.
        """
        return site_visit_schedules.get_by_onschedule_model(
            onschedule_model=self._meta.label_lower
        )[1]

    class Meta:
        abstract = True
        indexes = [
            models.Index(
                fields=["id", "subject_identifier", "onschedule_datetime", "site"]
            )
        ]
