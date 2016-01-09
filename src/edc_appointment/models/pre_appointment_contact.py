from django.db import models

from edc_base.audit_trail import AuditTrail
from edc_base.encrypted_fields import EncryptedTextField
from edc_base.model.models.base_uuid_model import BaseUuidModel
from edc_constants.choices import YES_NO
from edc_sync.models.sync_model_mixin import SyncModelMixin

from ..models import Appointment


class PreAppointmentContactManager(models.Manager):
    def get_by_natural_key(self, contact_datetime, visit_instance, visit_definition_code, subject_identifier_as_pk):
        RegisteredSubject = models.get_model('registration', 'RegisteredSubject')
        VisitDefinition = models.get_model('edc_visit_schedule', 'VisitDefinition')
        registered_subject = RegisteredSubject.objects.get_by_natural_key(subject_identifier_as_pk)
        visit_definition = VisitDefinition.objects.get_by_natural_key(visit_definition_code)
        appointment = Appointment.objects.get(
            registered_subject=registered_subject,
            visit_definition=visit_definition,
            visit_instance=visit_instance)
        return self.get(contact_datetime=contact_datetime, appointment=appointment)


class PreAppointmentContact(SyncModelMixin, BaseUuidModel):
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

    objects = PreAppointmentContactManager()

    history = AuditTrail()

    def natural_key(self):
        return (self.contact_datetime, ) + self.appointment.natural_key()

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
        unique_together = ('contact_datetime', 'appointment')
