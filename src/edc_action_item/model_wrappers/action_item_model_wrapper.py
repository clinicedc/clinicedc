from edc_model_wrapper import ModelWrapper

from ..helpers import ActionItemHelper
from ..models import ActionItem


class ActionItemModelWrapper(ModelWrapper):

    model_cls = ActionItem
    next_url_attrs = ["subject_identifier"]
    next_url_name = "subject_dashboard_url"

    def __init__(self, model_obj=None, **kwargs):
        super().__init__(model_obj=model_obj, **kwargs)
        helper = ActionItemHelper(action_item=self.object, href=self.href)
        for key, value in helper.get_context().items():
            try:
                setattr(self, key, value)
            except AttributeError as e:
                raise AttributeError(f"{e}. Got {key}, {value}")

    @property
    def subject_identifier(self):
        return self.object.subject_identifier

    @property
    def report_date(self):
        return self.object.report_datetime.date()
