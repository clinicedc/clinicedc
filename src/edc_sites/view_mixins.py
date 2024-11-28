from __future__ import annotations

from django.core.exceptions import ObjectDoesNotExist

from .models import SiteProfile
from .site import SiteNotRegistered, sites


class SiteViewMixin:
    def get_context_data(self, **kwargs) -> dict:
        kwargs = self.get_context_data_for_sites(**kwargs)
        return super().get_context_data(**kwargs)

    def get_context_data_for_sites(self, **kwargs):
        try:
            site_profile = SiteProfile.objects.get(site__id=self.request.site.id)
        except ObjectDoesNotExist:
            site_profile = None
        kwargs.update(site_profile=site_profile)
        try:
            kwargs.update(site_title=site_profile.title)
        except AttributeError:
            if not sites.all():
                raise SiteNotRegistered(
                    "Unable to determine site profile 'title'. No sites have been registered! "
                )
            raise
        return kwargs
