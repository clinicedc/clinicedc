from django.contrib.sites.managers import CurrentSiteManager as BaseCurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models

from .utils import raise_on_save_if_reviewer


class SiteModelError(Exception):
    pass


class CurrentSiteManager(BaseCurrentSiteManager):

    use_in_migrations = True


class SiteModelMixin(models.Model):

    site = models.ForeignKey(
        Site, on_delete=models.PROTECT, null=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.site:
            self.site = Site.objects.get_current()
        raise_on_save_if_reviewer()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class SiteProfile(models.Model):

    title = models.CharField(max_length=50, null=True)

    description = models.TextField(null=True)

    site = models.OneToOneField(Site, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.site.id}: {self.title}"


class EdcSite(Site):

    @property
    def title(self):
        return SiteProfile.objects.get(site=self).title

    @property
    def description(self):
        return SiteProfile.objects.get(site=self).description

    class Meta:
        proxy = True
