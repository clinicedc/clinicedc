from django.apps import apps as django_apps


class NavbarError(Exception):
    pass


class NavbarItem:

    """A class that represents a single item on a navbar,
    e.g. name and url.
    """

    app_config_name = None

    def __init__(self, name=None, title=None,
                 label=None, url_name=None, html_id=None, fa_icon=None):
        self.url_name = url_name
        self.name = name
        self.label = label
        self.title = title or self.label
        self.html_id = html_id or label
        self.fa_icon = fa_icon
        if not label and not fa_icon:
            raise NavbarError(
                'Specify a value for label and/or fa_icon. Got None for both.')

    def __repr__(self):
        return (f'{self.__class__.__name__}(name={self.name}, title={self.title})')

    def __str__(self):
        return f'{self.name}, {self.label}'

#     @property
#     def url_name(self):
#         if not self._url_name:
#             self._url_name = getattr(self.app_config, self.app_config_attr)
#         return self._url_name
#
#     @property
#     def app_config(self):
#         if not self._app_config:
#             try:
#                 self._app_config = django_apps.get_app_config(
#                     self.app_config_name)
#             except LookupError as e:
#                 raise NavbarError(f'Invalid {repr(self)}. Got {e}')
#         return self._app_config
