from django.views.generic.base import TemplateView
from edc_dashboard.utils import get_bootstrap_version
from edc_dashboard.view_mixins import EdcViewMixin


class HomeView(EdcViewMixin, TemplateView):
    template_name = f"edc_appointment/bootstrap{get_bootstrap_version()}/home.html"
