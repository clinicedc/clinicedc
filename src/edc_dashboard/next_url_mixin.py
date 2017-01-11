import copy

from collections import OrderedDict


class NextUrlMixin:

    """User is responsible for making sure the url_name can be reversed
    with the given parameters.

    * next_url_attrs and extra_querystring_attrs:
        Format is:
            {key1: [param1, param2, ...], key2: [param1, param2, ...]}

    """

    next_url_name = 'listboard_url'
    extra_querystring_attrs = {}
    next_url_attrs = {}
    url_instance_attrs = []  # a list of attr names. Only these are available, see `url_parameters`

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
        attrs = self.next_url_attrs.get(key)
        if not attrs:
            return ''
        parameters = {k: v for k, v in options.items() if k in self.next_url_attrs.get(key)}
        return '{},{}&{}'.format(
            self.next_url_name, ','.join(parameters),
            self.urlify(**parameters))

    def get_extra_querystring(self, key=None, obj=None):
        """Returns a querystring for attrs in extra_querystring_attrs."""
        parameters = OrderedDict()
        for k, v in self.url_parameters(obj=obj).items():
            if k in self.extra_querystring_attrs.get(key, {}):
                parameters.update({k: v})
        return self.urlify(**parameters)

    def url_parameters(self, obj=None, **options):
        """Prepares a dictionary of parameters available to next_url or extra_querystring."""
        options = OrderedDict(**options)
        for attr in self.url_instance_attrs:
            try:
                assert self._mocked_object
            except AttributeError:
                try:
                    value = getattr(obj, attr)
                except AttributeError:
                    try:
                        value = getattr(self, attr)
                    except AttributeError as e:
                        try:
                            obj._mocked_object
                            value = None
                        except AttributeError:
                            raise ValueError(e)
            else:
                value = None
            options.update({attr: value or ''})
        return self.sanitize_parameters(**options)

    def sanitize_parameters(self, **parameters):
        """Converts model instances to uuid string, everything else to str"""
        copied = copy.copy(parameters)
        for key, value in parameters.items():
            try:
                if value.id:
                    value = str(value.id)
            except AttributeError:
                if value:
                    value = str(value)
            copied[key] = value or ''
        return copied

    def urlify(self, **parameters):
        """Converts dict to a url querystring."""
        return '&'.join(['='.join(z) for z in list(parameters.items())])
