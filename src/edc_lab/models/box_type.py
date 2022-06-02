from django.db import models
from edc_model import models as edc_models

from ..choices import FILL_ORDER
from ..constants import FILL_ACROSS


class BoxTypeManager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, name):
        return self.get(name=name)


class BoxType(edc_models.BaseUuidModel):

    name = models.CharField(
        max_length=25, unique=True, help_text="a unique name to describe this box type"
    )

    across = models.IntegerField(
        help_text="number of cells in a row counting from left to right"
    )

    down = models.IntegerField(
        help_text="number of cells in a column counting from top to bottom"
    )

    total = models.IntegerField(help_text="total number of cells in this box type")

    fill_order = models.CharField(max_length=15, default=FILL_ACROSS, choices=FILL_ORDER)

    objects = BoxTypeManager()

    def __str__(self):
        return f"{self.name} max={self.total}"

    def natural_key(self):
        return (self.name,)  # noqa

    class Meta(edc_models.BaseUuidModel.Meta):
        verbose_name = "Box Type"
        ordering = ("name",)
