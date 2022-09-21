from django.contrib.sites.managers import CurrentSiteManager
from edc_action_item.models import ActionNoManagersModelMixin
from edc_model.models import HistoricalRecords
from edc_visit_tracking.managers import CrfModelManager

from .crf_model_mixin import CrfNoManagerModelMixin


class CrfWithActionModelMixin(
    CrfNoManagerModelMixin,
    ActionNoManagersModelMixin,
):

    action_name = None

    on_site = CurrentSiteManager()
    objects = CrfModelManager()
    history = HistoricalRecords(inherit=True)

    class Meta(CrfNoManagerModelMixin.Meta):
        abstract = True
