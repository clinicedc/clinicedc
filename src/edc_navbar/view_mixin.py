from django.apps import apps as django_apps
from django.views.generic.base import ContextMixin

from .site_navbars import site_navbars


class NavbarViewMixin(ContextMixin):

    navbar_selected_item = None
    navbar_name = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        app_config = django_apps.get_app_config('edc_navbar')
        navbar = site_navbars.get_navbar(name=self.navbar_name)
        navbar.render(selected_item=self.navbar_selected_item)

        if (app_config.default_navbar_name
                and self.navbar_name != app_config.default_navbar_name):
            default_navbar = site_navbars.get_navbar(
                name=app_config.default_navbar_name)
            default_navbar.render(
                selected_item=self.navbar_selected_item)

        context.update(
            navbar=navbar,
            default_navbar=default_navbar,
            default_navbar_name=app_config.default_navbar_name)

        return context
