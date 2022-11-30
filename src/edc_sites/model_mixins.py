from django.contrib.sites.managers import CurrentSiteManager as BaseCurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models


class CurrentSiteManager(BaseCurrentSiteManager):

    use_in_migrations = True

    def get_by_natural_key(self, subject_identifier):
        return self.get(subject_identifier=subject_identifier)


class SiteModelMixin(models.Model):

    site = models.ForeignKey(
        Site, on_delete=models.PROTECT, null=True, editable=False, related_name="+"
    )

    on_site = CurrentSiteManager()

    def save(self, *args, **kwargs):
        if not self.site:
            self.site = Site.objects.get_current()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
