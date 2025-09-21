from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_search.model_mixins import SearchSlugManager, SearchSlugModelMixin
from edc_sites.managers import CurrentSiteManager

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
    BaseUuidModel,
):
    def get_search_slug_fields(self):
        return (
            "aliquot_identifier",
            "human_readable_identifier",
            "subject_identifier",
            "parent_identifier",
            "requisition_identifier",
        )

    objects = Manager()

    on_site = CurrentSiteManager()

    history = HistoricalRecords()

    @property
    def human_readable_identifier(self):
        """Returns a human readable aliquot identifier."""
        x = self.aliquot_identifier
        return f"{x[0:3]}-{x[3:6]}-{x[6:10]}-{x[10:14]}-{x[14:18]}"

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Aliquot"
