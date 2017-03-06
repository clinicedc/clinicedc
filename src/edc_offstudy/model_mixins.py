from django.apps import apps as django_apps
from django.db import models
from django.utils import timezone

from edc_base.model_fields import OtherCharField
from edc_base.model_validators import datetime_not_future
from edc_protocol.validators import datetime_not_before_study_start
from edc_identifier.model_mixins import UniqueSubjectIdentifierFieldMixin
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from dateutil.relativedelta import relativedelta
from django.db.models import options

options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('consent_model', )


class OffstudyError(Exception):
    pass


class OffstudyModelManager(models.Manager):

    def get_by_natural_key(self, subject_identifier):
        return self.get(subject_identifier=subject_identifier)


class OffstudyModelMixin(UniqueSubjectIdentifierFieldMixin, models.Model):
    """Mixin for the Off Study model."""
    dateformat = '%Y-%m-%d %H:%M'

    offstudy_datetime = models.DateTimeField(
        verbose_name="Off-study Date",
        validators=[
            datetime_not_before_study_start,
            datetime_not_future])

    reason = models.CharField(
        verbose_name="Please code the primary reason participant taken off-study",
        max_length=115)

    reason_other = OtherCharField()

    comment = models.TextField(
        max_length=250,
        verbose_name="Comment",
        blank=True,
        null=True)

    objects = OffstudyModelManager()

    def save(self, *args, **kwargs):
        if not self.consented_before_offstudy:
            raise OffstudyError('Offstudy date may not be before the date of consent. Got {}.'.format(
                timezone.localtime(self.offstudy_datetime).strftime(self.dateformat)))
        self.offstudy_datetime_after_last_visit_or_raise()
        app_config = django_apps.get_app_config('edc_appointment')
        Appointment = app_config.model
        Appointment.objects.delete_for_subject_after_date(
            self.subject_identifier, self.offstudy_datetime)
        super(OffstudyModelMixin, self).save(*args, **kwargs)

    def natural_key(self):
        return (self.subject_identifier, )

    def __str__(self):
        return "{0} {1}".format(
            self.subject_identifier, timezone.localtime(self.offstudy_datetime).strftime(self.dateformat))

    @property
    def consented_before_offstudy(self):
        consent = None
        try:
            Consent = django_apps.get_model(*self._meta.consent_model.split('.'))
            consent = Consent.objects.get(
                subject_identifier=self.subject_identifier,
                consent_datetime__lte=self.offstudy_datetime)
        except Consent.DoesNotExist:
            consent = None
        except AttributeError as e:
            if 'consent_model' in str(e):
                raise AttributeError('For model {} got: {}'.format(self._meta.label_lower, str(e)))
            raise OffstudyError(str(e))
        return consent

    def offstudy_datetime_after_last_visit_or_raise(self):
        try:
            last_visit_datetime = site_visit_schedules.last_visit_datetime(self.subject_identifier)
            if relativedelta(self.offstudy_datetime, last_visit_datetime).days < 0:
                raise OffstudyError(
                    'Offstudy datetime cannot precede the last visit datetime {}. Got {}'.format(
                        timezone.localtime(last_visit_datetime),
                        timezone.localtime(self.offstudy_datetime)))
        except AttributeError as e:
            raise OffstudyError(str(e))

    class Meta:
        abstract = True
        consent_model = None


class OffstudyMixin(models.Model):

    """A mixin for CRF models to add the ability to determine
    if the subject is off study."""

    def save(self, *args, **kwargs):
        self.is_offstudy_or_raise()
        super(OffstudyMixin, self).save(*args, **kwargs)

    @property
    def offstudy_model(self):
        try:
            return self.visit.schedule.offstudy_model
        except AttributeError as e:
            if 'visit' in str(e):
                try:
                    return self.schedule.offstudy_model
                except AttributeError as e:
                    raise OffstudyError(str(e))
            else:
                raise OffstudyError(str(e))

    def is_offstudy_or_raise(self):
        """Return True if the off-study report exists. """
        try:
            offstudy = self.offstudy_model.objects.get(
                offstudy_datetime__lte=self.report_datetime,
                subject_identifier=self.subject_identifier
            )
            raise OffstudyError(
                'Participant was reported off study on \'{0}\'. Data reported after this date'
                ' cannot be captured.'.format(timezone.localtime(offstudy.offstudy_datetime).strftime('%Y-%m-%d')))
        except self.offstudy_model.DoesNotExist:
            offstudy = None
        return offstudy

    class Meta:
        abstract = True
