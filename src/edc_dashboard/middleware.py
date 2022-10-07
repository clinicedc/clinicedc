from django.conf import settings

from .dashboard_templates import dashboard_templates
from .url_names import url_names
from .utils import insert_bootstrap_version


class DashboardMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            request.url_name_data
        except AttributeError:
            request.url_name_data = url_names.registry
        try:
            request.template_data
        except AttributeError:
            request.template_data = {}
        request.template_data = insert_bootstrap_version(**request.template_data)
        response = self.get_response(request)
        return response

    def process_view(self, request, *args):
        """Adds/Updates references to urls and templates."""
        template_data = dashboard_templates
        try:
            template_data.update(settings.DASHBOARD_BASE_TEMPLATES)
        except AttributeError:
            pass
        template_data = insert_bootstrap_version(**template_data)
        request.template_data.update(**template_data)

    def process_template_response(self, request, response):
        return response
