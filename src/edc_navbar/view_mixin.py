from django.views.generic.base import ContextMixin

from .site_navbars import site_navbars


class NavbarViewMixin(ContextMixin):

    navbar_selected_item = None
    navbar_name = None
    default_navbar_name = 'default'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        navbar = site_navbars.get_navbar(name=self.navbar_name)
        rendered_navbar = navbar.render(
            selected_item=self.navbar_selected_item)

        if self.default_navbar_name and self.navbar_name != self.default_navbar_name:
            navbar = site_navbars.get_navbar(name=self.default_navbar_name)
            rendered_navbar += navbar.render(
                selected_item=self.navbar_selected_item)
        context.update(rendered_navbar=rendered_navbar)

        return context
