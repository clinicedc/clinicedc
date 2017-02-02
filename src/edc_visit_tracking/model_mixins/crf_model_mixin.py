import arrow
from dateutil.relativedelta import relativedelta

from django.apps import apps as django_apps
from django.db import models

from edc_base.model.validators.date import datetime_not_future
from edc_base.utils import get_utcnow
from edc_protocol.validators import datetime_not_before_study_start
from edc_visit_tracking.managers import CrfModelManager

from ..exceptions import VisitReportDateAllowanceError
from .model_mixins import ModelMixin


class CrfModelMixin(ModelMixin, models.Model):

    """Base mixin for all CRF models.

    You need to define the visit model foreign_key, e.g:

        subject_visit = models.ForeignKey(SubjectVisit)

    Uses edc_visit_tracking.AppConfig attributes.
    """
    report_datetime = models.DateTimeField(
        verbose_name="Report Date",
        validators=[
            datetime_not_before_study_start,
            datetime_not_future, ],
        default=get_utcnow,
        help_text=('If reporting today, use today\'s date/time, otherwise use '
                   'the date/time this information was reported.'))

    objects = CrfModelManager()

    def __str__(self):
        return str(self.visit)

    def common_clean(self):
        report_datetime = arrow.Arrow.fromdatetime(
            self.report_datetime, self.report_datetime.tzinfo).to('utc').datetime
        datetime_not_before_study_start(report_datetime)
        datetime_not_future(report_datetime)
        if report_datetime.date() < self.visit.report_datetime.date():
            raise VisitReportDateAllowanceError(
                'Report datetime may not be before the visit report datetime.',
                'report_datetime')
        app_config = django_apps.get_app_config('edc_visit_tracking')
        if app_config.report_datetime_allowance > 0:
            max_report_datetime = (
                report_datetime
                + relativedelta(days=app_config.report_datetime_allowance))
            if max_report_datetime.date() < self.visit.report_datetime.date():
                raise VisitReportDateAllowanceError(
                    'Report datetime may not more than {} days greater than the '
                    'visit report datetime. Got {} days.'.format(
                        app_config.report_datetime_allowance,
                        (max_report_datetime.date()
                         - self.visit.report_datetime.date()).days),
                    'report_datetime')
        super().clean()

    @property
    def common_clean_exceptions(self):
        return super().common_clean_exceptions + [VisitReportDateAllowanceError]

    def natural_key(self):
        return (getattr(self, self.visit_model_attr()).natural_key(), )
    # TODO: need to add the natural key dependencies !!

    @classmethod
    def visit_model_attr(cls):
        app_config = django_apps.get_app_config('edc_visit_tracking')
        return app_config.visit_model_attr(cls._meta.label_lower)

    @classmethod
    def visit_model(cls):
        app_config = django_apps.get_app_config('edc_visit_tracking')
        return app_config.visit_model(cls._meta.app_label)

    @property
    def visit(self):
        return getattr(self, self.visit_model_attr())

    class Meta:
        abstract = True
