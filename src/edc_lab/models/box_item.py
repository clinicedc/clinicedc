import re

from django.db import models
from django.db.models.deletion import PROTECT
from edc_base.model_managers import HistoricalRecords
from edc_base.model_mixins import BaseUuidModel
from edc_search.model_mixins import SearchSlugModelMixin, SearchSlugManager

from ..patterns import aliquot_pattern
from .box import Box
from .model_mixins.shipping import VerifyModelMixin


class BoxItemManager(SearchSlugManager, models.Manager):

    def get_by_natural_key(self, position, identifier, box_identifier):
        return self.get(
            position=position,
            identifier=identifier,
            box_identifier=box_identifier)


class BoxItem(SearchSlugModelMixin, VerifyModelMixin, BaseUuidModel):

    box = models.ForeignKey(Box, on_delete=PROTECT)

    position = models.IntegerField()

    identifier = models.CharField(
        max_length=25)

    comment = models.CharField(
        max_length=25,
        null=True,
        blank=True)

    objects = BoxItemManager()

    history = HistoricalRecords()

    def natural_key(self):
        return (self.position, self.identifier) + self.box.natural_key()
    natural_key.dependencies = ['edc_lab.box', 'edc_lab.boxtype', 'sites.Site']

    @property
    def human_readable_identifier(self):
        """Returns a human readable identifier.
        """
        if self.identifier:
            x = self.identifier
            if re.match(aliquot_pattern, self.identifier):
                return '{}-{}-{}-{}-{}'.format(x[0:3], x[3:6], x[6:10], x[10:14], x[14:18])
        return self.identifier

    def get_slugs(self):
        slugs = [self.identifier,
                 self.human_readable_identifier]
        return slugs

    class Meta:
        app_label = 'edc_lab'
        ordering = ('position', )
        unique_together = (('box', 'position'), ('box', 'identifier'))
