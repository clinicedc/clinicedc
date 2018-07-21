from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from edc_constants.constants import EDC_SHORT_DATE_FORMAT
from edc_constants.date_constants import EDC_SHORT_DATETIME_FORMAT


class SubjectOffstudyError(Exception):
    pass


class OffstudyCrf:

    def __init__(self, subject_identifier=None, report_datetime=None,
                 offstudy_model=None, compare_as_datetimes=None, **kwargs):
        self.offstudy_model_cls = django_apps.get_model(offstudy_model)
        self.compare_as_datetimes = compare_as_datetimes
        self.subject_identifier = subject_identifier
        self.report_datetime = report_datetime
        self.onstudy_or_raise(**kwargs)

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'{self.subject_identifier}, {self.report_datetime})')

    def onstudy_or_raise(self, **kwargs):
        """Raises an exception if subject is off-study relative to this
        CRF's report_datetime.
        """
        if self.compare_as_datetimes:
            opts = {'offstudy_datetime__lt': self.report_datetime}
            date_format = EDC_SHORT_DATETIME_FORMAT
        else:
            opts = {'offstudy_datetime__date__lt': self.report_datetime.date()}
            date_format = EDC_SHORT_DATE_FORMAT
        try:
            offstudy_model_obj = self.offstudy_model_cls.objects.get(
                subject_identifier=self.subject_identifier, **opts)
        except ObjectDoesNotExist:
            offstudy_model_obj = None
        else:
            formatted_offstudy_datetime = timezone.localtime(
                offstudy_model_obj.offstudy_datetime).strftime(date_format)
            raise SubjectOffstudyError(
                f'Invalid. '
                f'Participant was reported off-study on {formatted_offstudy_datetime}. '
                f'Scheduled data reported after the off-study date '
                f'may not be captured.')
