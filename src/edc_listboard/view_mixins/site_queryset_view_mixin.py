from edc_sites.permissions import get_view_only_sites_for_user


class SiteQuerysetViewMixin:
    def get_queryset_filter_options(self, request, *args, **kwargs):
        options = super().get_queryset_filter_options(request, *args, **kwargs)
        site_ids = [request.site.id] + get_view_only_sites_for_user(
            self.request.user, self.request.site.id, request=self.request
        )
        options.update(site__id__in=site_ids)
        return options
