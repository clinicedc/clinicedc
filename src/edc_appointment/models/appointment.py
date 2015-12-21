from django.db import models

from edc_base.audit_trail import AuditTrail
from edc_registration.models import RegisteredSubject

from ..mixins import SyncMixin

from .base_appointment import BaseAppointment


class Appointment(SyncMixin, BaseAppointment):

    registered_subject = models.ForeignKey(RegisteredSubject)

    history = AuditTrail()

    class Meta:
        app_label = 'edc_appointment'
        unique_together = (('registered_subject', 'visit_definition', 'visit_instance'),)
        ordering = ['registered_subject', 'appt_datetime', ]
