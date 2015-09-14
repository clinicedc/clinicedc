from django.apps import apps
from django.db import models

from simple_history.models import HistoricalRecords

from edc_base.model.models import BaseUuidModel
from edc_base.model.validators import datetime_not_before_study_start

from edc_consent.exceptions import ConsentTypeError


class ConsentTypeManager(models.Manager):

    def get_by_natural_key(self, app_label, model_name, version):
        return self.get(app_label=app_label, model_name=model_name, version=version)

    def get_by_report_datetime(self, consent_model, report_datetime):
        return self.get_by_consent_datetime(consent_model, report_datetime, field_label='report_datetime')

    def get_by_consent_datetime(self, consent_model, consent_datetime, field_label=None):
        field_label = field_label or 'consent_datetime'
        try:
            consent_type = ConsentType.objects.get(
                app_label=consent_model._meta.app_label,
                model_name=consent_model._meta.model_name,
                start_datetime__lte=consent_datetime,
                end_datetime__gte=consent_datetime
            )
        except ConsentType.DoesNotExist:
            raise ConsentTypeError(
                'Cannot find a version of consent \'{}\' using {} \'{}\'. '
                'See ConsentType.'.format(
                    consent_model._meta.verbose_name,
                    field_label,
                    consent_datetime.isoformat()))
        return consent_type


class ConsentType(BaseUuidModel):

    get_latest_by = 'start_datetime'

    app_label = models.CharField(max_length=25)

    model_name = models.CharField(max_length=25)

    start_datetime = models.DateTimeField(
        verbose_name='Valid starting',
        validators=[datetime_not_before_study_start, ],
    )

    end_datetime = models.DateTimeField(
        verbose_name='Valid ending',
        validators=[datetime_not_before_study_start, ],
    )

    version = models.CharField(max_length=10)

    history = HistoricalRecords()

    objects = ConsentTypeManager()

    def natural_key(self):
        return (self.app_label, self.model_name, self.version)

    def __str__(self):
        return '{}.{} v{}'.format(self.app_label, self.model_name, self.version)

    def model_class(self):
        """Returns the consent model class."""
        return apps.get_model(self.app_label, self.model_name)

    class Meta:
        app_label = 'edc_consent'
        unique_together = (('app_label', 'model_name', 'version'),)
        ordering = ['app_label', 'model_name', 'version']
