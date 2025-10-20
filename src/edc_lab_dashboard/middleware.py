from django.conf import settings
from edc_lab.constants import SHIPPED

from .dashboard_templates import dashboard_templates
from .dashboard_urls import dashboard_urls


class DashboardMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, *args):
        try:
            request.url_name_data  # noqa: B018
        except AttributeError:
            request.url_name_data = {}
        lab_dashboard_urls = getattr(settings, "LAB_DASHBOARD_URL_NAMES", {})
        dashboard_urls.update(**lab_dashboard_urls)
        request.url_name_data.update(**dashboard_urls)

        try:
            request.template_data  # noqa: B018
        except AttributeError:
            request.template_data = {}
        template_data = getattr(settings, "LAB_DASHBOARD_BASE_TEMPLATES", {})
        template_data.update(**dashboard_templates)
        request.template_data.update(**template_data)

    def process_template_response(self, request, response):
        if response.context_data:
            response.context_data.update(**request.url_name_data)
            response.context_data.update(**request.template_data)
            response.context_data.update(SHIPPED=SHIPPED)
        return response
