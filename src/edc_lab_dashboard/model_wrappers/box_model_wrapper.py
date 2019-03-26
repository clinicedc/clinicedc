from edc_lab.models import Box
from edc_model_wrapper import ModelWrapper


class BoxModelWrapper(ModelWrapper):

    model_cls = Box
    next_url_name = "pack_listboard_url"

    @property
    def human_readable_identifier(self):
        return self.object.human_readable_identifier
