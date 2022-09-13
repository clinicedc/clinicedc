from edc_model.models import BaseUuidModel

from .container_model_mixin import ContainerModelMixin


class GenericContainer(ContainerModelMixin, BaseUuidModel):
    class Meta(ContainerModelMixin.Meta, BaseUuidModel.Meta):
        verbose_name = "Item"
        verbose_name_plural = "Items"
