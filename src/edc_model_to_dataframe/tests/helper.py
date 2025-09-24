from __future__ import annotations

from typing import TYPE_CHECKING

from clinicedc_tests.helper import Helper as BaseHelper
from clinicedc_tests.models import SubjectScreening

if TYPE_CHECKING:
    from edc_appointment.models import Appointment


class Helper(BaseHelper):
    @property
    def screening_model_cls(self):
        return SubjectScreening

    def create_unscheduled(self, appointment: Appointment):
        return self.add_unscheduled_appointment(appointment)
