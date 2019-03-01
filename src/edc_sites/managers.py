from django.contrib.sites.managers import CurrentSiteManager as BaseCurrentSiteManager


class CurrentSiteManager(BaseCurrentSiteManager):

    use_in_migrations = True
