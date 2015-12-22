from django.db import models

from edc_base.audit_trail import AuditTrail
from edc.subject.contact.models import BaseContactLogItem

from ..models import Appointment


class PreAppointmentContact(BaseContactLogItem):
    """Tracks contact, modifies appt_datetime, changes type and confirms and appointment."""

    appointment = models.ForeignKey(Appointment)

    is_confirmed = models.BooleanField(
        verbose_name='Appointment confirmed',
        default=False)

    history = AuditTrail()

    objects = models.Manager()

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
        db_table = 'bhp_appointment_preappointmentcontact'
