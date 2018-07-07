from django.conf import settings
from edc_model_wrapper import ModelWrapper

from ..models import ActionItem


class ActionItemModelWrapper(ModelWrapper):

    model_cls = ActionItem
    next_url_attrs = ['subject_identifier']
    next_url_name = settings.DASHBOARD_URL_NAMES.get('subject_dashboard_url')

    @property
    def subject_identifier(self):
        return self.object.subject_identifier
