from django.apps import apps as django_apps
from django.db import models
from django.utils import timezone

from edc_base.model.fields import OtherCharField
from edc_base.model.validators import date_not_future
from edc_protocol.validators import date_not_before_study_start
from edc_registration.model_mixins import SubjectIdentifierModelMixin
from django.db.models import options
from django.db.models.deletion import ProtectedError

options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('offstudy_model',)


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
            date_not_before_study_start,
            date_not_future])

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
        Appointment = app_config.model
        try:
            Appointment.objects.delete_for_subject_after_date(
                self.subject_identifier, self.offstudy_datetime, self._meta.visit_schedule_name)
        except ProtectedError:
            raise OffstudyError(
                'Cannot save Offstudy. Some appointments after {} '
                'already have visit reports.'.format(self.offstudy_datetime.strftime(self.dateformat)))
        super(OffstudyModelMixin, self).save(*args, **kwargs)

    def natural_key(self):
        return (self.subject_identifier, )

    def __str__(self):
        return "{0} {1}".format(self.subject_identifier, self.offstudy_datetime.strftime(self.dateformat))

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

    class Meta:
        abstract = True
        visit_schedule_name = None
        consent_model = None


class OffstudyMixin(models.Model):

    """A mixin for CRF models to add the ability to determine
    if the subject is off study."""

    def save(self, *args, **kwargs):
        self.is_offstudy_or_raise()
        super(OffstudyMixin, self).save(*args, **kwargs)

    @property
    def offstudy_model(self):
        return django_apps.get_model(*self._meta.offstudy_model.split('.'))

    def is_offstudy_or_raise(self):
        """Return True if the off-study report exists. """
        try:
            offstudy = self.offstudy_model.objects.get(
                offstudy_datetime__lte=self.report_datetime,
                subject_identifier=self.get_subject_identifier()
            )
            raise OffstudyError(
                'Participant was reported off study on \'{0}\'. Data reported after this date'
                ' cannot be captured.'.format(offstudy.offstudy_datetime.strftime('%Y-%m-%d')))
        except self.offstudy_model.DoesNotExist:
            offstudy = None
        return offstudy

    class Meta:
        abstract = True
        offstudy_model = None
