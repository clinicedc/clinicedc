from django.db import models
from django_pylabels.models import LabelSpecification

from edc_model.models import BaseUuidModel
from edc_pylabels.site_label_configs import site_label_configs


class LabelConfigurationError(Exception):
    pass


class LabelConfiguration(BaseUuidModel):

    name = models.CharField(
        verbose_name="System config name",
        max_length=50,
        unique=True,
        help_text="Name of configuration registered with site_label_config.",
    )

    label_specification = models.ForeignKey(LabelSpecification, on_delete=models.PROTECT)

    requires_allocation = models.BooleanField(
        verbose_name="Configuration is for a subject label", default=False
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name not in site_label_configs.all():
            raise LabelConfigurationError(
                "Label configuration not registered with site_label_config."
            )
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Label configuration"
        verbose_name_plural = "Label configurations"
