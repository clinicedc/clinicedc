from edc_model_wrapper import ModelWrapper
from django.conf import settings


class ActionItemModelWrapper(ModelWrapper):

    model = 'edc_action_item.actionitem'
    next_url_attrs = ['subject_identifier']
    next_url_name = settings.DASHBOARD_URL_NAMES.get('subject_dashboard_url')

    @property
    def subject_identifier(self):
        return self.object.subject_identifier
