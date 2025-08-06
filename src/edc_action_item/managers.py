from django.db import models

from edc_sites.managers import CurrentSiteManager as BaseCurrentSiteManager


class ActionIdentifierSiteManager(BaseCurrentSiteManager):
    use_in_migrations = True

    def get_by_natural_key(self, action_identifier):
        return self.get(action_identifier=action_identifier)


class ActionIdentifierModelManager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, action_identifier):
        return self.get(action_identifier=action_identifier)
