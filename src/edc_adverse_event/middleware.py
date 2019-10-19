from django.conf import settings
from edc_dashboard import insert_bootstrap_version

from .dashboard_templates import dashboard_templates
from .dashboard_urls import dashboard_urls


class DashboardMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, *args):
        request.url_name_data.update(**dashboard_urls)
        try:
            url_name_data = settings.LAB_DASHBOARD_URL_NAMES
        except AttributeError:
            pass
        else:
            request.url_name_data.update(**url_name_data)

        template_data = dashboard_templates
        try:
            template_data.update(settings.LAB_DASHBOARD_BASE_TEMPLATES)
        except AttributeError:
            pass
        template_data = insert_bootstrap_version(**template_data)
        request.template_data.update(**template_data)

    def process_template_response(self, request, response):
        if response.context_data:
            response.context_data.update(**request.url_name_data)
            response.context_data.update(**request.template_data)
        return response
