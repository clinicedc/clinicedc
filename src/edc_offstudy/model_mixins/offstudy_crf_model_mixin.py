from django.apps import apps as django_apps
from django.db import models

from ..offstudy_crf import OffstudyCrf


class OffstudyCrfModelMixinError(Exception):
    pass


class OffstudyCrfModelMixin(models.Model):

    """A mixin for CRF models to add the ability to determine
    if the subject is off study as of this CRFs report_datetime.

    CRFs by definition include CrfModelMixin in their declaration.
    See edc_visit_tracking.

    Also requires field "report_datetime"
    """

    offstudy_cls = OffstudyCrf

    # If True, compares report_datetime and offstudy_datetime as datetimes
    # If False, (Default) compares report_datetime and
    # offstudy_datetime as dates
    offstudy_compare_dates_as_datetimes = False

    def save(self, *args, **kwargs):
        try:
            offstudy_model = self.visit.visit_schedule.offstudy_model
        except AttributeError as e:
            if 'visit' in str(e):
                raise OffstudyCrfModelMixinError(
                    f'Model requires property \'visit\'. See {repr(self)}, Got {e}.')
            raise
        offstudy_model_cls = django_apps.get_model(offstudy_model)
        self.offstudy_cls(
            subject_identifier=self.visit.subject_identifier,
            offstudy_model_cls=offstudy_model_cls,
            compare_as_datetimes=self.offstudy_compare_dates_as_datetimes,
            **self.__dict__)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
