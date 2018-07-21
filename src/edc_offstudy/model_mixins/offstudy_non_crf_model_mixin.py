from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import options
from edc_visit_schedule.model_mixins import VisitScheduleMethodsModelMixin

from ..offstudy_non_crf import OffstudyNonCrf

if 'offstudy_model' not in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('offstudy_model',)


MISSING_META_OFFSTUDY_MODEL = 'missing_meta_offstudy_model'
META_OFFSTUDY_MODEL = 'meta_offstudy_model'


class OffstudyNonCrfModelMixinError(ValidationError):
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
            offstudy_model = self._meta.offstudy_model
        except AttributeError as e:
            raise OffstudyNonCrfModelMixinError(
                f'Missing Meta class option. See {repr(self)}. Got {e}.',
                code=MISSING_META_OFFSTUDY_MODEL)
        if not offstudy_model:
            raise OffstudyNonCrfModelMixinError(
                f'meta.offstudy_model not defined. See {repr(self)}.',
                code=META_OFFSTUDY_MODEL)
        self.offstudy_cls(
            offstudy_model=offstudy_model,
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
        offstudy_model = None
