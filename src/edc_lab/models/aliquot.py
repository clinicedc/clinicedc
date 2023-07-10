from edc_model import models as edc_models
from edc_search.model_mixins import SearchSlugManager, SearchSlugModelMixin
from edc_sites.models import CurrentSiteManager

from ..managers import AliquotManager
from ..model_mixins import (
    AliquotIdentifierModelMixin,
    AliquotModelMixin,
    AliquotShippingMixin,
    AliquotTypeModelMixin,
)


class Manager(AliquotManager, SearchSlugManager):
    pass


class Aliquot(
    AliquotModelMixin,
    AliquotIdentifierModelMixin,
    AliquotTypeModelMixin,
    AliquotShippingMixin,
    SearchSlugModelMixin,
    edc_models.BaseUuidModel,
):
    def get_search_slug_fields(self):
        return [
            "aliquot_identifier",
            "human_readable_identifier",
            "subject_identifier",
            "parent_identifier",
            "requisition_identifier",
        ]

    objects = Manager()

    on_site = CurrentSiteManager()

    history = edc_models.HistoricalRecords()

    @property
    def human_readable_identifier(self):
        """Returns a human readable aliquot identifier."""
        x = self.aliquot_identifier
        return "{}-{}-{}-{}-{}".format(x[0:3], x[3:6], x[6:10], x[10:14], x[14:18])

    class Meta(edc_models.BaseUuidModel.Meta):
        verbose_name = "Aliquot"
