from django.db import models

from simple_history.models import HistoricalRecords

from edc_registration.models import RegisteredSubject

from .base_appointment import BaseAppointment

try:
    from edc_sync.mixins import SyncMixin
except ImportError:
    SyncMixin = type('SyncMixin', (object, ), {})


class Appointment(SyncMixin, BaseAppointment):

    registered_subject = models.ForeignKey(RegisteredSubject)

    history = HistoricalRecords()

    class Meta:
        app_label = 'edc_appointment'
        unique_together = (('registered_subject', 'visit_definition', 'visit_instance'),)
        ordering = ['registered_subject', 'appt_datetime', ]
