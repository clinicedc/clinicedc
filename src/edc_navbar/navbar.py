class NavbarError(Exception):
    pass


class Navbar:

    """A class to contain a list of navbar items. See NavbarItem.
    """

    def __init__(self, name=None, navbar_items=None):
        self.name = name
        self.items = navbar_items or []
        self.rendered_items = []
        self.codenames = {}

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name}, items='{self.items}')"

    def __iter__(self):
        return iter(self.items)

    def append_item(self, navbar_item=None):
        self.items.append(navbar_item)
        if not navbar_item.codename:
            raise NavbarError(f"Invalid codename. Got None. See {repr(navbar_item)}.")
        else:
            codename_tuple = (
                navbar_item.codename,
                f'Can access {" ".join(navbar_item.codename.split("_"))}',
            )
            self.codenames.update({navbar_item.codename: codename_tuple})

    def render(self, selected_item=None, request=None, **kwargs):
        """Renders the navbar.

        Note: usually called in NavbarViewMixin.
        """
        self.rendered_items = []
        for item in self.items:
            if item.codename and item.codename not in self.codenames:
                raise NavbarError(
                    f"Permission code is invalid. "
                    f"Expected one of {list(self.codenames.keys())}."
                    f" Got {item.codename}."
                )
            if not item.codename or (
                item.codename and request.user.has_perm(item.codename)
            ):
                self.rendered_items.append(
                    item.render(selected_item=selected_item, request=request, **kwargs)
                )

    def show_user_permissions(self, user=None):
        """Returns the permissions required to access this Navbar
        and True if the given user has such permissions.
        """
        permissions = {}
        for navbar_item in self.items:
            has_perm = {}
            has_perm.update({navbar_item.codename: user.has_perm(navbar_item.codename)})
            permissions.update({navbar_item.name: has_perm})
        return permissions
