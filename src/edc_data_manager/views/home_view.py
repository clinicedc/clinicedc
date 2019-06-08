from django.conf import settings
from django.views.generic.base import TemplateView
from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin


class HomeView(EdcViewMixin, NavbarViewMixin, TemplateView):

    template_name = f"edc_data_manager/bootstrap{settings.EDC_BOOTSTRAP}/home.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "data_manager_home"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
