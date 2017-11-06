from django.views.generic.base import ContextMixin

from edc_base.navbar.navbar_collection import site_navbars


class NavbarViewMixin(ContextMixin):

    navbar_selected_item = 'home'
    navbar_name = 'edc_base'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(**site_navbars.context(
            name=self.navbar_name,
            selected_item=self.navbar_selected_item))
        return context
