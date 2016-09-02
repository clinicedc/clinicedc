from django.db import models


class AliquotManager(models.Manager):

    def get_by_natural_key(self, aliquot_identifier):
        return self.get(aliquot_identifier=aliquot_identifier)
