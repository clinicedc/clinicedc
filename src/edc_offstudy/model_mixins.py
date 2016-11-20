from django.apps import apps as django_apps
from django.db import models
from django.db.models import Max
from django.utils import timezone

from edc_base.model.fields import OtherCharField
from edc_base.model.validators import datetime_not_future
from edc_protocol.validators import datetime_not_before_study_start
from edc_registration.model_mixins import SubjectIdentifierModelMixin
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from dateutil.relativedelta import relativedelta


class OffstudyError(Exception):
    pass


class OffstudyModelManager(models.Manager):

    def get_by_natural_key(self, subject_identifier):
        return self.get(subject_identifier=subject_identifier)


class OffstudyModelMixin(SubjectIdentifierModelMixin, models.Model):
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

    def save(self, *args, **kwargs):
        if not self.consented_before_offstudy:
            raise OffstudyError('Offstudy date may not be before the date of consent. Got {}.'.format(
                timezone.localtime(self.offstudy_datetime).strftime(self.dateformat)))
        app_config = django_apps.get_app_config('edc_appointment')
        self.validate_offstudy_datetime()
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
        return consent

    def validate_offstudy_datetime(self):
        if relativedelta(self.offstudy_datetime, self.last_visit_datetime).days < 0:
            raise OffstudyError('Offstudy datetime cannot precede the last visit datetime {}. Got {}'.format(
                timezone.localtime(self.last_visit_datetime), timezone.localtime(self.offstudy_datetime)))

    @property
    def last_visit_datetime(self):
        visit_models = []
        max_visit_datetimes = []
        for visit_schedule in site_visit_schedules.registry.values():
            if visit_schedule.visit_model not in visit_models:
                visit_models.append(visit_schedule.visit_model)
                last_visit = visit_schedule.visit_model.objects.last_visit()
                if last_visit:
                    max_visit_datetimes.append(last_visit.report_datetime)
        if max_visit_datetimes:
            return max(max_visit_datetimes)
        return None

    class Meta:
        abstract = True
        consent_model = None
        visit_schedule_name = None


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
        except AttributeError:
            return self.schedule.offstudy_model

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
