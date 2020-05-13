from django.db import models
from django.db.models.deletion import PROTECT

from edc_model import models as edc_models
from edc_sites.models import SiteModelMixin
from edc_search.model_mixins import SearchSlugModelMixin, SearchSlugManager

from ...model_mixins import VerifyModelMixin
from .manifest import Manifest


class ManifestItemManager(SearchSlugManager, models.Manager):
    def get_by_natural_key(self, identifier, manifest_identifier):
        return self.get(identifier=identifier, manifest_identifier=manifest_identifier)


class ManifestItem(
    SiteModelMixin, SearchSlugModelMixin, VerifyModelMixin, edc_models.BaseUuidModel
):
    def get_search_slug_fields(self):
        return ["identifier", "human_readable_identifier"]

    manifest = models.ForeignKey(Manifest, on_delete=PROTECT)

    identifier = models.CharField(max_length=25)

    comment = models.CharField(max_length=25, null=True, blank=True)

    objects = ManifestItemManager()

    def natural_key(self):
        return (self.identifier,) + self.manifest.natural_key()

    natural_key.dependencies = ["edc_lab.manifest", "sites.Site"]

    @property
    def human_readable_identifier(self):
        x = self.identifier
        return "{}-{}-{}".format(x[0:4], x[4:8], x[8:12])

    class Meta(edc_models.BaseUuidModel.Meta):
        verbose_name = "Manifest Item"
        ordering = ("created",)
        unique_together = ("manifest", "identifier")
