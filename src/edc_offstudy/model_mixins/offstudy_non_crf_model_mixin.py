from django.apps import apps as django_apps
from django.db import models
from edc_visit_schedule.model_mixins import VisitScheduleMethodsModelMixin

from ..offstudy_non_crf import OffstudyNonCrf


class OffstudyNonCrfModelMixinError(Exception):
    pass


class OffstudyNonCrfModelMixin(VisitScheduleMethodsModelMixin, models.Model):

    """A mixin for non-CRF models to add the ability to determine
    if the subject is off study as of this non-CRFs report_datetime.

    Requires fields "subject_identifier" and "report_datetime"

    """

    offstudy_cls = OffstudyNonCrf

    # If True, compares report_datetime and offstudy_datetime as datetimes
    # If False, (Default) compares report_datetime and
    # offstudy_datetime as dates
    offstudy_compare_dates_as_datetimes = False

    def save(self, *args, **kwargs):
        try:
            offstudy_model = self.visit_schedule.offstudy_model
        except AttributeError:
            raise OffstudyNonCrfModelMixinError(
                f'Unable to determine offstudy model. Non-CRF model '
                f'requires method \'visit_schedule\'. See {repr(self)}.')
        offstudy_model_cls = django_apps.get_model(offstudy_model)
        self.offstudy_cls(
            offstudy_model_cls=offstudy_model_cls,
            compare_as_datetimes=self.offstudy_compare_dates_as_datetimes,
            **self.__dict__)
        super().save(*args, **kwargs)

    @property
    def visit(self):
        raise NotImplementedError()

    @property
    def visits(self):
        raise NotImplementedError()

    @property
    def schedule(self):
        raise NotImplementedError()

    class Meta:
        abstract = True
