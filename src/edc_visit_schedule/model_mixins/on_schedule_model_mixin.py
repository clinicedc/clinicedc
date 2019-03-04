from django.db import models
from edc_model.validators import datetime_not_future
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

    class Meta:
        abstract = True
