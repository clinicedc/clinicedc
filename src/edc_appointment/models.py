from django.db.models.signals import post_save
from django.dispatch import receiver

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.apps import apps as django_apps
from django_crypto_fields.fields import EncryptedTextField
from django.utils import timezone

from edc_base.model.models import BaseUuidModel
from edc_constants.choices import YES_NO_NA
from edc_constants.constants import CLOSED, OPEN, NEW_APPT, IN_PROGRESS, NOT_APPLICABLE
from simple_history.models import HistoricalRecords


class Holiday(BaseUuidModel):

    holiday_name = models.CharField(
        max_length=25,
        default='holiday')
    holiday_date = models.DateField(
        unique=True)

    objects = models.Manager()

    def __unicode__(self):
        return "%s on %s" % (self.holiday_name, self.holiday_date)

    class Meta:
        ordering = ['holiday_date', ]
        app_label = 'edc_appointment'


class TimePointStatusManager(models.Manager):

    def get_by_natural_key(self, subject_identifier, visit_code):
        return self.get(subject_identifier=subject_identifier, visit_code=visit_code)


class TimePointStatus(BaseUuidModel):
    """ All completed appointments are noted in this form.

    Only authorized users can access this form. This form allows
    the user to definitely confirm that the appointment has
    been completed"""

    visit_code = models.CharField(max_length=15)

    subject_identifier = models.CharField(max_length=25)

    close_datetime = models.DateTimeField(
        verbose_name='Date closed.',
        null=True,
        blank=True)

    status = models.CharField(
        max_length=15,
        choices=(
            (OPEN, 'Open'),
            ('feedback', 'Feedback'),
            (CLOSED, 'Closed')),
        default=OPEN)

    comment = EncryptedTextField(
        max_length=500,
        null=True,
        blank=True)

    subject_withdrew = models.CharField(
        verbose_name='Did the participant withdraw consent?',
        max_length=15,
        choices=YES_NO_NA,
        default=NOT_APPLICABLE,
        null=True,
        help_text='Use ONLY when subject has changed mind and wishes to withdraw consent')

    reasons_withdrawn = models.CharField(
        verbose_name='Reason participant withdrew consent',
        max_length=35,
        choices=(
            ('changed_mind', 'Subject changed mind'),
            (NOT_APPLICABLE, 'Not applicable')),
        null=True,
        default=NOT_APPLICABLE)

    withdraw_datetime = models.DateTimeField(
        verbose_name='Date and time participant withdrew consent',
        null=True,
        blank=True)

    objects = TimePointStatusManager()

    history = HistoricalRecords()

    def __unicode__(self):
        return "{}".format(self.status.upper())

    def natural_key(self):
        return (self.subject_identifier, self.visit_code)

    def get_report_datetime(self):
        return self.close_datetime

    def save(self, *args, **kwargs):
        self.validate_status()
        if self.status == CLOSED and not self.close_datetime:
            self.close_datetime = timezone.now()
        else:
            self.close_datetime = None
        super(TimePointStatus, self).save(*args, **kwargs)

    def status_display(self):
        """Formats and returns the status for the dashboard."""
        if self.status == OPEN:
            return '<span style="color:green;">Open</span>'
        elif self.status == CLOSED:
            return '<span style="color:red;">Closed</span>'
        elif self.status == 'feedback':
            return '<span style="color:orange;">Feedback</span>'
    status_display.allow_tags = True

    def validate_status(self, instance=None, exception_cls=None):
        """Closing off only appt that are either done/incomplete/cancelled ONLY."""
        exception_cls = exception_cls or ValidationError
        instance = instance or self
        if instance.status == CLOSED:
            for appointment in self.get_appointments():
                if appointment.appt_status in [NEW_APPT, IN_PROGRESS]:
                    raise exception_cls(
                        'Cannot close timepoint. Appointment status is {0}.'.format(
                            appointment.appt_status.upper()))

    @property
    def appointment_app_config(self):
        return django_apps.get_app_config('edc_appointment')

    @property
    def appointment_model(self):
        return self.appointment_app_config.appointment_model

    def get_appointments(self):
        return self.appointment_model.objects.filter(time_point_status__pk=self.pk)

    @property
    def base_appointment(self):
        return self.appointment_model.objects.get(
            time_point_status__pk=self.pk, visit_instance='0')

    def dashboard(self):
        url = reverse('subject_dashboard_url',
                      kwargs={'dashboard_type': self.base_appointment.registered_subject.subject_type.lower(),
                              'dashboard_model': 'appointment',
                              'dashboard_id': self.base_appointment.pk,
                              'show': 'appointments'})
        return """<a href="{url}" />dashboard</a>""".format(url=url)

    dashboard.allow_tags = True

    class Meta:
        app_label = "edc_appointment"
        verbose_name = "Time Point Completion"
        verbose_name_plural = "Time Point Completion"
        ordering = ['subject_identifier', 'visit_code']
        unique_together = ('subject_identifier', 'visit_code')


@receiver(post_save, weak=False, dispatch_uid="appointment_post_save")
def appointment_post_save(sender, instance, raw, created, using, **kwargs):
    """Creates the TimePointStatus instance if it does not already exist."""
    if not raw:
        try:
            if not instance.time_point_status:
                try:
                    instance.time_point_status = TimePointStatus.objects.get(
                        visit_code=instance.visit_definition.code,
                        subject_identifier=instance.registered_subject.subject_identifier)
                except TimePointStatus.DoesNotExist:
                    instance.time_point_status = TimePointStatus.objects.create(
                        visit_code=instance.visit_definition.code,
                        subject_identifier=instance.registered_subject.subject_identifier)
                instance.save(update_fields=['time_point_status'])
        except AttributeError as e:
            if 'time_point_status' not in str(e):
                raise AttributeError(str(e))
