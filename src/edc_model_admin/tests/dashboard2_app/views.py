from edc_dashboard.view_mixins import EdcViewMixin
from django.views.generic.base import TemplateView


class DashboardView(EdcViewMixin, TemplateView):

    template_name = "dashboard2.html"
