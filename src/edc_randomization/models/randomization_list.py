from edc_model import models as edc_models

from ..model_mixins import RandomizationListModelMixin


class RandomizationList(RandomizationListModelMixin, edc_models.BaseUuidModel):
    class Meta(RandomizationListModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        pass
