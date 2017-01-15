import copy

from collections import OrderedDict


class UrlMixin:

    """
    * url_instance_attrs: an explicit list of attrnames available to url building methods.

    Prevents `url_parameters` from accessing an attribute that may not be ready
    or not wanted to be available for urls.
    """

    url_instance_attrs = []

    def get_url_instance_attrs(self):
        return self.url_instance_attrs

    def url_parameters(self, obj=None, **options):
        """Prepares a dictionary of parameters available to  the class."""
        options = OrderedDict(**options)
        for attr in self.get_url_instance_attrs():
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
