from edc_lab.models import Box
from edc_model_wrapper import ModelWrapper

from ..dashboard_urls import dashboard_urls


class BoxModelWrapper(ModelWrapper):

    model_cls = Box
    next_url_name = dashboard_urls.get("pack_listboard_url")

    @property
    def human_readable_identifier(self):
        return self.object.human_readable_identifier
