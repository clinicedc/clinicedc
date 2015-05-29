from django.db import models
from django_crypto_fields.fields import EncryptedTextField

from simple_history.models import HistoricalRecords

# from edc.audit.audit_trail import AuditTrail

from edc_base.model.models import BaseUuidModel
from edc_constants.choices import YES_NO

from .appointment import Appointment


class PreAppointmentContact(BaseUuidModel):
    """Tracks contact, modifies appt_datetime, changes type and confirms and edc_appointment."""

    appointment = models.ForeignKey(Appointment)

    is_confirmed = models.BooleanField(
        verbose_name='Appointment confirmed',
        default=False,
    )

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

    # history = AuditTrail()
    history = HistoricalRecords()

    objects = models.Manager()

    def get_requires_consent(self):
        return False

    def get_subject_identifier(self):
        return self.appointment.get_subject_identifier()

    def get_report_datetime(self):
        return self.appointment.get_report_datetime()

    def __unicode__(self):
        return str(self.appointment)

    class Meta:
        app_label = 'edc_appointment'
        db_table = 'bhp_appointment_preappointmentcontact'
