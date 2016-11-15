from django.apps import apps as django_apps
from django.db import models
from django.db.models import options

from edc_base.model.fields import OtherCharField
from edc_base.model.validators import date_not_future
from edc_protocol.validators import date_not_before_study_start
from edc_registration.model_mixins import SubjectIdentifierModelMixin

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

    objects = OffstudyModelManager()

    def natural_key(self):
        return (self.subject_identifier, )

    def __str__(self):
        return "{0} {1}".format(self.subject_identifier, self.offstudy_date.strftime('%Y-%m-%d'))

    class Meta:
        abstract = True


class OffstudyMixin(models.Model):

    """A mixin for CRF models to add the ability to determine
    if the subject is off study."""

    def save(self, *args, **kwargs):
        self.is_offstudy_or_raise()
        super(OffstudyMixin, self).save(*args, **kwargs)

    def get_subject_identifier(self):
        try:
            subject_identifier = self.visit.appointment.subject_identifier
        except AttributeError:
            None
        return subject_identifier

    @property
    def offstudy_model(self):
        return django_apps.get_model(*self._meta.offstudy_model.split('.'))

    def is_offstudy_or_raise(self):
        """Return True if the off-study report exists or
        a previous visit reason is off study, otherwise False.

        Once consented, a subject must be deliberately taken
        "off study" using a model that uses the
        :class:`edc_offstudy.models.OffstudyModelMixin`."""

        subject_identifier = self.get_subject_identifier()
        if not subject_identifier:
            raise ValueError(
                '{} cannot determine the subject identifier. '
                'Got None'.format(self.__class__.__name__))
        try:
            report_datetime = self.report_datetime
        except AttributeError:
            report_datetime = self.get_report_datetime()
        report_date = report_datetime.date()
        offstudy = self.has_offstudy_report_or_raise(subject_identifier, report_date)
        return offstudy

    def has_offstudy_report_or_raise(self, subject_identifier, report_date):
        """Raises an exception if an off study report exists for this subject with an
        off study date before the report_date."""
        try:
            offstudy = self.offstudy_model.objects.get(
                offstudy_date__lt=report_date,
                subject_identifier=subject_identifier
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
