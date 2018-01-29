from edc_model_wrapper import ModelWrapper
from django.conf import settings


class CrfModelWrapper(ModelWrapper):

    visit_model_attr = 'subject_visit'

    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'subject_dashboard_url')
    next_url_attrs = ['appointment', 'subject_identifier']
    querystring_attrs = [visit_model_attr]

    @property
    def subject_visit(self):
        return str(getattr(self.object, self.visit_model_attr).id)

    @property
    def appointment(self):
        return str(getattr(self.object, self.visit_model_attr).appointment.id)

    @property
    def subject_identifier(self):
        return getattr(self.object, self.visit_model_attr).subject_identifier
