import urllib


class MetaListboardViewFilters(type):

    def __new__(cls, name, bases, attrs):
        parents = [b for b in bases if isinstance(b, MetaListboardViewFilters)]
        if not parents:
            attrs.update({'filters': []})
            attrs.update({'default_include_filter': None})
            attrs.update({'default_exclude_filter': None})
            return super().__new__(cls, name, bases, attrs)
        filters = []
        default_include_filter = None
        default_exclude_filter = None
        for attrname, obj in attrs.items():
            if not attrname.startswith('_'):
                if isinstance(obj, ListboardFilter):
                    obj.name = attrname
                    if obj.default and not obj.exclude_filter:
                        default_include_filter = obj
                    elif obj.default and obj.exclude_filter:
                        default_exclude_filter = obj
                    filters.append(obj)
        filters.sort(key=lambda x: x.position)
        attrs.update({'filters': filters})
        attrs.update({'default_include_filter': default_include_filter})
        attrs.update({'default_exclude_filter': default_exclude_filter})
        return super().__new__(cls, name, bases, attrs)


class ListboardFilter:

    def __init__(self, name=None, label=None, lookup=None,
                 exclude_filter=None, default=None, position=None):
        self.name = name
        self.label = label or name
        self.position = position or 0
        self.exclude_filter = exclude_filter
        if exclude_filter:
            self.attr = 'e'
        else:
            self.attr = 'f'
        self.lookup = lookup or {}
        self.default = default

    def __repr__(self):
        return (
            '{0.__class__.__name__}({0.name}, {0.label}, '
            'exclude_filter={0.exclude_filter}, {0.default})'.format(self))

    @property
    def querystring(self):
        return urllib.parse.urlencode({self.attr: self.name})

    @property
    def lookup_options(self):
        lookup_options = {}
        for k, v in self.lookup.items():
            try:
                lookup_options.update({k: v()})
            except TypeError:
                lookup_options.update({k: v})
        return lookup_options


class ListboardViewFilters(metaclass=MetaListboardViewFilters):

    @property
    def include_filters(self):
        return [f for f in self.filters if f.attr == 'f']

    @property
    def exclude_filters(self):
        return [f for f in self.filters if f.attr == 'e']
