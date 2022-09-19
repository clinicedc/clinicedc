from edc_consent.model_mixins import RequiresConsentFieldsModelMixin
from edc_model import models as edc_models
from edc_sites.models import CurrentSiteManager, SiteModelMixin

from .model_mixins import OffstudyModelManager, OffstudyModelMixin


class SubjectOffstudy(
    RequiresConsentFieldsModelMixin,
    OffstudyModelMixin,
    SiteModelMixin,
    edc_models.BaseUuidModel,
):

    on_site = CurrentSiteManager()

    objects = OffstudyModelManager()

    history = edc_models.HistoricalRecords()

    class Meta(edc_models.BaseUuidModel.Meta):
        verbose_name = "Subject Offstudy"
        verbose_name_plural = "Subject Offstudy"
