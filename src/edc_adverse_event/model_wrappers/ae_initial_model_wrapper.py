from edc_model_wrapper import ModelWrapper

from ..utils import get_adverse_event_app_label


class AeInitialModelWrapper(ModelWrapper):
    model = f"{get_adverse_event_app_label()}.aeinitial"
    next_url_name = "ae_listboard_url"
    next_url_attrs = ["subject_identifier"]

    @property
    def pk(self):
        return str(self.object.pk)

    @property
    def subject_identifier(self):
        return self.object.subject_identifier
