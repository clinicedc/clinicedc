from django.db import models
from edc_model import models as edc_models

from ..utils import get_list_model_app


class DxLocationModelMixin(models.Model):

    dx_location = models.ForeignKey(
        f"{get_list_model_app()}.diagnosislocations",
        verbose_name="Where was the diagnosis made?",
        on_delete=models.PROTECT,
    )

    dx_location_other = edc_models.OtherCharField()

    class Meta:
        abstract = True
