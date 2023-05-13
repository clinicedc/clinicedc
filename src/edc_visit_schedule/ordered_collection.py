import itertools
from collections import OrderedDict


class OrderedCollection(OrderedDict):
    key: str = None  # key name in dictionary key/value pair
    ordering_attr: str = None  # value.attrname to order dictionary on.

    def update(self, *args, **kwargs) -> None:
        """Updates and reorders."""

        def key_order(v):
            return getattr(v, self.ordering_attr)

        super().update(*args, **kwargs)
        od = self.copy()
        self.clear()
        super().update(**{getattr(v, self.key): v for v in sorted(od.values(), key=key_order)})

    @property
    def first(self):
        """Returns the first item."""
        return next(iter(self.values()))

    @property
    def last(self):
        """Returns the last item."""
        return next(reversed(self.values()))

    def previous(self, key):
        """Returns the previous item or None."""
        return self.get(self._iter_keys(key=key, reverse=True))

    def next(self, key):
        """Returns the next item or None."""
        return self.get(self._iter_keys(key=key))

    def _iter_keys(self, key=None, reverse=None):
        if reverse:
            seq = reversed(self.keys())
        else:
            seq = iter(self.keys())
        keys = itertools.dropwhile(lambda x: x != key, seq)
        try:
            k = next(keys)
        except StopIteration:
            pass
        else:
            if k != key:
                raise AssertionError
        try:
            return next(keys)
        except StopIteration:
            return None
