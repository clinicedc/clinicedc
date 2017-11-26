from django.apps import apps as django_apps
from edc_model_wrapper import ModelWrapper

from ..dashboard_urls import dashboard_urls

edc_lab_app_config = django_apps.get_app_config('edc_lab')


class RequisitionModelWrapper(ModelWrapper):

    model = edc_lab_app_config.requisition_model
    next_url_name = dashboard_urls.get('requisition_listboard_url')
    # querystring_attrs = ['subject_visit']
    next_url_attrs = ['appointment', 'subject_identifier']
    querystring_attrs = ['subject_visit', 'panel_name']

    @property
    def subject_visit(self):
        return str(self.object.subject_visit.id)

    @property
    def appointment(self):
        return str(self.object.subject_visit.appointment.id)

    @property
    def subject_identifier(self):
        return self.object.subject_visit.subject_identifier

    @property
    def panel_name(self):
        return self.object.panel_name
