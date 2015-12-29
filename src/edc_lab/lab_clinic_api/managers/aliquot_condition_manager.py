from django.db import models
from django.conf import settings


class AliquotConditionManager(models.Manager):

    def get_ok(self):
        """Returns the instance for the "condition OK" record."""
        if not 'ALIQUOT_CONDITION_OK' in dir(settings):
            ok = '10'
        if self.filter(short_name=ok):
            aliquot_condition = self.get(short_name=ok)
        else:
            raise TypeError('AliquotCondition must have at least one entry that has short_name=\'{0}\' for condition is OK. Got None'.format(ok))
        return aliquot_condition

    def get_by_natural_key(self, name):
        return self.get(name=name)
