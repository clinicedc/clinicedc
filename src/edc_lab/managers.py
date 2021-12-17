from django.db import models
from edc_search.model_mixins import SearchSlugManager
from edc_visit_tracking.managers import CrfModelManager


class AliquotManager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, aliquot_identifier):
        return self.get(aliquot_identifier=aliquot_identifier)


class ManifestManager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, manifest_identifier):
        return self.get(manifest_identifier=manifest_identifier)


class RequisitionManager(CrfModelManager, SearchSlugManager, models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, requisition_identifier):
        return self.get(requisition_identifier=requisition_identifier)
