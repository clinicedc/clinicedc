from django.apps import apps as django_apps
from django.views.generic.base import ContextMixin

from .site_navbars import site_navbars


class NavbarViewMixin(ContextMixin):

    navbar_selected_item = None
    navbar_name = None

    def get_context_data(self, **kwargs):
        """Add rendered navbar <navbar_name> to the context for
        this view.

        Also adds the "default" navbar.
        """
        context = super().get_context_data(**kwargs)
        return self.get_navbar_context_data(context)

    def get_navbar_context_data(self, context):
        navbar = site_navbars.get_navbar(name=self.navbar_name)
        navbar.render(selected_item=self.navbar_selected_item, request=self.request)
        app_config = django_apps.get_app_config("edc_navbar")
        default_navbar_name = app_config.default_navbar_name

        if default_navbar_name and self.navbar_name != default_navbar_name:
            default_navbar = site_navbars.get_navbar(name=default_navbar_name)
            default_navbar.render(
                selected_item=self.navbar_selected_item, request=self.request
            )
            context.update(
                default_navbar=default_navbar, default_navbar_name=default_navbar_name
            )
        context.update(navbar=navbar)
        return context
