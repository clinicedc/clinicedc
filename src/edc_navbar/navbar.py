from __future__ import annotations

from typing import TYPE_CHECKING

from .exceptions import NavbarError

if TYPE_CHECKING:
    from .navbar_item import NavbarItem


class Navbar:

    """A class to contain a list of navbar items. See NavbarItem."""

    def __init__(self, name: str = None, navbar_items: list[NavbarItem] = None):
        self.name: str = name
        self.navbar_items: list[NavbarItem] = navbar_items or []
        self.rendered_items: list[NavbarItem] = []
        self.codenames = {}

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name}, items='{self.navbar_items}')"

    def __iter__(self):
        return iter(self.navbar_items)

    def append_item(self, navbar_item: NavbarItem = None):
        self.navbar_items.append(navbar_item)
        if not navbar_item.codename:
            raise NavbarError(f"Invalid codename. Got None. See {repr(navbar_item)}.")
        else:
            codename_tuple = (
                navbar_item.codename,
                f'Can access {" ".join(navbar_item.codename.split("_"))}',
            )
            self.codenames.update({navbar_item.codename: codename_tuple})

    def render(self, selected_item: list[NavbarItem] = None, request=None, **kwargs):
        """Renders the navbar.

        Note: usually called in NavbarViewMixin.
        """
        self.rendered_items: list[NavbarItem] = []
        for item in self.navbar_items:
            if item.codename and item.codename not in self.codenames:
                raise NavbarError(
                    f"Permission code is invalid. "
                    f"Expected one of {list(self.codenames.keys())}."
                    f" Got {item.codename}."
                )
            if not item.codename or (item.codename and request.user.has_perm(item.codename)):
                self.rendered_items.append(
                    item.render(selected_item=selected_item, request=request, **kwargs)
                )

    def show_user_permissions(self, user=None) -> dict[str, dict[str, bool]]:
        """Returns the permissions required to access this Navbar
        and True if the given user has such permissions.
        """
        permissions = {}
        for navbar_item in self.navbar_items:
            has_perm = {}
            has_perm.update({navbar_item.codename: user.has_perm(navbar_item.codename)})
            permissions.update({navbar_item.name: has_perm})
        return permissions
