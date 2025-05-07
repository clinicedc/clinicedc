from edc_model.models import BaseUuidModel

# from ..normal_reference import NormalReference
from .model_mixins import ReferenceModelMixin


class NormalData(ReferenceModelMixin, BaseUuidModel):

    def __str__(self):
        return f"{self.label}: {self.description}"

    # @property
    # def reference(self) -> NormalReference:
    #     return NormalReference(self.__dict__)

    class Meta:
        verbose_name = "Normal Reference"
        verbose_name_plural = "Normal References"
