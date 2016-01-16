from django.db import models

from edc_appointment.models import Appointment


class VisitManager(models.Manager):

    def get_by_natural_key(self, visit_instance, visit_definition_code, subject_identifier_as_pk):
        appointment = Appointment.objects.get_by_natural_key(
            visit_instance, visit_definition_code, subject_identifier_as_pk)
        return self.get(appointment=appointment)
