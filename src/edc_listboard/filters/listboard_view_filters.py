from .listboard_filter import ListboardFilter


class MetaListboardViewFilters(type):
    def __new__(mcs, name, bases, attrs):
        parents = [b for b in bases if isinstance(b, MetaListboardViewFilters)]
        if not parents:
            attrs.update({"filters": []})
            attrs.update({"default_include_filter": None})
            attrs.update({"default_exclude_filter": None})
            return super().__new__(mcs, name, bases, attrs)
        filters = []
        default_include_filter = None
        default_exclude_filter = None
        for attrname, obj in attrs.items():
            if not attrname.startswith("_"):
                if isinstance(obj, ListboardFilter):
                    obj.name = attrname
                    if obj.default and not obj.exclude_filter:
                        default_include_filter = obj
                    elif obj.default and obj.exclude_filter:
                        default_exclude_filter = obj
                    filters.append(obj)
        filters.sort(key=lambda x: x.position)
        attrs.update({"filters": filters})
        attrs.update({"default_include_filter": default_include_filter})
        attrs.update({"default_exclude_filter": default_exclude_filter})
        return super().__new__(mcs, name, bases, attrs)


class ListboardViewFilters(metaclass=MetaListboardViewFilters):
    @property
    def include_filters(self):
        return [f for f in self.filters if f.attr == "f"]

    @property
    def exclude_filters(self):
        return [f for f in self.filters if f.attr == "e"]
