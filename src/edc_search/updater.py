from .search_slug import SearchSlug


class SearchSlugDuplicateFields(Exception):
    pass


class SearchSlugUpdater:
    search_slug_cls = SearchSlug
    sep = "|"

    def __init__(self, fields, model_obj=None):
        if len(fields) > len(list(set(fields))):
            raise SearchSlugDuplicateFields(
                f"Duplicate search slug fields detected. Got {fields}. " f"See {repr(self)}"
            )
        search_slug = self.search_slug_cls(obj=model_obj, fields=fields, sep=self.sep)
        self.warning = search_slug.warning
        self.slug = search_slug.slug
