from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from django.core.management.color import color_style
from django.urls import NoReverseMatch
from django.urls.base import reverse

from edc_dashboard.url_names import InvalidDashboardUrlName, url_names

if TYPE_CHECKING:
    from django.contrib.auth.models import User

style = color_style()


@dataclass
class NavbarItem:
    """A class that represents a single item on a navbar."""

    name: str = field(default=None, compare=True)
    title: str = field(default=None)
    label: str | None = field(default=None)
    codename: str = field(default=None)
    url_name: str = field(default=None)
    no_url_namespace: bool = field(default=None)
    fa_icon: str | None = field(default=None)
    disabled: str = field(default="disabled")

    active: bool = field(default=None)

    template_name: str = field(
        default="edc_navbar/navbar_item.html",
        repr=False,
    )

    def __post_init__(self):
        self.title = self.title or self.label or self.name.title()  # the anchor title

    def get_url(self, raise_exception: bool | None = None) -> str | None:
        try:
            url = reverse(self.real_url_name)
        except NoReverseMatch:
            url = None
            if raise_exception:
                raise
        return url

    @property
    def real_url_name(self) -> str:
        try:
            url_name = url_names.get(self.url_name)
        except InvalidDashboardUrlName:
            url_name = self.url_name.split(":")[1] if self.no_url_namespace else self.url_name
        return url_name

    def set_disabled(self, user: User | None = None):
        if user and user.has_perm(self.codename):
            self.disabled = ""
