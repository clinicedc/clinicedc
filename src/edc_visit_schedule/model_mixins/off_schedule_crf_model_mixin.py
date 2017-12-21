from django.db import models

from ..offschedule_crf import OffScheduleCrf


class OffScheduleCrfModelMixinError(Exception):
    pass


class OffScheduleCrfModelMixin(models.Model):

    """A mixin for CRF models to add the ability to determine
    if the subject is off schedule as of this CRFs report_datetime.

    CRFs by definition include CrfModelMixin in their declaration.
    See edc_visit_tracking.

    Also requires field "report_datetime"
    """

    offschedule_cls = OffScheduleCrf

    # If True, compares report_datetime and offschedule_datetime as datetimes
    # If False, (Default) compares report_datetime and
    # offschedule_datetime as dates
    offschedule_compare_dates_as_datetimes = False

    def save(self, *args, **kwargs):
        self.offschedule_cls(
            subject_identifier=self.visit.subject_identifier,
            visit_schedule_name=self.visit.visit_schedule_name,
            schedule_name=self.visit.schedule_name,
            compare_as_datetimes=self.offschedule_compare_dates_as_datetimes,
            **self.__dict__)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
