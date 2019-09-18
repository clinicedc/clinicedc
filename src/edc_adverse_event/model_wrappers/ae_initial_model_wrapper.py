from django.conf import settings
from edc_model_wrapper import ModelWrapper


class AeInitialModelWrapper(ModelWrapper):

    model = f"{settings.ADVERSE_EVENT_APP_LABEL}.aeinitial"
    next_url_name = "ae_listboard_url"
    next_url_attrs = ["subject_identifier"]

    @property
    def pk(self):
        return str(self.object.pk)

    @property
    def subject_identifier(self):
        return self.object.subject_identifier
