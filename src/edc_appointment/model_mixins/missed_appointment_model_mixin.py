from django.db import models

from edc_appointment.constants import MISSED_APPT


class MissedAppointmentModelMixin(models.Model):
    def create_missed_visit_from_appointment(self):
        if self.appt_timing == MISSED_APPT:
            self.visit_model_cls().objects.create_missed_from_appointment(
                appointment=self,
            )

    class Meta:
        abstract = True
