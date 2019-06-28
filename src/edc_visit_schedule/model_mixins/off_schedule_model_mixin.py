import arrow

from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models import options
from edc_model.validators import datetime_not_future, date_not_future
from edc_protocol.validators import date_not_before_study_start
from edc_protocol.validators import datetime_not_before_study_start
from edc_utils import get_utcnow

from .schedule_model_mixin import ScheduleModelMixin

if "offschedule_datetime_field" not in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = options.DEFAULT_NAMES + ("offschedule_datetime_field",)


class OffScheduleModelMixin(ScheduleModelMixin):
    """Model mixin for a schedule's OffSchedule model.
    """

    offschedule_datetime = models.DateTimeField(
        verbose_name="Date and time subject taken off schedule",
        validators=[datetime_not_before_study_start, datetime_not_future],
        default=get_utcnow,
    )

    def save(self, *args, **kwargs):
        try:
            self._meta.offschedule_datetime_field
        except AttributeError:
            offschedule_datetime_field = "offschedule_datetime"
        else:
            offschedule_datetime_field = self._meta.offschedule_datetime_field
        if not offschedule_datetime_field:
            raise ImproperlyConfigured(
                f"Meta attr 'offschedule_datetime_field' "
                f"cannot be None. See model {self.__class__.__name__}"
            )
        dt = getattr(self, offschedule_datetime_field)
        try:
            dt.date()
        except AttributeError:
            date_not_before_study_start(dt)
            date_not_future(dt)
            self.offschedule_datetime = arrow.Arrow.fromdate(dt).datetime
        else:
            datetime_not_before_study_start(dt)
            datetime_not_future(dt)
            self.offschedule_datetime = dt
        self.report_datetime = self.offschedule_datetime
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
        offschedule_datetime_field = "offschedule_datetime"
        indexes = [
            models.Index(
                fields=["id", "subject_identifier", "offschedule_datetime", "site"]
            )
        ]
