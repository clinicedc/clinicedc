import copy

from .base import Base


class NextUrlMixin(Base):

    """User is responsible for making sure the url_name can be reversed
    with the given parameters.

    For example:

        url(r'^dashboard/(?P<subject_identifier>' + subject_identifier + ')/',
    """

    dashboard_url = 'dashboard_url'

    def get_next_url(self, key=None, **options):
        """Returns the next_url querystring segment."""
        options.update(**self.kwargs)
        parameters = self.get_next_url_parameters(key, **options)
        if not parameters:
            return ''
        # convert model instances to uuid string, everything else to str
        copied_parameters = copy.copy(parameters)
        for key, value in copied_parameters.items():
            try:
                if value.id:
                    value = str(value.id)
            except AttributeError:
                value = str(value)
            parameters[key] = value
        return '{},{}&{}'.format(
            self.dashboard_url, ','.join(parameters),
            '&'.join(['='.join(z) for z in list(parameters.items())]))

    def get_next_url_parameters(self, key, **options):
        parameters = {k: v for k, v in options.items() if k in self.next_url_parameters.get(key)}
        return {k: v for k, v in parameters.items() if v}

    @property
    def next_url_parameters(self):
        return {}
