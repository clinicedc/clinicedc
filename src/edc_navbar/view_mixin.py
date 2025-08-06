from typing import Any

from django.apps import apps as django_apps

from .get_default_navbar import get_default_navbar
from .site_navbars import site_navbars


class NavbarViewMixin:
    navbar_selected_item = None
    navbar_name = get_default_navbar()

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Add rendered navbar <navbar_name> to the context for
        this view.

        Also adds the "default" navbar.
        """
        kwargs = self.get_navbar_context_data(kwargs)
        return super().get_context_data(**kwargs)

    def get_navbar_name(self):
        return self.navbar_name

    def get_navbar_context_data(self, context) -> dict:
        navbar = site_navbars.get_navbar(name=self.get_navbar_name())
        navbar.set_active(self.get_navbar_selected(**context))
        context.update(navbar=navbar)
        app_config = django_apps.get_app_config("edc_navbar")
        default_navbar_name = app_config.default_navbar_name
        if default_navbar_name and self.get_navbar_name() != default_navbar_name:
            default_navbar = site_navbars.get_navbar(name=default_navbar_name)
            default_navbar.set_active(self.navbar_selected_item)
            context.update(
                default_navbar=default_navbar, default_navbar_name=default_navbar_name
            )
        return context

    def get_navbar_selected(self, **kwargs) -> str:
        return self.navbar_selected_item
