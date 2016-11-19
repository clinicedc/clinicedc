from django.apps import apps as django_apps
from django.db import models

from edc_base.model.fields import OtherCharField
from edc_base.model.validators import date_not_future
from edc_protocol.validators import date_not_before_study_start
from edc_registration.model_mixins import SubjectIdentifierModelMixin
from django.db.models import options

options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('offstudy_model',)


class OffstudyError(Exception):
    pass


class OffstudyModelManager(models.Manager):

    def get_by_natural_key(self, subject_identifier):
        return self.get(subject_identifier=subject_identifier)


class OffstudyModelMixin(SubjectIdentifierModelMixin, models.Model):
    """Mixin for the Off Study model."""

    offstudy_date = models.DateField(
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

    def natural_key(self):
        return (self.subject_identifier, )

    def __str__(self):
        return "{0} {1}".format(self.subject_identifier, self.offstudy_date.strftime('%Y-%m-%d'))

    def delete_future_appointments_on_offstudy(self):
        """Deletes appointments created after the off-study datetime.

        Called in the post-save signal."""
        app_config = django_apps.get_app_config('edc_appointment')
        Appointment = app_config.model
        Appointment.objects.filter(
            subject_identifier=self.subject_identifier,
            appt_datetime__gt=self.offstudy_date).delete()

    class Meta:
        abstract = True


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
                offstudy_date__lte=self.report_datetime.date(),
                subject_identifier=self.get_subject_identifier()
            )
            raise OffstudyError(
                'Participant was reported off study on \'{0}\'. Data reported after this date'
                ' cannot be captured.'.format(offstudy.offstudy_date.strftime('%Y-%m-%d')))
        except self.offstudy_model.DoesNotExist:
            offstudy = None
        return offstudy

    class Meta:
        abstract = True
        offstudy_model = None
