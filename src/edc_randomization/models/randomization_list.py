from edc_model.models import BaseUuidModel

from ..model_mixins import RandomizationListModelMixin


class RandomizationList(RandomizationListModelMixin, BaseUuidModel):
    class Meta(RandomizationListModelMixin.Meta, BaseUuidModel.Meta):
        pass
