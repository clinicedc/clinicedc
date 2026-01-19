from django.conf import settings
from django.views.generic.base import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin

from ..constants import CENTRAL_LOCATION
from .auths_view_mixin import AuthsViewMixin


class HomeView(EdcViewMixin, NavbarViewMixin, AuthsViewMixin, TemplateView):
    template_name = "edc_pharmacy/home.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(CENTRAL_LOCATION=CENTRAL_LOCATION)
        return context
