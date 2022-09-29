from edc_model.models import HistoricalRecords
from edc_sites.models import SiteModelMixin
from edc_visit_tracking.managers import CrfCurrentSiteManager, CrfModelManager

from .crf_no_manager_model_mixin import CrfNoManagerModelMixin


class CrfModelMixin(SiteModelMixin, CrfNoManagerModelMixin):

    on_site = CrfCurrentSiteManager()
    objects = CrfModelManager()
    history = HistoricalRecords(inherit=True)

    class Meta(CrfNoManagerModelMixin.Meta):
        abstract = True
