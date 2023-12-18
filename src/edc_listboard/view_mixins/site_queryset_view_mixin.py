class SiteQuerysetViewMixin:
    def get_queryset_filter_options(self, request, *args, **kwargs):
        options = super().get_queryset_filter_options(request, *args, **kwargs)
        options.update(site__id__in=self.get_sites_for_user())
        return options
