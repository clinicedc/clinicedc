from edc_action_item.models import ActionNoManagersModelMixin
from edc_model.models import HistoricalRecords
from edc_sites.models import SiteModelMixin
from edc_visit_tracking.managers import CrfCurrentSiteManager, CrfModelManager

from .crf_model_mixin import CrfNoManagerModelMixin


class CrfWithActionModelMixin(
    SiteModelMixin,
    CrfNoManagerModelMixin,
    ActionNoManagersModelMixin,
):
    action_name = None

    objects = CrfModelManager()
    on_site = CrfCurrentSiteManager()
    history = HistoricalRecords(inherit=True)

    class Meta(CrfNoManagerModelMixin.Meta):
        abstract = True
