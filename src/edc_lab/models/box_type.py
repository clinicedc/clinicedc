from django.db import models

from edc_base.model_mixins import BaseUuidModel

FILL_ORDER = (
    ('across', 'Across'),
    ('down', 'Down'),
)


class BoxTypeManager(models.Manager):

    def get_by_natural_key(self, name):
        return self.get(name=name)


class BoxType(BaseUuidModel):

    name = models.CharField(
        max_length=25,
        unique=True,
        help_text="a unique name to describe this box type")

    across = models.IntegerField(
        help_text="number of cells in a row counting from left to right")

    down = models.IntegerField(
        help_text="number of cells in a column counting from top to bottom")

    total = models.IntegerField(
        help_text="total number of cells in this box type")

    fill_order = models.CharField(
        max_length=15,
        default='across',
        choices=FILL_ORDER)

    objects = BoxTypeManager()

    def __str__(self):
        return '{} max={}'.format(self.name, self.total)

    def natural_key(self):
        return (self.name, )

    class Meta:
        app_label = 'edc_lab'
        ordering = ('name', )
