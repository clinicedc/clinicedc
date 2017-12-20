from django.utils import timezone
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from .subject_schedule_history import SubjectScheduleHistory
from django.core.exceptions import ObjectDoesNotExist


class OffScheduleError(Exception):
    pass


class OffScheduleValidator:

    """A class to validate that to take off-schedule is valid.
    """

    def __init__(self, subject_identifier=None, offschedule_datetime=None,
                 visit_schedule_name=None, schedule_name=None):
        self.offschedule_datetime = offschedule_datetime
        self.schedule_name = schedule_name
        self.subject_identifier = subject_identifier
        self.visit_schedule_name = visit_schedule_name
        self.validate()

    def validate(self):
        visit_schedule = site_visit_schedules.get_visit_schedule(
            visit_schedule_name=self.visit_schedule_name)
        schedule = visit_schedule.get_schedule(
            schedule_name=self.schedule_name)

        try:
            onschedule = schedule.onschedule_model_cls.objects.get(
                subject_identifier=self.subject_identifier)
        except ObjectDoesNotExist as e:
            raise OffScheduleError(
                f'Cannot take off schedule before on schedule. '
                f'Subject \'{self.subject_identifier}\' '
                f'is not on schedule \'{self.visit_schedule_name}.{self.schedule_name}\'. '
                f'Got {e}') from e

        tdelta = onschedule.onschedule_datetime - self.offschedule_datetime
        if tdelta.days > 0:
            raise OffScheduleError(
                f'Off-schedule datetime cannot precede the on-schedule '
                f'datetime {timezone.localtime(onschedule.onschedule_datetime)}. '
                f'Got {timezone.localtime(self.offschedule_datetime)}')

        history = SubjectScheduleHistory(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule_name,
            schedule_name=self.schedule_name)
        try:
            last_visit = history.visits[-1:][0]
        except IndexError:
            pass
        else:
            tdelta = last_visit.report_datetime - self.offschedule_datetime
            if tdelta.days > 0:
                raise OffScheduleError(
                    f'OffSchedule datetime cannot precede the last visit '
                    f'datetime {timezone.localtime(last_visit.report_datetime)}. '
                    f'Got {timezone.localtime(self.offschedule_datetime)}')
