from django.db import models
from edc_model import models as edc_models


class DxLocationModelMixin(models.Model):
    dx_location = models.ForeignKey(
        "edc_dx_review.diagnosislocations",
        verbose_name="Where was the diagnosis made?",
        on_delete=models.PROTECT,
        null=True,
        blank=False,
    )

    dx_location_other = edc_models.OtherCharField()

    class Meta:
        abstract = True
