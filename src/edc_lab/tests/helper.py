from __future__ import annotations

from lab_app.models import SubjectScreening

from edc_appointment.tests.helper import Helper as BaseHelper


class Helper(BaseHelper):
    @property
    def screening_model_cls(self):
        return SubjectScreening
