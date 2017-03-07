from collections import OrderedDict

from .url_mixin import UrlMixin


class ExtraQuerystringMixin(UrlMixin):

    """A class to set  `extra_querystring`.

    extra_querystring: any additional key,value pair need for model admin. For
        example, foreignkeys need a uuid to ensure they are filtered.

    * extra_querystring_attrs:
        Format is:
            {key1: [param1, param2, ...], key2: [param1, param2, ...]}

    """
    extra_querystring_attrs = {}

    def __init__(self, **kwargs):
        self.extra_querystring_attrs = kwargs.get(
            'extra_querystring_attrs', self.extra_querystring_attrs)
        self.extra_querystring_attrs.update(
            kwargs.get('extra_extra_querystring_attrs', {}))

    def get_extra_querystring(self, key=None, obj=None):
        """Returns a querystring segment of format key=value&key=value, etc ...

        The querystring includes the parameters listed in extra_querystring_attrs.get(key).

        Note: Any parameters must be listed in url_parameters_attrs to be made
            available to this method"""
        parameters = OrderedDict()
        for k, v in self.url_parameters(obj=obj).items():
            if k in self.get_extra_querystring_attrs().get(key, {}):
                parameters.update({k: v})
        return self.urlify(**parameters)

    def get_extra_querystring_attrs(self):
        return self.extra_querystring_attrs
