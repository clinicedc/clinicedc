from django.urls.base import reverse
from django.urls.exceptions import NoReverseMatch
from django.template.loader import render_to_string


class NavbarItemError(Exception):
    pass


class NavbarItem:

    """A class that represents a single item on a navbar,
    e.g. name and url.
    """

    template_name = 'edc_navbar/navbar_item.html'

    def __init__(self, name=None, title=None,
                 label=None, url_name=None, html_id=None, fa_icon=None):
        self.url_name = url_name
        self.name = name
        self.label = label
        self.title = title or self.label
        self.html_id = html_id or label
        self.fa_icon = fa_icon
        if not label and not fa_icon:
            raise NavbarItemError(
                'Specify a value for label and/or fa_icon. Got None for both.')
        if not self.url_name:
            raise NavbarItemError(
                f'\'url_name\' not specified. See {repr(self)}')
        else:
            try:
                self.reversed_url = reverse(self.url_name)
            except NoReverseMatch:
                raise NavbarItemError(
                    f'Invalid url name \'{self.url_name}\'. See {repr(self)} ')

    def __repr__(self):
        return (f'{self.__class__.__name__}(name={self.name}, '
                f'title={self.title}, url_name={self.url_name})')

    def __str__(self):
        return f'{self.name}, {self.label}'

    def get_context(self, selected_item=None, **kwargs):
        context = self.__dict__
        context.update(**kwargs)
        if selected_item == self.name:
            context.update(active=True)
        return context

    def render(self, **kwargs):
        return render_to_string(
            template_name=self.template_name,
            context=self.get_context(**kwargs))


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
