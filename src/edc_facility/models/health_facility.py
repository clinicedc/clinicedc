from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_sites.models import CurrentSiteManager, SiteModelMixin

from ..model_mixins import HealthFacilityModelMixin, Manager


class HealthFacility(SiteModelMixin, HealthFacilityModelMixin, BaseUuidModel):
    objects = Manager()
    on_site = CurrentSiteManager()
    history = HistoricalRecords()

    class Meta(SiteModelMixin.Meta, BaseUuidModel.Meta):
        verbose_name = "Health Facility"
        verbose_name_plural = "Health Facilities"
