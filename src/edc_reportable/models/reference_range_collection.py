from django.db import models
from edc_model.models import BaseUuidModel


class ReferenceRangeCollection(BaseUuidModel):

    name = models.CharField(max_length=50, unique=True)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Reference Range Collection"
        verbose_name_plural = "Reference Range Collections"
