from django.contrib.sites.managers import CurrentSiteManager
from edc_model.models import HistoricalRecords
from edc_visit_tracking.managers import CrfModelManager

from .crf_no_manager_model_mixin import CrfNoManagerModelMixin


class CrfModelMixin(CrfNoManagerModelMixin):

    on_site = CurrentSiteManager()
    objects = CrfModelManager()
    history = HistoricalRecords(inherit=True)

    class Meta(CrfNoManagerModelMixin.Meta):
        abstract = True
