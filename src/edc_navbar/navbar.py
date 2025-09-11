from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .exceptions import NavbarError

if TYPE_CHECKING:
    from django.contrib.auth.models import User

    from .navbar_item import NavbarItem


@dataclass
class Navbar:
    """A class to contain a list of navbar items. See NavbarItem."""

    name: str = None
    navbar_items: list[NavbarItem] = field(default_factory=list, init=False)

    def register(self, navbar_item: NavbarItem):
        if navbar_item in self.navbar_items:
            raise NavbarError(f"Duplicate navbar item. See {self}. Got{navbar_item.name}")
        self.navbar_items.append(navbar_item)

    @property
    def names(self) -> list[str]:
        return [navbar_item.name for navbar_item in self.navbar_items]

    def get(self, name: str) -> NavbarItem | None:
        try:
            navbar_item = [nb for nb in self.navbar_items if nb.name == name][0]
        except IndexError:
            navbar_item = None
        return navbar_item

    def set_active(self, name: str) -> None:
        if name:
            for navbar_item in self.navbar_items:
                navbar_item.active = True if navbar_item.name == name else False

    def show_user_permissions(self, user: User = None) -> dict[str, dict[str, bool]]:
        """Returns the permissions required to access this Navbar
        and True if the given user has such permissions.
        """
        permissions = {}
        for navbar_item in self.navbar_items:
            has_perm = {}
            has_perm.update({navbar_item.codename: user.has_perm(navbar_item.codename)})
            permissions.update({navbar_item.name: has_perm})
        return permissions
