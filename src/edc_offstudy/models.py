from edc_model import models as edc_models
from edc_sites.models import CurrentSiteManager, SiteModelMixin

from .model_mixins import OffstudyModelMixin, OffstudyModelManager


class SubjectOffstudy(OffstudyModelMixin, SiteModelMixin, edc_models.BaseUuidModel):

    on_site = CurrentSiteManager()

    objects = OffstudyModelManager()

    history = edc_models.HistoricalRecords()

    class Meta(edc_models.BaseUuidModel.Meta):
        pass
