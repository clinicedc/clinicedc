from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from edc_constants.constants import EDC_SHORT_DATE_FORMAT
from edc_constants.date_constants import EDC_SHORT_DATETIME_FORMAT
from edc_visit_schedule.site_visit_schedules import site_visit_schedules


class SubjectOffScheduleError(Exception):
    pass


class OffScheduleCrf:

    def __init__(self, subject_identifier=None, report_datetime=None,
                 visit_schedule_name=None, schedule_name=None,
                 compare_as_datetimes=None, **kwargs):
        visit_schedule = site_visit_schedules.get_visit_schedule(
            visit_schedule_name)
        schedule = visit_schedule.schedules.get(schedule_name)
        offschedule_model = schedule.offschedule_model
        self.offschedule_model_cls = django_apps.get_model(offschedule_model)
        self.compare_as_datetimes = compare_as_datetimes
        self.subject_identifier = subject_identifier
        self.report_datetime = report_datetime
        self.onschedule_or_raise(**kwargs)

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'{self.subject_identifier}, {self.report_datetime})')

    def onschedule_or_raise(self, **kwargs):
        """Raises an exception if subject is off-schedule relative to this
        CRF's report_datetime.
        """
        if self.compare_as_datetimes:
            opts = {'offschedule_datetime__lt': self.report_datetime}
            date_format = EDC_SHORT_DATETIME_FORMAT
        else:
            opts = {'offschedule_datetime__date__lt': self.report_datetime.date()}
            date_format = EDC_SHORT_DATE_FORMAT
        try:
            offschedule_model_obj = self.offschedule_model_cls.objects.get(
                subject_identifier=self.subject_identifier, **opts)
        except ObjectDoesNotExist:
            offschedule_model_obj = None
        else:
            formatted_offschedule_datetime = timezone.localtime(
                offschedule_model_obj.offschedule_datetime).strftime(date_format)
            raise SubjectOffScheduleError(
                f'Invalid. '
                f'Participant was reported taken off schedule \'{self.schedule.name}\' '
                f' on {formatted_offschedule_datetime}. '
                f'Scheduled data reported after the date subject taken '
                f'off schedule may not be captured.')
