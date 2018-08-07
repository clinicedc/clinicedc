from django.db import models


class AliquotManager(models.Manager):

    def get_by_natural_key(self, aliquot_identifier):
        return self.get(aliquot_identifier=aliquot_identifier)


class ManifestManager(models.Manager):

    def get_by_natural_key(self, manifest_identifier):
        return self.get(manifest_identifier=manifest_identifier)


class RequisitionManager(models.Manager):

    def get_by_natural_key(self, requisition_identifier):
        return self.get(requisition_identifier=requisition_identifier)
