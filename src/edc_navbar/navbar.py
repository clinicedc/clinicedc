class NavbarError(Exception):
    pass


class Navbar:

    """A class to contain a list of navbar items. See NavbarItem.
    """

    def __init__(self, name=None, navbar_items=None):
        self.name = name
        self.items = navbar_items or []
        self.rendered_items = []
        self.permission_codenames = {}

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name}, items='{self.items}')"

    def __iter__(self):
        return iter(self.items)

    def append_item(self, navbar_item=None):
        self.items.append(navbar_item)
        if not navbar_item.permission_codename:
            raise NavbarError(
                f"Invalid permission_codename. Got None. See {repr(navbar_item)}."
            )
        else:
            permission_codename_tuple = (
                navbar_item.permission_codename,
                f'Can access {" ".join(navbar_item.permission_codename.split("_"))}',
            )
            self.permission_codenames.update(
                {navbar_item.permission_codename: permission_codename_tuple}
            )

    def render(self, selected_item=None, request=None, **kwargs):
        self.rendered_items = []
        for item in self.items:
            if (
                item.permission_codename
                and item.permission_codename not in self.permission_codenames
            ):
                raise NavbarError(
                    f"Permission code is invalid. "
                    f"Expected one of {list(self.permission_codenames.keys())}."
                    f" Got {item.permission_codename}."
                )
            if not item.permission_codename or (
                item.permission_codename
                and request.user.has_perm(item.permission_codename)
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
            has_perm.update(
                {
                    navbar_item.permission_codename: user.has_perm(
                        navbar_item.permission_codename
                    )
                }
            )
            permissions.update({navbar_item.name: has_perm})
        return permissions
