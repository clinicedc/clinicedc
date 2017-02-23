from django.db import models
from django.db.models.deletion import PROTECT

from edc_base.model.models import BaseUuidModel, HistoricalRecords
from edc_dashboard.model_mixins import SearchSlugModelMixin, SearchSlugManager

from ..managers import ManifestManager
from ..model_mixins import ManifestModelMixin
from .destination import Destination


class Manager(ManifestManager, SearchSlugManager):
    pass


class Manifest(ManifestModelMixin, SearchSlugModelMixin, BaseUuidModel):

    destination = models.ForeignKey(
        Destination,
        verbose_name='Ship to',
        on_delete=PROTECT)

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return '{} created on {} by {}'.format(
            self.manifest_identifier,
            self.manifest_datetime.strftime('%Y-%m-%d'),
            self.user_created)

    def get_slugs(self):
        slugs = [self.manifest_identifier]
        return slugs

    class Meta(ManifestModelMixin.Meta):
        app_label = 'edc_lab'
