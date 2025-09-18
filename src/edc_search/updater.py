from __future__ import annotations

from typing import TYPE_CHECKING

from .search_slug import SearchSlug

if TYPE_CHECKING:
    from edc_model.models import BaseUuidModel

    from .model_mixins import SearchSlugModelMixin

    class Model(SearchSlugModelMixin, BaseUuidModel):
        pass


class SearchSlugDuplicateFields(Exception):  # noqa: N818
    pass


class SearchSlugUpdater:
    search_slug_cls = SearchSlug

    def __init__(self, fields: tuple[str], model_obj: Model | SearchSlugModelMixin = None):
        if len(fields) > len(list(set(fields))):
            raise SearchSlugDuplicateFields(
                f"Duplicate search slug fields detected. Got {fields}. See {self!r}"
            )
        search_slug = self.search_slug_cls(obj=model_obj, fields=fields)
        self.warning = search_slug.warning
        self.slug = search_slug.slug
