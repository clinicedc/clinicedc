from django.db import models
from django_pylabels.models import LabelSpecification
from edc_model.models import BaseUuidModel


class LabelConfiguration(BaseUuidModel):

    name = models.CharField(
        max_length=25,
        unique=True,
        help_text="Name of configuration registered with site_label_config.",
    )

    label_specification = models.ForeignKey(LabelSpecification, on_delete=models.PROTECT)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Label configuration"
        verbose_name_plural = "Label configurations"
