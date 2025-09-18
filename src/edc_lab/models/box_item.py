import re

from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.deletion import PROTECT

from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_search.model_mixins import SearchSlugManager, SearchSlugModelMixin

from ..model_mixins import VerifyModelMixin
from ..patterns import aliquot_pattern
from .box import Box


class BoxItemManager(SearchSlugManager, models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, position, identifier, box_identifier):
        return self.get(
            position=position, identifier=identifier, box_identifier=box_identifier
        )


class BoxItem(SearchSlugModelMixin, VerifyModelMixin, BaseUuidModel):
    box = models.ForeignKey(Box, on_delete=PROTECT)

    position = models.IntegerField()

    identifier = models.CharField(max_length=25)

    comment = models.CharField(max_length=25, default="", blank=True)

    objects = BoxItemManager()

    history = HistoricalRecords()

    def natural_key(self):
        return self.position, self.identifier, *self.box.natural_key()

    natural_key.dependencies = ("edc_lab.box", "edc_lab.boxtype", "sites.Site")

    @property
    def human_readable_identifier(self):
        """Returns a human-readable identifier"""
        if self.identifier:
            x = self.identifier
            if re.match(aliquot_pattern, self.identifier):
                return f"{x[0:3]}-{x[3:6]}-{x[6:10]}-{x[10:14]}-{x[14:18]}"
        return self.identifier

    def get_slugs(self):
        return self.identifier, self.human_readable_identifier

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Box Item"
        constraints = (
            UniqueConstraint(
                fields=["box", "position"], name="%(app_label)s_%(class)s_box_pos_uniq"
            ),
            UniqueConstraint(
                fields=["box", "identifier"],
                name="%(app_label)s_%(class)s_box_ide_uniq",
            ),
        )
