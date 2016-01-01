from django.db import models

from edc_base.audit_trail import AuditTrail
from edc_base.encrypted_fields import EncryptedTextField
from edc_constants.choices import YES_NO

from ..models import Appointment


class PreAppointmentContact(models.Model):
    """Tracks contact, modifies appt_datetime, changes type and confirms and appointment."""

    appointment = models.ForeignKey(Appointment)

    is_confirmed = models.BooleanField(
        verbose_name='Appointment confirmed',
        default=False)
    contact_datetime = models.DateTimeField(
        verbose_name='Date of call')

    is_contacted = models.CharField(
        verbose_name='Did someone answer?',
        max_length=10,
        choices=YES_NO,
    )

    information_provider = models.CharField(
        verbose_name="Who answered?",
        max_length=20,
        help_text="",
        null=True,
        blank=True,
    )

    comment = EncryptedTextField(
        max_length=100,
        blank=True,
        null=True,
    )

    objects = models.Manager()

    history = AuditTrail()

    def get_requires_consent(self):
        return False

    def get_subject_identifier(self):
        return self.appointment.get_subject_identifier()

    def get_report_datetime(self):
        return self.appointment.get_report_datetime()

    def __unicode__(self):
        return unicode(self.appointment)

    class Meta:
        app_label = 'edc_appointment'
