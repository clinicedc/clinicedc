from edc_base.model_mixins import BaseUuidModel
from edc_base.sites import CurrentSiteManager, SiteModelMixin

from .managers import CrfMetadataManager, RequisitionMetadataManager
from .model_mixins.metadata_models import CrfModelMixin, RequisitionMetadataModelMixin


class CrfMetadata(CrfModelMixin, SiteModelMixin, BaseUuidModel):

    on_site = CurrentSiteManager()

    objects = CrfMetadataManager()

    def natural_key(self):
        return super().natural_key()
    natural_key.dependencies = ['sites.Site']

    class Meta(CrfModelMixin.Meta):
        app_label = 'edc_metadata'


class RequisitionMetadata(RequisitionMetadataModelMixin, SiteModelMixin, BaseUuidModel):

    on_site = CurrentSiteManager()

    objects = RequisitionMetadataManager()

    def natural_key(self):
        return super().natural_key()
    natural_key.dependencies = ['sites.Site']

    class Meta(RequisitionMetadataModelMixin.Meta):
        app_label = 'edc_metadata'
