from django.views.generic.base import ContextMixin

from .models import SiteProfile


class SiteViewMixin(ContextMixin):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        site_profile = SiteProfile.objects.get(site__id=self.request.site.id)
        context.update(
            site_title=site_profile.title
        )
        return context
