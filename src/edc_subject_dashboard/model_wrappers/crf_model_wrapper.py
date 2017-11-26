from edc_model_wrapper import ModelWrapper
from django.conf import settings


class CrfModelWrapper(ModelWrapper):

    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'subject_dashboard_url')
    next_url_attrs = ['appointment', 'subject_identifier']
    querystring_attrs = ['subject_visit']

    @property
    def subject_visit(self):
        return str(self.object.subject_visit.id)

    @property
    def appointment(self):
        return str(self.object.subject_visit.appointment.id)

    @property
    def subject_identifier(self):
        return self.object.subject_visit.subject_identifier
