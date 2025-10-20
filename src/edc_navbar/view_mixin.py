from typing import Any

from .site_navbars import site_navbars
from .utils import get_default_navbar_name


class NavbarViewMixin:
    navbar_selected_item = None
    navbar_name = get_default_navbar_name()

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Add rendered navbar <navbar_name> to the context for
        this view.

        Also adds the "default" navbar.
        """
        kwargs = self.get_context_data_for_navbars(kwargs)
        return super().get_context_data(**kwargs)

    def get_navbar_name(self):
        return self.navbar_name

    def get_context_data_for_navbars(self, context) -> dict:
        navbar = site_navbars.get_navbar(name=self.get_navbar_name())
        navbar.set_active(self.get_navbar_selected(**context))
        context.update(navbar=navbar)
        default_navbar_name = get_default_navbar_name()
        if default_navbar_name and self.get_navbar_name() != default_navbar_name:
            default_navbar = site_navbars.get_navbar(name=default_navbar_name)
            default_navbar.set_active(self.navbar_selected_item)
            context.update(
                default_navbar=default_navbar, default_navbar_name=default_navbar_name
            )
        return context

    def get_navbar_selected(self, **kwargs) -> str:  # noqa: ARG002
        return self.navbar_selected_item
