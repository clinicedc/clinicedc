from __future__ import annotations

from django.core.exceptions import ObjectDoesNotExist

from .models import SiteProfile


class SiteViewMixin:
    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        try:
            site_profile = SiteProfile.objects.get(site__id=self.request.site.id)
        except ObjectDoesNotExist:
            context.update(site_profile=None)
        else:
            context.update(site_title=site_profile.title)
            context.update(site_profile=site_profile)
        return context
