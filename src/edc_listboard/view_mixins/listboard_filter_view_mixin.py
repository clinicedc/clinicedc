from __future__ import annotations

from typing import TYPE_CHECKING, Any

from edc_dashboard.url_names import url_names

from ..filters import ListboardViewFilters

if TYPE_CHECKING:
    from django.db.models import Q


class ListboardFilterViewMixin:
    listboard_view_filters = ListboardViewFilters()
    listboard_filter_url = None

    def __init__(self, **kwargs):
        self.listboard_view_exclude_filter_applied = False  # TODO: ??
        self.listboard_view_include_filter_applied = False  # TODO: ??
        super().__init__(**kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        listboard_url = getattr(self, "listboard_url", None)
        kwargs.update(
            listboard_view_filters=self.listboard_view_filters.filters,
            listboard_filter_url=url_names.get(self.listboard_filter_url or listboard_url),
        )
        return super().get_context_data(**kwargs)

    def get_queryset_filter_options(self, request, *args, **kwargs) -> tuple[Q, dict]:
        q_object, options = super().get_queryset_filter_options(request, *args, **kwargs)
        self.listboard_view_include_filter_applied = False
        for listboard_filter in self.listboard_view_filters.include_filters:
            if self.request.GET.get(listboard_filter.attr) == listboard_filter.name:
                lookup_options = listboard_filter.lookup_options
                if lookup_options:
                    options.update(**listboard_filter.lookup_options)
                self.listboard_view_include_filter_applied = True
        if (
            not self.listboard_view_include_filter_applied
            and self.listboard_view_filters.default_include_filter
        ):
            options.update(**self.listboard_view_filters.default_include_filter.lookup_options)
        return q_object, options

    def get_queryset_exclude_options(self, request, *args, **kwargs) -> tuple[Q, dict]:
        q_object, options = super().get_queryset_exclude_options(request, *args, **kwargs)
        self.listboard_view_exclude_filter_applied = False
        for listboard_filter in self.listboard_view_filters.exclude_filters:
            if self.request.GET.get(listboard_filter.attr) == listboard_filter.name:
                lookup_options = listboard_filter.lookup_options
                if lookup_options:
                    options.update(**listboard_filter.lookup_options)
                self.listboard_view_exclude_filter_applied = True
        if (
            not self.listboard_view_exclude_filter_applied
            and not self.listboard_view_include_filter_applied
            and self.listboard_view_filters.default_exclude_filter
        ):
            options.update(**self.listboard_view_filters.default_exclude_filter.lookup_options)
        return q_object, options
