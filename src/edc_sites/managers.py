from django.contrib.sites.managers import CurrentSiteManager as BaseCurrentSiteManager


class CurrentSiteManager(BaseCurrentSiteManager):
    use_in_migrations = True

    def get_by_natural_key(self, subject_identifier):
        return self.get(subject_identifier=subject_identifier)
