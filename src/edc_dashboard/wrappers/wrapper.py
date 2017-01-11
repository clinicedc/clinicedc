from ..next_url_mixin import NextUrlMixin


class Wrapper(NextUrlMixin):

    def __init__(self, obj):
        self._wrapped = True
        self._original_object = obj

    def object_url_wrapper(self, key=None, obj=None):
        obj.extra_querystring = self.get_extra_querystring(key=key, obj=obj)
        obj.next_url = self.get_next_url(key=key, obj=obj)
        return obj
