from django.conf import settings
from edc_model_wrapper import ModelWrapper


class SubjectVisitModelWrapper(ModelWrapper):

    model = None
    next_url_attrs = ['subject_identifier', 'appointment', 'reason']
    next_url_name = settings.DASHBOARD_URL_NAMES.get('subject_dashboard_url')

    @property
    def appointment(self):
        return str(self.object.appointment.id)

    @property
    def subject_identifier(self):
        return self.object.subject_identifier
