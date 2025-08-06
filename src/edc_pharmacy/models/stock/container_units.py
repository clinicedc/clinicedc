from django.db import models

from edc_list_data.model_mixins import ListModelMixin


class ContainerUnits(ListModelMixin):
    """Container Units Model

    For example, tablets, ml, etc
    """

    display_name = models.CharField(
        verbose_name="Name",
        max_length=250,
        unique=True,
        null=True,
        blank=True,
        help_text="(suggest 40 characters max.)",
    )

    class Meta(ListModelMixin.Meta):
        verbose_name = "Container units"
        verbose_name_plural = "Container units"
