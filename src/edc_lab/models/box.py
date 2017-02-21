import re

from django.db import models
from django.db.models.deletion import PROTECT
from django.utils import timezone

from edc_base.model.models import BaseUuidModel, HistoricalRecords
from edc_constants.constants import OTHER, CLOSED, OPEN
from edc_dashboard.model_mixins import SearchSlugModelMixin, SearchSlugManager

from ..identifier.box_identifier import BoxIdentifier
from .aliquot import pattern as aliquot_identifier_pattern

BOX_DIMENSIONS = (
    ('8 x 8', '8 x 8'),
    ('9 x 9', '9 x 9'),
    ('10 x 10', '10 x 10'),
)

BOX_CATEGORY = (
    ('testing', 'Testing'),
    ('storage', 'Storage'),
    (OTHER, 'Other'),
)

STATUS = (
    (OPEN, 'Open'),
    (CLOSED, 'Closed'),
)

FILL_ORDER = (
    ('across', 'Across'),
    ('down', 'Down'),
)

human_readable_pattern = '^[A-Z]{3}\-[0-9]{4}\-[0-9]{2}$'


class BoxTypeManager(models.Manager):

    def get_by_natural_key(self, name):
        return self.get(name=name)


class BoxManager(SearchSlugManager, models.Manager):

    def get_by_natural_key(self, box_identifier):
        return self.get(box_identifier=box_identifier)


class BoxItemManager(models.Manager):

    def get_by_natural_key(self, position, identifier, box_identifier):
        return self.get(
            position=position,
            identifier=identifier,
            box_identifier=box_identifier)


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

    def natural_key(self):
        return (self.name, )

    class Meta:
        app_label = 'edc_lab'
        ordering = ('name', )


class Box(SearchSlugModelMixin, BaseUuidModel):

    box_identifier = models.CharField(
        max_length=25,
        editable=False,
        unique=True)

    name = models.CharField(
        max_length=25,
        null=True,
        blank=True)

    box_datetime = models.DateTimeField(
        default=timezone.now)

    box_type = models.ForeignKey(
        BoxType, on_delete=PROTECT)

    category = models.CharField(
        max_length=25,
        default='testing',
        choices=BOX_CATEGORY)

    category_other = models.CharField(
        max_length=25,
        null=True,
        blank=True)

    specimen_types = models.CharField(
        max_length=25,
        help_text=(
            'List of specimen types in this box. Use two-digit numeric '
            'codes separated by commas.'))

    status = models.CharField(
        max_length=15,
        default=OPEN,
        choices=STATUS)

    comment = models.TextField(
        null=True,
        blank=True)

    objects = BoxManager()

    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if not self.box_identifier:
            self.box_identifier = BoxIdentifier().identifier
        if not self.name:
            self.name = self.box_identifier
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.box_identifier, )

    @property
    def count(self):
        return self.boxitem_set.all().count()

    @property
    def items(self):
        return self.boxitem_set.all().order_by('position')

    @property
    def human_box_identifier(self):
        x = self.box_identifier
        return '{}-{}-{}'.format(x[0:3], x[3:7], x[7:9])

    @property
    def next_position(self):
        """Returns an integer or None.
        """
        last_obj = self.boxitem_set.all().order_by('position').last()
        if not last_obj:
            next_position = 1
        else:
            next_position = last_obj.position + 1
        if next_position > self.box_type.total:
            next_position = None
        return next_position

    @property
    def max_position(self):
        return

    def get_slugs(self):
        slugs = [self.box_identifier,
                 self.human_box_identifier,
                 self.name]
        return slugs

    class Meta:
        app_label = 'edc_lab'
        ordering = ('-box_datetime', )
        verbose_name_plural = 'Boxes'


class BoxItem(BaseUuidModel):

    box = models.ForeignKey(Box, on_delete=PROTECT)

    position = models.IntegerField(null=True)

    identifier = models.CharField(
        max_length=25,
        null=True)

    comment = models.CharField(
        max_length=25,
        null=True,
        blank=True)

    objects = BoxItemManager()

    def natural_key(self):
        return (self.position, self.identifier) + self.box.natural_key()

    @property
    def human_readable_identifier(self):
        """Returns a human readable identifier.
        """
        x = self.identifier
        if re.match(aliquot_identifier_pattern, self.identifier):
            return '{}-{}-{}-{}-{}'.format(x[0:3], x[3:6], x[6:10], x[10:14], x[14:18])
        return self.identifier

    class Meta:
        app_label = 'edc_lab'
        ordering = ('position', )
        unique_together = (('box', 'position'), ('box', 'identifier'))


class SimpleBox(Box):

    class Meta:
        proxy = True
