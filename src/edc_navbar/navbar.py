
class NavbarError(Exception):
    pass


class Navbar:

    """A class to contain a list of navbar items. See NavbarItem.
    """

    def __init__(self, name=None, navbar_items=None):
        self.name = name
        self.items = navbar_items or []

    def __repr__(self):
        return f'{self.__class__.__name__}(name={self.name}, items=\'{self.items}\')'

    def __iter__(self):
        return iter(self.items)

    def append_item(self, navbar_item=None):
        self.items.append(navbar_item)

#     def render(self, navbar_item_selected=None):
#         rendered = []
#         for navbar_item in self.items:
#             rendered.append()
#             active = 'active' if navbar_item_selected == navbar_item.name else ''
#             rendered = (
#                 f'<li id="li-topbar-{navbar_item.html_id}"'
#                 f'class="{active}">'
#                 f'<a title="{navbar_item.title}"'
#                 f'href="{navbar_item.reversed_url}">')
#             if self.fa_icon:
#                 rendered + f'<i class="fa {{self.fa_icon}} fa-fw"></i>'
#                     {% if navbar_item.fa_icon %}
#                        <i class="fa {{navbar_item.fa_icon}} fa-fw"></i>
#                     {% endif %}
#                     {% if navbar_item.label %}
#                        {{ navbar_item.label|title }}
#                     {% endif %}
#                 </a>
#             </li>
#
