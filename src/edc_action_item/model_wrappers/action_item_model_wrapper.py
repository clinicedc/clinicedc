from django.conf import settings
from edc_model_wrapper import ModelWrapper

from ..helpers import ActionItemHelper
from ..models import ActionItem


class ActionItemModelWrapper(ModelWrapper):

    model_cls = ActionItem
    next_url_attrs = ['subject_identifier']
    next_url_name = settings.DASHBOARD_URL_NAMES.get('subject_dashboard_url')

    def __init__(self, model_obj=None, **kwargs):
        super().__init__(model_obj=model_obj, **kwargs)
        helper = ActionItemHelper(model_wrapper=self)
        for key, value in helper.get_context().items():
            setattr(self, key, value)

    @property
    def subject_identifier(self):
        return self.object.subject_identifier

    @property
    def report_date(self):
        return self.object.report_datetime.date()
