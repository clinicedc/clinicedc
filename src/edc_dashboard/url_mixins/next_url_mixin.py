from collections import OrderedDict

from .url_mixin import UrlMixin
from django.urls.base import reverse


class NextUrlMixin(UrlMixin):

    """A class to set `next_url`.

    `next_url` is  a qyerystring that follows the format of edc_base model
        admin mixin for redirecting the model admin on save
        to a url other than the default changelist.
        * Note: This is not a url but parameters need to reverse
                to one in the template.

    User is responsible for making sure the url_name can be reversed
    with the given parameters.

    * next_url_attrs:
        A dict with a list of querystring attrs to include in the next url.

        Format is:
            {key1: [param1, param2, ...], key2: [param1, param2, ...]}

    """
    next_url_name = None
    next_url_attrs = {}

    def __init__(self, **kwargs):
        self._next_kwargs = {}
        self.next_url_name = kwargs.get('next_url_name', self.next_url_name)
        self.next_url_attrs = kwargs.get('next_url_attrs', self.next_url_attrs)
        self.next_url_attrs.update(kwargs.get('extra_next_url_attrs', {}))

    def get_next_url(self, key=None, obj=None, **options):
        """Returns the next_url querystring for attrs in next_url_attrs."""
        options = options or {}
        options = OrderedDict(**options)
        options = self.sanitize_parameters(**options)
        try:
            kwargs = self.sanitize_parameters(**self.kwargs)
            options.update(kwargs)
        except AttributeError:
            options.update(**self.url_parameters(obj=obj))

        if not self.get_next_url_attrs().get(key):
            return ''
        parameters = {k: v for k, v in options.items()
                      if k in self.get_next_url_attrs().get(key)}
        self._next_kwargs = parameters
        return '{},{}&{}'.format(
            self.next_url_name, ','.join(parameters),
            self.urlify(**parameters))

    def get_next_url_attrs(self):
        return self.next_url_attrs

    def reverse(self):
        return reverse(self.next_url_name, kwargs=self._next_kwargs)
