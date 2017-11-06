import os
import copy

from django.template.loader import render_to_string
from django.urls.base import reverse
from django.urls.exceptions import NoReverseMatch


class NavbarItemError(Exception):
    pass


class NavbarItem:

    """A class that represents a single item on a navbar.
    """

    template_name = 'edc_navbar/navbar_item.html'
    icon_folder = 'images'  # subfolder or static

    def __init__(self, name=None, title=None,
                 label=None, url_name=None, html_id=None,
                 fa_icon=None, icon=None, icon_width=None, icon_height=None):
        self.url_name = url_name
        self.name = name
        self.label = label
        self.title = title or self.label
        self.html_id = html_id or label
        self.fa_icon = fa_icon
        self.icon = icon
        self.icon_height = icon_height
        self.icon_width = icon_width
        if not label and not fa_icon:
            raise NavbarItemError(
                f'Specify a value for label and/or fa_icon. '
                f'Got None for both. See {repr(self)}')
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
        """Returns a dictionary of context data.
        """
        context = copy.copy(self.__dict__)
        if context.get('icon'):
            icon = context.get('icon')
            context.update(icon=os.path.join(self.icon_folder, icon))
        context.update(**kwargs)
        if selected_item == self.name:
            context.update(active=True)
        return context

    def render(self, **kwargs):
        """Render to string the template and context data.
        """
        return render_to_string(
            template_name=self.template_name,
            context=self.get_context(**kwargs))
