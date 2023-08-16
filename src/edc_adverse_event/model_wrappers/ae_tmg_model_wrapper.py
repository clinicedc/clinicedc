from edc_model_wrapper import ModelWrapper

from ..utils import get_adverse_event_app_label


class AeTmgModelWrapper(ModelWrapper):
    next_url_name = "tmg_ae_listboard_url"
    model = f"{get_adverse_event_app_label()}.aetmg"
    next_url_attrs = ["subject_identifier"]

    @property
    def pk(self):
        return str(self.object.pk)

    @property
    def subject_identifier(self):
        return self.object.subject_identifier
