from __future__ import print_function


class MostRecentQuery(object):

    def __init__(self, model_cls, order_by=None, query_options=None, limit=None):
        self._model_cls = model_cls
        self._limit = limit or 50
        self._query_options = query_options or {}
        self._order_by = order_by or ('-modified', 'created')

    def get_model_cls(self):
        return self._model_cls

    def get_limit(self):
        return self._limit

    def get_query_options(self):
        return self._query_options

    def get_order_by(self):
        return self._order_by

    def query(self):
        print(self.get_model_cls())
        return self.get_model_cls().objects.filter(
            **self.get_query_options()).order_by(*self.get_order_by())[0:self.get_limit()]
