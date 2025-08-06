from __future__ import annotations

import re
from typing import Any

from django.contrib.messages import WARNING
from django.db.models import Q
from django.db.models.constants import LOOKUP_SEP
from django.utils.html import escape
from django.utils.translation import gettext as _

from edc_model_admin.utils import add_to_messages_once


class SearchListboardMixin:
    search_fields = ["slug"]

    default_querystring_attrs: str = "q"
    alternate_search_attr: str = "subject_identifier"
    default_lookup = "icontains"
    operators: list[str] = [
        "exact",
        "iexact",
        "contains",
        "icontains",
        "regex",
        "iregex",
        "gt",
        "gte",
        "lt",
        "lte",
        "startswith",
        "endswith",
        "istartswith",
        "iendswith",
    ]

    def __init__(self, **kwargs):
        self._search_term = None
        super().__init__(**kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        kwargs.update(search_term=self.search_term)
        return super().get_context_data(**kwargs)

    def get_queryset_filter_options(self, request, *args, **kwargs) -> tuple[Q, dict]:
        """Override to add conditional logic to filter on search term."""
        q_object, options = super().get_queryset_filter_options(request, *args, **kwargs)
        if self.search_term and not re.match(r"^[A-Za-z0-9\-]+?$", self.search_term):
            add_to_messages_once(
                request=request,
                level=WARNING,
                message=_("Invalid search term. May only include letters, numbers and '-'."),
            )
        elif self.search_term:
            for field, lookup in self.get_field_lookups():
                q_object |= Q(**{f"{field}__{lookup}": self.search_term})
        return q_object, options

    @property
    def raw_search_term(self) -> str | None:
        raw_search_term = self.request.GET.get(self.default_querystring_attrs)
        if not raw_search_term:
            raw_search_term = self.kwargs.get(self.alternate_search_attr)
        return raw_search_term

    @property
    def search_term(self) -> str | None:
        if not self._search_term:
            if search_term := self.raw_search_term:
                self._search_term = escape(search_term).strip()
        return self._search_term

    def get_search_fields(self) -> list[str]:
        """Override to add additional search fields"""
        return self.search_fields

    def get_field_lookups(self) -> list[tuple[str, str]]:
        fields = []

        for field in self.get_search_fields():
            nlookups = field.split(LOOKUP_SEP)
            if nlookups[-1:][0] in self.operators:
                fld = LOOKUP_SEP.join(nlookups[:-1])
                lookup = nlookups[-1:][0]
            else:
                fld, lookup = LOOKUP_SEP.join(nlookups), self.default_lookup
            fields.append((fld, lookup))
        return fields
