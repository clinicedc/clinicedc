from django.contrib.sites.models import Site
from edc_model.models import HistoricalRecords
from edc_sites.models import SiteModelMixin
from edc_visit_tracking.managers import CrfCurrentSiteManager, CrfModelManager

from .crf_no_manager_model_mixin import CrfNoManagerModelMixin


class CrfModelMixin(SiteModelMixin, CrfNoManagerModelMixin):
    objects = CrfModelManager()
    on_site = CrfCurrentSiteManager()
    history = HistoricalRecords(inherit=True)

    def get_site_on_create(self) -> Site:
        """Expect site instance to be set from the related_visit
        model instance.
        """
        return self.related_visit.site

    class Meta(CrfNoManagerModelMixin.Meta):
        abstract = True
