from django.contrib.sites.managers import CurrentSiteManager as BaseCurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models


class SiteModelError(Exception):
    pass


class CurrentSiteManager(BaseCurrentSiteManager):

    use_in_migrations = True


class SiteModelMixin(models.Model):

    site = models.ForeignKey(
        Site, on_delete=models.PROTECT, null=True, editable=False, related_name="+"
    )

    def save(self, *args, **kwargs):
        if not self.site:
            self.site = Site.objects.get_current()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class SiteProfile(models.Model):

    country = models.CharField(max_length=250, null=True)

    country_code = models.CharField(max_length=15, null=True)

    title = models.CharField(max_length=250, null=True)

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

    @property
    def country(self):
        return SiteProfile.objects.get(site=self).country

    @property
    def country_code(self):
        return SiteProfile.objects.get(site=self).country_code

    class Meta:
        proxy = True
