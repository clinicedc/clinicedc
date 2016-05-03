from django.core.exceptions import MultipleObjectsReturned
from django.apps import apps as django_apps
from django.db import models
from django.db.models import Q
from simple_history.models import HistoricalRecords as AuditTrail

from edc_base.model.validators import datetime_not_before_study_start

from ..exceptions import ConsentTypeError


class ConsentTypeManager(models.Manager):

    def get_by_natural_key(self, app_label, model_name, version):
        return self.get(app_label=app_label, model_name=model_name, version=version)

    def get_by_report_datetime(self, consent_model, report_datetime, exception_cls=None):
        return self.get_by_consent_datetime(
            consent_model, report_datetime, field_label='report_datetime', exception_cls=exception_cls)

    def get_by_consent_datetime(self, consent_model, consent_datetime, field_label=None, exception_cls=None):
        field_label = field_label or 'consent_datetime'
        exception_cls = exception_cls or ConsentTypeError
        try:
            consent_type = ConsentType.objects.get(
                app_label=consent_model._meta.app_label,
                model_name=consent_model._meta.model_name,
                start_datetime__lte=consent_datetime,
                end_datetime__gte=consent_datetime
            )
        except ValueError as e:
            if 'Cannot use None as a query value' in str(e):
                raise ValueError('{} Got consent_datetime=\'{}\''.format(str(e), str(consent_datetime)))
        except ConsentType.DoesNotExist:
            raise exception_cls(
                'Cannot find a version of consent \'{}\' using {} \'{}\'. '
                'See ConsentType.'.format(
                    consent_model._meta.verbose_name,
                    field_label,
                    consent_datetime.isoformat()))
        return consent_type


class ConsentType(models.Model):

    get_latest_by = 'start_datetime'

    app_label = models.CharField(max_length=25)

    model_name = models.CharField(max_length=25)

    start_datetime = models.DateTimeField(
        verbose_name='Valid starting',
        validators=[datetime_not_before_study_start, ])

    end_datetime = models.DateTimeField(
        verbose_name='Valid ending',
        validators=[datetime_not_before_study_start, ])

    version = models.CharField(max_length=10)

    updates_version = models.CharField(
        max_length=50,
        null=True,
        blank=True)

    objects = ConsentTypeManager()

    history = AuditTrail()

    def save(self, *args, **kwargs):
        if self.updates_version:
            self.updates_version = ''.join([s for s in self.updates_version if s != ' '])
            try:
                self.__class__.objects.get(
                    app_label=self.app_label,
                    model_name=self.model_name,
                    version__in=self.updates_version.split(','))
            except MultipleObjectsReturned:
                pass
            except self.__class__.DoesNotExist:
                raise ConsentTypeError(
                    'Consent version {1} cannot be an update to version(s) \'{0}\'. '
                    'Version(s) \'{0}\' not found in \'{2}\''.format(
                        self.updates_version.split(','), self.version, self.__class__._meta.verbose_name))
        try:
            other_consent_type = self.__class__.objects.get(
                (Q(start_datetime__range=(self.start_datetime, self.end_datetime)) |
                 Q(end_datetime__range=(self.start_datetime, self.end_datetime))),
                app_label=self.app_label,
                model_name=self.model_name)
            if other_consent_type.pk != self.id:
                raise ConsentTypeError(
                    'Consent period for version {0} overlaps with version \'{1}\'. '
                    'Got {2} to {3} overlaps with {4} to {5}.'.format(
                        self.updates_version, self.version,
                        other_consent_type.start_datetime.strftime('%Y-%m-%d'),
                        other_consent_type.end_datetime.strftime('%Y-%m-%d'),
                        self.start_datetime.strftime('%Y-%m-%d'),
                        self.end_datetime.strftime('%Y-%m-%d')))
        except self.__class__.DoesNotExist:
            pass
        super(ConsentType, self).save(*args, **kwargs)

    def natural_key(self):
        return (self.app_label, self.model_name, self.version)

    def __str__(self):
        return '{}.{} v{}'.format(self.app_label, self.model_name, self.version)

    def model_class(self):
        """Returns the consent model class."""
        return django_apps.get_model(self.app_label, self.model_name)

    class Meta:
        app_label = 'edc_consent'
        unique_together = (('app_label', 'model_name', 'version'),)
        ordering = ['app_label', 'model_name', 'version', 'updates_version']
