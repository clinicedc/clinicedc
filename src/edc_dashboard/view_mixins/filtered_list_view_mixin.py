from ..paginator_mixin import PaginatorMixin


class FilteredListViewMixin(PaginatorMixin):

    url_lookup_parameters = []
    filtered_model_wrapper_class = None
    filtered_queryset_ordering = '-created'
    filter_model = None

    def __init__(self, **kwargs):
        self.filter_options = {}
        super().__init__(**kwargs)

    def get(self, request, *args, **kwargs):
        for url_lookup_parameter in self.url_lookup_parameters:
            attrname, lookup = url_lookup_parameter
            if kwargs.get(attrname):
                self.filter_options.update({lookup: kwargs.get(attrname)})
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Updates the context with the paginated filtered results."""
        context = super().get_context_data(**kwargs)
        context.update(
            show_paginator_control=True if self.filtered_queryset.count() > self.paginate_by else False,
            results=self.paginate(
                queryset=self.filtered_queryset,
                model_wrapper_class=self.filtered_model_wrapper_class),
            result_count_total=self.filtered_queryset.count())
        return context

    @property
    def filtered_queryset(self):
        """Returns a queryset."""
        return self.filter_model.objects.filter(
            **self.filter_options).order_by(self.filtered_queryset_ordering)
