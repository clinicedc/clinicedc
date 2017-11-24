from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.db import models
from django.utils import timezone
from edc_constants.constants import EDC_SHORT_DATE_FORMAT
from edc_constants.date_constants import EDC_SHORT_DATETIME_FORMAT


class SubjectOffstudyError(Exception):
    pass


class OffstudyMixin(models.Model):

    """A mixin for CRF models to add the ability to determine
    if the subject is off study as of this CRFs report_datetime.

    CRFs by definition include CrfModelMixin in their declaration.
    See edc_visit_tracking.
    """

    # If True, compares report_datetime and offstudy_datetime as datetimes
    # If False, compares report_datetime and offstudy_datetime as dates
    offstudy_compare_dates_as_datetimes = False

    def save(self, *args, **kwargs):
        self.is_offstudy_or_raise()
        super().save(*args, **kwargs)

    @property
    def offstudy_model_cls(self):
        """Returns the off study model class for this CRF's visit schedule.
        """
        try:
            model = self.visit.visit_schedule.offstudy_model
        except AttributeError as e:
            if 'visit' in str(e):
                raise ImproperlyConfigured(
                    f'Model requires method \'visit\'. Got {e}. See {repr(self)}')
            raise
        return django_apps.get_model(model)

    def is_offstudy_or_raise(self):
        """Return True if an off-study instance was submitted
        for this subject before this CRF report_datetime.
        """
        if self.offstudy_compare_dates_as_datetimes:
            opts = {'offstudy_datetime__lt': self.report_datetime}
            date_format = EDC_SHORT_DATETIME_FORMAT
        else:
            opts = {'offstudy_datetime__date__lt': self.report_datetime.date()}
            date_format = EDC_SHORT_DATE_FORMAT
        try:
            model_obj = self.offstudy_model_cls.objects.get(
                subject_identifier=self.subject_identifier, **opts)
        except ObjectDoesNotExist:
            model_obj = None
        else:
            formatted_date = timezone.localtime(
                model_obj.offstudy_datetime).strftime(date_format)
            raise SubjectOffstudyError(
                f'Participant is off study. Participant was reported off '
                f'study on {formatted_date}. Scheduled data reported after this date '
                f'may not be captured.')
        return model_obj

    class Meta:
        abstract = True
