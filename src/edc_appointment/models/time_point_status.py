from datetime import datetime

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django_crypto_fields.fields import EncryptedTextField

from simple_history.models import HistoricalRecords

from edc_base.model.models import BaseUuidModel
from edc_constants.constants import CLOSED, OPEN, NEW
from edc_constants.choices import YES_NO_NA

from edc_constants.constants import IN_PROGRESS

from ..mixins import SyncMixin

from .appointment import Appointment


class TimePointStatusManager(models.Manager):

    def get_by_natural_key(self, visit_instance, visit_definition_code, subject_identifier_as_pk):
        appointment = Appointment.objects.get_by_natural_key(
            visit_instance, visit_definition_code, subject_identifier_as_pk)
        return self.get(appointment=appointment)


class TimePointStatus(SyncMixin, BaseUuidModel):
    """ All completed appointments are noted in this form.

    Only authorized users can access this form. This form allows
    the user to definitely confirm that the appointment has
    been completed"""

    appointment = models.OneToOneField(Appointment)

    close_datetime = models.DateTimeField(
        verbose_name='Date and time appointment "closed" for edit.',
        default=datetime.today)

    status = models.CharField(
        max_length=15,
        choices=(
            (OPEN, 'Open'),
            ('feedback', 'Feedback'),
            (CLOSED, 'Closed')),
        default=OPEN,
        help_text='')

    comment = EncryptedTextField(
        max_length=500,
        null=True,
        blank=True)

    subject_withdrew = models.CharField(
        verbose_name='Did the participant withdraw consent?',
        max_length=15,
        choices=YES_NO_NA,
        default='N/A',
        null=True,
        help_text='Use ONLY when subject has changed mind and wishes to withdraw consent')

    reasons_withdrawn = models.CharField(
        verbose_name='Reason participant withdrew consent',
        max_length=35,
        choices=(
            ('changed_mind', 'Subject changed mind'),
            ('N/A', 'Not applicable')),
        null=True,
        default='N/A',
        help_text='')

    withdraw_datetime = models.DateTimeField(
        verbose_name='Date and time participant withdrew consent',
        null=True,
        blank=True)

    objects = TimePointStatusManager()

    # history = HistoricalRecords()

    def __unicode__(self):
        return "{}: {}".format(self.appointment, self.status.upper())

    def natural_key(self):
        return self.get_appointment().natural_key()

    @property
    def report_datetime(self):
        return self.close_datetime

    def save(self, *args, **kwargs):
        self.validate_status()
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
        if instance.status == CLOSED and instance.appointment.appt_status in [NEW, IN_PROGRESS]:
            raise exception_cls(
                'Cannot close timepoint. Appointment status is {0}.'.format(
                    instance.appointment.appt_status.upper()))

    def dashboard(self):
        ret = None
        if self.appointment:
            url = reverse(
                'subject_dashboard_url',
                kwargs={
                    'dashboard_type': self.appointment.registered_subject.subject_type.lower(),
                    'dashboard_model': 'appointment',
                    'dashboard_id': self.appointment.pk,
                    'show': 'appointments'})
            ret = """<a href="{url}" />dashboard</a>""".format(url=url)
        return ret
    dashboard.allow_tags = True

    class Meta:
        app_label = "edc_appointment"
        verbose_name = "Time Point Completion"
        verbose_name_plural = "Time Point Completion"
