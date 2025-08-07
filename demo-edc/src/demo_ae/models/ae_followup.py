from edc_adverse_event.model_mixins import AeFollowupModelMixin
from edc_model.models import BaseUuidModel


class AeFollowup(AeFollowupModelMixin, BaseUuidModel):
    class Meta(AeFollowupModelMixin.Meta, BaseUuidModel.Meta):
        pass
