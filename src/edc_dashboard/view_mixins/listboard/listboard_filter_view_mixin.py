from edc_dashboard.listboard_filter import ListboardViewFilters


class ListboardFilterViewMixin:

    listboard_view_filters = ListboardViewFilters()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            listboard_view_filters=self.listboard_view_filters.filters)
        return context

    def get_queryset_filter_options(self, request, *args, **kwargs):
        options = super().get_queryset_filter_options(request, *args, **kwargs)
        for listboard_filter in self.listboard_view_filters.include_filters:
            if self.request.GET.get(listboard_filter.attr) == listboard_filter.name:
                for k, v in listboard_filter.lookup_options.items():
                    try:
                        options.update({k: v()})
                    except TypeError:
                        options.update({k: v})
        return options

    def get_queryset_exclude_options(self, request, *args, **kwargs):
        options = super().get_queryset_exclude_options(
            request, *args, **kwargs)
        for listboard_filter in self.listboard_view_filters.exclude_filters:
            if self.request.GET.get(listboard_filter.attr) == listboard_filter.name:
                for k, v in listboard_filter.lookup_options.items():
                    try:
                        options.update({k: v()})
                    except TypeError:
                        options.update({k: v})
        return options
