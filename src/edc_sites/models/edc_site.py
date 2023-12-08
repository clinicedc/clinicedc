from django.contrib.sites.models import Site

from .site_profile import SiteProfile


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
