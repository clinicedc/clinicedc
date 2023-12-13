from edc_sites.permissions import (
    has_permissions_for_extra_sites,
    site_ids_with_permissions,
)


class SiteQuerysetViewMixin:
    def get_queryset_filter_options(self, request, *args, **kwargs):
        options = super().get_queryset_filter_options(request, *args, **kwargs)
        site_ids = [request.site.id]
        if has_permissions_for_extra_sites(self.request):
            site_ids = site_ids_with_permissions(self.request)
        options.update(site__id__in=site_ids)
        return options
