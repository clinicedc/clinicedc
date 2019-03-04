from django.conf import settings
from edc_model_wrapper import ModelWrapper

from ..dashboard_urls import dashboard_urls


class RequisitionModelWrapper(ModelWrapper):

    model = settings.LAB_DASHBOARD_REQUISITION_MODEL
    next_url_name = dashboard_urls.get("requisition_listboard_url")
    next_url_attrs = ["appointment", "subject_identifier"]
    querystring_attrs = ["subject_visit", "panel"]

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
    def panel(self):
        return str(self.object.panel.id)
