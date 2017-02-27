import urllib


class MetaListboardViewFilters(type):

    def __new__(cls, name, bases, attrs):
        parents = [b for b in bases if isinstance(b, MetaListboardViewFilters)]
        if not parents:
            attrs.update({'filters': []})
            return super().__new__(cls, name, bases, attrs)
        filters = []
        for attrname, obj in attrs.items():
            if not attrname.startswith('_'):
                if isinstance(obj, ListboardFilter):
                    obj.name = attrname
                    filters.append(obj)
        attrs.update({'filters': filters})
        return super().__new__(cls, name, bases, attrs)


class ListboardFilter:

    def __init__(self, name=None, label=None, lookup=None, exclude_filter=None):
        self.name = name
        self.label = label or name
        self.exclude_filter = exclude_filter
        if exclude_filter:
            self.attr = 'e'
        else:
            self.attr = 'f'
        self.lookup_options = lookup or {}

    def __repr__(self):
        return '{0.__class__.__name__}({0.name}, {0.label}, exclude_filter={0.exclude_filter})'.format(self)

    @property
    def querystring(self):
        return urllib.parse.urlencode({self.attr: self.name})


class ListboardViewFilters(metaclass=MetaListboardViewFilters):

    @property
    def include_filters(self):
        return [f for f in self.filters if f.attr == 'f']

    @property
    def exclude_filters(self):
        return [f for f in self.filters if f.attr == 'e']
