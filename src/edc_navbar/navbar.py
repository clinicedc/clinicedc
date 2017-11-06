
class Navbar:

    """A class to contain a list of navbar items. See NavbarItem.
    """

    def __init__(self, name=None, navbar_items=None):
        self.name = name
        self.navbar_items = navbar_items

    def __repr__(self):
        return f'{self.__class__.__name__}(name={self.name}, items=\'{self.navbar_items}\')'

    def iter(self):
        return iter(self.navbar_items)
