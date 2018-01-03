from django.db import models
from edc_base import get_utcnow
from edc_base.model_validators import datetime_not_future
from edc_protocol.validators import datetime_not_before_study_start

from ..site_visit_schedules import site_visit_schedules
from .schedule_model_mixin import ScheduleModelMixin


class OffScheduleModelMixin(ScheduleModelMixin):
    """Model mixin for a schedule's OffSchedule model.
    """

    offschedule_datetime = models.DateTimeField(
        verbose_name="Date and time subject taken off schedule",
        validators=[
            datetime_not_before_study_start,
            datetime_not_future],
        default=get_utcnow)

    def save(self, *args, **kwargs):
        self.report_datetime = self.offschedule_datetime
        super().save(*args, **kwargs)

    def take_off_schedule(self):
        _, schedule = site_visit_schedules.get_by_offschedule_model(
            self._meta.label_lower)
        schedule.take_off_schedule(offschedule_model_obj=self)

    class Meta:
        abstract = True
