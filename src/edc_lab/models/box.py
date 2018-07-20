from django.db import models
from django.db.models.deletion import PROTECT
from django.utils import timezone
from edc_base.model_managers import HistoricalRecords
from edc_base.model_mixins import BaseUuidModel
from edc_base.sites import CurrentSiteManager, SiteModelMixin
from edc_constants.constants import OTHER, OPEN
from edc_search.model_mixins import SearchSlugModelMixin, SearchSlugManager

from ..constants import VERIFIED, PACKED, SHIPPED, TESTING, STORAGE
from ..identifiers import BoxIdentifier
from .box_type import BoxType
from .model_mixins.shipping import VerifyBoxModelMixin


BOX_DIMENSIONS = (
    ('8 x 8', '8 x 8'),
    ('9 x 9', '9 x 9'),
    ('10 x 10', '10 x 10'),
)

BOX_CATEGORY = (
    (TESTING, 'Testing'),
    (STORAGE, 'Storage'),
    (OTHER, 'Other'),
)

STATUS = (
    (OPEN, 'Open'),
    (VERIFIED, 'Verified'),
    (PACKED, 'Packed'),
    (SHIPPED, 'Shipped'),
)

human_readable_pattern = '^[A-Z]{3}\-[0-9]{4}\-[0-9]{2}$'


class BoxManager(SearchSlugManager, models.Manager):

    def get_by_natural_key(self, box_identifier):
        return self.get(box_identifier=box_identifier)


class Box(SearchSlugModelMixin, VerifyBoxModelMixin, SiteModelMixin, BaseUuidModel):

    search_slug_fields = [
        'box_identifier', 'human_readable_identifier', 'name']

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
        default=TESTING,
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

    accept_primary = models.BooleanField(
        default=False,
        help_text='Tick to allow \'primary\' specimens to be added to this box')

    comment = models.TextField(
        null=True,
        blank=True)

    on_site = CurrentSiteManager()

    objects = BoxManager()

    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if not self.box_identifier:
            identifier = BoxIdentifier()
            self.box_identifier = identifier.identifier
        if not self.name:
            self.name = self.box_identifier
        self.update_verified()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.box_identifier,)
    natural_key.dependencies = ['edc_lab.boxtype', 'sites.Site']

    @property
    def count(self):
        return self.boxitem_set.all().count()

    @property
    def items(self):
        return self.boxitem_set.all().order_by('position')

    @property
    def human_readable_identifier(self):
        x = self.box_identifier
        return '{}-{}-{}'.format(x[0:4], x[4:8], x[8:12])

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

    class Meta:
        app_label = 'edc_lab'
        ordering = ('-box_datetime',)
        verbose_name_plural = 'Boxes'
