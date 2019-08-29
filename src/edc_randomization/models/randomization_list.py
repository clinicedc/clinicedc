from edc_model.models import BaseUuidModel

from .model_mixin import RandomizationListModelMixin


class RandomizationList(RandomizationListModelMixin, BaseUuidModel):
    class Meta(RandomizationListModelMixin.Meta):
        pass
