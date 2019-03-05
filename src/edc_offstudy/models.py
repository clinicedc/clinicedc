from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_sites.models import CurrentSiteManager, SiteModelMixin

from .model_mixins import OffstudyModelMixin, OffstudyModelManager


class SubjectOffstudy(OffstudyModelMixin, SiteModelMixin, BaseUuidModel):

    on_site = CurrentSiteManager()

    objects = OffstudyModelManager()

    history = HistoricalRecords()
