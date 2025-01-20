from django.views.generic.base import TemplateView
from edc_dashboard.view_mixins import EdcViewMixin


class HomeView(EdcViewMixin, TemplateView):
    template_name = "edc_appointment/home.html"
