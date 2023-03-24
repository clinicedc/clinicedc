from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_sites.model_mixins import CurrentSiteManager, SiteModelMixin

from ..managers import SubjectRefusalManager
from ..model_mixins import SubjectRefusalModelMixin


class SubjectRefusal(SubjectRefusalModelMixin, SiteModelMixin, BaseUuidModel):
    on_site = CurrentSiteManager()

    objects = SubjectRefusalManager()

    history = HistoricalRecords()

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Subject Refusal"
        verbose_name_plural = "Subject Refusals"
