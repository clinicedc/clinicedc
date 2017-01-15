from ..paginator_mixin import PaginatorMixin


class FilteredListViewMixin(PaginatorMixin):

    url_lookup_parameters = []
    filtered_model_wrapper_class = None  # e.g. ModelWrapper
    filtered_queryset_ordering = '-created'
    filter_model = None

    def __init__(self, **kwargs):
        self.filter_options = {}
        super().__init__(**kwargs)

    def get_context_data(self, **kwargs):
        """Updates the context with the paginated filtered results and a few other simple attrs.

        Results are filtered according to the `updated_filter_options_from` the context."""
        context = super().get_context_data(**kwargs)
        self.update_filter_options_from(context)
        context.update(
            show_paginator_control=True if self.filtered_queryset.count() > self.paginate_by else False,
            results=self.paginate(
                queryset=self.filtered_queryset,
                model_wrapper_class=self.filtered_model_wrapper_class),
            result_count_total=self.filtered_queryset.count())
        return context

    @property
    def filtered_queryset(self):
        """Returns a queryset filtered by values from the context,
        see `update_filter_options_from`.

        This is not the "search" queryset"""
        return self.filter_model.objects.filter(
            **self.filter_options).order_by(self.filtered_queryset_ordering)

    def update_filter_options_from(self, context):
        """Intercepts from the context and returns options for the `filtered_queryset`.

        url_lookup_parameters correspond with parameters defined in urls.py"""
        lookups = []
        self.filter_options = {}
        for attrname in self.url_lookup_parameters:
            if isinstance(attrname, tuple):
                lookups.append((attrname[0], attrname[1]))
            else:
                lookups.append((attrname, attrname))
        for attrname, lookup in lookups:
            if context.get(attrname):
                self.filter_options.update({lookup: context.get(attrname)})
                # TODO: ??
                # context['search_term'] = context.get(attrname)
        return context
