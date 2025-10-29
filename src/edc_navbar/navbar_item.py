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
    url_names_key: str | None = field(
        default=None
    )  # must be valid key in url_names dictionary
    url_with_namespace: str | None = field(default=None)
    url_without_namespace: str | None = field(default=None)
    fa_icon: str | None = field(default=None)
    disabled: str | None = field(default="disabled")

    active: bool = field(default=None)

    template_name: str = field(
        default="edc_navbar/navbar_item.html",
        repr=False,
    )

    def __post_init__(self):
        self.title = self.title or self.label or self.name.title()  # the anchor title
        if self.url_with_namespace and ":" not in self.url_with_namespace:
            raise InvalidDashboardUrlName(
                f"Invalid url_with_namespace. Got {self.url_with_namespace}"
            )

    def get_url(self, raise_exception: bool | None = None) -> str | None:
        url = (
            self.url_without_namespace
            or self.url_with_namespace
            or url_names.get(self.url_names_key)
        )
        try:
            url = reverse(url)
        except NoReverseMatch as e:
            if raise_exception:
                errmsg = (
                    f"Reverse for Navbar url not found. Tried {url}. "
                    f"See NavbarItem(name={self.name}"
                )
                if self.url_without_namespace == url:
                    errmsg = f"{errmsg}, url_without_namespace={self.url_without_namespace})."
                elif self.url_with_namespace == url:
                    errmsg = f"{errmsg}, url_with_namespace={self.url_with_namespace})."
                elif url_names.get(self.url_names_key) == url:
                    errmsg = f"{errmsg}, url_names_key={self.url_names_key})."
                raise NoReverseMatch(errmsg) from e
            url = None
        return url

    def set_disabled(self, user: User | None = None):
        if user and user.has_perm(self.codename):
            self.disabled = ""
