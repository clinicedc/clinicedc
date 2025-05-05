from edc_model.models import BaseUuidModel

from .model_mixins import ReferenceModelMixin


class NormalData(ReferenceModelMixin, BaseUuidModel):

    def __str__(self):
        return f"{self.label}: {self.description}"

    class Meta:
        verbose_name = "Normal Reference"
        verbose_name_plural = "Normal References"
