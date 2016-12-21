from django.apps import apps as django_apps
from django.db import models

from edc_base.model.validators.date import datetime_not_future
from edc_base.utils import get_utcnow
from edc_protocol.validators import datetime_not_before_study_start
from edc_visit_tracking.managers import CrfModelManager

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

    def save(self, *args, **kwargs):
        datetime_not_before_study_start(self.report_datetime)
        datetime_not_future(self.report_datetime)
        super(CrfModelMixin, self).save(*args, **kwargs)

    def natural_key(self):
        return (getattr(self, self.visit_model_attr()).natural_key(), )
    # TODO: need to add the natural key dependencies !!

    @classmethod
    def visit_model_attr(cls):
        app_config = django_apps.get_app_config('edc_visit_tracking')
        return app_config.visit_model_attr(cls._meta.label_lower)

    @property
    def visit(self):
        return getattr(self, self.visit_model_attr())

    class Meta:
        abstract = True
