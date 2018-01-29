
class NavbarError(Exception):
    pass


class Navbar:

    """A class to contain a list of navbar items. See NavbarItem.
    """

    def __init__(self, name=None, navbar_items=None):
        self.name = name
        self.items = navbar_items or []
        self.rendered_items = []

    def __repr__(self):
        return f'{self.__class__.__name__}(name={self.name}, items=\'{self.items}\')'

    def __iter__(self):
        return iter(self.items)

    def append_item(self, navbar_item=None):
        self.items.append(navbar_item)

    def render(self, selected_item=None, **kwargs):
        self.rendered_items = []
        for item in self.items:
            self.rendered_items.append(item.render(
                selected_item=selected_item, **kwargs))
