from __future__ import annotations

import copy

from django.core.management.color import color_style
from django.template.loader import render_to_string
from django.urls.base import reverse
from django.urls.exceptions import NoReverseMatch
from edc_dashboard.url_names import InvalidDashboardUrlName, url_names
from edc_dashboard.utils import get_bootstrap_version

from .exceptions import NavbarItemError

style = color_style()


class NavbarItem:

    """A class that represents a single item on a navbar."""

    template_name = f"edc_navbar/bootstrap{get_bootstrap_version()}/navbar_item.html"

    def __init__(
        self,
        name: str = None,
        title: str = None,
        label: str | None = None,
        alt: str | None = None,
        url_name: str = None,
        html_id=None,
        glyphicon: str = None,
        fa_icon: str | None = None,
        icon: str = None,
        icon_width=None,
        icon_height=None,
        no_url_namespace=None,
        active=None,
        codename: str = None,
    ):
        self._reversed_url = None
        self._url_name = None
        self.active = active
        self.alt = alt or label or name

        if fa_icon and fa_icon.startswith("fa-"):
            self.fa_icon = f"fa-solid {fa_icon}"
        else:
            self.fa_icon = fa_icon

        self.glyphicon = glyphicon
        self.html_id = html_id or name
        self.icon = icon
        self.icon_height = icon_height
        self.icon_width = icon_width
        self.label = label
        self.name: str = name
        self.no_url_namespace = no_url_namespace
        self.title = title or self.label or name.title()  # the anchor title
        self.url_name = url_name
        self.codename: str = codename

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(name={self.name}, "
            f"title={self.title}<url_name={self.url_name}>)"
        )

    def __str__(self):
        return f"{self.name}<url={self.url_name}>"

    def get_context(self, selected_item=None, **kwargs):
        """Returns a dictionary of context data."""
        context = copy.copy(self.__dict__)
        context.update(reversed_url=self.reversed_url, url_name=self.url_name)
        context.update(**kwargs)

        if selected_item == self.name or self.active:
            context.update(active=True)
        return context

    def render(self, request=None, **kwargs):
        """Render to string the template and context data.

        If permission codename is specified, check the user
        has permissions. If not return a disabled control.
        """
        context = self.get_context(**kwargs)
        if not self.codename:
            context.update(has_navbar_item_permission=True)
        else:
            context.update(has_navbar_item_permission=request.user.has_perm(self.codename))
        return render_to_string(template_name=self.template_name, context=context)

    @property
    def url_name(self):
        return self._url_name

    @url_name.setter
    def url_name(self, value):
        try:
            self._url_name = url_names.get(value)
        except InvalidDashboardUrlName:
            self._url_name = value.split(":")[1] if self.no_url_namespace else value
        if not self._url_name:
            raise NavbarItemError(f"'url_name' not specified. See {repr(self)}")

    @property
    def reversed_url(self):
        reversed_url = "#"
        if self.url_name != "#":
            try:
                reversed_url = reverse(self.url_name)
            except NoReverseMatch:
                # broadcast as Error in system_checks
                pass
        return reversed_url
