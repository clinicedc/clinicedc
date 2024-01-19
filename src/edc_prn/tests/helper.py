from edc_appointment.tests.helper import Helper as BaseHelper

from prn_app.models import SubjectScreening


class Helper(BaseHelper):
    @property
    def screening_model_cls(self):
        return SubjectScreening
