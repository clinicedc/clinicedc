from __future__ import annotations

from django.contrib.sites.models import Site
from django.db import models

from .model_mixins import CurrentSiteManager, SiteModelMixin  # noqa


class SiteModelError(Exception):
    pass


class SiteProfile(models.Model):

    id = models.BigAutoField(primary_key=True)

    country = models.CharField(max_length=250, null=True)

    country_code = models.CharField(max_length=15, null=True)

    languages = models.TextField(null=True)

    title = models.CharField(max_length=250, null=True)

    description = models.TextField(null=True)

    site = models.OneToOneField(Site, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.site.id}: {self.title}"


class EdcSite(Site):
    @property
    def title(self) -> str:
        return SiteProfile.objects.get(site=self).title

    @property
    def description(self) -> str:
        return SiteProfile.objects.get(site=self).description

    @property
    def country(self) -> str:
        return SiteProfile.objects.get(site=self).country

    @property
    def country_code(self) -> str:
        return SiteProfile.objects.get(site=self).country_code

    @property
    def languages(self) -> str | None:
        return SiteProfile.objects.get(site=self).languages

    class Meta:
        proxy = True
