from django.views.generic.base import ContextMixin

from .site_navbars import site_navbars


class NavbarViewMixin(ContextMixin):

    navbar_selected_item = None
    navbar_name = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rendered_navbar = []
        navbar = site_navbars.get_navbar(name=self.navbar_name)
        for item in navbar:
            rendered_navbar.append(item.render(
                selected_item=self.navbar_selected_item))
        context.update(rendered_navbar=rendered_navbar)
        return context
